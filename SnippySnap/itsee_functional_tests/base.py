import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


DEFAULT_WAIT = 5

class BaseFunctionalTest(StaticLiveServerTestCase):

    
    def setUp(self):
        self.browser = webdriver.Firefox()
        
    def tearDown(self):
        ContentType.objects.clear_cache() #necessary for content type problems in add_citation_manager_permissions
        self.browser.quit()
        
    def wait_for(self, function_with_assertion, timeout=DEFAULT_WAIT):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return function_with_assertion()
            except (AssertionError, WebDriverException):
                time.sleep(0.1)
        # one more try, which will raise any errors if they are outstanding
        return function_with_assertion()
        
    def check_for_link_href_value_on_page(self, href_value):
        links = self.browser.find_elements_by_tag_name('a')
        self.assertIn(href_value, [link.get_attribute('href') for link in links])
        
    def check_for_link_text_value_on_page(self, text_value):
        links = self.browser.find_elements_by_tag_name('a')
        self.assertIn(text_value.lower(), [link.text.lower() for link in links])
        
    def check_for_link_text_value_not_on_page(self, text_value):
        links = self.browser.find_elements_by_tag_name('a')
        self.assertNotIn(text_value.lower(), [link.text.lower() for link in links])
        
    def check_rows_in_table(self, table_id, row_count_wanted):
        table = self.browser.find_element_by_id(table_id) 
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(len(rows) == row_count_wanted, 'The table does not have the required number of rows. Required: %d; Present: %d' % (row_count_wanted, len(rows))) 
        
    def check_text_of_table_cell(self, table_id, row_position, cell_position, test_text):
        table = self.browser.find_element_by_id(table_id) 
        rows = table.find_elements_by_tag_name('tr')
        row_cells = rows[row_position].find_elements_by_tag_name('td')
        self.assertEqual(test_text, row_cells[cell_position].text)
        
    def check_row_has_edit_link(self, table_id, row_position):
        table = self.browser.find_element_by_id(table_id) 
        rows = table.find_elements_by_tag_name('tr')
        row_cells = rows[row_position].find_elements_by_tag_name('td')
        edit_cell = row_cells[-1]
        self.assertTrue(len(edit_cell.find_elements_by_class_name('edit_link')) == 1)
        
    def check_row_has_no_edit_link(self, table_id, row_position):
        table = self.browser.find_element_by_id(table_id) 
        rows = table.find_elements_by_tag_name('tr')
        row_cells = rows[row_position].find_elements_by_tag_name('td')
        edit_cell = row_cells[-1]
        self.assertTrue(len(edit_cell.find_elements_by_class_name('edit_link')) == 0)
        
    def element_is_on_page(self, element_id):
        try:
            self.browser.find_element_by_id(element_id)
            return True
        except NoSuchElementException:
            return False
    
