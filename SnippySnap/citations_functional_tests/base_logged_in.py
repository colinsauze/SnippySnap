from .base import FunctionalTest
from unittest import skip
from django.utils import timezone
from django.contrib.auth.models import User
from accounts import models as ac_models
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from citations import models
from transcriptions import models as transcription_models

class LoggedInFunctionalTest(FunctionalTest):

    def addProjectData(self):
        project_data = {'identifier': 'B09_grc',
                        'name': 'Galatians Greek',
                        'biblical_work': self.bw2,
                        'public': True,
                        'language': 'grc',
                        'base_text_siglum': 'TR',
                        'base_text_label': 'TR',
                        'form_settings': {'citation' : {'online_transcribers': ['source_details', 'search_details_div', 'citation_details','biblical_catena_div', 'source_section', 'comments_section', 'status_details'],
                                                        'edition_transcribers': ['source_details', 'citation_details', 'ms_variants_div', 'biblical_catena_div', 'dependencies_div', 'parallels_div', 'source_section', 'comments_section', 'status_details']}},
                        'submit_settings': {'citation' : {'online_transcribers': ['submit_same', 'submit_home', 'submit_continue', 'reset_form'],
                                                          'edition_transcribers': ['submit_same', 'submit_home', 'submit_next', 'submit_continue', 'reset_form']} },
                        'edition_lookup': [{'id': 'series', 'label': 'Series', 'model': 'series', 'criteria': ['work__language']}],
                        'preselects': {'citation' : {'online_transcribers': {'language': 'grc', 'onlinecorpus': 'TO2'},
                                                    'edition_transcribers': {'language': 'grc'}},
                                        'edition' : {'language': 'grc'},
                                        'author' : {'language': 'grc'},
                                        'work' : {'language': 'grc'}
                                  },
                        }
        self.p1 = models.Project.objects.create(**project_data)

    def logUserIn(self, credentials):
        ## I can't find a simple way of logging a user in so we need to do it the long way for now
        #She goes to the citations database home page and clicks the login link
        self.browser.get('%s/citations' % self.live_server_url)
        assert 'Citations Home' in self.browser.title
        self.browser.find_element_by_link_text('login').click()

        self.wait_for(lambda: self.assertTrue('ITSEE Login' in self.browser.title))
        self.browser.find_element_by_id('id_username').send_keys(credentials['username'])
        self.browser.find_element_by_id('id_password').send_keys(credentials['password'])
        self.browser.find_element_by_id('login_submit_button').click()
        self.wait_for(lambda: self.assertFalse('ITSEE Login' in self.browser.title))

    def addCitationManagerUser(self, credentials):
        g2 = Group(name='citation_managers')
        g2.save()
        self.add_citation_manager_permissions(g2)
        if 'display_name' in credentials:
            display_name = credentials['display_name']
            del credentials['display_name']
            user = User.objects.create_user(**credentials)
            user.groups.add(g2)
            user.save()
            user.profile.display_name = display_name
            user.save()
        else:
            user = User.objects.create_user(**credentials)
            user.groups.add(g2)
            user.save()
        return user

    def add_citation_manager_permissions(self, group):
        group.permissions.add(Permission.objects.get(codename='add_citation'))
        group.permissions.add(Permission.objects.get(codename='change_citation'))
        group.permissions.add(Permission.objects.get(codename='delete_citation'))
        group.permissions.add(Permission.objects.get(codename='add_dependency'))
        group.permissions.add(Permission.objects.get(codename='change_dependency'))
        group.permissions.add(Permission.objects.get(codename='delete_dependency'))
        group.permissions.add(Permission.objects.get(codename='add_author'))
        group.permissions.add(Permission.objects.get(codename='change_author'))
        group.permissions.add(Permission.objects.get(codename='delete_author'))
        group.permissions.add(Permission.objects.get(codename='add_edition'))
        group.permissions.add(Permission.objects.get(codename='change_edition'))
        group.permissions.add(Permission.objects.get(codename='delete_edition'))
        group.permissions.add(Permission.objects.get(codename='add_series'))
        group.permissions.add(Permission.objects.get(codename='change_series'))
        group.permissions.add(Permission.objects.get(codename='delete_series'))
        group.permissions.add(Permission.objects.get(codename='add_onlinecorpus'))
        group.permissions.add(Permission.objects.get(codename='change_onlinecorpus'))
        group.permissions.add(Permission.objects.get(codename='delete_onlinecorpus'))
        #work has to take into account content type because of a clash with the transcriptions.work model
        content_type = ContentType.objects.get_for_model(models.Work)
        permission = Permission.objects.get(content_type=content_type, codename='add_work')
        group.permissions.add(permission)
        permission = Permission.objects.get(content_type=content_type, codename='change_work')
        group.permissions.add(permission)
        permission = Permission.objects.get(content_type=content_type, codename='delete_work')
        group.permissions.add(permission)
        group.save()


    def addCitationEditorUser(self, credentials):
        g1 = Group(name='citation_editors')
        g1.save()
        self.add_citation_editor_permissions(g1)
        if 'display_name' in credentials:
            display_name = credentials['display_name']
            del credentials['display_name']
            user = User.objects.create_user(**credentials)
            user.groups.add(g1)
            user.save()
            user.profile.display_name = display_name
            user.save()
        else:
            user = User.objects.create_user(**credentials)
            user.groups.add(g1)
            user.save()
        return user

    def add_citation_editor_permissions(self, group):
        group.permissions.add(Permission.objects.get(codename='add_citation'))
        group.permissions.add(Permission.objects.get(codename='change_citation'))
        group.permissions.add(Permission.objects.get(codename='add_dependency'))
        group.permissions.add(Permission.objects.get(codename='change_dependency'))
        group.save()


    def addPrivateCitationManagerUser(self, credentials):
        g3 = Group(name='private_citation_managers')
        g3.save()
        self.add_private_citation_manager_permissions(g3)
        if 'display_name' in credentials:
            display_name = credentials['display_name']
            del credentials['display_name']
            user = User.objects.create_user(**credentials)
            user.groups.add(g3)
            user.save()
            user.profile.display_name = display_name
            user.save()
        else:
            user = User.objects.create_user(**credentials)
            user.groups.add(g3)
            user.save()
        return user


    def add_private_citation_manager_permissions(self, group):
        group.permissions.add(Permission.objects.get(codename='add_privatecitation'))
        group.permissions.add(Permission.objects.get(codename='change_privatecitation'))
        group.permissions.add(Permission.objects.get(codename='delete_privatecitation'))
        group.permissions.add(Permission.objects.get(codename='add_privatedependency'))
        group.permissions.add(Permission.objects.get(codename='change_privatedependency'))
        group.permissions.add(Permission.objects.get(codename='delete_privatedependency'))
        group.save()
