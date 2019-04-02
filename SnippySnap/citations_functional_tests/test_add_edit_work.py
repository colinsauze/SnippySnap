from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from rest_framework.renderers import JSONRenderer
from citations.serializers import WorkSerializer
from django.utils import timezone
from citations import models
import re
import pickle
import time
from unittest import skip


class AddAndEditWorkAsCitationEditor(LoggedInFunctionalTest):
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

    def test_editorsCantAddOrEditWorks(self):
        #Tess wants to add a new work to the database
        #she is already logged in
        #she is a citation editor
        #she is a member of a single project, the Greek Galatians project
        #she goes to the list of works but cannot see a link at add a new work
        self.browser.get('%s/citations/work' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title))
        self.wait_for(lambda: self.check_for_link_text_value_not_on_page('add new work'))

        #she tries to bypass the system by going straight to the URL for adding a work
        self.browser.get('%s/citations/work/edit' % self.live_server_url)
        #but she does not have the correct permissions
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('container').find_element_by_xpath('.//p').text, 'You do not have permission to edit this work.')

        #she goes back to the homepage
        self.browser.get('%s/citations/work' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title))

        #she also has no links to edit any of the existing works
        self.wait_for(lambda: self.check_for_link_text_value_not_on_page('edit'))

        #she tries to access an work for editing directly
        self.browser.get('%s/citations/work/edit/%s' % (self.live_server_url, self.w2.id))
        #but she does not have the correct permissions
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('container').find_element_by_xpath('.//p').text, 'You do not have permission to edit this work.')

        #she gives up - there is no way in

