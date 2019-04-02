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

class LoggedInCitationManagerListAndItemViewTests(LoggedInFunctionalTest):
     
    def setUp(self):
        self.browser = webdriver.Firefox()
        #self.browser.implicitly_wait(DEFAULT_WAIT)
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
      
    #@skip('timesaver')
    def test_logged_in_user_has_correct_view_and_edit_permissions_for_citations_and_authors(self):
         
        ##setup function handles user login, permissions and database population
         
        #Edith has now been promoted to a citaiton_manager but is still a member of a single project, Galatians Greek
        #she logs in
         
        #check the permissions have been set
        self.assertTrue(self.edith.has_perm('citations.add_citation'))
        self.assertTrue(self.edith.has_perm('citations.add_author'))
         
        #when the home page loads she sees that she is logged in under the Galatians project       
        self.wait_for(lambda: self.assertTrue('Citations Home' in self.browser.title))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('project_name').text, self.p1.name))
           
        #when edith clicks on the link to the citations she has a link to add a new one
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
          
        #she checks to see if she can also add authors and she has a link for adding a new one
        self.browser.get('%s/citations/author' % self.live_server_url)
        self.wait_for(lambda: self.check_for_link_text_value_on_page('add new author'))
        #and links for editing the two Greek authors
        self.check_row_has_edit_link('data_table', 1)
        self.check_row_has_edit_link('data_table', 2)
        
        #but not the Latin author
        self.check_row_has_no_edit_link('data_table', 3)
          
        #Edith is pleased that she can now add and edit all of the data relevant to her project
 

       