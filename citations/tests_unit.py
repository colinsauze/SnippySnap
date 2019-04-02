from django.test import TestCase
from django.utils import timezone
from django.db.models import Q
from citations import models
from citations import views
from transcriptions import models as transcription_models
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.http import HttpRequest
import urllib
import json




class SearchHelperTests(TestCase):

    def test_getTargetSearchModel(self):

        key = 'work__author__abbreviation'
        result = views.getTargetSearchModel(models.Citation, key)
        self.assertEqual(result[0], models.Author)
        self.assertEqual(result[1], 'abbreviation')
        self.assertEqual(result[2], 'TextField')

        key = 'edition__work__author__abbreviation'
        result = views.getTargetSearchModel(models.Citation, key)
        self.assertEqual(result[0], models.Author)
        self.assertEqual(result[1], 'abbreviation')
        self.assertEqual(result[2], 'TextField')

        key = 'abbreviation'
        result = views.getTargetSearchModel(models.Work, key)
        self.assertEqual(result[0], models.Work)
        self.assertEqual(result[1], 'abbreviation')
        self.assertEqual(result[2], 'TextField')

        #test with junk data to make sure it returns None
        key = 'edition__abbreviation'
        result = views.getTargetSearchModel(models.Citation, key)
        self.assertEqual(result, None)

        key = 'junk'
        result = views.getTargetSearchModel(models.Citation, key)
        self.assertEqual(result, None)




    def test_getSearchValues(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        a1 = models.Author.objects.create(**a1_data)
        a2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA2',
                   'full_name': 'Test Author 2',
                   'language': 'lat'
                   }
        a2 = models.Author.objects.create(**a2_data)

        response = self.client.get('/citations/author/searchvalues/?abbreviation=t')
        expected_result = ['TA1', 'TA2']
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content,'utf-8'), expected_result)

        response = self.client.get('/citations/author/searchvalues/?abbreviation=A')
        expected_result = []
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content,'utf-8'), expected_result)

        response = self.client.get('/citations/citation/searchvalues/?work__author__abbreviation=t')
        expected_result = ['TA1', 'TA2']
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content,'utf-8'), expected_result)


    def test_getSearchFields(self):
        response = self.client.get('/citations/author/searchfields')

        expected_result = [{"label": "Abbreviation", "position": 0, "id": "abbreviation", "field_type": "TextField"},
                           {"label": "Biblindex identifiers", "position": 1, "id": "biblindex_identifiers", "field_type": "ArrayField"},
                           {"label": "Full Name", "position": 2, "id": "full_name", "field_type": "TextField"},
                           {"label": "Clavis", "position": 3, "id": "clavis", "field_type": "TextField"},
                           {"label": "Century Active", "position": 4, "id": "century_active", "field_type": "IntegerField"},
                           {"label": "Language", "position": 5, "id": "language", "field_type": "TextField"},
                           {"label": "Place", "position": 6, "id": "place", "field_type": "TextField"},
                           {"label": "Pseudonymous", "position": 7, "id": "pseudonymous", "field_type": "NullBooleanField"},
                           {"label": "Anonymous", "position": 8, "id": "anonymous_collective", "field_type": "NullBooleanField"},
                           {"label": "Transmitted in Another", "position": 9, "id": "transmitted_by_another", "field_type": "NullBooleanField"},
                           {"label": "Translated", "position": 10, "id": "translated_source", "field_type": "NullBooleanField"}
                           ]

        self.assertEqual(response.status_code, 200)
        json_response = str(response.content,'utf-8')
        self.assertJSONEqual(json_response, expected_result)


