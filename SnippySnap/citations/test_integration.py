from django.test import TestCase
from django.test import Client
from citations import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.utils import timezone
from transcriptions import models as transcription_models

class SearchTest(TestCase):

    def test_simple_search(self):
        response = self.client.get('/citations/search/')
        self.assertTemplateUsed(response, 'citations/search.html')

    def test_advanced_search(self):
        response = self.client.get('/citations/search/advanced/')
        self.assertTemplateUsed(response, 'citations/advancedsearch.html')

class HomePageTest(TestCase):

    def test_root_renders_main_index_page(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'index.html')

    def test_citations_url_renders_citations_index_page_for_not_logged_in_users(self):
        response = self.client.get('/citations')
        self.assertTemplateUsed(response, 'citations/index.html')

    def test_citations_url_renders_citations_index_page_for_logged_in_users_with_no_group_permissions(self):
        user = User.objects.create_user(username='user', password='secret')
        user.save()
        c = Client()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations')
        self.assertTemplateUsed(response, 'citations/index.html')

    def test_citations_url_renders_citations_index_page_for_logged_in_users_in_citation_editors_group(self):
        g1 = Group(name='citation_editors')
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        c = Client()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations')
        self.assertTemplateUsed(response, 'citations/index_citation_editor.html')

    def test_citations_url_renders_citations_index_page_for_logged_in_users_in_citation_managers_group(self):
        g1 = Group(name='citation_managers')
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        c = Client()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations')
        self.assertTemplateUsed(response, 'citations/index_citation_manager.html')

    def test_project_select(self):
        g1 = Group(name='citation_managers')
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        c = Client()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations/projectselect')
        self.assertTemplateUsed(response, 'citations/project_select.html')

    def test_post_select_manager(self):
        g1 = Group(name='citation_managers')
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        c = Client()
        login_status = c.login(username='user', password='secret')
        response = c.post('/citations/', {'project': 1})
        self.assertTemplateUsed(response, 'citations/index_citation_manager.html')

    def test_post_select_editor(self):
        g1 = Group(name='citation_editors')
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        c = Client()
        login_status = c.login(username='user', password='secret')
        response = c.post('/citations/', {'project': 1})
        self.assertTemplateUsed(response, 'citations/index_citation_editor.html')

    def test_post_select_no_group(self):
        c = Client()
        user = User.objects.create_user(username='user', password='secret')
        user.save()
        login_status = c.login(username='user', password='secret')
        response = c.post('/citations/', {'project': 1})
        self.assertTemplateUsed(response, 'citations/index.html')

    def test_multiple_projects(self):
        user = User.objects.create_user(username='user', password='secret')
        user.save()
        project_1_data = {'public': True, 'language': 'grc', 'identifier': 'ECM_04'}
        p1 = models.Project.objects.create(**project_1_data)
        p1.online_transcribers.add(user)
        p1.save()
        project_2_data = {'public': True, 'language': 'grc', 'identifier': 'ECM_09'}
        p2 = models.Project.objects.create(**project_2_data)
        p2.online_transcribers.add(user.id)
        p2.save()
        c = Client()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations')
        self.assertTemplateUsed(response, 'citations/project_select.html')

    def test_single_private_project(self):
        user = User.objects.create_user(username='user', password='secret')
        user.save()
        project_1_data = {'public': False, 'language': 'grc', 'identifier': 'ECM_04'}
        p1 = models.Project.objects.create(**project_1_data)
        p1.online_transcribers.add(user)
        p1.save()
        c = Client()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations')
        self.assertTemplateUsed(response, 'citations/project_select.html')

#     def test_project_settings_on_index_page(self):
#         g1 = Group(name='citation_managers')
#         g1.save()
#         user = User.objects.create_user(username='user', password='secret')
#         user.groups.add(g1)
#         user.save()
#
#         c = Client()
#         login_status = c.login(username='user', password='secret')
#         session = c.session
#         session['project'] = 'ECM_04'
#         session.save()
#         response = c.get('/citations')
#         self.assertTemplateUsed(response, 'citations/index_citation_manager.html')

