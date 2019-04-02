import api.views
import json
import urllib
from collections import OrderedDict
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from rest_framework.request import Request
from rest_framework import parsers
from django.apps import apps
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
from api.serializers import SimpleSerializer
from citations.models import Project
from citations import models
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie

#this just selects the project on login if it can
def getProject(sender, user, request, **kwargs):
    try:
        projects = Project.objects.filter(online_transcribers=request.user.id) | Project.objects.filter(edition_transcribers=request.user.id)
        if len(projects) == 1:
            request.session['project'] = projects[0].id
    #TODO: should this redirect to project select if there is more than one to chose from?
    except:
        pass

user_logged_in.connect(getProject)

def getTargetSearchModel(model, field):
    if field.find('__') == -1:
        fields = model.get_fields()
        if field in fields:
            return [model, field, fields[field]]
        return None
    related_model = api.views.getRelatedModel(model, field, )
    related_fields = related_model.get_fields()
    if '__' in field and field.split('__')[1] in related_fields:
        field_type = related_fields[field.split('__')[1]]
        if field_type != 'ForeignKey':
            return [related_model, field.split('__')[1], field_type]
        else:
            return getTargetSearchModel(related_model, '__'.join(field.split('__')[1:]))
    else:
        return None

#used for populating the suggestion box in the search form
def getSearchValues(request, model):
    for key in request.GET.keys():
        field = key
    search_value = '%s*|i' % request.GET.get(field)
    target_data = getTargetSearchModel(apps.get_model('citations', model), key)
    query_tuple = api.views.getQueryTuple(target_data[2], target_data[1], search_value)
    query = Q(query_tuple)
    results = [getattr(x, target_data[1]) for x in target_data[0].objects.filter(query)]
    return JsonResponse(results, safe=False)


def getSearchFields(request, model):
    target = apps.get_model('citations', model)
    data = target.get_search_fields(inc_related=True)
    return JsonResponse(data, safe=False)

@ensure_csrf_cookie
def search(request, advanced=False):
    post_login_url = request.path + '?' + request.GET.urlencode()
    login_details = getLoginStatus(request)
    models = [{'id': 'author', 'label': 'authors'},
              {'id': 'work', 'label': 'works'},
              {'id': 'edition', 'label': 'edition'},
              {'id': 'citation', 'label': 'citations'} ]
    data = {
            'page_title': 'Citations Search',
            'login_status': login_details,
            'post_logout_url': '/citations',
            'post_login_url': post_login_url,
            'models': models,
            'advanced': advanced
        }
    if advanced:
        return render(request, 'citations/advancedsearch.html', data)
    else:
        return render(request, 'citations/search.html', data)

def sort_by_list(dict_, list_):
    for key in list_:
        dict_.move_to_end(key)


def getLoginStatus(request):
    if request.user.is_authenticated:
        return request.user.username
    else:
        return None

def getProjectFilters(project, model, model_instance):
    model_fields = model_instance.get_fields()
    query = Q()
    if project.public == False and 'private' in model:
        query &= Q(('project__id', project.id))
    if 'language' in model_fields and project.language != '':
        query &= Q(('language', project.language))
    if model == 'edition'and project.language != '':
        query &= Q(('work__language', project.language))

    #now filter on biblical book if relevant
    if model in ['citation', 'privatecitation'] and project.biblical_work:
        query &= Q(('biblical_work__id', project.biblical_work.id))

    #these are reverse manytomany filters (for author_ids)
    if len(project.author_ids.all()) > 0 and (model == 'author' or 'author' in model_fields):
        if model == 'author':
            query &= Q(('project__id', int(project.id)))
        else:
            query &= Q(('author__project__id', int(project.id)))
    return query

def addCircaToApproximateYearFields(model, data):
    if model in ['author', 'work']:
        for key in data:
            split_key = key.split('_')
            if len(split_key) > 1:
                if split_key[-1] == 'approximate':
                    if data[key]['value'] == True:
                        data[split_key[0]]['value'] = 'c%s' % data[split_key[0]]['value']

