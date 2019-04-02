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


#citation managers always see all boxes on the form

class AddAndEditCitationAsCitationManager(LoggedInFunctionalTest):

    #Edith is a citation Manager and an edition transcriber for the Greek Galatians project

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


        credentials = {
            'username': 'edith',
            'password': 'secret',
            'display_name': 'Edith Tester'
            }
        self.edith = self.addCitationManagerUser(credentials)

        self.addProjectData()
        self.p1.edition_transcribers.add(self.edith)

        #she logs in
        self.logUserIn(credentials)

    def test_addAndEditNewCitation(self):

        #Edith wants to add a new citation to the database
        #she has already logged in
        #she is only a member of one project right now so she is logged into that
        #It is the project for Greek Galatians
        #she is an edition transcriber on that project

        ##check that our project specified sources are working by adding some to the project
        self.p1.sources = ['test1', 'test2']
        self.p1.save()

        #she goes to the list of citations and clicks on the link to add a new citation
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))
        self.wait_for(lambda: self.browser.find_element_by_link_text('add new citation').click())

        #she gets a form to add a new edition
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #As Edith is a citation manager for this project the form has all of the form sections
        #source_details, citation_details, ms_variants_div, biblical_catena_div, dependencies_div, parallels_div, comments_section, status_details, search_details_div
        self.assertTrue(self.browser.find_element_by_id('source_details').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('citation_details').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('ms_variants_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('biblical_catena_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('dependencies_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('parallels_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('comments_section').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('status_details').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('search_details_div').is_displayed())

        #As she is a citation manager it has these action buttons in the submit section
        #submit_same, submit_next, submit_home, submit_continue, delete
        self.assertTrue(self.browser.find_element_by_id('submit_section').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_same').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_next').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_home').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('submit_continue').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('delete').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('reset_form').is_displayed())

        #the sources specified in the project settings are visible
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_0').text, 'test1'))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_1').text, 'test2'))

        #the date and Edith's name is shown in the boxes on the right
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('created_by').get_attribute('value'), ''))
        self.assertEqual(self.browser.find_element_by_id('created_by').get_attribute('value'), 'Edith Tester')
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

        #Edith adds the chapter and verse 1:1
        self.browser.find_element_by_id('chapter').send_keys('1')
        self.browser.find_element_by_id('verse').send_keys('1')

        #Edith moves the cursor from the verse box (to trigger the event on verse text box)
        self.browser.find_element_by_id('language').click()
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'), 50)
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

        #Edith selects the author TA2
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

        #the biblical_work, chapter, verse, author, work, work reference, online corpus and reference sections are completed correctly but can still be edited
        ##wait until the data is loaded as we go along
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''))
        self.assertEqual(int(self.browser.find_element_by_id('author').get_attribute('value')), self.a2.id)
        self.assertTrue(self.browser.find_element_by_id('author').is_enabled())

        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('work').get_attribute('value'), ''))
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.browser.save_screenshot('citation_form.png')
        self.assertTrue(self.browser.find_element_by_id('work').is_enabled())

        self.assertEqual(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')
        self.assertTrue(self.browser.find_element_by_id('language').is_enabled())
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        self.assertTrue(self.browser.find_element_by_id('biblical_work').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1')
        self.assertTrue(self.browser.find_element_by_id('verse').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('chapter').get_attribute('value'), '1')
        self.assertTrue(self.browser.find_element_by_id('chapter').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('work_reference').get_attribute('value'), '15.3')
        self.assertTrue(self.browser.find_element_by_id('work_reference').is_enabled())

        #the clavis is also displayed
        self.assertEqual(self.browser.find_element_by_id('clavis_check').text, 'Clavis: 1234')

        #her name is still shown in the transcribed by box
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('created_by').get_attribute('value'), 'Edith Tester'), 50)

        #Edith adds the other details needed
        #she selects edition
        self.assertTrue(self.browser.find_element_by_id('edition').is_enabled())
        Select(self.browser.find_element_by_id('edition')).select_by_visible_text('Jones, 1997')
        #and the full edition details appear to confirm the choice
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('edition_details').text, 'Jones (1997) .'))
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

        self.browser.find_element_by_id('add_manuscript_variants').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_manuscript_variants').click()

        #she clicks the add manuscript variants button again and more boxes appear
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('manuscript_variants_2_headword')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('manuscript_variants_2_variant')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('manuscript_variants_2_support')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('manuscript_variants_2_maj')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_manuscript_variants_2')))

        #she realises there are no more to add and clicks the delete button for the empty boxes
        self.browser.find_element_by_id('delete_manuscript_variants_2').click()

        #the boxes disappear
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('manuscript_variants_2_headword')))
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('manuscript_variants_2_variant')))
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('manuscript_variants_2_support')))
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('manuscript_variants_2_maj')))
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('delete_manuscript_variants_2')))

        #she is able to reorder the manuscript variant lines by clicking on the square on the left and dragging them
        self.browser.find_element_by_id('manuscript_variants_0_headword').location_once_scrolled_into_view

        source = self.browser.find_element_by_id('drag1').find_elements_by_xpath('.//td[@class="rowhandler"]/div')[1]
        target = self.browser.find_element_by_id('drag1').find_elements_by_xpath('.//td[@class="rowhandler"]/div')[0]
        action = ActionChains(self.browser)
        action.drag_and_drop(source, target).perform()
        ##action.drag_and_drop_by_offset(target, 0, 10).perform()

        #the order of the rows has switched
        first_row = self.browser.find_element_by_id('MS_variants').find_elements_by_xpath('.//tr')[0]
        self.assertEqual(first_row.find_elements_by_xpath('.//td')[1].find_elements_by_xpath('.//input')[2].get_attribute('id'), 'manuscript_variants_1_support')
        self.assertEqual(first_row.find_elements_by_xpath('.//td')[1].find_elements_by_xpath('.//input')[2].get_attribute('value'), 'N T G')
        second_row = self.browser.find_element_by_id('MS_variants').find_elements_by_xpath('.//tr')[1]
        self.assertEqual(second_row.find_elements_by_xpath('.//td')[1].find_elements_by_xpath('.//input')[2].get_attribute('id'), 'manuscript_variants_0_support')
        self.assertEqual(second_row.find_elements_by_xpath('.//td')[1].find_elements_by_xpath('.//input')[2].get_attribute('value'), '01 05 13')

        #she adds biblical catena
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('book_catena').find_elements_by_xpath('./option')), 3))
        Select(self.browser.find_element_by_id('book_catena')).select_by_visible_text('Galatians')
        self.browser.find_element_by_id('chapter_catena').send_keys('1')
        self.browser.find_element_by_id('verse_catena').send_keys('1')
        self.browser.find_element_by_id('add_catena').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_catena').click()

        #the reference has been added to a box above the form elements
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblical_catena_0')))
        self.assertEqual(self.browser.find_element_by_id('biblical_catena_0').text, 'Galatians 1:1')

        #and the data has gone from the form elements
        self.assertEqual(self.browser.find_element_by_id('book_catena').get_attribute('value'), 'none')
        ## I can't work out how to test for no text in a text element so checking the 1s have gone instead
        self.assertEqual(self.browser.find_element_by_id('chapter_catena').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('verse_catena').get_attribute('value'), '')

        #she adds another
        Select(self.browser.find_element_by_id('book_catena')).select_by_visible_text('Galatians')
        self.browser.find_element_by_id('chapter_catena').send_keys('1')
        self.browser.find_element_by_id('verse_catena').send_keys('2')
        self.browser.find_element_by_id('add_catena').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_catena').click()

        #the reference is added to a box above the form elements
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblical_catena_1')))
        self.assertEqual(self.browser.find_element_by_id('biblical_catena_1').text, 'Galatians 1:2')

        #and another
        Select(self.browser.find_element_by_id('book_catena')).select_by_visible_text('Galatians')
        self.browser.find_element_by_id('chapter_catena').send_keys('1')
        self.browser.find_element_by_id('verse_catena').send_keys('3')
        self.browser.find_element_by_id('add_catena').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_catena').click()

        #the reference is added to a box above the form elements
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblical_catena_2')))
        self.assertEqual(self.browser.find_element_by_id('biblical_catena_2').text, 'Galatians 1:3')

        #the catena can be rearranged by dragging the squares
        self.browser.find_element_by_id('biblical_catena_0').location_once_scrolled_into_view

        source = self.browser.find_element_by_id('drag2').find_elements_by_xpath('.//td[@class="rowhandler"]/div')[2]
        target = self.browser.find_element_by_id('drag2').find_elements_by_xpath('.//td[@class="rowhandler"]/div')[0]
        action = ActionChains(self.browser)
        action.drag_and_drop(source, target).perform()

        #the order of the rows has switched
        first_row = self.browser.find_element_by_id('catena_table').find_elements_by_xpath('.//tr')[0]
        self.assertEqual(first_row.find_elements_by_xpath('.//td')[1].get_attribute('id'), 'biblical_catena_2')
        self.assertEqual(first_row.find_elements_by_xpath('.//td')[1].text, 'Galatians 1:3')
        second_row = self.browser.find_element_by_id('catena_table').find_elements_by_xpath('.//tr')[1]
        self.assertEqual(second_row.find_elements_by_xpath('.//td')[1].get_attribute('id'), 'biblical_catena_0')
        self.assertEqual(second_row.find_elements_by_xpath('.//td')[1].text, 'Galatians 1:1')
        third_row = self.browser.find_element_by_id('catena_table').find_elements_by_xpath('.//tr')[2]
        self.assertEqual(third_row.find_elements_by_xpath('.//td')[1].get_attribute('id'), 'biblical_catena_1')
        self.assertEqual(third_row.find_elements_by_xpath('.//td')[1].text, 'Galatians 1:2')

        #she deletes the Galatians 1:1 catena from the middle
        self.browser.find_element_by_id('delete_catena_0').click()
        self.assertFalse(self.element_is_on_page('biblical_catena_0'))
        second_row = self.browser.find_element_by_id('catena_table').find_elements_by_xpath('.//tr')[1]
        self.assertEqual(second_row.find_elements_by_xpath('.//td')[1].get_attribute('id'), 'biblical_catena_1')
        self.assertEqual(second_row.find_elements_by_xpath('.//td')[1].text, 'Galatians 1:2')



        #Edith moves on to adding dependencies with other works
        #there are boxes for relation type, author, work and work reference
        self.assertTrue(self.element_is_on_page('dependencies_0_relation_type'))
        self.assertTrue(self.element_is_on_page('dependencies_0_author'))
        self.assertTrue(self.element_is_on_page('dependencies_0_work'))
        self.assertTrue(self.element_is_on_page('dependencies_0_work_reference'))
        self.assertTrue(self.element_is_on_page('delete_dependency_0'))

        #author and work have drop downs which are populated
        self.assertEqual(len(self.browser.find_element_by_id('dependencies_0_author').find_elements_by_xpath('./option')), 5)
        self.assertEqual(len(self.browser.find_element_by_id('dependencies_0_work').find_elements_by_xpath('./option')), 5)

        #she selects the relation type
        Select(self.browser.find_element_by_id('dependencies_0_relation_type')).select_by_visible_text('is quotation of')

        #She selects the author and as there is only one work for the author the work is automatically completed
        Select(self.browser.find_element_by_id('dependencies_0_author')).select_by_visible_text('TA1, Test Author 1')
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('dependencies_0_work').get_attribute('value'), 'none'))
        self.assertEqual(int(self.browser.find_element_by_id('dependencies_0_work').get_attribute('value')), self.w1.id)

        #she adds the work reference
        self.browser.find_element_by_id('dependencies_0_work_reference').send_keys('12.5')

        #she adds another work reference
        self.browser.find_element_by_id('add_dependencies').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_dependencies').click()

        #another set of boxes appear
        self.assertTrue(self.element_is_on_page('dependencies_1_relation_type'))
        self.assertTrue(self.element_is_on_page('dependencies_1_author'))
        self.assertTrue(self.element_is_on_page('dependencies_1_work'))
        self.assertTrue(self.element_is_on_page('dependencies_1_work_reference'))
        self.assertTrue(self.element_is_on_page('delete_dependency_1'))

        #she selects the relation type
        Select(self.browser.find_element_by_id('dependencies_1_relation_type')).select_by_visible_text('see also')

        #she selects the author, the work is then filtered by author
        Select(self.browser.find_element_by_id('dependencies_1_author')).select_by_visible_text('TA4, Test Author 4')
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('dependencies_1_work').find_elements_by_xpath('./option')), 3))

        #she selects the work
        Select(self.browser.find_element_by_id('dependencies_1_work')).select_by_visible_text('TW4, Test Work 4')

        #she adds another work reference
        self.browser.find_element_by_id('add_dependencies').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_dependencies').click()
        #another set of boxes appear
        self.assertTrue(self.element_is_on_page('dependencies_2_relation_type'))
        self.assertTrue(self.element_is_on_page('dependencies_2_author'))
        self.assertTrue(self.element_is_on_page('dependencies_2_work'))
        self.assertTrue(self.element_is_on_page('dependencies_2_work_reference'))
        self.assertTrue(self.element_is_on_page('delete_dependency_2'))

        #and then deletes it
        self.browser.find_element_by_id('delete_dependency_2').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_dependency_2').click()
        #the boxes disappear
        self.assertFalse(self.element_is_on_page('dependencies_2_relation_type'))
        self.assertFalse(self.element_is_on_page('dependencies_2_author'))
        self.assertFalse(self.element_is_on_page('dependencies_2_work'))
        self.assertFalse(self.element_is_on_page('dependencies_2_work_reference'))
        self.assertFalse(self.element_is_on_page('delete_dependency_2'))

        #################
        #She adds the biblical parallels
        Select(self.browser.find_element_by_id('book_parallel')).select_by_visible_text('John')
        self.browser.find_element_by_id('chapter_parallel').send_keys('1')
        self.browser.find_element_by_id('verse_parallel').send_keys('1')
        self.browser.find_element_by_id('add_parallel').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_parallel').click()

        #the reference has been added to a box above the form elements
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblical_parallels_0')))
        self.assertTrue(self.element_is_on_page('delete_parallel_0'))
        self.assertEqual(self.browser.find_element_by_id('biblical_parallels_0').text, 'John 1:1')

        #and the data has gone from the form elements
        self.assertEqual(self.browser.find_element_by_id('book_parallel').get_attribute('value'), 'none')
        ## I can't work out how to test for no text in a text element so checking the 1s have gone instead
        self.assertEqual(self.browser.find_element_by_id('chapter_parallel').get_attribute('value'), '')
        self.assertEqual(self.browser.find_element_by_id('verse_parallel').get_attribute('value'), '')

        #she adds another
        Select(self.browser.find_element_by_id('book_parallel')).select_by_visible_text('Galatians')
        self.browser.find_element_by_id('chapter_parallel').send_keys('2')
        self.browser.find_element_by_id('verse_parallel').send_keys('2')
        self.browser.find_element_by_id('add_parallel').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_parallel').click()

        #the reference is added to a box above the form elements
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblical_parallels_1')))
        self.assertTrue(self.element_is_on_page('delete_parallel_1'))
        self.assertEqual(self.browser.find_element_by_id('biblical_parallels_1').text, 'Galatians 2:2')

        #and another
        Select(self.browser.find_element_by_id('book_parallel')).select_by_visible_text('Galatians')
        self.browser.find_element_by_id('chapter_parallel').send_keys('1')
        self.browser.find_element_by_id('verse_parallel').send_keys('3')
        self.browser.find_element_by_id('add_parallel').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_parallel').click()

        #the reference is added to a box above the form elements
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblical_parallels_2')))
        self.assertTrue(self.element_is_on_page('delete_parallel_2'))
        self.assertEqual(self.browser.find_element_by_id('biblical_parallels_2').text, 'Galatians 1:3')

        #she deletes the parallel to John as it is an error
        self.browser.find_element_by_id('delete_parallel_0').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_parallel_0').click()

        #the item has gone from the list
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('delete_parallel_0')))

        #she adds a comment
        self.browser.find_element_by_id('comments').send_keys('this is Edith\'s first citation')

        #the status value is currently Live
        self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'live')
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Live')
        #she flags the citations for needing attention as she needs to check it later
        self.browser.find_element_by_id('flag').location_once_scrolled_into_view
        self.browser.find_element_by_id('flag').click()
        #the status changes to Live but flagged
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'live but flagged'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Live but flagged')


        #she is done with her citation and presses save and return to citations list
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        #the list still has 3 entries (and a header row)
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 4)

        ##now check loading and saving does not produce changes
        ## get existing version of the record
        stored_citation = models.Citation.objects.get(id=new_citation_id)
        #fix the things we know always change on save and should always change on save
        stored_citation.last_modified_time = 'test'
        stored_citation.version_number = 1
        stored_json = JSONRenderer().render(CitationSerializer(stored_citation).data)
        stored = pickle.dumps(stored_json)

        #Edith reloads the record for editing
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[3].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title), 15)

        #check the data is loaded (we have tested lots of this in forms.js tests so here I am mostly focussing on the complex things)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('chapter').get_attribute('value'), '1'), 25)
        self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1')
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.assertEqual(int(self.browser.find_element_by_id('edition').get_attribute('value')), self.e2.id)
        self.assertEqual(self.browser.find_element_by_id('citation_text').get_attribute('value'), '{Διὸ καὶ οὕτως ἤρξατο·} Παῦλος ἀπόστολος, οὐκ ἀπ’ ἀνθρώπων, οὐδὲ δι’ ἀνθρώπων.')
        self.assertEqual(self.browser.find_element_by_id('citation_type').get_attribute('value'), 'CIT')
        self.assertEqual(self.browser.find_element_by_id('citation_reference_type').get_attribute('value'), 'reference')
        self.assertEqual(self.browser.find_element_by_id('comments').get_attribute('value'), 'this is Edith\'s first citation')
        self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'live but flagged')
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Live but flagged')
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Unflag')
        #biblical parallels
        self.assertTrue(self.element_is_on_page('biblical_parallels_0'))
        self.assertEqual(self.browser.find_element_by_id('biblical_parallels_0').text, 'Galatians 2:2')
        self.assertTrue(self.element_is_on_page('biblical_parallels_1'))
        self.assertEqual(self.browser.find_element_by_id('biblical_parallels_1').text, 'Galatians 1:3')
        self.assertFalse(self.element_is_on_page('biblical_parallels_2'))
        #dependencies
        self.assertEqual(int(self.browser.find_element_by_id('dependencies_0_author').get_attribute('value')), self.a1.id)
        self.assertEqual(int(self.browser.find_element_by_id('dependencies_0_work').get_attribute('value')), self.w1.id)
        self.assertEqual(self.browser.find_element_by_id('dependencies_0_relation_type').get_attribute('value'), 'is_quotation_of')
        self.assertEqual(self.browser.find_element_by_id('dependencies_0_work_reference').get_attribute('value'), '12.5')
        self.assertEqual(int(self.browser.find_element_by_id('dependencies_1_author').get_attribute('value')), self.a4.id)
        self.assertEqual(int(self.browser.find_element_by_id('dependencies_1_work').get_attribute('value')), self.w4.id)
        self.assertEqual(self.browser.find_element_by_id('dependencies_1_relation_type').get_attribute('value'), 'see_also')
        self.assertEqual(self.browser.find_element_by_id('dependencies_1_work_reference').get_attribute('value'), '')
        self.assertFalse(self.element_is_on_page('dependencies_2_author'))

        #manuscript variants
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_headword').get_attribute('value'), 'ἀνθρώπων')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_variant').get_attribute('value'), 'ἀνθρώπω')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_support').get_attribute('value'), 'N T G')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_0_maj').is_selected(), True)
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_1_headword').get_attribute('value'), 'ἀνθρώπων')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_1_variant').get_attribute('value'), 'ἀνθρώπος')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_1_support').get_attribute('value'), '01 05 13')
        self.assertEqual(self.browser.find_element_by_id('manuscript_variants_1_maj').is_selected(), False)
        self.assertFalse(self.element_is_on_page('manuscript_variants_2_headword'))

        #the clavis number is displayed
        self.assertEqual(self.browser.find_element_by_id('clavis_check').text, 'Clavis: 1234')

        #Ediths name is shown in the transcribed by and last modified by boxes
        self.assertEqual(self.browser.find_element_by_id('created_by').get_attribute('value'), 'Edith Tester')
        self.assertEqual(self.browser.find_element_by_id('last_modified_by').get_attribute('value'), 'Edith Tester')

        #there are two sources (added from the project) that are displayed
        self.assertTrue(self.browser.find_element_by_id('sources_table').is_displayed())
        self.assertEqual(self.browser.find_element_by_id('sources_0').text, 'test1')
        self.assertEqual(self.browser.find_element_by_id('sources_1').text, 'test2')
        self.assertFalse(self.element_is_on_page('sources_2'))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'))
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, '‾‾ Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν,')

        #and the full edition details appear to confirm the choice
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('edition_details').text, 'Jones (1997) .'))

        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 4)

        new_citation = models.Citation.objects.get(id=new_citation_id)
        new_citation.last_modified_time = 'test'
        new_citation.version_number = 1
        new_json = JSONRenderer().render(CitationSerializer(new_citation).data)
        new = pickle.dumps(new_json)

        self.wait_for(lambda: self.assertEqual(stored, new))

    def test_statusButtons(self):

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
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων'
                   }
        self.c3 = models.Citation.objects.create(**c3_data)

        #Edith loads a citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c3.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #the status value is currently Live
        self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'live')
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Live')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Flag for attention')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Deprecate')

        #she flags the citations for needing attention as she needs to check it later
        self.browser.find_element_by_id('flag').location_once_scrolled_into_view
        self.browser.find_element_by_id('flag').click()
        #the status changes to Live but flagged
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'live but flagged'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Live but flagged')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Unflag')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Deprecate')
        #she clicks deprecate and the status changes to 'Deprecated'
        self.browser.find_element_by_id('deprecate').location_once_scrolled_into_view
        self.browser.find_element_by_id('deprecate').click()

        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'deprecated'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Deprecated')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Flag for attention')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Make live')

        #she clicks flag again
        self.browser.find_element_by_id('flag').location_once_scrolled_into_view
        self.browser.find_element_by_id('flag').click()
        #the status changes to Deprecated but flagged
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'deprecated but flagged'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Deprecated but flagged')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Unflag')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Make live')

        #she clicks flag again to remove it
        self.browser.find_element_by_id('flag').location_once_scrolled_into_view
        self.browser.find_element_by_id('flag').click()
        #the status changes to deprecated
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'deprecated'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Deprecated')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Flag for attention')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Make live')

        #she clicks Live to make it live again
        ##confusingly the button is still called deprecate although the text is not
        self.browser.find_element_by_id('deprecate').location_once_scrolled_into_view
        self.browser.find_element_by_id('deprecate').click()
        #the status changes to Live
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'live'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Live')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Flag for attention')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Deprecate')

        #and she flags it again
        self.browser.find_element_by_id('flag').location_once_scrolled_into_view
        self.browser.find_element_by_id('flag').click()
        #the status changes to Live but flagged
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'live but flagged'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Live but flagged')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Unflag')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Deprecate')

        #she clicks deprecate and the status changes to 'Deprecated'
        self.browser.find_element_by_id('deprecate').location_once_scrolled_into_view
        self.browser.find_element_by_id('deprecate').click()
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'deprecated'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Deprecated')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Flag for attention')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Make live')

        #she clicks Live to make it live again
        ##confusingly the button is still called deprecate although the text is not
        self.browser.find_element_by_id('deprecate').location_once_scrolled_into_view
        self.browser.find_element_by_id('deprecate').click()
        #the status changes to Live
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'live'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Live')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Flag for attention')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Deprecate')

        #She saves
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #Edith reloads the citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c2.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #the status is currently deprecated but flagged
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('status').get_attribute('value'), 'deprecated but flagged'))
        self.assertEqual(self.browser.find_element_by_id('status_value').text, 'Deprecated but flagged')
        ##also check button text for good measure
        self.assertEqual(self.browser.find_element_by_id('flag').get_attribute('value'), 'Unflag')
        self.assertEqual(self.browser.find_element_by_id('deprecate').get_attribute('value'), 'Make live')



        #She saves
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

    def test_submitSame(self):
        #Edith loads an existing citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c2.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        ##wait until all the data has been completed
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('author').get_attribute('value'), self.a2.id))

        #she clicks the save and add another button
        self.browser.find_element_by_id('submit_same').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_same').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(self.browser.current_url.split('#')[0] == '%s/citations/citation/edit' % self.live_server_url), 50)
        #the verse details are completed and are for the same verse
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('biblical_work').get_attribute('value') == ''))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), self.c2.chapter))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('verse').get_attribute('value')), self.c2.verse))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'), 50)
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, '‾‾ Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν,')

    def test_submitNext(self):
        ##add some extra citations specifically required for this test
        c3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.1.2',
                   'biblical_reference_sortable': 9001002,
                   'chapter': 1,
                   'verse': 2,
                   'biblical_work': self.bw2,
                   'status': 'deprecated but flagged',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν'

                   }
        self.c3 = models.Citation.objects.create(**c3_data)

        ##add some extra citations specifically required for this test
        c4_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.2.2',
                   'biblical_reference_sortable': 9002002,
                   'chapter': 2,
                   'verse': 2,
                   'biblical_work': self.bw2,
                   'status': 'deprecated but flagged',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν'

                   }
        self.c4 = models.Citation.objects.create(**c4_data)

        #Edith loads an existing citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c2.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('biblical_work').get_attribute('value'), ''))

        #she clicks the save and add another button
        self.browser.find_element_by_id('submit_next').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_next').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(self.browser.current_url.split('#')[0] == '%s/citations/citation/edit' % self.live_server_url), 50)
        #the verse details are completed and are for the next verse
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('biblical_work').get_attribute('value') == ''))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), self.c2.chapter))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('verse').get_attribute('value')), 2))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'), 50)
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, 'καὶ οἱ σὺν ἐμοὶ πάντες ἀδελφοί, ταῖς ἐκκλησίαις τῆς Γαλατίας·')


        #she loads another which is at the end of a chapter
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c3.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('biblical_work').get_attribute('value'), ''), 50)

        #she clicks the save and add another button
        self.browser.find_element_by_id('submit_next').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_next').click()


        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(self.browser.current_url.split('#')[0] == '%s/citations/citation/edit' % self.live_server_url), 50)
        #the verse details are completed and are for the first verse in the next chapter
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('biblical_work').get_attribute('value') == 'none'), 50)

        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), 2))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('verse').get_attribute('value')), 1))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'))
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, '‾‾ Ἔπειτα διὰ δεκατεσσάρων ἐτῶν πάλιν ἀνέβην εἰς Ἱεροσόλυμα μετὰ Βαρνάβα, συμπαραλαβὼν καὶ Τίτον.')

        #she loads the last verse of the book
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c4.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        ##wait until all the data has been completed
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('author').get_attribute('value'), '2'))
        #she clicks the save and add another button
        self.browser.find_element_by_id('submit_next').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_next').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(self.browser.current_url.split('#')[0] == '%s/citations/citation/edit' % self.live_server_url), 50)
        #this is the last verse in the book so the verse details stay as they were for the previous citation (there is no next verse)
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('biblical_work').get_attribute('value') == ''))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), 2))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('verse').get_attribute('value')), 2))

        #the basetext of the verse has also been loaded
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('basetext_label').text, 'TR text:'))
        self.assertEqual(self.browser.find_element_by_id('basetext_text').text, 'ἀνέβην δὲ κατὰ ἀποκάλυψιν, καὶ ἀνεθέμην αὐτοῖς τὸ εὐαγγέλιον ὃ κηρύσσω ἐν τοῖς ἔθνεσι, κατ᾿ ἰδίαν δὲ τοῖς δοκοῦσι, μή πως εἰς κενὸν τρέχω ἢ ἔδραμον.')


    def test_changeBiblicalReference(self):

        #as Edith is a manager she can change the biblical reference in any already saved citations if they are wrong
        #She loads one of the citations from the Greek Galatians project which she is automatically logged into
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c2.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('project_name').text, 'Galatians Greek')

        #The biblical reference fields are completed but available for editing
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('biblical_work').get_attribute('value'), ''), 50)
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        self.assertTrue(self.browser.find_element_by_id('biblical_work').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1')
        self.assertTrue(self.browser.find_element_by_id('verse').is_enabled())
        self.assertEqual(self.browser.find_element_by_id('chapter').get_attribute('value'), '1')
        self.assertTrue(self.browser.find_element_by_id('chapter').is_enabled())

        #She changes the book to John and the chapter and verse to 2
        Select(self.browser.find_element_by_id('biblical_work')).select_by_visible_text('John')
        self.browser.find_element_by_id('chapter').send_keys(Keys.BACKSPACE)
        self.browser.find_element_by_id('chapter').send_keys('2')
        self.browser.find_element_by_id('verse').send_keys(Keys.BACKSPACE)
        self.browser.find_element_by_id('verse').send_keys('2')

        self.assertEqual(self.browser.find_element_by_id('chapter').get_attribute('value'), '2')
        self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '2')

        #she clicks on 'save and continue editing' to save the changes
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        #The changes are saved to the database
        stored_citation = models.Citation.objects.get(id=self.c2.id)

        self.assertEqual(stored_citation.verse, 2)
        self.assertEqual(stored_citation.chapter, 2)
        self.assertEqual(stored_citation.biblical_work, self.bw1)

    def test_submitNextAsFirstSave(self):

        #Edith enters a new citation of Galatians 1:1
        self.browser.get('%s/citations/citation/edit' % (self.live_server_url))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        Select(self.browser.find_element_by_id('biblical_work')).select_by_visible_text('Galatians')
        self.browser.find_element_by_id('chapter').send_keys('1')
        self.browser.find_element_by_id('verse').send_keys('1')

        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA2, Test Author 2')
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.browser.find_element_by_id('work_reference').send_keys('15.3')

        #she saves using the submit next button
        self.browser.find_element_by_id('submit_next').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_next').click()

        #a new form is loaded with the biblical reference pre-completed for Galatians 1:2
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '2'), 50)
        self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), 1)
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        ##check it is a new form by checking the author has been reset
        self.assertEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none')

        #she tried a second time to save and add a new citation
        ##to check it still works when there is already a # in the url
        #she adds the required information
        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA2, Test Author 2')
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.browser.find_element_by_id('work_reference').send_keys('15.5')

        #she saves using the submit next button
        self.browser.find_element_by_id('submit_next').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_next').click()

        #a new form is loaded with the biblical reference pre-completed for Galatians 2:1 (which is the next verse in our data)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1'), 50)
        self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), 2)
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        ##check it is a new form by checking the author has been reset
        self.assertEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none')

    def test_submitSameAsFirstSave(self):

        #Edith enters a new citation of Galatians 1:1
        self.browser.get('%s/citations/citation/edit' % (self.live_server_url))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        Select(self.browser.find_element_by_id('biblical_work')).select_by_visible_text('Galatians')
        self.browser.find_element_by_id('chapter').send_keys('1')
        self.browser.find_element_by_id('verse').send_keys('1')

        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA2, Test Author 2')
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.browser.find_element_by_id('work_reference').send_keys('15.3')

        #she saves using the submit same button
        self.browser.find_element_by_id('submit_same').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_same').click()

        ## wait till the author has been reset
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none'), 50)

        #a new form is loaded with the biblical reference pre-completed for Galatians 1:1
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1'), 50)
        self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), 1)
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('biblical_work').get_attribute('value'), ''))
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        ##check it is a new form by checking the author has been reset
        self.assertEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none')

        #she tried a second time to save and add a new citation
        ##to check it still works when there is already a # in the url
        #she adds the required information
        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA2, Test Author 2')
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w2.id)
        self.browser.find_element_by_id('work_reference').send_keys('15.5')

        #she saves using the submit same button
        self.browser.find_element_by_id('submit_same').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_same').click()

        ## wait till the author has been reset
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none'), 50)

        #a new form is loaded with the biblical reference pre-completed for Galatians 1:1 (still the same verse)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('verse').get_attribute('value'), '1'), 50)
        self.assertEqual(int(self.browser.find_element_by_id('chapter').get_attribute('value')), 1)
        self.assertEqual(int(self.browser.find_element_by_id('biblical_work').get_attribute('value')), self.bw2.id)
        ##check it is a new form by checking the author has been reset
        self.assertEqual(self.browser.find_element_by_id('author').get_attribute('value'), 'none')


    def test_dataDrivenDisplayFields1(self):

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

        #Edith loads a citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c3.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #as there is data in the manuscript_info field that textfield is visible
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('manuscript_info').is_displayed()), 50)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_info').get_attribute('value'), 'Παῦλος] Παῦλο M G X'), 35)

        #as there is data in the dependencies_string field that textfield is visible
        self.assertTrue(self.browser.find_element_by_id('dependencies_string').is_displayed())
        self.assertEqual(self.browser.find_element_by_id('dependencies_string').get_attribute('value'), '> AU ep')

        #as there are sources specified in the data
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('sources_table').is_displayed()))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_0')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_source_0')))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_0').text, 'COMPAUL'))

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_1')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_source_1')))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_1').text, 'Biblindex'))

        self.assertFalse(self.element_is_on_page('sources_2'))


    def test_dataDrivenDisplayFields2(self):

        ##check that our project specified sources are working by adding some to the project
        self.p1.sources = ['test1', 'test2']
        self.p1.save()

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

        #Edith loads a citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c3.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #as there is data in the manuscript_info field that text field and its div are visible
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('manuscript_info_div').is_displayed()), 25)
        self.assertTrue(self.browser.find_element_by_id('manuscript_info').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('delete_manuscript_info').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('manuscript_info').get_attribute('value'), 'Παῦλος] Παῦλο M G X'), 35)
        self.browser.find_element_by_id('delete_manuscript_info').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_manuscript_info').click()

        #she gets an alert message
        self.wait_for(lambda: EC.alert_is_present())
        alert = self.browser.switch_to.alert

        #the message warns her to ensure that all of the details have been added into the correct boxes before deleting this
        message = 'Are you sure you want to delete the manuscript information?\nThis should only be done if all of the data has been incorporated into the manuscript variants boxes above.'
        self.assertEqual(alert.text, message)

        #she decides to double check all of the data has been added elsewhere so she dismisses the alert
        alert.dismiss()
        #the legacy data is still there
        self.assertTrue(self.browser.find_element_by_id('manuscript_info_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('manuscript_info').is_displayed())
        self.assertEqual(self.browser.find_element_by_id('manuscript_info').get_attribute('value'), 'Παῦλος] Παῦλο M G X')

        #she checks all the data is correct and then clicks the delete button again
        self.browser.find_element_by_id('delete_manuscript_info').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_manuscript_info').click()
        #she gets the confirm message again
        self.wait_for(lambda: EC.alert_is_present())
        #she agrees
        alert = self.browser.switch_to.alert
        alert.accept()

        #the manuscript info box has gone
        self.assertFalse(self.browser.find_element_by_id('manuscript_info_div').is_displayed())
        self.assertFalse(self.browser.find_element_by_id('manuscript_info').is_displayed())

        #as there is data in the dependencies_string field that textfield is visible
        self.assertTrue(self.browser.find_element_by_id('dependencies_string').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('delete_dependencies_string').is_displayed())
        self.assertEqual(self.browser.find_element_by_id('dependencies_string').get_attribute('value'), '> AU ep')

        self.browser.find_element_by_id('delete_dependencies_string').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_dependencies_string').click()

        #she gets an alert message
        self.wait_for(lambda: EC.alert_is_present())
        alert = self.browser.switch_to.alert

        #the message warns her to ensure that all of the details have been added into the correct boxes before deleting this
        message = 'Are you sure you want to delete this dependency information?\nThis should only be done if all of the data has been incorporated into the dependency boxes above.'
        self.assertEqual(alert.text, message)

        #she decides to double check all of the data has been added elsewhere so she dismisses the alert
        alert.dismiss()
        #the legacy data is still there
        self.assertTrue(self.browser.find_element_by_id('dependencies_string_div').is_displayed())
        self.assertTrue(self.browser.find_element_by_id('dependencies_string').is_displayed())
        self.assertEqual(self.browser.find_element_by_id('dependencies_string').get_attribute('value'), '> AU ep')

        #she checks all the data is correct and then clicks the delete button again
        self.browser.find_element_by_id('delete_dependencies_string').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_dependencies_string').click()
        #she gets the confirm message again
        self.wait_for(lambda: EC.alert_is_present())
        #she agrees
        alert = self.browser.switch_to.alert
        alert.accept()

        #the dependencies string box has gone
        self.assertFalse(self.browser.find_element_by_id('dependencies_string_div').is_displayed())
        self.assertFalse(self.browser.find_element_by_id('dependencies_string').is_displayed())

        #as there are sources specified in the data Edith can see those that are entered
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('sources_table').is_displayed()))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_0')))
        self.assertTrue(self.browser.find_element_by_id('sources_0').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_0').text, 'COMPAUL'))

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_1')))
        self.assertTrue(self.browser.find_element_by_id('sources_1').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_1').text, 'Biblindex'))

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_2')))
        self.assertTrue(self.browser.find_element_by_id('sources_2').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_2').text, 'test1'))

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_3')))
        self.assertTrue(self.browser.find_element_by_id('sources_3').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_3').text, 'test2'))

        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('sources_4')))

        #and she can delete them
        self.assertTrue(self.element_is_on_page('delete_source_0'))
        self.assertTrue(self.element_is_on_page('delete_source_1'))
        self.assertTrue(self.element_is_on_page('delete_source_2'))
        self.assertTrue(self.element_is_on_page('delete_source_3'))

        #and she can add new ones
        self.assertTrue(self.browser.find_element_by_id('new_source_div').is_displayed())

        #she deletes the COMPAUL source entry
        self.browser.find_element_by_id('delete_source_0').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_source_0').click()
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('sources_0')))

        #the other entries is still there
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_1')))
        self.assertTrue(self.browser.find_element_by_id('sources_1').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_1').text, 'Biblindex'))

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_2')))
        self.assertTrue(self.browser.find_element_by_id('sources_2').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_2').text, 'test1'))

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_3')))
        self.assertTrue(self.browser.find_element_by_id('sources_3').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_3').text, 'test2'))

        #she adds a new one
        Select(self.browser.find_element_by_id('source_select')).select_by_visible_text('COMPAUL')
        self.browser.find_element_by_id('add_source').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_source').click()

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_4')))
        self.assertTrue(self.browser.find_element_by_id('sources_4').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_4').text, 'COMPAUL'))

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

        #the correct sources are displayed
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('sources_table').is_displayed()))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_0').text, 'Biblindex'))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_1').text, 'test1'))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_2').text, 'test2'))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_3').text, 'COMPAUL'))

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


    def test_sourcesForExistingRecrodsWithNoSource(self):

        ##check that our project specified sources are working by adding some to the project
        self.p1.sources = ['test1', 'test2']
        self.p1.save()

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
                   'dependencies_string': '> AU ep'
                   }
        self.c3 = models.Citation.objects.create(**c3_data)

        #Edith loads a citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c3.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))

        #the correct sources are displayed
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('sources_table').is_displayed()))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_0')))
        self.assertTrue(self.browser.find_element_by_id('sources_0').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_0').text, 'test1'))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('sources_1')))
        self.assertTrue(self.browser.find_element_by_id('sources_1').is_displayed())
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('sources_1').text, 'test2'))
