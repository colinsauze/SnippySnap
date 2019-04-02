from django.core.management.base import BaseCommand, CommandError
from citations.models import Project
from citations.models import Author
from transcriptions.models import Work as Biblical_Work
from django.contrib.auth.models import User


class Command(BaseCommand):

    def load_project(self, data, edition_transcribers, online_transcribers):
        try:
            retrieved = Project.objects.get(identifier=data['identifier'])
            data['id'] = retrieved.id
        except:
            pass
        if 'book' in data:
            bw = Biblical_Work.objects.get(identifier=data['book'])
            if bw:
                data['biblical_work'] = bw
                del data['book']

        p = Project(**data)
        p.save()
        #need to have created it before updating manytomany fields
        #project
        for user in edition_transcribers:
            u = User.objects.get(username=user)
            if u:
                p.edition_transcribers.add(u)

        for user in online_transcribers:
            u = User.objects.get(username=user)
            if u:
                p.edition_transcribers.add(u)
        return


    def handle(self, *args, **options):

    #Latin master
        project = {
                   'identifier': 'master_lat',
                   'name': 'Latin Master',
                   'language': 'lat',
                   'base_text_siglum': 'vg^st5',
                   'base_text_label': 'Vulgate',
                   'preselects': {'author' : {'language': 'lat'},
                                  'work' : {'language': 'lat'},
                                  'edition' : {'language': 'lat'},
                                  'citation': {'language': 'lat'}
                                  },
                   'public': True
                   }

        edition_transcribers = ['Tess']
        online_transcribers = []
        self.load_project(project, edition_transcribers, online_transcribers)


    #Greek master
        project = {
                   'identifier': 'master_grc',
                   'name': 'Greek Master',
                   'language': 'grc',
                   'base_text_siglum': 'TR',
                   'base_text_label': 'TR',
                    'preselects': {'author' : {'language': 'grc'},
                                  'work' : {'language': 'grc'},
                                  'edition' : {'language': 'grc'},
                                  'citation' : {'language': 'grc'}
                                  },
                   'public': True
                   }
        edition_transcribers = ['Tess']
        online_transcribers = []
        self.load_project(project, edition_transcribers, online_transcribers)



    #Latin Paul base project settings
    #when merging this projects data the base project will override anything local so it is important not to try to override on local projects before the merge

        latin_paul_base_project = {
                         'language': 'lat',
                         'base_text_siglum': 'vg^st5',
                         'base_text_label': 'Vulgate',
                         'preselects': {'citation' : {'onlinecorpus': 'VLD', 'language': 'lat'},
                                        'edition' : {'language': 'lat'},
                                        'author' : {'language': 'lat'},
                                        'work' : {'language': 'lat'}
                                        },
                         'submit_settings': {'citation' : {'online_transcribers': ['submit_same', 'submit_home', 'submit_continue'],
                                                          'edition_transcribers': ['submit_same', 'submit_home', 'submit_continue']} },
                         'form_settings': {'citation' : {'online_transcribers': ['source_details', 'search_details_div', 'citation_details', 'comments_section', 'status_details'],
                                                        'edition_transcribers': ['source_details', 'citation_details', 'ms_variants_div', 'biblical_catena_div', 'dependencies_div', 'parallels_div', 'comments_section', 'status_details']}},
                         'public': True
                         }

    #B06_lat
        project = {
                   'identifier': 'B06_lat',
                   'name': 'Latin Romans',
                   'book': 'NT_Rom',
                   }
        project.update(latin_paul_base_project)

        edition_transcribers = ['Tess']
        online_transcribers = []
        self.load_project(project, edition_transcribers, online_transcribers)

    #B07_lat
        project = {
                   'identifier': 'B07_lat',
                   'name': 'Latin 1 Corinthians',
                   'book': 'NT_1Cor',
                   }
        project.update(latin_paul_base_project)

        edition_transcribers = ['Tess']
        online_transcribers = []
        self.load_project(project, edition_transcribers, online_transcribers)

    #B08_lat
        project = {
                   'identifier': 'B08_lat',
                   'name': 'Latin 2 Corinthians',
                   'book': 'NT_2Cor',
                   }
        project.update(latin_paul_base_project)

        edition_transcribers = []
        online_transcribers = ['Tess']
        self.load_project(project, edition_transcribers, online_transcribers)

    #B09_lat
        project = {
                   'identifier': 'B09_lat',
                   'name': 'Latin Galatians',
                   'book': 'NT_Gal',
                   'edition_lookup': [{'id': 'series', 'label': 'Series', 'model': 'series', 'criteria': ['work__language']}],
                   }
        project.update(latin_paul_base_project)

        edition_transcribers = []
        online_transcribers = ['Tess']
        self.load_project(project, edition_transcribers, online_transcribers)

#B09_grc
        project = {
                   'identifier': 'B09_grc',
                   'name': 'Greek Galatians',
                   'book': 'NT_Gal',
                   'language': 'grc',
                   'base_text_siglum': 'TR',
                   'base_text_label': 'TR',
                   'form_settings': {'citation' : {'online_transcribers': ['source_details', 'search_details_div', 'citation_details','biblical_catena_div',  'comments_section', 'status_details'],
                                                        'edition_transcribers': ['source_details', 'citation_details', 'ms_variants_div', 'biblical_catena_div', 'dependencies_div', 'parallels_div', 'comments_section', 'status_details']}},
                   'submit_settings': {'citation' : {'online_transcribers': ['submit_same', 'submit_home', 'submit_continue', 'reset_form'],
                                                          'edition_transcribers': ['submit_same', 'submit_home', 'submit_continue', 'submit_next', 'reset_form']} },
                   'edition_lookup': [{'id': 'series', 'label': 'Series', 'model': 'series', 'criteria': ['work__language']}],
                   'preselects': {'citation' : {'onlinecorpus': 'TLG', 'language': 'grc'},
                                  'edition' : {'language': 'grc'},
                                  'author' : {'language': 'grc'},
                                  'work' : {'language': 'grc'}
                                  },
                   'public': True
                   }
        edition_transcribers = ['Tess', 'Edith']
        online_transcribers = []
        self.load_project(project, edition_transcribers, online_transcribers)