#changes item_fields and returns dependencies
def prepareLegacyCitationDependencyData(data, dependencies, item_fields):
    dep_pair_fields = ['dependencies_string', 'dependencies']
    if 'dependencies_string' in data and data['dependencies_string']['value'] == '':
        item_fields.remove('dependencies_string')
        dep_pair_fields.remove('dependencies_string')
    if 'dependencies_string' in dep_pair_fields and len(dependencies) == 0:
        dependencies = None
    return dependencies


#changes item fields - no return
def prepareLegacyCitationManuscriptData(data, item_fields):
    #manuscript_info is legacy string, manuscript_variants is a properly structured JSON field
    #but has not always been used appropriately
    ms_pair_fields = ['manuscript_info', 'manuscript_variants']
    if 'manuscript_info' in data and  data['manuscript_info']['value'] == '':
        item_fields.remove('manuscript_info')
        ms_pair_fields.remove('manuscript_info')
    #if there is no data for manuscript_variants delete it from our checklist
    #we will delete from item_fields later if necessary
    if 'manuscript_variants' in data and data['manuscript_variants']['value'] == None:
        ms_pair_fields.remove('manuscript_variants')
    #if we have data for manuscript_info but not manuscript_variants then delete
    #manuscript_variants from item_fields
    if len(ms_pair_fields) == 1 and 'manuscript_variants' not in ms_pair_fields:
        item_fields.remove('manuscript_variants')


#take our list of dictionaries that are our data and turn it into an ordered list of data with id as key
def refactorData(hit, data, item_fields):
    if 'biblical_reference' in data:
        data['biblical_reference']['value'] = '%s %d:%d' % (hit.biblical_work.name, hit.chapter, hit.verse)
    if 'language' in data:
        if data['language']['value'] == 'grc':
            data['language']['value'] = 'Greek'
        elif data['language']['value'] == 'lat':
            data['language']['value'] = 'Latin'
    for key in data:
        if 'BooleanField' in data[key]['field_type']:
            if data[key]['value'] == True:
                data[key]['value'] = '✓'
            else:
                data[key]['value'] = '✗'
        elif data[key]['field_type'] == 'ArrayField':
            if data[key]['value'] != None:
                data[key]['value'] = '; '.join(data[key]['value'])
            else:
                data[key]['value'] = ''
        elif data[key]['value'] == None:
            data[key]['value'] = ''

def cleanAndSortData(data, item_fields):
    for key in list(data): #needed in python 3.5
        if key not in item_fields:
            del data[key]
    sort_by_list(data, item_fields)

def convertToOrderedDict(data):
    ordered_data = OrderedDict()
    for entry in data:
        key = entry['id']
        del entry['id']
        ordered_data[key] = entry
    return ordered_data

def getItemViewReturnLink(query_dict, item_id):
    query_dict['_show'] = item_id
    return query_dict

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

def getBackLink(query_dict):
    if '_show' in query_dict:
        del query_dict['_show']
    return query_dict

def getPageSelectLink(query_dict):
    if '_show' in query_dict:
        del query_dict['_show']
    if 'offset' in query_dict:
        del query_dict['offset']
    return query_dict

def getNoSizeLink(query_dict):
    if '_show' in query_dict:
        del query_dict['_show']
    query_dict['offset'] = 0
    if 'limit' in query_dict:
        del query_dict['limit']
    return query_dict

def getNoSortLink(query_dict, page_size):
    if '_show' in query_dict:
        del query_dict['_show']
    query_dict['offset'] = 0
    query_dict['limit'] = page_size
    if '_sort' in query_dict:
        del query_dict['_sort']
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

def getApplyProjectFilterLink(query_dict):
    query_dict['_applyprojectfilter'] = True
    return query_dict

def getNoProjectFilterLink(query_dict):
    if '_applyprojectfilter' in query_dict:
        del query_dict['_applyprojectfilter']
    return query_dict

