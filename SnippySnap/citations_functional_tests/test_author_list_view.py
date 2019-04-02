from .base import FunctionalTest
import time
from citations.models import Author
from django.utils import timezone
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from unittest import skip

class GeneralUserAuthorViewsTest(FunctionalTest):
    
    #@skip('timesaver')
    def test_unlogged_in_user_can_see_author_data_but_not_edit(self):
             
        #Edith comes to visit the citations page (using the direct URL supplied by a friend)
        #to see what authors we have in the database
         
        ## First add data so we have some authors for her to find
        self.addTestData()

        ##change the name of author TA2 so we can test alphabetical sorting
        self.a2.full_name = 'A Second Test Author'
        self.a2.save()
        
        #She sees a list of all of the Authors in the database
        self.browser.get('%s/citations/author' % self.live_server_url)
        self.check_rows_in_table('data_table', 4)##check we have 3 authors and a header row
         
        #She notices that she can view the details of an author by clicking on a 'view' link 
        self.check_for_link_text_value_on_page('view')
          
        #She can't see any way to add or edit data
        self.check_for_link_text_value_not_on_page('add new author')
        self.check_for_link_text_value_not_on_page('edit')
         
        #She notices that she can filter the data 
        filter_select = Select(self.browser.find_element_by_id('search_field'))
        filter_input = self.browser.find_element_by_id('search_text')
        filter_button = self.browser.find_element_by_id('search')        
         
        #she adds a filter for abbreviation and only sees that author
        filter_select.select_by_visible_text('Abbreviation')
        filter_input.send_keys('TA2')
        filter_button.click()
        self.wait_for(lambda: self.check_rows_in_table('data_table', 2)) ##check we have 1 author and a header row
         
        #she removes the filter using the 'remove filter' button that has appeared and all of the authors are visible again
        self.browser.find_element_by_id('remove_filter_button').click()
        self.wait_for(lambda: self.check_rows_in_table('data_table', 4)) ##check we have 3 authors and a header row again
        
        #she sorts the data based on the full name of the author
        self.browser.find_element_by_id('full_name_up').click()
        self.wait_for(lambda: self.check_text_of_table_cell('data_table', 1, 2, 'A Second Test Author'))
        self.wait_for(lambda: self.check_text_of_table_cell('data_table', 2, 2, 'Test Author 1'))
        self.wait_for(lambda: self.check_text_of_table_cell('data_table', 3, 2, 'Test Author 3'))

        #she click on the view link for the first author which takes her to the full details of that author
        self.browser.find_element_by_css_selector('.view_link').click()
        self.wait_for(
            lambda: self.assertIn('/citations/author/%s?' % self.a2.id, self.browser.current_url)
        )

        #when she click to return to the author list the sort she had just done was still in place  
        self.browser.find_element_by_link_text('Author List').click()
        self.wait_for(lambda: self.check_text_of_table_cell('data_table', 1, 2, 'A Second Test Author'))
        self.wait_for(lambda: self.check_text_of_table_cell('data_table', 2, 2, 'Test Author 1'))
        self.wait_for(lambda: self.check_text_of_table_cell('data_table', 3, 2, 'Test Author 3'))
        