class ViewHelperTests(TestCase):

    def test_convertToOrderedDict(self):
        test_data = [
                     {'id': 'abbreviation', 'label': 'Abbreviation', 'value': 'TA', 'field_type': 'TextField'},
                     {'id': 'full_name', 'label': 'Full name', 'value': 'Test Author', 'field_type': 'TextField'},
                     {'id': 'pseudonymous', 'label': 'Pseudonymous', 'value': True, 'field_type': 'BooleanField'}
                     ]
        ordered_data = views.convertToOrderedDict(test_data)
        self.assertIn('abbreviation', ordered_data)
        self.assertIn('full_name', ordered_data)
        self.assertIn('pseudonymous', ordered_data)
        self.assertDictEqual(ordered_data['abbreviation'], {'label': 'Abbreviation', 'value': 'TA', 'field_type': 'TextField'})

    def test_refactorData1(self):
        biblical_work_data = {'identifier': 'NT_John',
                              'sort_value': 4,
                              'name': 'John',
                              'abbreviation': 'John'
                              }
        bw = transcription_models.Work.objects.create(**biblical_work_data)

        test_author_data = {
                        'created_by': 'cat',
                        'created_time': timezone.now(),
                        'abbreviation': 'TA',
                        'full_name': 'Test Author',
                        }
        a = models.Author.objects.create(**test_author_data)

        work_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'abbreviation': 'WorkAbb',
                       'author': a
                     }
        w = models.Work.objects.create(**work_data)

        citation_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'chapter': 1,
                       'verse': 1,
                       'biblical_work': bw,
                       'work': w,
                       'dependencies_string': 'dep string',
                       'corrections_required': True,
                       'biblical_catena': ['John 1:1', 'John 1:2', 'John 1:3'],
                       'biblical_parallels': None,
                       'biblical_reference': 'B04K01V01',
                       'biblical_reference_sortable': 4001001,
                       'language': 'lat',
                       'manuscript_variants': None
                       }
        c = models.Citation.objects.create(**citation_data)
        item_fields = models.Citation.ITEM_FIELDS[:]
        data = views.convertToOrderedDict(c.get_row_dict())

        views.refactorData(c, data, item_fields)
        self.assertEqual(data['language']['value'], 'Latin')
        self.assertEqual(data['corrections_required']['value'], '✓')
        self.assertEqual(data['biblical_catena']['value'], 'John 1:1; John 1:2; John 1:3')
        self.assertEqual(data['biblical_reference']['value'], 'John 1:1')
        self.assertEqual(data['dependencies_string']['value'], 'dep string')
        self.assertEqual(data['manuscript_variants']['value'], '')
        self.assertEqual(data['biblical_parallels']['value'], '')

        #test False boolean (we only have one boolean in citation model)
        c.corrections_required = False
        data = views.convertToOrderedDict(c.get_row_dict())
        views.refactorData(c, data, item_fields)
        self.assertEqual(data['corrections_required']['value'], '✗')

        #try the second language just to get full coverage
        c.language = 'grc'
        data = views.convertToOrderedDict(c.get_row_dict())
        views.refactorData(c, data, item_fields)
        self.assertEqual(data['language']['value'], 'Greek')


    def test_orderData(self):
        biblical_work_data = {'identifier': 'NT_John',
                              'sort_value': 4,
                              'name': 'John',
                              'abbreviation': 'John'

                              }

        bw = transcription_models.Work.objects.create(**biblical_work_data)

        test_author_data = {
                        'created_by': 'cat',
                        'created_time': timezone.now(),
                        'abbreviation': 'TA',
                        'full_name': 'Test Author',
                        }
        a = models.Author.objects.create(**test_author_data)

        work_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'abbreviation': 'WorkAbb',
                       'author': a
                     }
        w = models.Work.objects.create(**work_data)

        citation_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'chapter': 1,
                       'verse': 1,
                       'biblical_work': bw,
                       'work': w,
                       'dependencies_string': 'dep string',
                       'corrections_required': True,
                       'biblical_catena': ['John 1:1', 'John 1:2', 'John 1:3'],
                       'biblical_reference': 'B04K01V01',
                       'biblical_reference_sortable': 4001001
                       }
        c = models.Citation.objects.create(**citation_data)
        item_fields = models.Citation.ITEM_FIELDS[:]
        data = views.convertToOrderedDict(c.get_row_dict())
        views.cleanAndSortData(data, item_fields)
        self.assertEqual(len(item_fields), len(data))
        for i, key in enumerate(data):
            self.assertEqual(key, item_fields[i])

    def test_prepareLegacyCitationDependencyData(self):
        biblical_work_data = {'identifier': 'NT_John',
                              'sort_value': 4,
                              'name': 'John',
                              'abbreviation': 'John'
                              }
        bw = transcription_models.Work.objects.create(**biblical_work_data)

        test_author_data = {
                        'created_by': 'cat',
                        'created_time': timezone.now(),
                        'abbreviation': 'TA',
                        'full_name': 'Test Author',
                        }
        a = models.Author.objects.create(**test_author_data)

        work_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'abbreviation': 'WorkAbb',
                       'author': a
                     }
        w = models.Work.objects.create(**work_data)

        citation_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'chapter': 1,
                       'verse': 1,
                       'biblical_work': bw,
                       'work': w,
                       'dependencies_string': 'dep string',
                       'biblical_reference_sortable': 4001001
                       }
        c = models.Citation.objects.create(**citation_data)
        dependencies = c.dependencies.all()
        item_fields = models.Citation.ITEM_FIELDS[:]
        data = views.convertToOrderedDict(c.get_row_dict())
        dependencies = views.prepareLegacyCitationDependencyData(data, dependencies, item_fields)
        self.assertIn('dependencies_string', item_fields)
        self.assertEqual(dependencies, None)

        citation_data_2 = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'chapter': 1,
                       'verse': 1,
                       'biblical_work': bw,
                       'work': w,
                       'dependencies_string': '',
                       'biblical_reference_sortable': 4001001
                       }
        c2 = models.Citation.objects.create(**citation_data_2)

        dependency = {'citation': c2,
                      'relation_type': 'is_same_as',
                      'author': a,
                      'work': w
                      }
        d = models.Dependency.objects.create(**dependency)

        item_fields = models.Citation.ITEM_FIELDS[:]
        data = views.convertToOrderedDict(c2.get_row_dict())
        dependencies = c2.dependencies.all()
        dependencies = views.prepareLegacyCitationDependencyData(data, dependencies, item_fields)
        self.assertNotIn('dependencies_string', item_fields)
        self.assertNotEqual('dependencies', None)

        citation_data_3 = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'chapter': 1,
                       'verse': 1,
                       'biblical_work': bw,
                       'work': w,
                       'dependencies_string': '',
                       'biblical_reference_sortable': 4001001
                       }
        c3 = models.Citation.objects.create(**citation_data_3)

        item_fields = models.Citation.ITEM_FIELDS[:]
        data = views.convertToOrderedDict(c3.get_row_dict())
        dependencies = c3.dependencies.all()
        dependencies = views.prepareLegacyCitationDependencyData(data, dependencies, item_fields)
        self.assertNotIn('dependencies_string', item_fields)
        self.assertNotEqual('dependencies', None)



    def test_prepareLegacyCitationManuscriptData(self):
        biblical_work_data = {'identifier': 'NT_John',
                              'sort_value': 4,
                              'name': 'John',
                              'abbreviation': 'John'
                              }
        bw = transcription_models.Work.objects.create(**biblical_work_data)

        test_author_data = {
                        'created_by': 'cat',
                        'created_time': timezone.now(),
                        'abbreviation': 'TS',
                        'full_name': 'Test Author',
                        }
        a = models.Author.objects.create(**test_author_data)

        work_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'abbreviation': 'WorkAbb',
                       'author': a
                     }
        w = models.Work.objects.create(**work_data)

        citation_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'chapter': 1,
                       'verse': 1,
                       'biblical_work': bw,
                       'work': w,
                       'manuscript_info': 'ms info',
                       'manuscript_variants': None,
                       'biblical_reference_sortable': 4001001
                       }
        c = models.Citation.objects.create(**citation_data)
        item_fields = models.Citation.ITEM_FIELDS[:]
        data = views.convertToOrderedDict(c.get_row_dict())
        views.prepareLegacyCitationManuscriptData(data, item_fields)
        self.assertNotIn('manuscript_variants', item_fields)
        self.assertIn('manuscript_info', item_fields)

        citation_data_2 = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'chapter': 1,
                       'verse': 1,
                       'biblical_work': bw,
                       'work': w,
                       'manuscript_info': '',
                       'manuscript_variants': {'headterm': 'test'},
                       'biblical_reference_sortable': 4001001
                       }
        c2 = models.Citation.objects.create(**citation_data_2)
        item_fields = models.Citation.ITEM_FIELDS[:]
        data = views.convertToOrderedDict(c2.get_row_dict())
        views.prepareLegacyCitationManuscriptData(data, item_fields)
        self.assertIn('manuscript_variants', item_fields)
        self.assertNotIn('manuscript_info', item_fields)

        citation_data_3 = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'chapter': 1,
                       'verse': 1,
                       'biblical_work': bw,
                       'work': w,
                       'manuscript_info': '',
                       'manuscript_variants': None,
                       'biblical_reference_sortable': 4001001
                       }
        c3 = models.Citation.objects.create(**citation_data_3)
        item_fields = models.Citation.ITEM_FIELDS[:]
        data = views.convertToOrderedDict(c3.get_row_dict())
        views.prepareLegacyCitationManuscriptData(data, item_fields)
        self.assertIn('manuscript_variants', item_fields)
        self.assertNotIn('manuscript_info', item_fields)


    def test_addCircaToApproximateYearFields(self):

        author_data = {'created_by': 'cat',
                       'created_time': timezone.now(),
                       'abbreviation': 'TS',
                       'full_name': 'Test Author',
                       'born': 500,
                       'born_is_approximate': True,
                       'died': 600,
                       'died_is_approximate': False}
        a = models.Author.objects.create(**author_data)
        data = views.convertToOrderedDict(a.get_row_dict())
        views.addCircaToApproximateYearFields('author', data)
        self.assertIn('c', data['born']['value'])
        self.assertEqual(data['died']['value'], 600)

    def test_correct_model_is_found(self):
        #we use citations and authors as test case
        #when no model is given
        model = views.getActualModel('citation', None)
        self.assertEqual(model, 'citation')
        #when a private project is given
        project_data = {'public': False}
        p = models.Project.objects.create(**project_data)
        model = views.getActualModel('citation', p)
        self.assertEqual(model, 'privatecitation')
        model = views.getActualModel('author', p)
        self.assertEqual(model, 'author')
        #when a public project is given
        p.public = True
        model = views.getActualModel('citation', p)
        self.assertEqual(model, 'citation')
        model = views.getActualModel('author', p)
        self.assertEqual(model, 'author')

    def test_getFilterLabel(self):
        field = {'label': 'Author', 'id': 'author'}
        filter_labels = views.getFilterLabel(field, [])
        self.assertEqual(filter_labels, ['Author'])
        field = {'id': 'author'}
        filter_labels = views.getFilterLabel(field, [])
        self.assertEqual(filter_labels, ['author'])
        field = 'author'
        filter_labels = views.getFilterLabel(field, [])
        self.assertEqual(filter_labels, ['author'])

    def test_getFieldFilterValue(self):
        field = {'search': 'work__author', 'label': 'Work', 'id': 'work'}
        filter_value = views.getFilterFieldValue(field)
        self.assertEqual(filter_value, 'work__author')
        field = {'label': 'Work', 'id': 'work'}
        filter_value = views.getFilterFieldValue(field)
        self.assertEqual(filter_value, 'work')
        field = 'work'
        filter_value = views.getFilterFieldValue(field)
        self.assertEqual(filter_value, 'work')
        field = None
        filter_value = views.getFilterFieldValue(field)
        self.assertEqual(filter_value, None)


    def test_totalPageCalculation(self):
        pages = views.getTotalPages(300, 100)
        self.assertEqual(pages, 3)
        pages = views.getTotalPages(301, 100)
        self.assertEqual(pages, 4)
        pages = views.getTotalPages(299, 100)
        self.assertEqual(pages, 3)

    def test_getCurrentPage(self):
        page = views.getCurrentPage(0, 100)
        self.assertEqual(page, 1)
        page = views.getCurrentPage(200, 100)
        self.assertEqual(page, 3)

    def test_getSearchLink(self):
        test_dict = {'limit': 100,
                     'offset': 0,
                     '_sort': 'biblical_reference',
                     'biblical_work__book_number': 4,
                     'chapter' : 1,
                     'verse':1,
                     '_advanced': 'true'
                     }
        query_dict = views.getSearchLink(test_dict.copy(), 'citation')
        del test_dict['limit']
        del test_dict['offset']
        del test_dict['_sort']
        del test_dict['_advanced']
        test_dict['model'] = 'citation'
        self.assertDictEqual(query_dict, test_dict)

    def test_getApplyProjectFilterLink(self):
        test_dict = {'limit': 100,
                     'offset': 0,
                     '_show': 12,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getApplyProjectFilterLink(test_dict.copy())
        test_dict['_applyprojectfilter'] = True
        self.assertDictEqual(query_dict, test_dict)

    def test_getNoProjectFilterLink(self):
        test_dict = {'limit': 100,
                     'offset': 0,
                     '_show': 12,
                     'abbreviation': 'A*',
                     '_sort': 'full_name',
                     '_applyprojectfilter': True
                     }
        query_dict = views.getNoProjectFilterLink(test_dict.copy())
        del test_dict['_applyprojectfilter']
        self.assertDictEqual(query_dict, test_dict)

    def test_getBackLink(self):
        #this should keep everything in the query except '_show'
        test_dict = {'limit': 100,
                     'offset': 0,
                     '_show': 12,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getBackLink(test_dict.copy())
        del test_dict['_show']
        self.assertDictEqual(query_dict, test_dict)
        #lets just check it doesn't break if there isn't a _show
        test_dict = {'limit': 100,
                     'offset': 0,
                     'abbreviation': 'A*'
                     }
        query_dict = views.getBackLink(test_dict.copy())
        self.assertDictEqual(query_dict, test_dict)

    def test_getNoSortLink(self):
        #remove _show and _sort, reset page to 1 and page_size to passed in value
        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getNoSortLink(test_dict.copy(), 25)
        del test_dict['_show']
        del test_dict['_sort']
        test_dict['limit'] = 25
        test_dict['offset'] = 0
        self.assertDictEqual(query_dict, test_dict)

    def test_getNoSizeLink(self):
        #remove _show and limit and reset offset to 0
        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getNoSizeLink(test_dict.copy())
        del test_dict['_show']
        del test_dict['limit']
        test_dict['offset'] = 0
        self.assertDictEqual(query_dict, test_dict)

    def test_getLastPageLink(self):
        #remove _show and change offset to deliver last page
        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getLastPageLink(test_dict.copy(), 6, 100)
        del test_dict['_show']
        test_dict['offset'] = 500
        self.assertDictEqual(query_dict, test_dict)

    def test_getFirstPageLink(self):
        #remove _show and change offset to 0
        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getFirstPageLink(test_dict.copy())
        del test_dict['_show']
        test_dict['offset'] = 0
        self.assertDictEqual(query_dict, test_dict)

    def test_getNextPageLink(self):
        #remove _show and change offset to next page offset
        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getNextPageLink(test_dict.copy(), 2, 100)
        del test_dict['_show']
        test_dict['offset'] = 200
        self.assertDictEqual(query_dict, test_dict)

    def test_getPreviousPageLink(self):
        #remove _show and change offset to previous page offset
        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getPreviousPageLink(test_dict.copy(), 2, 100)
        del test_dict['_show']
        test_dict['offset'] = 0
        self.assertDictEqual(query_dict, test_dict)

    def test_getPageSelectLink(self):
        #remove _show and remove offset
        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict = views.getPageSelectLink(test_dict.copy())
        del test_dict['_show']
        del test_dict['offset']
        self.assertDictEqual(query_dict, test_dict)

    def test_getItemViewReturnLink(self):
        test_dict = {'work__author__abbreviation' :'AM',
                     'offset': 0,
                     'limit': 100}
        view_id = 1
        query_dict = views.getItemViewReturnLink(test_dict.copy(), view_id)
        test_dict['_show'] = view_id
        self.assertDictEqual(query_dict, test_dict)


    def test_getFilterDetails(self):
        #remove _show and remove offset
        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict, button_label, button_required = views.getFilterDetails(test_dict.copy(), ['abbreviation', 'full_name'])
        del test_dict['_show']
        test_dict['offset'] = 0
        del test_dict['abbreviation']
        self.assertDictEqual(query_dict, test_dict)
        self.assertEqual(button_required, True)
        self.assertEqual(button_label.lower(), 'remove abbreviation filter')

        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     'abbreviation': 'A*',
                     'full_name': 'A*',
                     '_sort': 'full_name'
                     }
        query_dict, button_label, button_required = views.getFilterDetails(test_dict.copy(), ['abbreviation', 'full_name'])
        del test_dict['_show']
        test_dict['offset'] = 0
        del test_dict['abbreviation']
        del test_dict['full_name']
        self.assertDictEqual(query_dict, test_dict)
        self.assertEqual(button_required, True)
        self.assertEqual(button_label.lower(), 'remove all filters')

        test_dict = {'limit': 100,
                     'offset': 100,
                     '_show': 112,
                     '_sort': 'full_name'
                     }
        query_dict, button_label, button_required = views.getFilterDetails(test_dict.copy(), ['abbreviation', 'full_name'])
        del test_dict['_show']
        test_dict['offset'] = 0
        self.assertDictEqual(query_dict, test_dict)
        self.assertEqual(button_required, False)
        self.assertEqual(button_label.lower(), 'remove filter')

    def test_getProjectFilters(self):
        #simple language only
        project_data = {'public': True, 'language': 'grc'}
        p = models.Project.objects.create(**project_data)
        query = views.getProjectFilters(p, 'author', models.Author)
        test_query = Q()
        test_query &= Q(('language', 'grc'))
        self.assertEqual(str(query), str(test_query))

        #language only tested on edition using existing project
        query = views.getProjectFilters(p, 'edition', models.Edition)
        test_query = Q()
        test_query &= Q(('work__language', 'grc'))
        self.assertEqual(str(query), str(test_query))

        #language and authors tested on author
        test_author_data = {
                        'created_by': 'cat',
                        'created_time': timezone.now(),
                        'abbreviation': 'TS',
                        'full_name': 'Test Author',

                        }
        a = models.Author.objects.create(**test_author_data)
        p.author_ids.add(a)
        query = views.getProjectFilters(p, 'author', models.Author)
        test_query = Q()
        test_query &= Q(('language', p.language))
        test_query &= Q(('project__id', p.id))
        self.assertEqual(str(query), str(test_query))

        #language and authors tested on work
        query = views.getProjectFilters(p, 'work', models.Work)
        test_query = Q()
        test_query &= Q(('language', p.language))
        test_query &= Q(('author__project__id', p.id))
        self.assertEqual(str(query), str(test_query))

        #test private project with citation
        p.public = False
        query = views.getProjectFilters(p, 'privatecitation', models.PrivateCitation)
        test_query = Q()
        test_query &= Q(('project__id', p.id))
        test_query &= Q(('language', p.language))
        self.assertEqual(str(query), str(test_query))

        #test citation with biblical book
        biblical_work_data = {'identifier': 'NT_John',
                              'sort_value': 4,
                              'name': 'John',
                              'abbreviation': 'John'
                              }
        bw = transcription_models.Work.objects.create(**biblical_work_data)
        p.biblical_work = bw
        query = views.getProjectFilters(p, 'privatecitation', models.PrivateCitation)
        test_query = Q()
        test_query &= Q(('project__id', p.id))
        test_query &= Q(('language', p.language))
        test_query &= Q(('biblical_work__id', p.biblical_work.id))
        self.assertEqual(str(query), str(test_query))



#     def test_author_list_view(self):
#         a = self.create_author()
#         url = reverse("list", args=['author'])
#         resp = self.client.get(url)
#
#         self.assertEqual(resp.status_code, 200)
#         self.assertTemplateUsed(resp, 'citations/list_base.html')
#
#     def create_author(self):
#         test_author_data = {
#                         'created_by': 'cat',
#                         'created_time': timezone.now(),
#                         'abbreviation': 'TS',
#                         'full_name': 'Test Author',
#
#                         }
#         return Author.objects.create(**test_author_data)
#
#     def test_author_str_functions(self):
#         a = self.create_author()
#         self.assertTrue(isinstance(a, Author))
#         self.assertEqual(a.__str__(), '%s: %s' % (a.abbreviation, a.full_name))
#
#         a.full_name = ''
#         self.assertEqual(a.__str__(), a.abbreviation)
#
#         a.full_name = 'Test Author'
#
#     # views (uses reverse)
#     def test_author_list_view(self):
#         a = self.create_author()
#         url = reverse("list", args=['author'])
#         resp = self.client.get(url)
#
#         self.assertEqual(resp.status_code, 200)
#         #self.assertIn(a.title, resp.content)
#     def create_author(self):
#         test_author_data = {
#                         'created_by': 'cat',
#                         'created_time': timezone.now(),
#                         'abbreviation': 'T1',
#                         'full_name': 'Test Author 1',
#
#                         }
#         return Author.objects.create(**test_author_data)
