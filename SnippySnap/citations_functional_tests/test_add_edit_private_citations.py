from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from rest_framework.renderers import JSONRenderer
from citations.serializers import PrivateCitationSerializer
from citations import models
from transcriptions.models import Transcription
from transcriptions.models import Verse
import re
import pickle
import json
import time
from unittest import skip
from django.utils import timezone


class AddAndEditPrivateCitation(LoggedInFunctionalTest):

    #Ben has a private citation project

    #he logs into the system
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

        verse_data1 = {'identifier': 'NT_GRC_TR_B09K01V01',
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
        self.v1 = Verse.objects.create(**verse_data1)
        verse_data2 = {'identifier': 'NT_GRC_TR_B09K01V02',
                      'index': 1,
                      'work': self.bw2,
                      'chapter_number': 1,
                      'verse_number': 2,
                      'tei': '<ab xmlns="http://www.tei-c.org/ns/1.0" n="B09K1V2"><w>καὶ</w><w>οἱ</w><w>σὺν</w><w>ἐμοὶ</w><w>πάντες</w><w>ἀδελφοί</w><pc>,</pc><w>ταῖς</w><w>ἐκκλησίαις</w><w>τῆς</w><w>Γαλατίας</w><pc>·</pc></ab>',
                      'siglum': 'TR',
                      'transcription': self.tr1,
                      'language': 'grc',
                      'public': True
                      }
        self.v2 = Verse.objects.create(**verse_data2)
        verse_data3 = {'identifier': 'NT_GRC_TR_B09K02V01',
                      'index': 1,
                      'work': self.bw2,
                      'chapter_number': 2,
                      'verse_number': 1,
                      'tei': '<ab xmlns="http://www.tei-c.org/ns/1.0" n="B09K2V1"><seg type="line" subtype="here"><pc>‾‾</pc></seg><w>Ἔπειτα</w><w>διὰ</w><w>δεκατεσσάρων</w><w>ἐτῶν</w><w>πάλιν</w><w>ἀνέβην</w><w>εἰς</w><w>Ἱεροσόλυμα</w><w>μετὰ</w><w>Βαρνάβα</w><pc>,</pc><w>συμπαραλαβὼν</w><w>καὶ</w><w>Τίτον</w><pc>.</pc></ab>',
                      'siglum': 'TR',
                      'transcription': self.tr1,
                      'language': 'grc',
                      'public': True
                      }
        self.v3 = Verse.objects.create(**verse_data3)
        verse_data4 = {'identifier': 'NT_GRC_TR_B09K02V02',
                      'index': 1,
                      'work': self.bw2,
                      'chapter_number': 2,
                      'verse_number': 2,
                      'tei': '<ab xmlns="http://www.tei-c.org/ns/1.0" n="B09K2V2"><w>ἀνέβην</w><w>δὲ</w><w>κατὰ</w><w>ἀποκάλυψιν</w><pc>,</pc><w>καὶ</w><w>ἀνεθέμην</w><w>αὐτοῖς</w><w>τὸ</w><w>εὐαγγέλιον</w><w>ὃ</w><w>κηρύσσω</w><w>ἐν</w><w>τοῖς</w><w>ἔθνεσι</w><pc>,</pc><w>κατ᾿</w><w>ἰδίαν</w><w>δὲ</w><w>τοῖς</w><w>δοκοῦσι</w><pc>,</pc><w>μή</w><w>πως</w><w>εἰς</w><w>κενὸν</w><w>τρέχω</w><w>ἢ</w><w>ἔδραμον</w><pc>.</pc></ab>',
                      'siglum': 'TR',
                      'transcription': self.tr1,
                      'language': 'grc',
                      'public': True
                      }
        self.v4 = Verse.objects.create(**verse_data4)

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
                        'name': 'Galatians Greek 2',
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

        ##add some private citations (including a decoy from another project)
        pc1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 2,
                   'biblical_work': self.bw2,
                   'status': 'live',
                   'citation_text': 'και αρνῃ μεν το θεος ην ο λογος',
                   'project': self.p2,
                   'copied_to_private_time': timezone.now(),
                   }
        self.pc1 = models.PrivateCitation.objects.create(**pc1_data)
        pc2_data = {'created_by': 'ben',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw2,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου',
                   'project': self.p1,
                   'copied_to_private_time': timezone.now(),
                   'private_comments': 'This needs checking again'
                   }
        self.pc2 = models.PrivateCitation.objects.create(**pc2_data)

        pc3_data = {'created_by': 'ben',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'Gal.2.1',
                   'biblical_reference_sortable': 9002001,
                   'chapter': 2,
                   'verse': 1,
                   'biblical_work': self.bw2,
                   'status': 'live but flagged',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ',
                   'project': self.p1,
                   'copied_to_private_time': timezone.now(),
                   }
        self.pc3 = models.PrivateCitation.objects.create(**pc3_data)

        credentials = {
            'username': 'ben',
            'password': 'secret',
            'display_name': 'Ben Tester'
            }
        self.ben = self.addPrivateCitationManagerUser(credentials)

        self.p1.edition_transcribers.add(self.ben)

        #he logs in
        self.logUserIn(credentials)

    def test_ListViewPrivateCitation(self):

        #Ben wants to see his citations
        #he has already logged in
        #he is only a member of one project right now so he is logged into that
        #It is his private project for Greek Galatians
        #he is an edition transcriber on that project

        #he goes to the list of citations
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))

        #he sees two citations in the list (plus the header row)
        self.check_rows_in_table('data_table', 3)
        #there is no button to apply a project filter
        self.assertFalse(self.element_is_on_page('apply_project_filter_button'))
        #or remove one
        self.assertFalse(self.element_is_on_page('remove_project_filter_button'))

        #he clicks on the view link for the first citation which takes him to the full details of that citation
        self.browser.find_element_by_css_selector('.view_link').click()
        self.wait_for(
            lambda: self.assertIn('/citations/citation/%s?' % self.pc2.id, self.browser.current_url)
        )
        #he sees the correct citation
        self.check_text_of_table_cell('data_instance_table', 0, 0, 'Galatians 1:1')

        #he clicks the link to go back to the list of citations
        self.browser.find_element_by_link_text('Citation List').click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))

        #he tried to bypass the system by entering the url to edit a citation that is not part of his project
        self.browser.get('%s/citations/citation/%s' % (self.live_server_url, self.pc1.id))
        #but the system will not even let him see it (well done system!)
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title), 50)



    def test_editPrivateCitation(self):

        #Ben wants to edit one of his citations
        #he goes to the list of citations
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))
        #he sees two citations in the list (plus the header row)
        self.check_rows_in_table('data_table', 3)

        #he clicks on the edit link for the first citation which takes him to the form to edit that citations
        self.browser.find_elements_by_css_selector('.edit_link')[0].click()

        #the citation opens in the editing form
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('citation_text').get_attribute('value'), 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου'))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('project').get_attribute('value')), self.p1.id))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('private_comments').get_attribute('value'), self.pc2.private_comments))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('copied_to_private_time').get_attribute('value'), ''))

        #and saves again without making changes
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #now just check the entire model is the same after loading and saving
        stored_citation = models.PrivateCitation.objects.get(id=self.pc2.id)
        stored_citation.last_modified_time = 'test'
        stored_citation.version_number = 1
        stored_json = JSONRenderer().render(PrivateCitationSerializer(stored_citation).data)
        stored = pickle.dumps(stored_json)

        #he reopens the citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.pc2.id))

        #the citation opens in the editing form
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 4), 100)
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none'))
        #he saves again without making changes
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #get the data back from the database
        new_citation = models.PrivateCitation.objects.get(id=self.pc2.id)
        new_citation.last_modified_time = 'test'
        new_citation.version_number = 1
        new_json = JSONRenderer().render(PrivateCitationSerializer(new_citation).data)
        new = pickle.dumps(new_json)

        self.wait_for(lambda: self.assertEqual(stored, new))



    def test_addNewPrivateCitation(self):

        #Ben wants to add a new citation to the database
        #he has already logged in
        #he is only a member of one project right now so he is logged into that
        #It is his private project for Greek Galatians
        #he is an edition transcriber on that project

        ##first add some author restrictions
        self.p1.author_ids.add(self.a1)
        self.p1.author_ids.add(self.a4)
        #and check they have saved because there were some timing problems
        self.wait_for(lambda: self.assertTrue(models.Project.objects.get(pk=self.p1.id).author_ids.all().count() == 2))

        #he goes to the list of citations and clicks on the link to add a new citation
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))
        #he only sees the 2 citations assigned to his project
        #there are lots more public citations in the database and another private one which is not part of the project
        #they do not show up here
        self.check_rows_in_table('data_table', 3)

        self.wait_for(lambda: self.browser.find_element_by_link_text('add new citation').click())

        #he goes to the list of citations and clicks on the link to add a new citation
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))
        self.wait_for(lambda: self.browser.find_element_by_link_text('add new citation').click())

        #he gets a form to add a new citation
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #the project id is automatically completed
        self.wait_for(lambda: self.assertTrue(int(self.browser.find_element_by_id('project').get_attribute('value')), self.p1.id))

        #As Ben is a citation manager for this project he can see all of the form fields requested in his project settings
        ##there is no manager overide for private citations it just all needs to be specified in project settings
        self.assertTrue(self.browser.find_element_by_id('source_details').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('citation_details').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('ms_variants_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('biblical_catena_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('dependencies_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('parallels_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('comments_section').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('status_details').is_displayed())

        #he cannot see the div that is not specified in the settings
        self.assertFalse(self.browser.find_element_by_id('search_details_div').is_displayed())

        #He also has these action buttons in the submit section because they were specified in the project settings
        #submit_same, submit_next, submit_home, submit_continue, delete
        self.assertTrue(self.browser.find_element_by_id('submit_section').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_same').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_next').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_home').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_continue').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('delete').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('reset_form').is_displayed())

        #the date and Ben's initials are shown in the boxes on the right
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('created_by').get_attribute('value'), ''))
        self.assertEqual(self.browser.find_element_by_id('created_by').get_attribute('value'), 'Ben Tester')
        ##we can't predict the date so we will just check it isn't empty
        self.assertNotEqual(self.browser.find_element_by_id('created_time_display').get_attribute('value'), '')

        #There is a dropdown menu to select the biblical work which is already filled in with the project settings but as she is a citation manager the options are still enabled
        self.assertEqual(len(self.browser.find_element_by_id('biblical_work').find_elements_by_xpath('./option')), 3)
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        self.assertTrue(self.browser.find_element_by_id('biblical_work').is_enabled())

        #There is another for language which is already completed with projects settings but as she is a citation manager the options are still enabled
        self.assertEqual(len(self.browser.find_element_by_id('language').find_elements_by_xpath('./option')), 3)
        self.assertEqual(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')
        self.assertTrue(self.browser.find_element_by_id('language').is_enabled())

        #There is also one for onlinecorpus which has two options and is enabled
        self.assertEqual(len(self.browser.find_element_by_id('onlinecorpus').find_elements_by_xpath('./option')), 3)
        self.assertTrue(self.browser.find_element_by_id('onlinecorpus').is_enabled())

        #Ben adds the chapter and verse 1:1
        self.browser.find_element_by_id('chapter').send_keys('1')
        self.browser.find_element_by_id('verse').send_keys('1')

        #He moves the cursor from the verse box (to trigger the event on verse text box)
        self.browser.find_element_by_id('language').click()
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'), 50)
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, '‾‾ Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν,')

        #There is a dropdown for selecting the author which is populated and enabled
        ##there are 3 greek authors in the database but this project specifies 2 so
        #the author dropdown has 2 options (plus a select/none line)
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 3), 100)

        self.assertTrue(self.browser.find_element_by_id('author').is_enabled())

        #work is not populated properly but has a single option and disabled (because it is determined by author selection)
        self.assertEqual(len(self.browser.find_element_by_id('work').find_elements_by_xpath('./option')), 1)
        self.assertFalse(self.browser.find_element_by_id('work').is_enabled())

        #and the same is true for edition which is dependent on work selection
        self.assertEqual(len(self.browser.find_element_by_id('edition').find_elements_by_xpath('./option')), 1)
        self.assertFalse(self.browser.find_element_by_id('edition').is_enabled())

        #he then clicks save
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        #he gets an error message that tells him the data is not valid and the text of the author and work labels
        #is highlighted in red indicating that this data is required.
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('error')))
        self.assertTrue('The data is not valid and cannot be saved' in self.browser.find_element_by_id('error').get_attribute('innerHTML'))
        ##I'm not sure how to test for colour so I will just check the appropriate class has been applied
        self.assertTrue('missing' in self.browser.find_element_by_id('author').find_element_by_xpath('.//ancestor::label').get_attribute('class'))
        self.assertTrue('missing' in self.browser.find_element_by_id('work').find_element_by_xpath('.//ancestor::label').get_attribute('class'))

        #he closes the error message
        self.browser.find_element_by_id('error_close').click()

        #Ben selects the author TA2
        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA4, Test Author 4')
        #the work select box is populated and now enabled for selection
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('work').find_elements_by_xpath('./option')), 3))
        self.assertTrue(self.browser.find_element_by_id('work').is_enabled())
        #he selects the work
        Select(self.browser.find_element_by_id('work')).select_by_visible_text('TW4, Test Work 4')

        #the clavis number is displayed
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('clavis_check').text, 'Clavis: 1236'))

        #she adds the work reference
        self.browser.find_element_by_id('work_reference').send_keys('15.3')

        #there are no edition of this work so the edition box has no options
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('edition').find_elements_by_xpath('./option')), 1))
        self.assertTrue(self.browser.find_element_by_id('edition').is_enabled())

        #he tries saving again
        ##get the current url for use later to make sure page has refreshed
        url = self.browser.current_url

        #he clicks on 'save and continue editing' to save her progress
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(url != self.browser.current_url), 100)

        #he is redirected to a slightly different url which now has the id of the current entry in the address
        self.assertTrue(re.compile('^.+?/citations/citation/edit/\d+\?_show=\d+$').match(self.browser.current_url))
        new_citation_id = re.compile('^.+?/citations/citation/edit/(\d+)\?_show=\d+$').match(self.browser.current_url).groups(1)[0]
        self.assertEqual(len(models.PrivateCitation.objects.all()), 4)

        ##the rest of this is tested in other files already, here I was just testing a new private citation could be saved



    ## the save options are worth testing here as well to make sure the urls all work
    def test_submitSame(self):
        #Edith loads an existing citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.pc2.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''), 50)

        #she clicks the save and add another button
        self.browser.find_element_by_id('submit_same').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_same').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(self.browser.current_url.split('#')[0] == '%s/citations/citation/edit' % self.live_server_url), 50)

        ## wait till the author has been reset
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none'), 50)


        #the verse details are completed and are for the same verse
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('verse').get_attribute('value')), self.pc2.verse))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), self.pc2.chapter))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'))
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, '‾‾ Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν,')


    def test_submitNext(self):
        ##add some extra citations specifically required for this test
        pc4_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.1.2',
                   'biblical_reference_sortable': 9001002,
                   'chapter': 1,
                   'verse': 2,
                   'biblical_work': self.bw2,
                   'status': 'deprecated but flagged',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν',
                   'project': self.p1,
                   }
        self.pc4 = models.PrivateCitation.objects.create(**pc4_data)

        ##add some extra citations specifically required for this test
        pc5_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.2.2',
                   'biblical_reference_sortable': 9002002,
                   'chapter': 2,
                   'verse': 2,
                   'biblical_work': self.bw2,
                   'status': 'deprecated but flagged',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν',
                   'project': self.p1,
                   }
        self.pc5 = models.PrivateCitation.objects.create(**pc5_data)

        #Edith loads an existing citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.pc2.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''), 50)

        #she clicks the save and add another button
        self.browser.find_element_by_id('submit_next').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_next').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(self.browser.current_url.split('#')[0] == '%s/citations/citation/edit' % self.live_server_url), 50)
        #the verse details are completed and are for the next verse
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('biblical_work').get_attribute('value') == ''))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), self.pc2.chapter))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('verse').get_attribute('value')), 2))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'), 50)
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, 'καὶ οἱ σὺν ἐμοὶ πάντες ἀδελφοί, ταῖς ἐκκλησίαις τῆς Γαλατίας·')


        #she loads another which is at the end of a chapter
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.pc4.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        ##wait until all the data has been completed
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('author').get_attribute('value'), self.a2.id))

        #she clicks the save and add another button
        self.browser.find_element_by_id('submit_next').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_next').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(self.browser.current_url.split('#')[0] == '%s/citations/citation/edit' % self.live_server_url), 50)
        #the verse details are completed and are for the first verse in the next chapter
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('biblical_work').get_attribute('value') == ''))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), 2))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('verse').get_attribute('value')), 1))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'))
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, '‾‾ Ἔπειτα διὰ δεκατεσσάρων ἐτῶν πάλιν ἀνέβην εἰς Ἱεροσόλυμα μετὰ Βαρνάβα, συμπαραλαβὼν καὶ Τίτον.')

        #she loads the last verse of the book
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.pc5.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''), 50)

        #she clicks the save and add another button
        self.browser.find_element_by_id('submit_next').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_next').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(self.browser.current_url.split('#')[0] == '%s/citations/citation/edit' % self.live_server_url), 50)
        #this is the last verse in the book so the verse details stay as they were for the previous citation (tthere is no next verse)
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('biblical_work').get_attribute('value') == ''))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), 2))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('verse').get_attribute('value')), 2))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'))
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, 'ἀνέβην δὲ κατὰ ἀποκάλυψιν, καὶ ἀνεθέμην αὐτοῖς τὸ εὐαγγέλιον ὃ κηρύσσω ἐν τοῖς ἔθνεσι, κατ᾿ ἰδίαν δὲ τοῖς δοκοῦσι, μή πως εἰς κενὸν τρέχω ἢ ἔδραμον.')

        #There is a dropdown for selecting the author which is populated and enabled
        #the author dropdown has 3 options (plus a select/none line)
        self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 4)
        self.assertTrue(self.browser.find_element_by_id('author').is_enabled())