class ListViewTests(TestCase):

    def test_uses_list_base_template(self):
        response = self.client.get('/citations/author/')
        self.assertTemplateUsed(response, 'citations/list_base.html')

    def test_uses_list_citation_template(self):
        response = self.client.get('/citations/citation/')
        self.assertTemplateUsed(response, 'citations/list_citation.html')

    def test_uses_list_work_template(self):
        response = self.client.get('/citations/work/')
        self.assertTemplateUsed(response, 'citations/list_work.html')

    def test_results_page_uses_base_template(self):
        response = self.client.get('/citations/author/results/')
        self.assertTemplateUsed(response, 'citations/search_no_results.html')


class ItemViewTests(TestCase):

    def test_uses_error_template(self):
        #there is no author with id 1
        response = self.client.get('/citations/author/1')
        self.assertTemplateUsed(response, 'citations/error.html')

    def test_uses_author_template(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        author = models.Author.objects.create(**a1_data)
        response = self.client.get('/citations/author/%d' % author.id)
        self.assertTemplateUsed(response, 'citations/item_author.html')

    def test_series_uses_item_base_template(self):
        s1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TS1',
                   'title': 'Test Series 1'
                   }
        series = models.Series.objects.create(**s1_data)
        response = self.client.get('/citations/series/%d' % series.id)
        self.assertTemplateUsed(response, 'citations/item_base.html')

    def test_onlinecorpus_uses_item_base_template(self):
        o1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TO1',
                   'title': 'Test Onlinecorpus 1'
                   }
        onlinecorpus = models.OnlineCorpus.objects.create(**o1_data)
        response = self.client.get('/citations/onlinecorpus/%d' % onlinecorpus.id)
        self.assertTemplateUsed(response, 'citations/item_base.html')

    def test_uses_work_template(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        author = models.Author.objects.create(**a1_data)
        w1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW1',
                   'author': author,
                   'title': 'Test Work 1',
                   'language': 'grc'
                   }
        work = models.Work.objects.create(**w1_data)
        response = self.client.get('/citations/work/%d' % work.id)
        self.assertTemplateUsed(response, 'citations/item_work.html')

    def test_uses_edition_template(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        author = models.Author.objects.create(**a1_data)
        w1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW1',
                   'author': author,
                   'title': 'Test Work 1',
                   'language': 'grc'
                   }
        work = models.Work.objects.create(**w1_data)
        e1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': work,
                   'editor': 'Migne',
                   'year': '1906',
                   'volume': '6'
                   }
        edition = models.Edition.objects.create(**e1_data)
        response = self.client.get('/citations/edition/%d' % edition.id)
        self.assertTemplateUsed(response, 'citations/item_edition.html')

    def test_uses_citation_template(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        author = models.Author.objects.create(**a1_data)
        w1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW1',
                   'author': author,
                   'title': 'Test Work 1',
                   'language': 'grc'
                   }
        work = models.Work.objects.create(**w1_data)
        biblical_work_data = {'identifier': 'NT_John',
                              'sort_value': 4,
                              'name': 'John',
                              'corpus': 'NT',
                              'abbreviation': 'John'
                              }
        bw = transcription_models.Work.objects.create(**biblical_work_data)
        c1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': work,
                   'biblical_reference': 'B04K01V01',
                   'biblical_reference_sortable': 4001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': bw,
                   'status': 'live',
                   'citation_text': 'και αρνῃ μεν το θεος ην ο λογος'
                   }
        citation = models.Citation.objects.create(**c1_data)
        response = self.client.get('/citations/citation/%d' % citation.id)
        self.assertTemplateUsed(response, 'citations/item_citation.html')