def getFilterFieldValue(field):
    filter_string = None
    try:
        filter_string = field['search']
    except:
        try:
            filter_string = field['id']
        except:
            filter_string = field
    return filter_string

def getFilterLabel(field, filter_field_labels):
    try:
        filter_field_labels.append(field['label'])
    except:
        try:
            filter_field_labels.append(field['id'])
        except:
            filter_field_labels.append(field)
    return filter_field_labels

def getFilterDetails(query_dict, fields):
    if '_show' in query_dict:
        del query_dict['_show']
    query_dict['offset'] = 0

    filter_field_labels = []
    remove_filter_required = False
    for field in fields:
        filter_string = getFilterFieldValue(field)
        if filter_string:
            if filter_string in query_dict:
                remove_filter_required = True
                del query_dict[filter_string]
                getFilterLabel(field, filter_field_labels)

    #filter button label code
    if len(filter_field_labels) == 1:
        remove_filter_button_label = 'Remove %s filter' % filter_field_labels[0].lower()
    elif len(filter_field_labels) > 1:
        remove_filter_button_label = 'Remove all filters'
    else:
        remove_filter_button_label = 'Remove filter'

    return (query_dict, remove_filter_button_label, remove_filter_required)

def getActualModel(model, project):
    if project:
        if model in ['citation', 'dependency'] and project.public == False:
            model = 'private%s' % model
    return model

#start of real views
@ensure_csrf_cookie
def index(request, select=None):
    """ This is a decision making function to deal with project selection if necessary.
        If we are not logged in at all it just shows the citations home page.
        If we are logged in and have a project selected for the session or we are only a member of
            one project it shows the project home page with a switch project button (because we might want to select None).
        If we are logged in are involved in more than one project and do not have a project selected for the session
            then it shows the project select page.
    """
    post_login_url = request.path + '?' + request.GET.urlencode()
    login_details = getLoginStatus(request)
    projects = Project.objects.filter(online_transcribers=request.user.id) | Project.objects.filter(edition_transcribers=request.user.id)
    citation_manager = request.user.groups.filter(name='citation_managers').exists()
    citation_editor = request.user.groups.filter(name='citation_editors').exists()

    if login_details is None:
        data = {'page_title': 'Citations Home',
                'login_status': login_details,
                'post_logout_url': '/citations',
                'post_login_url': post_login_url,
                'logged_in': False
            }
        return render(request, 'citations/index.html', data)

    #if we have asked to switch projects
    if select:
        data = {'projects': projects,
                'login_status': login_details,
                'post_logout_url': '/citations',
                'post_login_url': post_login_url,
                'page_title': 'Citations Project Select'
            }
        if 'project' in request.session:
            data['current_project'] = request.session['project']
        return render(request, 'citations/project_select.html', data)

    #if we have just selected a project
    if request.method == 'POST':

        if request.POST.get('project') != 'None':
            request.session['project'] = int(request.POST.get('project'))
        else:
            try:
                del request.session['project']
            except:
                pass
        try:
            project_string = Project.objects.get(id=request.session['project']).name
        except:
            project_string = ''

        data = {'page_title': 'Citations Home',
                'login_status': login_details,
                'post_logout_url': '/citations',
                'post_login_url': post_login_url,
                'switch_button': True,
                'switch_url': '/citations/projectselect?' + 'next=' + post_login_url,
                'project_name': project_string
            }

        if citation_manager:
            return render(request, 'citations/index_citation_manager.html', data)
        if citation_editor:
            return render(request, 'citations/index_citation_editor.html', data)
        return render(request, 'citations/index.html', data)

    if 'project' not in request.session and (len(projects) > 1 or (len(projects) == 1 and projects[0].public == False)):
        data = {'projects': projects,
                'login_status': login_details,
                'post_logout_url': '/citations',
                'post_login_url': post_login_url,
                'page_title': 'Citations Project Select'
                }
        return render(request, 'citations/project_select.html', data)

    data = {'page_title': 'Citations Home',
            'login_status': login_details,
            'post_logout_url': '/citations',
            'post_login_url': post_login_url,
            'logged_in': True,
            'switch_button': True,
            'switch_url': '/citations/projectselect?' + 'next=' + post_login_url
        }

    if (len(projects) == 1 and 'project' not in request.session):
        request.session['project'] = projects[0].id
        data['project_name'] = projects[0].name

    if 'project' in request.session and request.session['project'] \
            in [project.id for project in projects]:
        project = Project.objects.get(id=request.session['project'])
        data['project_name'] = project.name

    if citation_manager:
        return render(request, 'citations/index_citation_manager.html', data)

    if citation_editor:
        return render(request, 'citations/index_citation_editor.html', data)

    return render(request, 'citations/index.html', data)