class AddAndEditWorkAsCitationManager(LoggedInFunctionalTest):

    #Edith is a citation Manager for the Greek Galatians project

    #she logs into the system
    def setUp(self):
        self.browser = webdriver.Firefox()

        ## add some citations to work with
        self.addTestData()
        credentials = {
            'username': 'edith',
            'password': 'secret'}
        self.edith = self.addCitationManagerUser(credentials)

        self.addProjectData()
        self.p1.online_transcribers.add(self.edith)

        #she logs in
        self.logUserIn(credentials)


    def test_addAndEditNewWork(self):

        #Edith needs to add a new work to the database
        #she has already logged in
        #she is only a member of one project right now so she is logged into that
        #It is the project for Greek Galatians

        #she goes to the list of authors and clicks on the link to add a new work
        self.browser.get('%s/citations/work' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title))
        self.wait_for(lambda: self.browser.find_element_by_link_text('add new work').click())

        #she gets a form to add a new author and notices that the language is already filled in as Greek and but she could change it if she wanted
        self.wait_for(lambda: self.assertTrue('Add/Edit Work' in self.browser.title))
        language_select = Select(self.browser.find_element_by_id('language'))
        self.assertTrue(language_select.first_selected_option.get_attribute('value') == 'grc')
        self.assertTrue(self.browser.find_element_by_id('language').is_enabled())

        #she has one visible box to enter biblindex identifiers, one visible box for biblia patristica identifiers and one for other possible authors
        self.assertTrue(self.element_is_on_page('biblindex_identifiers_0'))
        self.assertTrue(self.element_is_on_page('biblia_patristica_identifiers_0'))
        self.assertTrue(self.element_is_on_page('other_possible_authors_0'))

        #she adds an abbreviation and a title
        self.browser.find_element_by_id('abbreviation').send_keys('InIoh')
        self.browser.find_element_by_id('title').send_keys('In Iohannem')

        #she then clicks save
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        #she gets an error message that tells her the data is not valid and the text of the author label
        #is highlighted in red indicating that this data is required.
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('error')))
        self.assertTrue('The data is not valid and cannot be saved' in self.browser.find_element_by_id('error').get_attribute('innerHTML'))
        ##I'm not sure how to test for colour so I will just check the appropriate class has been applied
        self.assertTrue('missing' in self.browser.find_element_by_id('author').find_element_by_xpath('.//ancestor::label').get_attribute('class'))

        #she closes the error message
        self.browser.find_element_by_id('error_close').click()

        #she goes to add an author and sees that there are two options (the other one in the database is Latin and so not available)
        ## test against 3 as we also have the select line
        self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 3)

        author_select = Select(self.browser.find_element_by_id('author'))
        #she adds an author and when she moves to another box the red text turns black again
        author_select.select_by_visible_text('TA1, Test Author 1')

        #to ensure the focus changes lets try to add a year
        self.browser.find_element_by_id('year').send_keys('380')
        self.wait_for(lambda: self.assertTrue('missing' not in self.browser.find_element_by_id('author').find_element_by_xpath('.//ancestor::label').get_attribute('class')))

        ##get the current url for use later to make sure page has refreshed
        url = self.browser.current_url

        #she clicks on 'save and continue editing' to save her progress
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(url != self.browser.current_url), 50)

        #she is redirected to a slightly different url which now has the id of the current entry in the address
        #she can still edit author and abbreviation and we have an extra work in our database
        self.assertTrue(re.compile('^.+?/citations/work/edit/\d+\?_show=\d+$').match(self.browser.current_url))
        self.wait_for(lambda: self.browser.find_element_by_id('author'))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''))
        self.assertTrue(self.browser.find_element_by_id('author').is_enabled())
        self.assertTrue(self.browser.find_element_by_id('abbreviation').is_enabled())
        self.assertEqual(len(models.Work.objects.all()), 3)

        #Edith adds the clavis number
        self.browser.find_element_by_id('clavis').send_keys('5678');

        #and saves the record using the 'save and return to work list button' and the new work has appeared in the table
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 4)


        #she realises she has forgotten to add some data so she clicks on the edit link for the new author
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[3].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        #she is returned to the edit page and the data is all visible in the form
        self.wait_for(lambda: self.assertTrue('Add/Edit Work' in self.browser.title))

        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('clavis').get_attribute('value'), '5678'), 50)
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('author').get_attribute('value'), '2'), 50)
        self.assertTrue(self.browser.find_element_by_id('abbreviation').get_attribute('value'), 'InIoh')
        self.assertTrue(self.browser.find_element_by_id('title').get_attribute('value'), 'In Iohannem')
        self.assertTrue(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')

        #abbreviation and language are enabled
        self.assertTrue(self.browser.find_element_by_id('abbreviation').is_enabled())
        self.assertTrue(self.browser.find_element_by_id('language').is_enabled())

        #Edith wants to add the relevant biblindex identifiers to the record
        #she adds one in the box that is visible
        self.browser.find_element_by_id('biblindex_identifiers_0').send_keys('IN IOHANNEM')

        #then she clicks on the plus image to add another box and adds the second one
        self.browser.find_element_by_id('add_biblindex_identifiers').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_biblindex_identifiers').click()
        self.browser.find_element_by_id('biblindex_identifiers_1').send_keys('On JOHN')

        #she clicks to add another box but she doesn't have any more data so she deletes it using the red cross
        self.browser.find_element_by_id('add_biblindex_identifiers').click()
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblindex_identifiers_2')))
        self.browser.find_element_by_id('delete_biblindex_identifiers_2').click()
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('biblindex_identifiers_2')))

        #she clicks adds a biblia patristica identifier too
        self.browser.find_element_by_id('biblia_patristica_identifiers_0').send_keys('InJo')

        #She has some alternative authors that are sometimes assigned to this work so she adds them
        #there are only two authors to select from (as the third in the database is Latin and so irrelevant
        ##test to 3 because we should have a select none as the first option
        self.assertEqual(len(self.browser.find_element_by_id('other_possible_authors_0').find_elements_by_xpath('./option')), 3)
        Select(self.browser.find_element_by_id('other_possible_authors_0')).select_by_visible_text('TA1, Test Author 1')
        self.browser.find_element_by_id('add_authors').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_authors').click()
        Select(self.browser.find_element_by_id('other_possible_authors_1')).select_by_visible_text('TA2, Test Author 2')


        #she also adds a comment and clicks save to return to the author list which has not got any longer as she is editing an existing author
        self.browser.find_element_by_id('comments').send_keys('Edith added this for the Galatians project')

        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title))
        self.check_rows_in_table('data_table', 4)

        ##now check loading and saving does not produce changes
        ## get existing version of the record
        stored_work = models.Work.objects.get(abbreviation='InIoh')
        stored_json = JSONRenderer().render(WorkSerializer(stored_work).data)
        stored = pickle.dumps(stored_json)

        #Edith reloads the record for editing
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[3].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        #there are two biblindex identifiers with data, one biblia patristica identifier box and two other possible authors
        self.wait_for(lambda: self.assertTrue('Add/Edit Work' in self.browser.title), 15)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('biblindex_identifiers_0').get_attribute('value'), 'IN IOHANNEM'))
        self.assertEqual(self.browser.find_element_by_id('biblindex_identifiers_1').get_attribute('value'), 'On JOHN')
        self.assertFalse(self.element_is_on_page('biblindex_identifiers_2'))

        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('biblia_patristica_identifiers_0').get_attribute('value'), 'InJo'))
        self.assertFalse(self.element_is_on_page('biblia_patristica_identifiers_1'))

        self.wait_for(lambda: self.assertNotEqual((self.browser.find_element_by_id('other_possible_authors_0').get_attribute('value')), ''))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('other_possible_authors_0').get_attribute('value')), self.a1.id))
        self.wait_for(lambda: self.assertEqual(int(self.browser.find_element_by_id('other_possible_authors_1').get_attribute('value')), self.a2.id))
        self.assertFalse(self.element_is_on_page('other_possible_authors_2'))

        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 4)

        new_work = models.Work.objects.get(abbreviation='InIoh')
        new_json = JSONRenderer().render(WorkSerializer(new_work).data)
        new = pickle.dumps(new_json)

        self.wait_for(lambda: self.assertEqual(stored, new))


    def test_obsoleteAuthorTriggers(self):

        ## add an obsolete author to the Database
        a4_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA4',
                   'full_name': 'Test Author 4',
                   'language': 'grc',
                   'obsolete': True
                   }
        self.a4 = models.Author.objects.create(**a4_data)

        #Edith needs to add a new work to the database
        #she has already logged in
        #she is only a member of one project right now so she is logged into that
        #It is the project for Greek Galatians

        #she goes to the list of authors and clicks on the link to add a new work
        self.browser.get('%s/citations/work' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title))
        self.wait_for(lambda: self.browser.find_element_by_link_text('add new work').click())

        #she goes to add an author and sees that there are three options (the other one in the database is Latin and so not available)
        ## test against 4 as we also have the select line
        self.wait_for(lambda: self.browser.find_element_by_id('author'))
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 4), 50)

        author_select = Select(self.browser.find_element_by_id('author'))
        author_select.select_by_visible_text('TA4, Test Author 4')

        #and noticed that the obsolete box for the work gets checked automatically
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('obsolete').get_attribute('value'), 'on'))

        # she thinks she must have selected the wrong author so changes it
        author_select.select_by_visible_text('TA2, Test Author 2')

        #and the obsolete box is unchecked
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('obsolete').get_attribute('value'), 'off'))

        #she realises she was right the first time and selects TA4
        author_select.select_by_visible_text('TA4, Test Author 4')
        #the obsolete box is ticked again but Edith can change it if she wants to
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('obsolete').get_attribute('value'), 'on'))
        self.assertTrue(self.browser.find_element_by_id('obsolete').is_enabled())

        #she adds an abbreviation
        self.browser.find_element_by_id('abbreviation').send_keys('InIoh')

        #she clicks on 'save and continue editing' to save her progress
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        #she is returned to the list of works where the new record can be seen in the table
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title))
        self.check_rows_in_table('data_table', 4)

        ##now check loading and saving does not produce changes
        ## get existing version of the record
        stored_work = models.Work.objects.get(abbreviation='InIoh')
        stored_json = JSONRenderer().render(WorkSerializer(stored_work).data)
        stored = pickle.dumps(stored_json)

        #Edith reloads the record for editing
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[3].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''), 50)
        self.wait_for(lambda: self.browser.find_element_by_id('obsolete'))
        self.assertTrue(self.browser.find_element_by_id('obsolete').get_attribute('value'), 'on')

        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 4)
        self.assertTrue(models.Work.objects.get(abbreviation='InIoh').obsolete, True)

        new_work = models.Work.objects.get(abbreviation='InIoh')
        new_json = JSONRenderer().render(WorkSerializer(new_work).data)
        new = pickle.dumps(new_json)

        self.wait_for(lambda: self.assertEqual(stored, new))


    def test_addNewWorkWithAuthorRestrictionInProject(self):
        #Edith's project has been restricted to only the author TA1

        ##first add an author restriction to the project
        self.p1.author_ids.add(self.a1)

        #she goes to the list of authors
        self.browser.get('%s/citations/work' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 3)
        #only the work assigned to TA1 has an edit link
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertEqual(len(rows[1].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')), 1)
        #she clicks on the apply project filter button and the only work that remains is the one with the edit link
        self.browser.find_element_by_id('apply_project_filter_button').location_once_scrolled_into_view
        self.browser.find_element_by_id('apply_project_filter_button').click()
        self.wait_for(lambda: self.check_rows_in_table('data_table', 2))
        self.assertEqual(len(self.browser.find_elements_by_class_name('edit_link')), 1)
        self.browser.save_screenshot('work-test.png')
        #she clicks to remove the project filter and all of the works come back
        self.browser.find_element_by_id('remove_project_filter_button').location_once_scrolled_into_view
        self.browser.find_element_by_id('remove_project_filter_button').click()
        self.wait_for(lambda: self.check_rows_in_table('data_table', 3))
        self.assertEqual(len(self.browser.find_elements_by_class_name('edit_link')), 1)

        #Edith tries to play the system and edit the work by the other author
        self.browser.get('%s/citations/work/edit/%d' % (self.live_server_url, self.w2.id))
        #she does not have the correct permissions and is told so
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('container').find_element_by_xpath('.//p').text, 'You do not have permission to edit this data in this project. To switch projects return to the homepage.')

        #she settles on editing the work by TA1
        self.browser.get('%s/citations/work/edit/%d' % (self.live_server_url, self.w1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Work' in self.browser.title), 15)

        #she only has a single choice of author in the dropdown menu
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 2), 50)
        #but the author box is still editable
        self.assertTrue(self.browser.find_element_by_id('author').is_enabled())

        #she returns to the homepage
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title), 50)

        #she checks that it is the same for new records
        self.browser.get('%s/citations/work/edit/' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Add/Edit Work' in self.browser.title), 15)

        #she still only has a single choice of author in the dropdown menu and it is selected for her
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('author').find_elements_by_xpath('./option')), 2))
        self.assertEqual(int(self.browser.find_element_by_id('author').get_attribute('value')), self.a1.id)