class DeleteTests(TestCase):

    def test_project_required(self):
        c = Client()
        user = User.objects.create_user(username='user', password='secret')
        user.save()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations/author/delete/1')
        self.assertTemplateUsed(response, 'citations/error.html')

    def test_permissions_required(self):
        #citation editors do not have delete author permissions so should get error
        c = Client()
        g1 = Group(name='citation_editors')
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        project_1_data = {'public': True, 'language': 'grc', 'identifier': 'ECM_04'}
        p1 = models.Project.objects.create(**project_1_data)
        p1.online_transcribers.add(user)
        p1.save()
        login_status = c.login(username='user', password='secret')
        session = c.session
        session['project'] = p1.id
        session.save()
        response = c.get('/citations/author/delete/1')
        self.assertTemplateUsed(response, 'citations/error.html')

    def test_error_if_item_does_not_exist(self):
        #citation managers do have delete author permissions
        #but the author doesn't exist so error
        c = Client()
        g1 = Group(name='citation_managers')
        g1.save()
        g1.permissions.add(Permission.objects.get(codename='delete_author'))
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        project_1_data = {'public': True, 'language': 'grc', 'identifier': 'ECM_04'}
        p1 = models.Project.objects.create(**project_1_data)
        p1.online_transcribers.add(user)
        p1.save()
        login_status = c.login(username='user', password='secret')
        session = c.session
        session['project'] = p1.id
        session.save()
        response = c.get('/citations/author/delete/1')
        self.assertTemplateUsed(response, 'citations/error.html')

    def test_item_delete(self):

        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        author = models.Author.objects.create(**a1_data)
        c = Client()
        g1 = Group(name='citation_managers')
        g1.save()
        g1.permissions.add(Permission.objects.get(codename='delete_author'))
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        project_1_data = {'public': True, 'language': 'grc', 'identifier': 'ECM_04'}
        p1 = models.Project.objects.create(**project_1_data)
        p1.online_transcribers.add(user)
        p1.save()
        login_status = c.login(username='user', password='secret')
        session = c.session
        session['project'] = p1.id
        session.save()
        response = c.get('/citations/author/delete/%s' % author.id)
        self.assertTemplateUsed(response, 'citations/delete_author.html')

class EditTests(TestCase):

    def test_permissions_required(self):
        #citation editors do not have delete author permissions so should get error
        c = Client()
        g1 = Group(name='citation_editors')
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations/author/edit/1')
        self.assertTemplateUsed(response, 'citations/error.html')

    def test_project_required(self):
        #citation editors do not have delete author permissions so should get error
        c = Client()
        g1 = Group(name='citation_editors')
        g1.save()
        g1.permissions.add(Permission.objects.get(codename='add_author'))
        g1.permissions.add(Permission.objects.get(codename='change_author'))
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        login_status = c.login(username='user', password='secret')
        response = c.get('/citations/author/edit/1')
        self.assertTemplateUsed(response, 'citations/error.html')

    def test_edit_author_wrong_project(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'lat'
                   }
        author = models.Author.objects.create(**a1_data)
        c = Client()
        g1 = Group(name='citation_managers')
        g1.save()
        g1.permissions.add(Permission.objects.get(codename='add_author'))
        g1.permissions.add(Permission.objects.get(codename='change_author'))
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        project_1_data = {'public': True, 'language': 'grc', 'identifier': 'ECM_04'}
        p1 = models.Project.objects.create(**project_1_data)
        p1.online_transcribers.add(user)
        p1.save()
        login_status = c.login(username='user', password='secret')
        session = c.session
        session['project'] = p1.id
        session.save()
        response = c.get('/citations/author/edit/%s' % author.id)
        self.assertTemplateUsed(response, 'citations/error.html')

    def test_edit_author_template_used(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        author = models.Author.objects.create(**a1_data)
        c = Client()
        g1 = Group(name='citation_managers')
        g1.save()
        g1.permissions.add(Permission.objects.get(codename='add_author'))
        g1.permissions.add(Permission.objects.get(codename='change_author'))
        g1.save()
        user = User.objects.create_user(username='user', password='secret')
        user.groups.add(g1)
        user.save()
        project_1_data = {'public': True, 'language': 'grc', 'identifier': 'ECM_04'}
        p1 = models.Project.objects.create(**project_1_data)
        p1.online_transcribers.add(user)
        p1.save()
        login_status = c.login(username='user', password='secret')
        session = c.session
        session['project'] = p1.id
        session.save()
        response = c.get('/citations/author/edit/%s' % author.id)
        self.assertTemplateUsed(response, 'citations/edit_author.html')