def listView(request, model, results=False, patristics=False):
    #we must get project regardless as we need it for filtering
    if 'project' in request.session and request.session['project'] != None:
        #TODO: this may need looking at again. I think projects are retainined
        #accross apps in the session and send with the request regardless of app
        #this may need fixing by changing the names of project between apps
        try:
            project = Project.objects.get(id=request.session['project'])
        except:
            project = None
    else:
        project = None

    #the requested model is the model without any private prefix and is the one that is passed in the url
    #the model is the actual model we will use for working with the database (inc private prefix)
    requested_model = model
    model = getActualModel(requested_model, project)
    model_instance = apps.get_model('citations', model)

    if '_applyprojectfilter' in request.GET:
        filter_by_project = True
    else:
        filter_by_project = False

    #first make a project filter if there is a project
    if project != None:
        project_filter = getProjectFilters(project, model, model_instance)
    else:
        project_filter = None

    #wrap request in a rest-framework request and add user so we can make an api call
    api_request = Request(request)
    api_request.user = request.user

    #if we are filtering by project just get the project filtered data
    public = True
    if project and project.public == False:
        public = False
        filter_by_project = True

    if not results and filter_by_project:
        data_dict = api.views.ItemList().get_objects(api_request, app='citations', model=model, format='html', default_size=100, supplied_filter=project_filter)
        editable_ids = []
    else:
        #if we are not filtering by project get all the data and then all the ids that have editing permissions so we can put the edit links in the right places!
        data_dict = api.views.ItemList().get_objects(api_request, app='citations', model=model, format='html', default_size=100)
        try:
            editable_ids = model_instance.objects.all().filter(project_filter).values_list('id', flat=True)
        except:
            editable_ids = []

    if results == True and data_dict['count'] == 0:
        data = {
                'page_title': '%s Search Results' % requested_model.title(),
                'login_status': getLoginStatus(request),
                'post_logout_url': '/citations',
                'post_login_url': request.path + '?' + request.GET.urlencode(),
                'model': requested_model,
                'results': True,
                'search_query': getSearchLink(request.GET.copy(), model).urlencode()
                }
        advanced = request.GET.get('_advanced', None)
        if advanced and advanced == 'true':
            data['advanced'] = True;
        return render (request, 'citations/search_no_results.html', data)

    fields = model_instance.LIST_FIELDS
    total_hits = data_dict['count']
    page_size = int(request.GET.get('limit', settings.REST_FRAMEWORK['PAGE_SIZE']))
    offset = int(data_dict['offset']) if 'offset' in data_dict else int(request.GET.get('offset', 0))
    current_page =  getCurrentPage(offset, page_size)
    total_pages= getTotalPages(total_hits, page_size)
    no_filter_link, remove_filter_button_label, remove_filter_required  = getFilterDetails(request.GET.copy(), fields)

    data = {

            'data': data_dict['results'],
            'fields': fields,
            'current_page':  current_page,
            'total_pages': total_pages,
            'back_query': getBackLink(request.GET.copy()).urlencode(),
            'last_link': '?%s' % getLastPageLink(request.GET.copy(), total_pages, page_size).urlencode(),
            'previous_link': '?%s' % getPreviousPageLink(request.GET.copy(), current_page, page_size).urlencode(),
            'next_link': '?%s' % getNextPageLink(request.GET.copy(), current_page, page_size).urlencode(),
            'first_link': '?%s' % getFirstPageLink(request.GET.copy()).urlencode(),
            'page_select_link': '?%s' % getPageSelectLink(request.GET.copy()).urlencode(),
            'no_size_link': '?%s' % getNoSizeLink(request.GET.copy()).urlencode(),
            'no_sort_link': '?%s' % getNoSortLink(request.GET.copy(), page_size).urlencode(),
            'no_filter_link': '?%s' % no_filter_link.urlencode(),
            'remove_filter_required' : remove_filter_required,
            'remove_filter_button_label': remove_filter_button_label,
            'model': requested_model,
            'sort_value': request.GET.get('_sort', ''),
            'page_size': page_size,
            'page_options': [25, 50, 100],
            'login_status': getLoginStatus(request),
            'post_logout_url': '/citations',
            'post_login_url': request.path + '?' + request.GET.urlencode(),
            'editable_ids': editable_ids,
            'filter_by_project': filter_by_project,
            'public': public,
            }


    #add extra fields to the data if we are displaying search results
    if results == True:
        data['search_results'] = True
        advanced = request.GET.get('_advanced', None)
        if advanced and advanced == 'true':
            data['advanced'] = True;
        data['search_query'] = getSearchLink(request.GET.copy(), model).urlencode()
        data['project_name'] = project.name if project else '',#Project.objects.get(id=request.session['project']).name if 'project' in request.session else '',
        data['page_title'] = '%s Search Results' % requested_model.title()

    elif patristics == True:
        data['page_title'] = 'Seleted Patristic Citations'
        data['patristics_results'] = True

    else:
        data['page_title'] =  '%s List' % requested_model.title()
        data['project_name'] = project.name if project else ''#Project.objects.get(id=request.session['project']).name if 'project' in request.session else '',

    #sort out permissions
    if request.user.is_authenticated:
        #check we are working in a project or no editing allowed!
        if 'project' in request.session and request.session['project'] is not None:
            if request.user.has_perm('citations.add_%s' % model):
                data['add_perms'] = True
            else:
                data['add_perms'] = False
            if request.user.has_perm('citations.change_%s' % model):
                data['edit_perms'] = True
            else:
                data['edit_perms'] = False
            #check to see if we are eligible for a filter by project button
            if not results:
                if filter_by_project:
                    data['remove_project_filter_link'] = '?%s' % getNoProjectFilterLink(request.GET.copy()).urlencode()
                else:
                    data['apply_project_filter_link'] = '?%s' % getApplyProjectFilterLink(request.GET.copy()).urlencode()

    if requested_model in ['author', 'onlinecorpus', 'series']:
        return render (request, 'citations/list_base.html', data)
    else:
        return render (request, 'citations/list_%s.html' % requested_model, data)

