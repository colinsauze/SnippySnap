import re
import os
import base64
import json
from lxml import etree
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.request import Request
import api.views

from transcriptions import models
from transcriptions import tasks


def getLoginStatus(request):
    if request.user.is_authenticated:
        return request.user.username
    else:
        return None

def getTotalPages(total_hits, page_size):
    total_pages = int(total_hits/page_size)
    if total_hits%page_size != 0:
        total_pages += 1
    return total_pages

def getCurrentPage(offset, page_size):
    if offset == 0:
        return 1
    else:
        return int(offset/page_size) + 1

def getNextPageLink(query_dict, current_page, page_size):
    if '_show' in query_dict:
        del query_dict['_show']
    query_dict['offset'] = current_page*page_size
    return query_dict

def getPreviousPageLink(query_dict, current_page, page_size):
    if '_show' in query_dict:
        del query_dict['_show']
    query_dict['offset'] = (current_page-2)*page_size
    return query_dict

def getFirstPageLink(query_dict):
    if '_show' in query_dict:
        del query_dict['_show']
    query_dict['offset'] = 0
    return query_dict

def getLastPageLink(query_dict, total_pages, page_size):
    if '_show' in query_dict:
        del query_dict['_show']
    query_dict['offset'] = (total_pages-1)*page_size
    return query_dict

def getPageSelectLink(query_dict):
    if '_show' in query_dict:
        del query_dict['_show']
    if 'offset' in query_dict:
        del query_dict['offset']
    return query_dict

def getSearchLink(query_dict, model):
    if '_sort' in query_dict:
        del query_dict['_sort']
    if 'offset' in query_dict:
        del query_dict['offset']
    if 'limit' in query_dict:
        del query_dict['limit']
    if '_advanced' in query_dict:
        del query_dict['_advanced']
    query_dict['model'] = model
    return query_dict

def processValidationErrors(log):
    errors = []
    for i in range(0, len(log)):
        error = str(log[i])
        error = error.replace('<string>:', 'Error in line ').replace('{http://www.tei-c.org/ns/1.0}', '').replace('0:ERROR:SCHEMASV:SCHEMAV_ELEMENT_CONTENT:', '')
        errors.append(error)
    return errors


def getProjectFilters(project):
    query = Q()
    query &= Q(('verse__language', 'grc'))
    query &= Q(('verse__work__id', 'NT_B04'))
    transcription_list = ['basetext', 'P2', 'P5', 'P6', 'P22', 'P28', 'P36', 'P39', 'P44', 'P45', 'P52', 'P55', 'P59', 'P60', 'P63', 'P66', 'P75', 'P76', 'P80', 'P84', 'P90', 'P93', 'P95', 'P106', 'P107', 'P108', 'P109', 'P119', 'P120', 'P121', 'P122', 'P128', '01', '02', '03', '04', '05', '05S', '07', '011', '017', '019', '022', '024', '026', '028', '029', '032', '032S', '033', '037', '038', '041', '044', '045', '050', '054', '060', '063', '065', '068', '070', '078', '083', '086', '087', '091', '0109', '0127', '0141', '0145', '0162', '0210', '0211', '0216', '0217', '0218', '0233', '0234', '0238', '0256', '0260', '0264', '0268', '0290', '0299', '0301', '0302', '0309', '1', '13', '18', '22', '33', '35', '69', '109', '118', '118S', '124', '138', '157', '168', '173', '209', '213', '213S', '226', '249', '265', '295', '317', '333', '333S', '346', '357', '377', '382', '397', '430', '543', '544', '565', '565S', '579', '597', '732', '788', '792', '799', '807', '821', '826', '828', '841', '869', '884', '892S', '865', '892', '983', '992', '994', '994S', '1009', '1010', '1010S', '1014', '1029', '1071', '1079', '1093', '1128', '1128S', '1192', '1210', '1219', '1230', '1241', '1242', '1253', '1278', '1293', '1319', '1320', '1321', '1344', '1424', '1463', '1546', '1561', '1571', '1571S', '1582', '1582S', '1654', '1689', '1788', '1797', '2106', '2192', '2193', '2193S', '2223', '2372', '2411', '2561', '2561S', '2575', '2585', '2615', '2680', '2713', '2718', '2766', '2768', '2786', '2790', '2886', 'L5', 'L17', 'L32', 'L60', 'L141', 'L141S', 'L252', 'L253', 'L329', 'L335', 'L387', 'L425', 'L638', 'L640', 'L640S', 'L663', 'L704', 'L704S', 'L735', 'L770', 'L847', 'L1000', 'L1000S', 'L1073', 'L1075', 'L1076', 'L1076S', 'L1077', 'L1082', 'L1086', 'L1091', 'L1091S', 'L1096', 'L1100', 'L1552', 'L1692', 'L1692S', 'L1692S2']
    subquery = Q()
    for item in transcription_list:
        subquery |= Q(('verse__transcription_siglum', item))
    query &= subquery
    return query


