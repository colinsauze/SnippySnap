from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from rest_framework.renderers import JSONRenderer
from citations.serializers import EditionSerializer
from citations import models
import re
import pickle
import time
from unittest import skip
from django.utils import timezone


class AddAndEditEditionAsCitationEditor(LoggedInFunctionalTest):
    #Tess is a citation Editor for the Greek Galatians project
    #she logs into the system
    def setUp(self):
        self.browser = webdriver.Firefox()

        ## add some citations to work with
        self.addTestData()
        credentials = {
            'username': 'tess',
            'password': 'secret'}
        self.tess = self.addCitationEditorUser(credentials)

        self.addProjectData()
        self.p1.online_transcribers.add(self.tess)

        self.logUserIn(credentials)

    def test_editorsCantAddOrEditEditions(self):
        #Tess wants to add a new edition to the database
        #she is already logged in
        #she is a citation editor
        #she is a member of a single project, the Greek Galatians project
        #she goes to the list of edition but cannot see a link at add a new edition
        self.browser.get('%s/citations/edition' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Edition List' in self.browser.title))
        self.wait_for(lambda: self.check_for_link_text_value_not_on_page('add new edition'))

        #she tries to bypass the system by going straight to the URL for adding an edition
        self.browser.get('%s/citations/edition/edit' % self.live_server_url)
        #but she does not have the correct permissions
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('container').find_element_by_xpath('.//p').text, 'You do not have permission to edit this edition.')

        #she goes back to the homepage
        self.browser.get('%s/citations/edition' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Edition List' in self.browser.title))

        #she also has no links to edit any of the existing works
        self.wait_for(lambda: self.check_for_link_text_value_not_on_page('edit'))

        #she tries to access an edition for editing directly
        self.browser.get('%s/citations/edition/edit/%s' % (self.live_server_url, self.e2.id))
        #but she does not have the correct permissions
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('container').find_element_by_xpath('.//p').text, 'You do not have permission to edit this edition.')

        #she gives up - there is no way in

