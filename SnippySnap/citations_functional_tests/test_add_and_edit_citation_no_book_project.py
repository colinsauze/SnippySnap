from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from rest_framework.renderers import JSONRenderer
from citations.serializers import CitationSerializer
from citations import models
from transcriptions.models import Transcription
from transcriptions.models import Verse
import re
import pickle
import json
import time
from unittest import skip
from django.utils import timezone


class AddAndEditCitationAsCitationEditorAndEditionTranscriber(LoggedInFunctionalTest):

    #Tess is a citation editor and an edition transcriber for the Greek Galatians project

    #she logs into the system
    def setUp(self):
        self.browser = webdriver.Firefox()

        ## add some citations to work with
        self.addTestData()
        ##add another author and another two works for testing this specifically (not added in base
        ##because I don't want them to mess up the other tests
        a4_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA4',
                   'full_name': 'Test Author 4',
                   'language': 'grc'
                   }
        self.a4 = models.Author.objects.create(**a4_data)
        w3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW3',
                   'author': self.a4,
                   'title': 'Test Work 3',
                   'language': 'grc',
                   'clavis': '1235'
                   }
        self.w3 = models.Work.objects.create(**w3_data)
        w4_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW4',
                   'author': self.a4,
                   'title': 'Test Work 4',
                   'language': 'grc',
                   'clavis': '1236'
                   }
        self.w4 = models.Work.objects.create(**w4_data)

        ##add a verse of transcription data to test against (and a transcription so we can create a verse)
        transcription_data = {'identifier': 'NT_GRC_TR_B09',
                              'corpus': self.grc_corpus,
                              'document_id': 'TR',
                              'tei': '',
                              'source': '',
                              'siglum': 'TR',
                              'document_type': 'edition',
                              'language': 'grc',
                              'total_verses': 1,
                              'total_unique_verses': 1,
                              'work': self.bw2,
                              'public': True
                              }
        self.tr1 = Transcription.objects.create(**transcription_data)

        verse_data = {'identifier': 'NT_GRC_TR_B09K01V01',
                      'index': 1,
                      'work': self.bw2,
                      'chapter_number': 1,
                      'verse_number': 1,
                      'tei': '<ab xmlns="http://www.tei-c.org/ns/1.0" n="B09K1V1"><seg type="line" subtype="here"><pc>‾‾</pc></seg><w>Παῦλος</w><w>ἀπόστολος</w><w>οὐκ</w><w>ἀπ᾿</w><w>ἀνθρώπων</w><pc>,</pc><w>οὐδὲ</w><w>δι᾿</w><w>ἀνθρώπου</w><pc>,</pc><w>ἀλλὰ</w><w>διὰ</w><w>Ἰησοῦ</w><w>Χριστοῦ</w><pc>,</pc><w>καὶ</w><w>Θεοῦ</w><w>πατρὸς</w><w>τοῦ</w><w>ἐγείραντος</w><w>αὐτὸν</w><w>ἐκ</w><w>νεκρῶν</w><pc>,</pc></ab>',
                      'siglum': 'TR',
                      'transcription': self.tr1,
                      'language': 'grc',
                      'public': True
                      }
        self.v1 = Verse.objects.create(**verse_data)

        project_data = {'identifier': 'B09_grc',
                'name': 'Galatians Greek',

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
        self.p3 = models.Project.objects.create(**project_data)

        credentials = {
            'username': 'tess',
            'password': 'secret',
            'display_name': 'Tess Edition Tester'
            }
        self.tess = self.addCitationEditorUser(credentials)


        self.p3.edition_transcribers.add(self.tess)

        #she logs in
        self.logUserIn(credentials)

    def test_noBiblicalWorkProject(self):

        #Tess goes to the list of citations
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))

        #there are 2 entries because the citations of John and Galatians are shown (plus a header row)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 3)

        #she clicks on the link to add a new citation
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))
        self.wait_for(lambda: self.browser.find_element_by_link_text('add new citation').click())

        #she gets a form to add a new edition
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        self.assertEqual(len(self.browser.find_element_by_id('biblical_work').find_elements_by_xpath('./option')), 3)
        self.assertEqual(self.browser.find_element_by_id('biblical_work').get_attribute('value'), 'none')
        self.assertTrue(self.browser.find_element_by_id('biblical_work').is_enabled())