def home(request):
    post_login_url = request.path + '?' + request.GET.urlencode()
    login_details = getLoginStatus(request)

    data = {
            'login_status': login_details,
            'post_login_url': post_login_url,
            'post_logout_url': '/transcriptions'
        }
    data['page_title'] = 'Transcription Home Page'
    return render(request, 'transcriptions/home.html', data)

def upload(request):
    post_login_url = request.path + '?' + request.GET.urlencode()
    login_details = getLoginStatus(request)

    data = {
            'login_status': login_details,
            'post_login_url': post_login_url,
            'post_logout_url': '/transcriptions'
        }
    if not login_details:
        data['page_title'] = 'Transcription Validator'
        return render(request, 'transcriptions/validate.html', data)
    data['page_title'] = 'Transcription Uploader'
    return render(request, 'transcriptions/upload.html', data)


@ensure_csrf_cookie
def search(request):
    post_login_url = request.path + '?' + request.GET.urlencode()
    login_details = getLoginStatus(request)

    data = {
            'page_title': 'Search Transcriptions',
            'login_status': login_details,
            'post_login_url': post_login_url,
            'post_logout_url': '/transcriptions'
        }
    return render(request, 'transcriptions/search.html', data)


#validation function
def validate_xml (tree, filename):
    schema_directory = os.path.join(settings.BASE_DIR, 'transcriptions', 'schema')
    schema = etree.XMLSchema(etree.parse(os.path.join(schema_directory, 'TEI-NTMSS.xsd')))

    result = schema.validate(tree)
    log = schema.error_log
    results = {}
    if result == False:
        results['valid'] = False
        results['errors'] = processValidationErrors(log)
        results['filename'] = filename
    else:
        results['valid'] = True
        results['filename'] = filename
    return results



@ensure_csrf_cookie
@require_http_methods(["POST"])
@permission_required(['transcriptions.delete_privatetranscription',
                      'transcriptions.delete_privateverse',
                      'transcriptions.add_privatetranscription',
                      'transcriptions.add_privateverse',
                     ], raise_exception=True)
