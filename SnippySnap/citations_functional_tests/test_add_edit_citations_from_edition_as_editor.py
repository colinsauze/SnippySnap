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

        credentials = {
            'username': 'tess',
            'password': 'secret',
            'display_name': 'Tess Editor Tester'
            }
        self.tess = self.addCitationEditorUser(credentials)

        self.addProjectData()
        self.p1.edition_transcribers.add(self.tess)

        #she logs in
        self.logUserIn(credentials)

    def test_resetForm(self):

        #Tess begins editing a new record
        self.browser.get('%s/citations/citation/edit' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #she adds the new data
        self.browser.find_element_by_id('chapter').send_keys('1')
        self.browser.find_element_by_id('verse').send_keys('1')
        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA2, Test Author 2')
        #the work select box is populated and now enabled for selection
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('work').find_elements_by_xpath('./option')), 2))
        self.assertTrue(self.browser.find_element_by_id('work').is_enabled())
        #As this author only has one work it is selected automatically
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.browser.find_element_by_id('work_reference').send_keys('15.3')

        #she realises she has made a mistake and wants to start again
        #she clicks the reset_form button
        self.browser.find_element_by_id('reset_form').location_once_scrolled_into_view
        self.browser.find_element_by_id('reset_form').click()
        ##wait until the data is is loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('work').get_attribute('value'), 'none'), 50)
        #the data she had entered has gone
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        self.assertFalse(self.browser.find_element_by_id('biblical_work').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('chapter').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')
        self.assertFalse(self.browser.find_element_by_id('language').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none')
        self.assertEqual(len(self.browser.find_element_by_id('work').find_elements_by_xpath('./option')), 1)
        self.assertEqual(self.browser.find_element_by_id('work').get_attribute('value'), 'none')
        self.assertEqual(self.browser.find_element_by_id('work_reference').get_attribute('value'), '')


        #she enters the data again
        self.browser.find_element_by_id('chapter').send_keys('1')
        self.browser.find_element_by_id('verse').send_keys('1')
        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA2, Test Author 2')
        self.browser.find_element_by_id('work_reference').send_keys('15.3')

        #she saves the data
        ##get the current url for use later to make sure page has refreshed
        url = self.browser.current_url

        #she clicks on 'save and continue editing' to save her progress
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(url != self.browser.current_url), 50)
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('biblical_work').get_attribute('value'), ''))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id), 50)
        self.browser.save_screenshot('citationform.png')
        #the saved data is back in the form
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        self.assertEqual(self.browser.find_element_by_id('chapter').get_attribute('value'), '1')
        self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1')
        self.assertEqual(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')
        self.assertEqual(int(self.browser.find_element_by_id('author').get_attribute('value')), self.a2.id)
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.assertEqual(self.browser.find_element_by_id('work_reference').get_attribute('value'), '15.3')

        #She adds some further details
        #she selects edition
        Select(self.browser.find_element_by_id('edition')).select_by_visible_text('Jones, 1997')
        #edition page and line refs
        self.browser.find_element_by_id('page_reference').send_keys('36')
        self.browser.find_element_by_id('line_reference').send_keys('42')
        #the citation text and reference type
        self.browser.find_element_by_id('citation_text').send_keys('{Διὸ καὶ οὕτως ἤρξατο·} Παῦλος ἀπόστολος, οὐκ ἀπ’ ἀνθρώπων, οὐδὲ δι’ ἀνθρώπων.')
        Select(self.browser.find_element_by_id('citation_reference_type')).select_by_visible_text('Reference')
        Select(self.browser.find_element_by_id('citation_type')).select_by_visible_text('CIT')

        #She has some manuscript variants to add
        self.browser.find_element_by_id('manuscript_variants_0_headword').send_keys('ἀνθρώπων')
        self.browser.find_element_by_id('manuscript_variants_0_variant').send_keys('ἀνθρώπος')
        self.browser.find_element_by_id('manuscript_variants_0_support').send_keys('01 05 13')

        #there is another variant to add so she clicks the add manuscript variants button and more boxes appear
        self.browser.find_element_by_id('add_manuscript_variants').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_manuscript_variants').click()
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('manuscript_variants_1_headword')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('manuscript_variants_1_variant')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('manuscript_variants_1_support')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('manuscript_variants_1_maj')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_manuscript_variants_1')))

        self.browser.find_element_by_id('manuscript_variants_1_headword').send_keys('ἀνθρώπων')
        self.browser.find_element_by_id('manuscript_variants_1_variant').send_keys('ἀνθρώπω')
        self.browser.find_element_by_id('manuscript_variants_1_support').send_keys('N T G')
        self.browser.find_element_by_id('manuscript_variants_1_maj').click()
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_variants_1_maj').is_selected(), True))

        #she realises she has got something wrong again and clicks the rest_form button
        #she clicks the reset_form button
        self.browser.find_element_by_id('reset_form').location_once_scrolled_into_view
        self.browser.find_element_by_id('reset_form').click()
        #wait for the page to reload
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('edition').get_attribute('value'), 'none'), 50)

        #the saved data is still in the form so it has not reset completely
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('biblical_work').get_attribute('value'), ''), 50)
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id), 50)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('chapter').get_attribute('value'), '1'), 50)
        self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1')
        self.assertEqual(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('author').get_attribute('value')), self.a2.id), 50)
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id), 50)
        self.assertEqual(self.browser.find_element_by_id('work_reference').get_attribute('value'), '15.3')

        #but the newly added unsaved data has been cleared
        self.assertEqual(self.browser.find_element_by_id('edition').get_attribute('value'), 'none')
        self.assertEqual(self.browser.find_element_by_id('page_reference').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('line_reference').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('citation_text').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('citation_reference_type').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('citation_type').get_attribute('value'), 'CIT')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_headword').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_variant').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_support').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_maj').is_selected(), False)

        #there is no second line of variants
        self.assertFalse(self.element_is_on_page('manuscript_variants_1_headword'))
        self.assertFalse(self.element_is_on_page('manuscript_variants_1_variant'))
        self.assertFalse(self.element_is_on_page('manuscript_variants_1_support'))
        self.assertFalse(self.element_is_on_page('manuscript_variants_1_maj'))

    def test_addAndEditNewCitation(self):

        #Tess wants to add a new citation to the database
        #she has already logged in
        #she is only a member of one project right now so she is logged into that
        #It is the project for Greek Galatians
        #she is an edition transcriber on that project

        #she goes to the list of citations and clicks on the link to add a new citation
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))
        self.wait_for(lambda: self.browser.find_element_by_link_text('add new citation').click())

        #she gets a form to add a new edition
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #As Tess is an edition transcriber for this project the form has the following sections
        #source_details, citation_details, ms_variants_div, biblical_catena_div, dependencies_div, parallels_div, comments_section, status_details
        self.assertTrue(self.browser.find_element_by_id('source_details').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('citation_details').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('ms_variants_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('biblical_catena_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('dependencies_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('parallels_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('comments_section').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('status_details').is_displayed())

        #it does not have these sections
        #search_details_div
        self.assertFalse(self.browser.find_element_by_id('search_details_div').is_displayed())

        #As she is a citation manager it has these action buttons in the submit section
        #submit_same, submit_next, submit_home, submit_continue, reset_form
        self.assertTrue(self.browser.find_element_by_id('submit_section').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_same').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_next').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_home').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_continue').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('reset_form').is_displayed())
        #and does not have a delete button
        self.assertFalse(self.browser.find_element_by_id('delete').is_displayed())

        #the date and Tess's name is shown in the boxes on the right
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('created_by').get_attribute('value'), ''), 50)
        self.assertEqual(self.browser.find_element_by_id('created_by').get_attribute('value'), 'Tess Editor Tester')
        ##we can't predict the date so we will just check it isn't empty
        self.assertNotEqual(self.browser.find_element_by_id('created_time_display').get_attribute('value'), '')

        #There is a dropdown menu to select the biblical work which is already filled in with the project settings and disabled
        self.assertEqual(len(self.browser.find_element_by_id('biblical_work').find_elements_by_xpath('./option')), 3)
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        self.assertFalse(self.browser.find_element_by_id('biblical_work').is_enabled())

        #There is another for language which is already completed with projects settings and disabled
        self.assertEqual(len(self.browser.find_element_by_id('language').find_elements_by_xpath('./option')), 3)
        self.assertEqual(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')
        self.assertFalse(self.browser.find_element_by_id('language').is_enabled())

        #There is also one for onlinecorpus which has two options and is enabled
        self.assertEqual(len(self.browser.find_element_by_id('onlinecorpus').find_elements_by_xpath('./option')), 3)
        self.assertTrue(self.browser.find_element_by_id('onlinecorpus').is_enabled())

        #as there is no data in the manuscript_info field that textfield is not visible
        self.assertFalse(self.browser.find_element_by_id('manuscript_info').is_displayed())

        #as there is no data in the dependencies_string field that textfield is not visible
        self.assertFalse(self.browser.find_element_by_id('dependencies_string').is_displayed())

        #Tess adds the chapter and verse 1:1
        self.browser.find_element_by_id('chapter').send_keys('1')
        self.browser.find_element_by_id('verse').send_keys('1')

        #Tess moves the cursor from the verse box (to trigger the event on verse text box)
        self.browser.find_element_by_id('author').click()
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'))
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, '‾‾ Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν,')


        #There is a dropdown for selecting the author which is populated and enabled
        #the author dropdown has 3 options (plus a select/none line)
        self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 4)
        self.assertTrue(self.browser.find_element_by_id('author').is_enabled())

        #work is not populated properly but has a single option and disabled (because it is determined by author selection)
        self.assertEqual(len(self.browser.find_element_by_id('work').find_elements_by_xpath('./option')), 1)
        self.assertFalse(self.browser.find_element_by_id('work').is_enabled())

        #and the same is true for edition which is dependent on work selection
        self.assertEqual(len(self.browser.find_element_by_id('edition').find_elements_by_xpath('./option')), 1)
        self.assertFalse(self.browser.find_element_by_id('edition').is_enabled())

        #she then clicks save
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        #she gets an error message that tells her the data is not valid and the text of the author and work labels
        #is highlighted in red indicating that this data is required.
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('error')))
        self.assertTrue('The data is not valid and cannot be saved' in self.browser.find_element_by_id('error').get_attribute('innerHTML'))
        ##I'm not sure how to test for colour so I will just check the appropriate class has been applied
        self.assertTrue('missing' in self.browser.find_element_by_id('author').find_element_by_xpath('.//ancestor::label').get_attribute('class'))
        self.assertTrue('missing' in self.browser.find_element_by_id('work').find_element_by_xpath('.//ancestor::label').get_attribute('class'))

        #she closes the error message
        self.browser.find_element_by_id('error_close').click()

        #Tess selects the author TA2
        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA2, Test Author 2')
        #the work select box is populated and now enabled for selection
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('work').find_elements_by_xpath('./option')), 2))
        self.assertTrue(self.browser.find_element_by_id('work').is_enabled())
        #As this author only has one work it is selected automatically
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)

        #the clavis number is displayed
        self.assertEqual(self.browser.find_element_by_id('clavis_check').text, 'Clavis: 1234')

        #she adds the work reference
        self.browser.find_element_by_id('work_reference').send_keys('15.3')

        #and the edition option box is populated and enabled
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('edition').find_elements_by_xpath('./option')), 3))
        self.assertTrue(self.browser.find_element_by_id('edition').is_enabled())
        #as we have more that one edition none is selected
        self.assertEqual(self.browser.find_element_by_id('edition').get_attribute('value'), 'none')

        #she tries saving again
        ##get the current url for use later to make sure page has refreshed
        url = self.browser.current_url

        #she clicks on 'save and continue editing' to save her progress
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(url != self.browser.current_url), 50)

        #she is redirected to a slightly different url which now has the id of the current entry in the address
        self.assertTrue(re.compile('^.+?/citations/citation/edit/\d+\?_show=\d+$').match(self.browser.current_url))
        new_citation_id = re.compile('^.+?/citations/citation/edit/(\d+)\?_show=\d+$').match(self.browser.current_url).groups(1)[0]
        self.assertEqual(len(models.Citation.objects.all()), 3)

        #the author, work, work reference, online corpus and reference sections are completed correctly but can still be edited
        ##wait until the data is loaded
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''))

        self.assertEqual(int(self.browser.find_element_by_id('author').get_attribute('value')), self.a2.id)
        self.assertFalse(self.browser.find_element_by_id('author').is_enabled())
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.assertFalse(self.browser.find_element_by_id('work').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')
        self.assertFalse(self.browser.find_element_by_id('language').is_enabled())
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        self.assertFalse(self.browser.find_element_by_id('biblical_work').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1')
        self.assertFalse(self.browser.find_element_by_id('verse').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('chapter').get_attribute('value'), '1')
        self.assertFalse(self.browser.find_element_by_id('chapter').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('work_reference').get_attribute('value'), '15.3')
        self.assertTrue(self.browser.find_element_by_id('work_reference').is_enabled())

        #the clavis is also displayed
        self.assertEqual(self.browser.find_element_by_id('clavis_check').text, 'Clavis: 1234')

    def test_dataDrivenDisplayFields(self):

        c3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw2,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων',
                   'manuscript_info': 'Παῦλος] Παῦλο M G X',
                   'dependencies_string': '> AU ep',
                   'sources': ['COMPAUL', 'Biblindex']
                   }
        self.c3 = models.Citation.objects.create(**c3_data)

        #Tess loads a citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c3.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #as there is data in the manuscript_info field that textfield is visible
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('manuscript_info').is_displayed()), 50)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_info').get_attribute('value'), 'Παῦλος] Παῦλο M G X'), 35)
        #as Tess is a citation editor she cannot delete the manuscript info
        self.assertFalse(self.browser.find_element_by_id('delete_manuscript_info').is_displayed())

        #she adds a ms variant using the proper boxes
        #She has some manuscript variants to add
        self.browser.find_element_by_id('manuscript_variants_0_headword').send_keys('ἀνθρώπων')
        self.browser.find_element_by_id('manuscript_variants_0_variant').send_keys('ἀνθρώπος')
        self.browser.find_element_by_id('manuscript_variants_0_support').send_keys('01 05 13')
        self.browser.find_element_by_id('manuscript_variants_0_maj').location_once_scrolled_into_view
        self.browser.find_element_by_id('manuscript_variants_0_maj').click()

        #as there is data in the dependencies_string field that textfield is visible
        self.assertTrue(self.browser.find_element_by_id('dependencies_string').is_displayed())
        self.assertEqual(self.browser.find_element_by_id('dependencies_string').get_attribute('value'), '> AU ep')
        #as Tess is a citation editor she cannot delete the dependency string
        self.assertFalse(self.browser.find_element_by_id('delete_dependencies_string').is_displayed())

        #she adds a new dependency
        Select(self.browser.find_element_by_id('dependencies_0_relation_type')).select_by_visible_text('is quotation of')
        Select(self.browser.find_element_by_id('dependencies_0_author')).select_by_visible_text('TA1, Test Author 1')
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('dependencies_0_work').get_attribute('value'), 'none'))
        self.assertEqual(int(self.browser.find_element_by_id('dependencies_0_work').get_attribute('value')), self.w1.id)
        #she adds the work reference
        self.browser.find_element_by_id('dependencies_0_work_reference').send_keys('12.5')

        #as there are sources specified in the data Tess can see those that are entered
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('sources_table').is_displayed()))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_0')))
        self.assertTrue(self.browser.find_element_by_id('sources_0').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_0').text, 'COMPAUL'))

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_1')))
        self.assertTrue(self.browser.find_element_by_id('sources_1').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_1').text, 'Biblindex'))

        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('sources_2')))

        #but she cannot delete them
        self.assertFalse(self.element_is_on_page('delete_source_0'))
        self.assertFalse(self.element_is_on_page('delete_source_1'))

        #and she cannot add new ones
        self.assertFalse(self.browser.find_element_by_id('new_source_div').is_displayed())

        #she saves and returns to the citation list
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        #the list still has 3 entries (and a header row)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #she reloads the citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c3.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #the old ms info is there
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('manuscript_info').is_displayed()), 50)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_info').get_attribute('value'), 'Παῦλος] Παῦλο M G X'), 35)

        #the new MS variant data is there
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_headword').get_attribute('value'), 'ἀνθρώπων'))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_variant').get_attribute('value'), 'ἀνθρώπος'))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_support').get_attribute('value'), '01 05 13'))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_maj').is_selected(), True))

        #the old dependecy data is there
        self.assertTrue(self.browser.find_element_by_id('dependencies_string').is_displayed())
        self.assertEqual(self.browser.find_element_by_id('dependencies_string').get_attribute('value'), '> AU ep')

        #the new dependecy data is there
        self.assertEqual(self.browser.find_element_by_id('dependencies_0_relation_type').get_attribute('value'), 'is_quotation_of')
        self.assertEqual(int(self.browser.find_element_by_id('dependencies_0_author').get_attribute('value')), self.a1.id)
        self.assertEqual(int(self.browser.find_element_by_id('dependencies_0_work').get_attribute('value')), self.w1.id)
        self.assertEqual(self.browser.find_element_by_id('dependencies_0_work_reference').get_attribute('value'), '12.5')


        ##now test data structures are the same here
        #she is done with her citation and presses save and return to citations list
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        #the list still has 3 entries (and a header row)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 4)

        ##now check loading and saving does not produce changes
        ## get existing version of the record
        stored_citation = models.Citation.objects.get(id=self.c3.id)
        stored_citation.last_modified_time = 'test'
        stored_citation.version_number = 1
        stored_json = JSONRenderer().render(CitationSerializer(stored_citation).data)
        stored = pickle.dumps(stored_json)

        #she reloads the citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c3.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 4))

        #and saves again without making changes
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #get the data back from the database
        new_citation = models.Citation.objects.get(id=self.c3.id)
        new_citation.last_modified_time = 'test'
        new_citation.version_number = 1
        new_json = JSONRenderer().render(CitationSerializer(new_citation).data)
        new = pickle.dumps(new_json)

        self.wait_for(lambda: self.assertEqual(stored, new))