def itemView (request, model, id):

    #we must get project regardless as we need if for filtering
    if 'project' in request.session and request.session['project'] != None:
        project = Project.objects.get(id=request.session['project'])
    else:
        project = None

    #the requested model is the model without any private prefix and is the one that is passed in the url
    #the model is the actual model we will use for working with the database (inc private prefix)
    requested_model = model
    model = getActualModel(requested_model, project)
    model_instance = apps.get_model('citations', model)

    filter_by_project = False
    if project and project.public == False:
        filter_by_project = True
    #first make a project filter if there is a project
    if project:
        project_filter = getProjectFilters(project, model, model_instance)
    else:
        project_filter = None

    #wrap request in a rest-framework request and add user so we can make an api call
    api_request = Request(request)
    api_request.user = request.user
    if filter_by_project:
        try:
            hit = api.views.ItemDetail().get_item(api_request, app='citations', model=model, pk=id, format='html', supplied_filter=project_filter)
        except:
            hit = None
    else:
        try:
            hit = api.views.ItemDetail().get_item(api_request, app='citations', model=model, pk=id, format='html')
        except:
            hit = None
    if not hit:
        return render (request, 'citations/error.html',
                        {'page_title': '403 error',
                         'login_status': getLoginStatus(request),
                         'post_logout_url': '/citations',
                         'post_login_url': request.path + '?' + request.GET.urlencode(),
                         'error_type': '403: incorrect permissions',
                         'error_message': 'You do not have permission to view this %s.' % model})
    data = convertToOrderedDict(hit.get_row_dict())
    addCircaToApproximateYearFields(model, data)

    item_fields = model_instance.ITEM_FIELDS[:]
    if requested_model == 'citation':
        dependencies = prepareLegacyCitationDependencyData(data, hit.dependencies.all(), item_fields)
        prepareLegacyCitationManuscriptData(data, item_fields)

    cleanAndSortData(data, item_fields)
    refactorData(hit, data, item_fields)

    return_data = {'data': data,
                   'page_title': requested_model.title(),
                   'model': requested_model,
                   'login_status': getLoginStatus(request),
                   'post_logout_url': '/citations',
                   'post_login_url': request.path + '?' + request.GET.urlencode(),
                   'project_name': project.name if project else '',
                   'back_query': getItemViewReturnLink(request.GET.copy(), id).urlencode()
                   }

    if requested_model == 'author':
        return_data['works'] = hit.works.all()
        return render (request, 'citations/item_author.html', return_data)
    elif requested_model == 'work':
        return_data['other_possible_authors'] = hit.other_possible_authors.all()
        return_data['edition'] = hit.editions.all()
        return_data['citations']= hit.citations.all()
        return render (request, 'citations/item_work.html', return_data)
    elif requested_model == 'edition':
        return_data['citations']= hit.citations.all()
        return render (request, 'citations/item_edition.html', return_data)
    elif model == 'citation':
        return_data['dependencies'] = dependencies
        return render (request, 'citations/item_citation.html', return_data)
    else:
        return render (request, 'citations/item_base.html', return_data)