#B04_ECM
        project = {
                   'identifier': 'B04_ECM',
                   'name': 'ECM John',
                   'book': 'NT_John',
                   'language': 'grc',
                   'base_text_siglum': 'TR',
                   'base_text_label': 'TR',
                   'preselects': {'edition' : {'language': 'grc'},
                                    'author' : {'language': 'grc'},
                                    'work' : {'language': 'grc'},
                                    'citation' : {'language': 'grc'}
                                },
                   'public': True
                   }
        edition_transcribers = ['Tess']
        online_transcribers = []
        self.load_project(project, edition_transcribers, online_transcribers)


#Haupt_PhD
        project = {
                   'identifier': 'Haupt_PhD',
                   'name': 'Haupt PhD',
                   'language': 'lat',
                   'base_text_siglum': 'vg^st5',
                   'base_text_label': 'Vulgate',
                   'preselects': {'edition' : {'language': 'lat'},
                                  'author' : {'language': 'lat'},
                                  'work' : {'language': 'lat'},
                                  'citation' : {'language': 'lat'}
                                  },
                   'public': False
                   }
        edition_transcribers = ['Tess']
        author_ids = ['TE', 'PS-TE', 'IR']

        try:
            retrieved = Project.objects.get(identifier= 'Haupt_PhD')
            project['id'] = retrieved.id
        except:
            pass
        p = Project(**project)
        p.save()
        #need to have created it before updating manytomany fields
        #project
        for user in edition_transcribers:
            u = User.objects.get(username=user)
            if u:
                p.edition_transcribers.add(u)

        for author in author_ids:
            a = Author.objects.get(abbreviation=author)
            if a:
                p.author_ids.add(a)

#B04_lat
        project = {
                   'identifier': 'B04_lat',
                   'name': 'Latin John',
                   'book': 'NT_John',
                   'language': 'lat',
                   'base_text_siglum': 'vg^st5',
                   'base_text_label': 'Vulgate',
                   'public': True
                   }
        edition_transcribers = ['Tess']

        try:
            retrieved = Project.objects.get(identifier= 'B04_lat')
            project['id'] = retrieved.id
        except:
            pass

        bw = Biblical_Work.objects.get(identifier=project['book'])
        if bw:
            project['biblical_work'] = bw
            del project['book']

        p = Project(**project)
        p.save()
        #need to have created it before updating manytomany fields
        #project
        for user in edition_transcribers:
            u = User.objects.get(username=user)
            if u:
                p.edition_transcribers.add(u)


#
#
# #B06_grc_bi
#         project = {
#                    'identifier': 'B06_grc_bi',
#                    'name': 'Greek Romans',
#                    'book_number': 6,
#                    'book_string': 'Rm',
#                    'language': 'grc',
#                    'base_text_siglum': 'TR',
#                    'base_text_label': 'TR',
#                    'public': True
#                    }
#         edition_transcribers = ['Tess']
#
#         try:
#             retrieved = Project.objects.get(identifier= 'B06_grc_bi')
#             project['id'] = retrieved.id
#         except:
#             pass
#         p = Project(**project)
#         p.save()
#         #need to have created it before updating manytomany fields
#         #project
#         for user in edition_transcribers:
#             u = User.objects.get(username=user)
#             if u:
#                 p.edition_transcribers.add(u)
#
# #B07_grc_bi
#         project = {
#                    'identifier': 'B07_grc_bi',
#                    'name': 'Greek 1 Corinthians',
#                    'book_number': 7,
#                    'book_string': '1 Co',
#                    'language': 'grc',
#                    'base_text_siglum': 'TR',
#                    'base_text_label': 'TR',
#                    'public': True
#                    }
#         edition_transcribers = ['Tess']
#
#         try:
#             retrieved = Project.objects.get(identifier= 'B07_grc_bi')
#             project['id'] = retrieved.id
#         except:
#             pass
#         p = Project(**project)
#         p.save()
#         #need to have created it before updating manytomany fields
#         #project
#         for user in edition_transcribers:
#             u = User.objects.get(username=user)
#             if u:
#                 p.edition_transcribers.add(u)
#
# #B08_grc_bi
#         project = {
#                    'identifier': 'B08_grc_bi',
#                    'name': 'Greek 2 Corinthians',
#                    'book_number': 8,
#                    'book_string': '2 Co',
#                    'language': 'grc',
#                    'base_text_siglum': 'TR',
#                    'base_text_label': 'TR'
#                    }
#         edition_transcribers = ['Tess']
#
#         try:
#             retrieved = Project.objects.get(identifier= 'B08_grc_bi')
#             project['id'] = retrieved.id
#         except:
#             pass
#         p = Project(**project)
#         p.save()
#         #need to have created it before updating manytomany fields
#         #project
#         for user in edition_transcribers:
#             u = User.objects.get(username=user)
#             if u:
#                 p.edition_transcribers.add(u)
#
#
#
