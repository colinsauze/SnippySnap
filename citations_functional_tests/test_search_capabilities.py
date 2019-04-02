from .base import FunctionalTest
import time
from citations import models
from transcriptions import models as transcription_models
from django.utils import timezone
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from unittest import skip


DEFAULT_WAIT = 5

class SearchTests(FunctionalTest):


    def setUp(self):
        self.browser = webdriver.Firefox()

        self.addTestData()

        #add an extra citation for greater search flexibility
        c3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'lat',
                   'work': self.w2,
                   'biblical_reference': 'John.1.1',
                   'biblical_reference_sortable': 4001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw1,
                   'citation_text': 'in principio erat uerbum et uerbum erat apud deum et deus erat uerbum'
                   }
        self.c3 = models.Citation.objects.create(**c3_data)
#

    #@skip('timesaver')
    def test_quick_search_function(self):

        #Edith decides to search for some citations in our database
        #she visits the search page
        self.browser.get('%s/citations/search' % self.live_server_url)

        #sees a quick search page with options to search for book, chapter verse and language
        self.wait_for(lambda: self.browser.find_element_by_id('book_select'))
        book_select = Select(self.browser.find_element_by_id('book_select'))
        chapter_input = self.browser.find_element_by_id('chapter_input')
        verse_input = self.browser.find_element_by_id('verse_input')
        language_select = Select(self.browser.find_element_by_id('language_select'))
        search_button = self.browser.find_element_by_id('quick_search_button')

        #she searches for Greek citations of John 1:1
        self.wait_for(lambda: book_select.select_by_visible_text('John'))
        chapter_input.send_keys(1)
        verse_input.send_keys(1)
        language_select.select_by_visible_text('Greek')
        search_button.click()
        #she gets 1 result
        self.wait_for(lambda: self.check_rows_in_table('data_table', 2)) ##check we have 1 result and a header row

        #the results page does not have a filter option
        self.assertFalse(self.element_is_on_page('search_field'))
        self.assertFalse(self.element_is_on_page('search_text'))
        self.assertFalse(self.element_is_on_page('search'))

        #she goes back to the search page has remembered her search
        self.browser.find_element_by_link_text('Search').click()
        self.wait_for(lambda:self.assertEqual(self.browser.find_element_by_id('book_select').get_attribute('value'), 'NT_John'))
        self.assertEqual(self.browser.find_element_by_id('chapter_input').get_attribute('value'), '1')
        self.assertEqual(self.browser.find_element_by_id('verse_input').get_attribute('value'), '1')
        self.assertEqual(self.browser.find_element_by_id('language_select').get_attribute('value'), 'grc')


        #she searches for Greek citations of John 1:1 in Greek and Latin
        book_select = Select(self.browser.find_element_by_id('book_select'))
        chapter_input = self.browser.find_element_by_id('chapter_input')
        verse_input = self.browser.find_element_by_id('verse_input')
        language_select = Select(self.browser.find_element_by_id('language_select'))
        search_button = self.browser.find_element_by_id('quick_search_button')
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('book_select').find_elements_by_xpath('./option')), 3), 50)
        book_select.select_by_visible_text('John')
        chapter_input.clear()
        chapter_input.send_keys(1)
        verse_input.clear()
        verse_input.send_keys(1)
        language_select.select_by_visible_text('Greek and Latin')
        search_button.click()
        #she gets 2 results
        self.wait_for(lambda: self.check_rows_in_table('data_table', 3)) ##check we have 2 results and a header row

        #she goes back to the search page which has the same quick search options
        self.browser.find_element_by_link_text('Search').click()
        #she searches for Greek citations of John 1:2
        self.wait_for(lambda: self.browser.find_element_by_id('book_select'))
        book_select = Select(self.browser.find_element_by_id('book_select'))
        chapter_input = self.browser.find_element_by_id('chapter_input')
        verse_input = self.browser.find_element_by_id('verse_input')
        language_select = Select(self.browser.find_element_by_id('language_select'))
        search_button = self.browser.find_element_by_id('quick_search_button')
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('book_select').find_elements_by_xpath('./option')), 3), 50)
        book_select.select_by_visible_text('John')
        chapter_input.clear()
        chapter_input.send_keys(1)
        verse_input.clear()
        verse_input.send_keys(2)
        language_select.select_by_visible_text('Greek')
        search_button.click()

        #she gets 0 results
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('no_results_found_message')))
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('data_table'))) ##check we just have a header row

        #she goes back to the search page and reruns the same search (just to make sure)
        self.browser.find_element_by_link_text('Search').click()
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('book_select').find_elements_by_xpath('./option')), 3), 50)
        self.wait_for(lambda: self.browser.find_element_by_id('quick_search_button'))
        search_button = self.browser.find_element_by_id('quick_search_button')
        search_button.click()

        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('no_results_found_message')))
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('data_table')))

        #she click on a return to search button which takes her back to her search and it has remembered her last search values
        return_to_search = self.browser.find_element_by_id('return_button')
        return_to_search.click()

        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('book_select').get_attribute('value'), 'NT_John'), 50)
        self.assertEqual(self.browser.find_element_by_id('chapter_input').get_attribute('value'), '1')
        self.assertEqual(self.browser.find_element_by_id('verse_input').get_attribute('value'), '2')
        self.assertEqual(self.browser.find_element_by_id('language_select').get_attribute('value'), 'grc')

        #she decides that is enough for today but perhaps another time she will try out the advanced search

    #@skip('timesaver')
    def test_advanced_search_function(self):
        #Edith decides to search for some citations in our database
        #she visits the search page
        self.browser.get('%s/citations/search' % self.live_server_url)

        #today she is going to try the advanced search option so she click on the advanced tab
        self.browser.find_element_by_id('advanced_search').click()

        #she gets a new page which has interesting search options
        self.wait_for(lambda: self.browser.find_element_by_id('model_select'))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('model_select').get_attribute('value'), 'citation'), 25)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('field_select_1').get_attribute('value'), 'biblical_work__identifier'), 35)


        #it looks like she can search different models
        model_select = Select(self.browser.find_element_by_id('model_select'))
        #she selects author
        model_select.select_by_visible_text('authors')
        #and as if by magic the value in the first field changes
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('field_select_1').get_attribute('value'), 'abbreviation'))
        #she decides to search for authors by abbreviation and types 'T' in the input box
        self.browser.find_element_by_id('search_text_1').send_keys('T')

        #and the system tried to help by making suggestions based on the database
        ## for some reason in Selenium 3 I can no longer access the actual suggestions directly instead I have to get the parent and then split its text on new lines!
        self.wait_for(lambda: len(self.browser.find_elements_by_css_selector('div.autocomplete-suggestions')) > 0)
        suggestions = self.browser.find_elements_by_css_selector('div.autocomplete-suggestions')

        self.wait_for(lambda: self.assertIn('TA1', suggestions[0].text.split('\n')))
        self.wait_for(lambda: self.assertIn('TA2', suggestions[0].text.split('\n')))
        self.browser.find_element_by_id('search_text_1').send_keys('A1')
        self.browser.find_element_by_id('advanced_search_button').click()
        #her search results return a single author
        self.wait_for(lambda: self.assertIn('Author Search Results', self.browser.find_element_by_id('page_title').text))
        self.wait_for(lambda: self.check_rows_in_table('data_table', 2)) ##check we have 1 result and a header row

        #she goes back to the search page and to see if the advanced search remembers her search too
        self.browser.find_element_by_link_text('Search').click()
        #it does
        self.wait_for(lambda: self.browser.find_element_by_id('search_text_1'))
        self.assertEqual(self.browser.find_element_by_id('search_text_1').get_attribute('value'), 'TA1')
        self.assertEqual(self.browser.find_element_by_id('field_select_1').get_attribute('value'), 'abbreviation')
        #she tries another search
        self.browser.find_element_by_id('search_text_1').clear()
        self.browser.find_element_by_id('search_text_1').send_keys('N')
        self.browser.find_element_by_id('advanced_search_button').click()

        #she gets 0 results
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('no_results_found_message')))
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('data_table'))) ##check we just have a header row

        #she click on a return to search button which takes her back to her search and it has remembered her last search values
        return_to_search = self.browser.find_element_by_id('return_button')
        return_to_search.click()
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('search_text_1').get_attribute('value'), 'N'))
        self.assertEqual(self.browser.find_element_by_id('field_select_1').get_attribute('value'), 'abbreviation')