def getRelations (model, item):
    relations = {}
    if model == 'author':
        relations['works_count'] = item.works.all().count()
        relations['works'] = item.works.all()[:100]
        relations['possible_works_count'] = models.Work.objects.filter(other_possible_authors__id = item.id).count()
        relations['possible_works'] = models.Work.objects.filter(other_possible_authors__id = item.id)[:100]
        relations['editions_count'] = models.Edition.objects.filter(work__author__id = item.id).count()
        relations['editions'] = models.Edition.objects.filter(work__author__id = item.id).select_related('work', 'series')[:100]
        relations['citations_count'] = models.Citation.objects.filter(work__author__id = item.id).count()
        relations['citations'] = models.Citation.objects.filter(work__author__id = item.id).select_related('work__author', 'work', 'biblical_work')[:100]
        relations['privatecitations_count'] = models.PrivateCitation.objects.filter(work__author__id = item.id).count()
        private_citations = models.PrivateCitation.objects.filter(work__author__id = item.id)
        relations['dependencies_count'] = item.dependency_set.all().count()
        relations['dependencies'] = item.dependency_set.all().select_related('citation', 'citation__work', 'citation__biblical_work', 'author', 'work', 'citation__work__author')[:100]
        relations['privatedependencies_count'] = item.privatedependency_set.all().count()
        relations['problem_works'] = list(private_citations.values_list('work__id', flat=True))
        relations['problem_works'].extend(list(item.privatedependency_set.all().values_list('work__id', flat=True)))
        relations['problem_editions'] = list(private_citations.values_list('edition__id', flat=True))
        return relations
    if model == 'work':
        relations['editions_count'] = item.editions.all().count()
        relations['editions'] = item.editions.all()[:100]
        relations['citations_count'] = item.citations.all().count()
        relations['citations'] = item.citations.all().select_related('work__author', 'work', 'biblical_work')[:100]
        relations['privatecitations_count'] = item.privatecitation_set.all().count()
        relations['problem_editions'] = list(item.privatecitation_set.all().values_list('edition__id', flat=True))
        relations['dependencies_count'] = item.dependency_set.all().count()
        relations['dependencies'] = item.dependency_set.all().select_related('citation', 'citation__work', 'citation__biblical_work', 'author', 'work', 'citation__work__author')[:100]
        relations['privatedependencies_count'] = item.privatedependency_set.all().count()
        return relations
    if model == 'edition':
        relations['citations_count'] = item.citations.all().count()
        relations['citations'] = item.citations.all()[:100]
        relations['privatecitations_count'] = item.privatecitation_set.all().count()
        return relations
    if model == 'series':
        relations['editions_count'] = item.editions.all().count()
        relations['editions'] = item.editions.all()[:100]
        return relations
    if model == 'onlinecorpus':
        relations['editions_count'] = item.editions.all().count()
        relations['editions'] = item.editions.all().select_related('work', 'series')[:100]
        relations['citations_count'] = item.citations.all().count()
        relations['citations'] = item.citations.all().select_related('work__author', 'work', 'biblical_work')[:100]
        relations['privatecitations_count'] = item.privatecitation_set.all().count()
        return relations
    return relations