class AddAndEditEditionAsCitationManager(LoggedInFunctionalTest):

    #Edith is a citation Manager for the Greek Galatians project

    #she logs into the system

    def setUp(self):
        self.browser = webdriver.Firefox()

        ## add some data to work with
        self.addTestData()
        credentials = {
            'username': 'edith',
            'password': 'secret'}
        self.edith = self.addCitationManagerUser(credentials)

        self.addProjectData()
        self.p1.online_transcribers.add(self.edith)

        #she logs in
        self.logUserIn(credentials)

    def test_addAndEditNewEdition(self):

        #Edith needs to add a new edition to the database
        #she has already logged in
        #she is only a member of one project right now so she is logged into that
        #It is the project for Greek Galatians

        #she goes to the list of edition and clicks on the link to add a new Edition
        self.browser.get('%s/citations/edition' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Edition List' in self.browser.title))
        self.wait_for(lambda: self.browser.find_element_by_link_text('add new edition').click())

        #she gets a form to add a new edition
        self.wait_for(lambda: self.assertTrue('Add/Edit Edition' in self.browser.title))

        #There are a dropdown menus for selecting an author, work, series and onlinecorpus
        #the author dropdown has 2 options (plus a select/none line)
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 3))
        #the work dropdown has 2 options (plus a select/none line)
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('work').find_elements_by_xpath('./option')), 3))
        #the onlinecorpus dropdown has 2 options (plus a select/none line)
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('onlinecorpus').find_elements_by_xpath('./option')), 3))
        #the series dropdown has 2 options (plus a select/none line)
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('series').find_elements_by_xpath('./option')), 3))
        #there is no input box for legacy_edition - as this is for legacy data
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('legacy_edition').is_displayed()))


        #she selects an author - TA1
        Select(self.browser.find_element_by_id('author')).select_by_visible_text('TA1, Test Author 1')

        #the work options have now been reduced to 1 because there is only one work by this author
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('work').find_elements_by_xpath('./option')), 2))
        #and the single remaining work has been selected
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w1.id)

        ##get the current url for use later to make sure page has refreshed
        url = self.browser.current_url
        #she then clicks save
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(url != self.browser.current_url), 50)

        #the author and work are no longer editable (because there is no point changing these you really need to add a new edition!)
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('author').is_enabled()))
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('work').is_enabled()))

        #she adds some more data
        Select(self.browser.find_element_by_id('series')).select_by_visible_text('TS1')
        Select(self.browser.find_element_by_id('onlinecorpus')).select_by_visible_text('TO1')
        self.browser.find_element_by_id('year').send_keys('1970')
        self.browser.find_element_by_id('volume').send_keys('2')
        self.browser.find_element_by_id('editor').send_keys('Testy')

        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        self.wait_for(lambda: self.assertTrue('Edition List' in self.browser.title))
        self.check_rows_in_table('data_table', 4)

        ##now check loading and saving does not produce changes
        ## get existing version of the record (we don't have a secure field to get by but since there is only one editor will do)
        stored_edition = models.Edition.objects.get(editor='Testy')
        stored_edition.last_modified_time = 'test'
        stored_edition.version_number = 1
        stored_json = JSONRenderer().render(EditionSerializer(stored_edition).data)
        stored = pickle.dumps(stored_json)

        #Edith reloads the record for editing
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[-1].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        self.wait_for(lambda: self.assertTrue('Add/Edit Edition' in self.browser.title))

        ##wait until we have an author and work populated
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''), 50)
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('work').get_attribute('value'), ''), 50)

        self.assertEqual(int(self.browser.find_element_by_id('author').get_attribute('value')), self.a1.id)
        self.assertEqual(int(self.browser.find_element_by_id('work').get_attribute('value')), self.w1.id)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('series').get_attribute('value'), self.s1.abbreviation))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('onlinecorpus').get_attribute('value'), self.o1.abbreviation))
        self.assertEqual(self.browser.find_element_by_id('year').get_attribute('value'), '1970')
        self.assertEqual(self.browser.find_element_by_id('volume').get_attribute('value'), '2')
        self.assertEqual(self.browser.find_element_by_id('editor').get_attribute('value'), 'Testy')

        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        self.wait_for(lambda: self.assertTrue('Edition List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 4)

        new_edition = models.Edition.objects.get(editor='Testy')
        new_edition.last_modified_time = 'test'
        new_edition.version_number = 1
        new_json = JSONRenderer().render(EditionSerializer(new_edition).data)

        new = pickle.dumps(new_json)

        self.wait_for(lambda: self.assertEqual(stored, new))


    def test_legacyEditionFunctions(self):
        #add an edition with legacy data to work with
        e3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'identifier': 'E3',
                   'work': self.w1,
                   'legacy_edition': 'Migne, My great edition. v3. 1970'
                   }
        self.e3 = models.Edition.objects.create(**e3_data)

        #Edith needs to add a new edition to the database
        #she has already logged in
        #she is only a member of one project right now so she is logged into that
        #It is the project for Greek Galatians

        #she goes to the list of edition and clicks on the link to add a new Edition
        self.browser.get('%s/citations/edition' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Edition List' in self.browser.title))

        #she loads the only edition in the table for editing
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')

        rows[3].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()


        self.wait_for(lambda: self.assertTrue('Add/Edit Edition' in self.browser.title))

        #there is a legacy edition field which contains loads of edition information but it is not editable
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('legacy_edition').is_displayed()))
        self.assertEqual(self.browser.find_element_by_id('legacy_edition').get_attribute('value'), 'Migne, My great edition. v3. 1970')
        self.assertFalse(self.browser.find_element_by_id('legacy_edition').is_enabled())
        self.assertTrue(self.element_is_on_page('delete_legacy_edition'))

        #Edith put the data in the fields where it belongs
        self.browser.find_element_by_id('editor').send_keys('Migne')
        self.browser.find_element_by_id('volume').send_keys('3')
        self.browser.find_element_by_id('independent_title').send_keys('My great edition')
        self.browser.find_element_by_id('year').send_keys('1970')

        #then she clicks on the get legacy edition button to delete the old version
        self.browser.find_element_by_id('delete_legacy_edition').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_legacy_edition').click()

        #she gets an alert message
        self.wait_for(lambda: EC.alert_is_present())
        alert = self.browser.switch_to.alert
        #the message warns her to ensure that all of the details have been added into the correct boxes before deleting this
        message = 'Are you sure you want to delete the legacy data?\nThis should only be done if the data has been encorporated into the edition details.'
        self.assertEqual(alert.text, message)

        #she decides to double check all of the data has been added elsewhere so she dismisses the alert
        alert.dismiss()
        #the legacy data is still there
        self.assertTrue(self.browser.find_element_by_id('legacy_edition').is_displayed())
        self.assertEqual(self.browser.find_element_by_id('legacy_edition').get_attribute('value'), 'Migne, My great edition. v3. 1970')

        #she checks all the data is correct and then clicks the delete button again
        self.browser.find_element_by_id('delete_legacy_edition').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_legacy_edition').click()
        #she gets the confirm message again
        self.wait_for(lambda: EC.alert_is_present())
        #she agrees
        alert = self.browser.switch_to.alert
        alert.accept()

        self.assertFalse(self.browser.find_element_by_id('legacy_edition').is_displayed())

        #she saves the data
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        self.wait_for(lambda: self.assertTrue('Edition List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 4)

        #She reloads the record for editing
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[1].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        #the legacy data field has not come back
        self.wait_for(lambda: self.assertTrue('Add/Edit Edition' in self.browser.title), 50)
        self.assertFalse(self.browser.find_element_by_id('legacy_edition').is_displayed())
        #good!
