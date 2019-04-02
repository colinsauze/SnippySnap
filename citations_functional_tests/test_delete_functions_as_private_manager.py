from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from rest_framework.renderers import JSONRenderer
from citations.serializers import CitationSerializer
from citations import models
from transcriptions import models as transcription_models
import re
import pickle
import json
import time
from unittest import skip
from django.utils import timezone




class PrivateDeletionTests(LoggedInFunctionalTest):

    #Ben is a private citation Manager so he has deletion permissions for
    #citations in that project (self.p1)

    # def addBiblicalWorkData(self):
    #     biblical_work_data = {'identifier': 'NT_GRC_John',
    #                           'book_number': 4,
    #                           'name': 'John',
    #                           'corpus': 'NT'
    #                           }
    #     self.bw1 = transcription_models.Work.objects.create(**biblical_work_data)
    #     biblical_work_data_2 = {'identifier': 'NT_GRC_Gal',
    #                           'book_number': 9,
    #                           'name': 'Galatians',
    #                           'corpus': 'NT',
    #                           'total_chapters': 2,
    #                           'verses_per_chapter': {1: 2, 2: 2}
    #                           }
    #     self.bw2 = transcription_models.Work.objects.create(**biblical_work_data_2)

    def add_data(self):
        ##add data specifically designed to test deletion relations properly
        #add the private project data
        project_data1 = {'identifier': 'B09_grc',
                        'name': 'Galatians Greek',
                        'biblical_work': self.bw2,
                        'public': False,
                        'language': 'grc',
                        'base_text_siglum': 'TR',
                        'base_text_label': 'TR',
                        'form_settings': {'privatecitation' : {'edition_transcribers': ['source_details', 'citation_details', 'ms_variants_div', 'biblical_catena_div', 'dependencies_div', 'parallels_div', 'source_section', 'comments_section', 'status_details']}},
                        'submit_settings': {'privatecitation' : {'edition_transcribers': ['submit_same', 'submit_home', 'submit_next', 'submit_continue', 'delete', 'reset_form']} },
                        'preselects': {'privatecitation' : {'online_transcribers': {'language': 'grc', 'onlinecorpus': 'TO2'},
                                                    'edition_transcribers': {'language': 'grc'}},
                                  },
                        }
        self.p1 = models.Project.objects.create(**project_data1)
        #add a decoy private project for testing
        project_data2 = {'identifier': 'B09_grc_2',
                        'name': 'Galatians Greek',
                        'biblical_work': self.bw2,
                        'public': False,
                        'language': 'grc',
                        'base_text_siglum': 'TR',
                        'base_text_label': 'TR',
                        'form_settings': {'privatecitation' : {'online_transcribers': ['source_details', 'search_details_div', 'citation_details','biblical_catena_div', 'source_section', 'comments_section', 'status_details'],
                                                        'edition_transcribers': ['source_details', 'citation_details', 'ms_variants_div', 'biblical_catena_div', 'dependencies_div', 'parallels_div', 'source_section', 'comments_section', 'status_details']}},
                        'submit_settings': {'privatecitation' : {'online_transcribers': ['submit_same', 'submit_home', 'submit_continue', 'reset_form'],
                                                          'edition_transcribers': ['submit_same', 'submit_home', 'submit_next', 'submit_continue', 'reset_form']} },
                        'preselects': {'privatecitation' : {'online_transcribers': {'language': 'grc', 'onlinecorpus': 'TO2'},
                                                    'edition_transcribers': {'language': 'grc'}},
                                  },
                        }
        self.p2 = models.Project.objects.create(**project_data2)

        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        self.a1 = models.Author.objects.create(**a1_data)
        a2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA2',
                   'full_name': 'Test Author 2',
                   'language': 'grc'
                   }
        self.a2 = models.Author.objects.create(**a2_data)
        a3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA3',
                   'full_name': 'Test Author 3',
                   'language': 'grc'
                   }
        self.a3 = models.Author.objects.create(**a3_data)


        w1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW1',
                   'author': self.a1,
                   'title': 'Test Work 1',
                   'language': 'grc'
                   }
        self.w1 = models.Work.objects.create(**w1_data)
        w2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW2',
                   'author': self.a2,
                   'title': 'Test Work 2',
                   'language': 'grc',
                   'clavis': '1234'
                   }
        self.w2 = models.Work.objects.create(**w2_data)
        w3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW3',
                   'author': self.a2,
                   'title': 'Test Work 3',
                   'language': 'grc',
                   'clavis': '1235',
                   }
        self.w3 = models.Work.objects.create(**w3_data)
        self.w3.other_possible_authors.add(self.a1)

        s1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TS1',
                   'title': 'Test Series 1'
                   }
        self.s1 = models.Series.objects.create(**s1_data)
        s2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TS2',
                   'title': 'Test Series 2'
                   }
        self.s2 = models.Series.objects.create(**s2_data)

        o1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TO1',
                   'title': 'Test Onlinecorpus 1'
                   }
        self.o1 = models.OnlineCorpus.objects.create(**o1_data)
        o2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TO2',
                   'title': 'Test Onlinecorpus 2'
                   }
        self.o2 = models.OnlineCorpus.objects.create(**o2_data)

        e1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': self.w1,
                   'editor': 'Migne',
                   'series': self.s1,
                   'year': '1906',
                   'volume': '6',
                   'onlinecorpus': self.o1
                   }
        self.e1 = models.Edition.objects.create(**e1_data)

        e2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': self.w1,
                   'series': self.s1,
                   'editor': 'Jones',
                   'year': '1997'
                   }
        self.e2 = models.Edition.objects.create(**e2_data)


        c1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e2,
                   'biblical_work': self.bw2,
                   'status': 'live',
                   'citation_text': 'και αρνῃ μεν το θεος ην ο λογος'
                   }
        self.c1 = models.Citation.objects.create(**c1_data)


        c2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'John.1.1',
                   'biblical_reference_sortable': 4001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e1,
                   'biblical_work': self.bw1,
                   'onlinecorpus': self.o1,
                   'status': 'deprecated but flagged',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν'
                   }
        self.c2 = models.Citation.objects.create(**c2_data)

        c3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw2,
                   'onlinecorpus': self.o1,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν'
                   }
        self.c3= models.Citation.objects.create(**c3_data)

        pc1_data = {'created_by': 'ben',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e1,
                   'biblical_work': self.bw2,
                   'onlinecorpus': self.o1,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων',
                   'project': self.p1,
                   'copied_to_private_time': timezone.now(),
                   }
        self.pc1= models.PrivateCitation.objects.create(**pc1_data)

        pc2_data = {'created_by': 'ben',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e1,
                   'biblical_work': self.bw2,
                   'onlinecorpus': self.o1,
                   'status': 'live',
                   'citation_text': 'οὐδὲ δι᾿ ἀνθρώπου ἀλλὰ διὰ Ἰησοῦ Χριστοῦ',
                   'project': self.p1,
                   'copied_to_private_time': timezone.now(),
                   }
        self.pc2= models.PrivateCitation.objects.create(**pc2_data)

        pc3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e1,
                   'biblical_work': self.bw2,
                   'onlinecorpus': self.o1,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν',
                   'project': self.p2,
                   'copied_to_private_time': timezone.now(),
                   }
        self.pc3= models.PrivateCitation.objects.create(**pc3_data)

        d1_data = {'relation_type': 'same_as',
                   'author': self.a2,
                   'work': self.w2,
                   'work_reference': '15.3',
                   'citation': self.c1
                   }
        self.d1 = models.Dependency.objects.create(**d1_data)

        d2_data = {'relation_type': 'same_as',
                   'author': self.a1,
                   'work': self.w1,
                   'work_reference': '15.1',
                   'citation': self.c3
                   }
        self.d2 = models.Dependency.objects.create(**d2_data)

        pd1_data = {'relation_type': 'same_as',
                   'author': self.a1,
                   'work': self.w1,
                   'work_reference': '15.2',
                   'citation': self.pc1
                   }
        self.pd1 = models.PrivateDependency.objects.create(**pd1_data)

    #she logs into the system
    def setUp(self):
        self.browser = webdriver.Firefox()

        credentials = {
            'username': 'ben',
            'password': 'secret',
            'display_name': 'Ben Tester'
            }
        self.ben = self.addPrivateCitationManagerUser(credentials)
        self.addBiblicalWorkData()
        self.add_data()

        self.p1.edition_transcribers.add(self.ben)

        #she logs in
        self.logUserIn(credentials)


    def test_deleteCitation(self):

        #Ben does to the edit screen for a citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.pc1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('citation_text').get_attribute('value'), 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων'))

        #he clicks on the delete button
        self.browser.find_element_by_id('delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete').click()
        self.wait_for(lambda: self.assertTrue('Delete Citation' in self.browser.title))

        #there is a table on the screen
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('dependency_table')))
        #there is a list containing the citation that he has asked to delete
        self.assertTrue(self.element_is_on_page('citation_list'))
        #The citation's string representation is shown
        citlist = self.browser.find_element_by_id('citation_list')
        list_items = citlist.find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.pc1.__str__())
        self.browser.save_screenshot('delete.png')
        #There is a button to delete it
        self.assertTrue(self.element_is_on_page('delete_privatecitation_%d' % self.pc1.id))
        #when Ben clicks on the string representation of the citation he is taken to the details to check it is the correct one
        links = self.browser.find_elements_by_tag_name('a')

        for link in links:
            if link.text == self.pc1.__str__():
                link.click()

        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Citation'))
        #the url is correct
        self.assertIn('/citations/citation/%s' % self.pc1.id, self.browser.current_url)
        #there is a table showing the citation
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))
        self.browser.save_screenshot('delete.png')
        #he clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Citation' in self.browser.title), 50)

        #he clicks to cancel and returns to the list of citations
        self.browser.find_element_by_id('cancel_delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('cancel_delete').click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #he clicks back and is returned to the deletion page
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Citation' in self.browser.title), 50)

        #he clicks to delete the only item on the page and is returned to the citation list
        self.browser.find_element_by_id('delete_privatecitation_%d' % self.pc1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_privatecitation_%d' % self.pc1.id).click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #there is now only one private citation in the table now (plus a header row)
        self.check_rows_in_table('data_table', 2)

         #the item is no longer in the database
        self.assertFalse(models.PrivateCitation.objects.filter(pk=self.pc1.id).exists())
        #all of the public citations are still there
        self.assertEqual(models.Citation.objects.all().count(), 3)
        #the dependncy associated with this private citation has also been deleted
        self.assertFalse(models.PrivateDependency.objects.filter(pk=self.pd1.id).exists())

    def test_deleteCitationFromOtherProject(self):

        #Ben tried to go to the delete page for a citation that is not in his Project
        self.browser.get('%s/citations/citation/delete/%s' % (self.live_server_url, self.pc3.id))
        #but he is not allowed
        self.wait_for(lambda: self.assertTrue('404 error' in self.browser.title), 50)


    def test_deleteAuthor(self):

        #Ben tried to go to the delete page for a citation that is not in his Project
        self.browser.get('%s/citations/author/delete/%s' % (self.live_server_url, self.a1.id))
        #but he is not allowed
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title), 50)