def getRelationsOrder (model):
    if model == 'author':
        return ['works', {'label': 'Possible works', 'id': 'possible_works'}, 'editions', 'citations', {'label': 'Dependencies within Citations', 'id': 'dependencies'}]
    if model == 'work':
        return ['editions', 'citations', {'label': 'Dependencies within Citations', 'id': 'dependencies'}]
    if model == 'edition':
        return ['citations']
    if model == 'series':
        return ['editions']
    if model == 'onlinecorpus':
        return ['editions', 'citations']
    return []

@ensure_csrf_cookie
@login_required
def deleteItem (request, model, id):

    login_details = getLoginStatus(request)
    post_login_url = request.path + '?' + request.GET.urlencode()

    #sort out whether this is a private model or not first then check permissions
    model_label = model

    project = None
    project_filter = None
    if 'project' in request.session and request.session['project'] != None:
        project = Project.objects.get(id=request.session['project'])
        if model in ['citation', 'dependency'] and project.public == False:
            model = 'private%s' % model
            project_filter = Q(('project__id', project.id))

    if project is not None:

        if request.user.has_perm('citations.delete_%s' % model):

            # login_details = getLoginStatus(request)
            # post_login_url = request.path + '?' + request.GET.urlencode()

            # We are not generally restricting deleting to project settings
            # because only citation managers can do it and it would be very difficult with dependencies
            #the exception is with private citations where we need to restrict to project id
            try:
                hit = api.views.ItemDetail().get_item(request, app='citations', model=model, pk=id, format='html', supplied_filter=project_filter)
            except:
                return render (request, 'citations/error.html',
                            {'page_title': '404 error',
                             'login_status': login_details,
                             'post_logout_url': '/citations',
                             'post_login_url': post_login_url,
                             'error_type': '404: Item not found',
                             'error_message': 'The requested %s cannot be found in the database.' % model_label})




            return_data = {'data': hit,
                           'page_title': 'Delete %s' % model_label.title(),
                           'model': model,
                           'model_label': model_label,
                           'login_status': login_details,
                           'post_logout_url': '/citations',
                           'post_login_url': post_login_url,
                           'project_name': project.name if project else '',
                           'relations_order': getRelationsOrder(model),
                           'privatedeps': False
                           }
            return_data.update(getRelations(model, hit))
            if ('privatecitations_count' in return_data and return_data['privatecitations_count'] > 0) \
                    or ('privatedependencies_count' in return_data and return_data['privatedependencies_count'] > 0):
                return_data['privatedeps'] = True

            return render (request, 'citations/delete_%s.html' % model_label, return_data)

        else:
            return render (request, 'citations/error.html',
                        {'page_title': '403 error',
                         'error_type': '403: incorrect permissions',
                         'login_status': login_details,
                         'post_logout_url': '/citations',
                         'post_login_url': post_login_url,
                         'error_message': 'You do not have permission to delete this %s.' % model_label})
    else:
        return render (request, 'citations/error.html',
                        {'page_title': '403 error',
                         'error_type': '403: incorrect permissions',
                         'login_status': login_details,
                         'post_logout_url': '/citations',
                         'post_login_url': post_login_url,
                         'error_message': 'You do need to be logged into a project to delete this %s.' % model_label})