def index(request):
    filename = request.POST.get('file_name', None)
    project_id = request.POST.get('project_id', None)
    transcription_id = request.POST.get('transcription_id', None)
    base64file = request.POST.get('src', None)
    if base64file != None:
        meta, content = base64file.split(',', 1)
        ext_m = re.match("data:.*?/(.*?);base64", meta)
        if not ext_m:
            raise ValueError("Can't parse base64 file data ({})".format(meta))
        xml_string = base64.b64decode(content)
    else:
        xml_string = self.get_argument('xml', None)
        xml_string = unquote(xml_string)
    try:
        tree = etree.fromstring(xml_string);
    except:
        return HttpResponse('the file was not well formed xml', status=415)

    #now validate against our schema
    results = validate_xml(tree, filename)

    if results['valid'] == False:
        return HttpResponse('the file did not validate with the TEI-NTMSS schema', status=415)

    #else we have a valid XML file so we can continue to indexing
    corpus = request.POST.get('corpus', 'unknown')
    username = request.user.username
    document_type = request.POST.get('document_type', 'unknown')
    tei_parser = request.POST.get('tei_parser', None)
    tree = etree.fromstring(xml_string);
    book = tree.xpath('//tei:div[@type="book"]/@n', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
    #if you are not signed into a project you are not allowed to upload to public repos
    if not project_id:
        public_flag = False
    if not transcription_id:
        siglum = tree.xpath('//tei:title[@type="document"]/@n', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        language = tree.xpath('//tei:text/@xml:lang', namespaces={'tei': 'http://www.tei-c.org/ns/1.0',
                                                                  'xml': 'http://www.w3.org/XML/1998/namespace'})[0]
        transcription_id = '%s_%s_%s_%s' % (corpus.upper(), language.upper(), siglum, book)
        if not public_flag:
            transcription_id = '%s_%s' % (transcription_id, username)
    print(transcription_id)
    tasks.index_transcription.delay(xml_string.decode('utf-8'),
                                    corpus,
                                    transcription_id=transcription_id,
                                    document_type=document_type,
                                    tei_parser=tei_parser,
                                    username=username)

    return HttpResponse(transcription_id, status=200)






#TODO work out how to do this and project stuff from handler code



@require_http_methods(["POST"])
def validate(request):
    filename = request.POST.get('file_name', None)
    base64file = request.POST.get('src', None)
    if base64file != None:
        meta, content = base64file.split(',', 1)
        ext_m = re.match("data:.*?/(.*?);base64", meta)
        if not ext_m:
            raise ValueError("Can't parse base64 file data ({})".format(meta))
        real_content = base64.b64decode(content)
    else:
        real_content = request.POST.get('xml', None)
        real_content = unquote(real_content)
    try:
        tree = etree.fromstring(real_content);
    except:
        return HttpResponse('the file was not well formed xml', status=415)

    #now validate against our schema
    results = validate_xml(tree, filename)

    return JsonResponse(results)


def results(request):
    post_login_url = request.path + '?' + request.GET.urlencode()
    login_details = getLoginStatus(request)

    #we must get project regardless as we need if for filtering
#     if 'project' in request.session and request.session['project'] != None:
        #TODO: this must be done properly for now I am cheating since it is only for David
#        project = Project.objects.get(id=request.session['project'])
    project = 'ECM_04'
    project_filter = getProjectFilters(project)
#     else:
#         project = None
#         project_filter = None

    #wrap request in a rest-framework request and add user so we can make an api call
    api_request = Request(request)
    api_request.user = request.user

    data_dict = api.views.ItemList().get_objects(api_request, app='transcriptions', model='versereading', format='html', default_size=100, supplied_filter=project_filter)
    total_hits = data_dict['count']
    page_size = int(request.GET.get('limit', settings.REST_FRAMEWORK['PAGE_SIZE']))
    offset = int(data_dict['offset']) if 'offset' in data_dict else int(request.GET.get('offset', 0))
    current_page =  getCurrentPage(offset, page_size)
    total_pages= getTotalPages(total_hits, page_size)

    data = {
            'page_title': 'Search Results',
            'login_status': login_details,
            'post_login_url': post_login_url,
            'post_logout_url': '/transcriptions',
            'page_size': page_size,
            'page_options': [25, 50, 100],
            'current_page':  current_page,
            'total_pages': total_pages,
            'data': data_dict['results'],
            'page_select_link': '?%s' % getPageSelectLink(request.GET.copy()).urlencode(),
            'last_link': '?%s' % getLastPageLink(request.GET.copy(), total_pages, page_size).urlencode(),
            'previous_link': '?%s' % getPreviousPageLink(request.GET.copy(), current_page, page_size).urlencode(),
            'next_link': '?%s' % getNextPageLink(request.GET.copy(), current_page, page_size).urlencode(),
            'first_link': '?%s' % getFirstPageLink(request.GET.copy()).urlencode(),
            'search_query':  getSearchLink(request.GET.copy(), 'versereading').urlencode()

        }
    return render(request, 'transcriptions/results.html', data)
