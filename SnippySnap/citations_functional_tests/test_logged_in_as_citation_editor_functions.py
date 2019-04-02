from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from unittest import skip
from django.utils import timezone
from transcriptions import models as transcription_models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from citations import models
DEFAULT_WAIT = 5

class LoggedInCitationEditorListAndItemViewTests(LoggedInFunctionalTest):

    def setUp(self):
        self.browser = webdriver.Firefox()
        #self.browser.implicitly_wait(DEFAULT_WAIT)
        ## add some citations to work with
        self.addTestData()
        credentials = {
            'username': 'edith',
            'password': 'secret'}
        self.edith = self.addCitationEditorUser(credentials)

        #The administrators add her to the Greek Galatians project as an online transcriber
        self.addProjectData()
        self.p1.online_transcribers.add(self.edith)

        #she logs in
        self.logUserIn(credentials)

    #@skip('timesaver')
    def test_logged_in_user_has_correct_view_and_edit_permissions_for_citations_and_authors(self):

        ##setup function handles user login, permissions and database population

        #Edith is currently a citaiton_editor and a member of a single project, Galatians Greek
        #she logs in

        #check the permissions have been set
        self.assertTrue(self.edith.has_perm('citations.add_citation'))

        #now when the home page loads she sees that she is logged in under the Galatians project
        self.wait_for(lambda: self.assertTrue('Citations Home' in self.browser.title))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('project_name').text, self.p1.name))

        #now when edith clicks on the link to the citations she has a link to add a new one
        self.browser.find_element_by_id('citations_link').click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))
        self.wait_for(lambda: self.check_for_link_text_value_on_page('add new citation'))

        #she sees all the citations in the database
        self.wait_for(lambda: self.check_rows_in_table('data_table', 3)) ##check we have 2 results and a header row

        #but she has no link to edit the first citation - it is from John and that is not her project
        ##citations by default are ordered by book so John will always be before Galatians
        self.check_row_has_no_edit_link('data_table', 1)

        #she does have a link to edit the citations from Greek Galatians though
        self.check_row_has_edit_link('data_table', 2)

        #She clicks to view the full details of the first citation (that she does not have an edit link for) and sees the full details
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[1].find_elements_by_tag_name('td')[0].find_elements_by_class_name('view_link')[0].click()
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she does the same to the second citation
        self.browser.find_element_by_link_text('Citation List').click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title))
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[2].find_elements_by_tag_name('td')[0].find_elements_by_class_name('view_link')[0].click()
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she checks to see if she can also add authors but she can neither add new ones nor edit existing ones
        self.browser.get('%s/citations/author' % self.live_server_url)
        self.wait_for(lambda: self.check_for_link_text_value_not_on_page('add new author'))
        self.check_row_has_no_edit_link('data_table', 1)
        self.check_row_has_no_edit_link('data_table', 2)

        #Edith is pleased with her progress. She decides that tomorrow she might try to add and edit citations!

    #@skip('timesaver')
    def test_options_for_getting_only_project_data(self):
        #Edith wants to try and restrict the citations she can see to only the citations she can edit
        #she logs in
        self.wait_for(lambda: self.assertTrue('Citations Home' in self.browser.title))
        #check the permissions have been set
        self.assertTrue(self.edith.has_perm('citations.add_citation'))

        #she goes to the search page and searches for Greek citations of Galatians in the quick search
        self.browser.get('%s/citations/search' % self.live_server_url)

        book_select = Select(self.browser.find_element_by_id('book_select'))
        self.wait_for(lambda: book_select.select_by_visible_text('Galatians'))
        language_select = Select(self.browser.find_element_by_id('language_select'))
        language_select.select_by_visible_text('Greek')
        self.browser.find_element_by_id('quick_search_button').click()

        #she can see a single citation in the results table and it has an edit link
        self.wait_for(lambda: self.check_rows_in_table('data_table', 2))
        self.wait_for(lambda: self.check_row_has_edit_link('data_table', 1))

        #there is no button in the footer talking about project filters
        self.assertFalse(self.element_is_on_page('apply_project_filter_button'))

        #'hmm I wonder if there is a way to do that without using the search function' she thinks
        #she goes to the list of citations
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.check_rows_in_table('data_table', 3))

        #and notices a button in the footer that says 'filter by project settings'
        self.assertTrue(self.element_is_on_page('apply_project_filter_button'))

        #she presses the button and she can see Greek citations of Galatians only
        self.browser.find_element_by_id('apply_project_filter_button').click()
        self.wait_for(lambda: self.check_rows_in_table('data_table', 2))

        #the filter by project button has been replaced with a 'remove project filter' button
        self.assertFalse(self.element_is_on_page('apply_project_filter_button'))
        self.assertTrue(self.element_is_on_page('remove_project_filter_button'))

        #she clicks it and all of the citations come back
        self.browser.find_element_by_id('remove_project_filter_button').click()
        self.wait_for(lambda: self.check_rows_in_table('data_table', 3))

        #'excellent', she thinks 'that was quicker'

    #@skip('timesaving')
    def test_filter_options_work_with_project_filter(self):
        #Edith is looking at the citations, she uses the filter option to see only the latin citations
        #she logs in
        self.wait_for(lambda: self.assertTrue('Citations Home' in self.browser.title))
        ##check the permissions have been set
        self.assertTrue(self.edith.has_perm('citations.add_citation'))
        self.browser.get('%s/citations/citation' % self.live_server_url)
        self.wait_for(lambda: self.check_rows_in_table('data_table', 3))

        #she adds a filter for biblical reference and sees only citations from John 1:1
        Select(self.browser.find_element_by_id('search_field')).select_by_visible_text('Ref')
        self.browser.find_element_by_id('search_text').send_keys('John.1.1')
        self.browser.find_element_by_id('search').click()
        self.wait_for(lambda: self.check_rows_in_table('data_table', 2)) ##check we have 1 author and a header row

        #she presses the button to filter to see Greek citations of Galatians only,
        #but there are no Galatians citations in the John filter results
        self.browser.find_element_by_id('apply_project_filter_button').click()
        self.wait_for(lambda: self.check_rows_in_table('data_table', 1))

        #she clicks the button to remove the project filter and all of the citations come back
        self.wait_for(lambda: self.browser.find_element_by_id('remove_project_filter_button'))
        self.browser.find_element_by_id('remove_project_filter_button').click()

        self.wait_for(lambda: self.check_rows_in_table('data_table', 2), 25)