@ensure_csrf_cookie
@login_required
def editItem(request, model, id=None):

    login_details = getLoginStatus(request)
    post_login_url = request.path + '?' + request.GET.urlencode()

    #sort out whether this is a private model or not first then check permissions
    model_label = model

    project = None
    if 'project' in request.session and request.session['project'] != None:
        project = Project.objects.get(id=request.session['project'])
        if model in ['citation', 'dependency'] and project.public == False:
            model = 'private%s' % model

    if request.user.has_perm('citations.add_%s' % model) and request.user.has_perm('citations.change_%s' % model):
        project_filter = None
        if project != None:
            target = apps.get_model('citations', model)
            project_filter = getProjectFilters(project, model, target)
            project_json = JSONRenderer().render(SimpleSerializer(project).data).decode('utf-8')

            project_id = project.id

            query_dict = request.GET.copy()
            if id != None:
                query_dict['_show'] = id
            back_url_query = query_dict.urlencode()

            try:
                id_string = request.user.profile.display_name
            except:
                id_string = request.user.username

            if request.user.groups.filter(name='citation_managers').exists():
                group_name = 'citation_managers'
            elif request.user.groups.filter(name='citation_editors').exists():
                group_name = 'citation_editors'
            elif project and project.public == False and request.user.groups.filter(name='private_citation_managers').exists():
                group_name = 'private_citation_managers'
            else:
                group_name = None

            data = {
                       'page_title': 'Add/Edit %s' % model_label.title(),
                       'model': model,
                       'login_status': login_details,
                       'post_logout_url': '/citations',
                       'post_login_url': post_login_url,
                       'breadcrumb_model': model_label.title(),
                       'project_name': project.name,
                       'user': JSONRenderer().render({'id': request.user.id, 'id_string': id_string, 'group_name': group_name }).decode('utf-8'),
                       'project': project_json,
                       # 'project': project_id,
                       'back_query': back_url_query,
                       'permission_granted': False
                    }
            if id:
                data['item_id'] = int(id)
                try:
                    item_json = api.views.ItemDetail().get_item(request, app='citations', model=model, pk=id, format='json', supplied_filter=project_filter)
                    data['permission_granted'] = True
                except:
                    return render (request, 'citations/error.html',
                           {'page_title': '403 error',
                            'login_status': login_details,
                            'post_logout_url': '/citations',
                            'post_login_url': post_login_url,
                            'error_type': '403: incorrect permissions',
                            'error_message': 'You do not have permission to edit this data in this project. To switch projects return to the homepage.'})

            return render (request, 'citations/edit_%s.html' % model, data)

        else:
            return render (request, 'citations/error.html',
                           {'page_title': '403 error',
                            'login_status': login_details,
                            'post_logout_url': '/citations',
                            'post_login_url': post_login_url,
                            'error_type': '403: incorrect permissions',
                            'error_message': 'You do not have permission to edit this data while you are not logged in to a project. To select a project return to the homepage.'})
    else:
        return render (request, 'citations/error.html',
                        {'page_title': '403 error',
                         'login_status': login_details,
                         'post_logout_url': '/citations',
                         'post_login_url': post_login_url,
                         'error_type': '403: incorrect permissions',
                         'error_message': 'You do not have permission to edit this %s.' % model})
