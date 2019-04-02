from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from rest_framework.renderers import JSONRenderer
from citations.serializers import AuthorSerializer
from citations import models
import re
import pickle
import time

class AddAndEditAuthorAsCitationEditor(LoggedInFunctionalTest):
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

    def test_editorsCantAddOrEditAuthors(self):
        #Tess wants to add a new Author to the database
        #she is already logged in
        #she is a citation editor
        #she is a member of a single project, the Greek Galatians project
        #she goes to the list of authors but cannot see a link at add a new author
        self.browser.get('%s/citations/author' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Author List' in self.browser.title))
        self.wait_for(lambda: self.check_for_link_text_value_not_on_page('add new author'))

        #she tries to bypass the system by going straight to the URL for adding an author
        self.browser.get('%s/citations/author/edit' % self.live_server_url)
        #but she does not have the correct permissions
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('container').find_element_by_xpath('.//p').text, 'You do not have permission to edit this author.')

        #she goes back to the homepage
        self.browser.get('%s/citations/author' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Author List' in self.browser.title))

        #she also has no links to edit any of the existing authors
        self.wait_for(lambda: self.check_for_link_text_value_not_on_page('edit'))

        #she tries to access an author for editing directly
        self.browser.get('%s/citations/author/edit/%s' % (self.live_server_url, self.a2.id))
        #but she does not have the correct permissions
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('container').find_element_by_xpath('.//p').text, 'You do not have permission to edit this author.')

        #she gives up - there is no way in

class AddAndEditAuthorAsCitationManager(LoggedInFunctionalTest):

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

        self.logUserIn(credentials)


    def test_addAndEditNewAuthor(self):

        #Edith needs to add a new author to the database
        #she has already logged in
        #she is only a member of one project right now so she is logged into that
        #It is the project for Greek Galatians

        #she goes to the list of authors and clicks on the link to add a new Author
        self.browser.get('%s/citations/author' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Author List' in self.browser.title))
        self.wait_for(lambda: self.browser.find_element_by_link_text('add new author').click())

        #she gets a form to add a new author and notices that the language is already filled in as Greek but she could change it if she liked
        self.wait_for(lambda: self.assertTrue('Add/Edit Author' in self.browser.title))
        language_select = Select(self.browser.find_element_by_id('language'))
        self.assertTrue(language_select.first_selected_option.get_attribute('value') == 'grc')
        self.assertTrue(self.browser.find_element_by_id('language').is_enabled())

        #she has one visible box to enter biblindex identifiers and one visible box for biblia patristica identifiers
        self.assertTrue(self.element_is_on_page('biblindex_identifiers_0'))
        self.assertTrue(self.element_is_on_page('biblia_patristica_identifiers_0'))

        #she adds the full name of the author
        self.browser.find_element_by_id('full_name').send_keys('Iohannes Chrysostomus')

        #she then clicks save
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        #she gets an error message that tells her the data is not valid and the text of the abbreviation label
        #is highlighted in red indicating that this data is required.
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('error')))
        self.assertTrue('The data is not valid and cannot be saved' in self.browser.find_element_by_id('error').get_attribute('innerHTML'))
        ##I'm not sure how to test for colour so I will just check the appropriate class has been applied
        self.assertTrue('missing' in self.browser.find_element_by_id('abbreviation').find_element_by_xpath('.//ancestor::label').get_attribute('class'))

        #she closes the error message
        self.browser.find_element_by_id('error_close').click()

        #she adds an abbreviation and when she moves to another box the red text turns black again
        self.browser.find_element_by_id('abbreviation').send_keys('Chrys')
        #to ensure the focus changes lets try to add an approximate date of death
        self.browser.find_element_by_id('died').send_keys('around 400')
        self.wait_for(lambda: self.assertTrue('missing' not in self.browser.find_element_by_id('abbreviation').find_element_by_xpath('.//ancestor::label').get_attribute('class')))

        #she tries to save again
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()
        #again she gets an error - this time the box for the year of death is red but the text is not
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('error')))
        self.assertTrue('The data is not valid and cannot be saved' in self.browser.find_element_by_id('error').get_attribute('innerHTML'))
        self.assertTrue('error' in self.browser.find_element_by_id('died').get_attribute('class'))
        self.assertTrue('missing' not in self.browser.find_element_by_id('died').find_element_by_xpath('.//ancestor::label').get_attribute('class'))

        #she closes the error message
        self.browser.find_element_by_id('error_close').click()

        #she changes the data to read 400 and ticks the box to say approximate
        self.browser.find_element_by_id('died').clear()
        self.browser.find_element_by_id('died').send_keys('400')
        self.browser.find_element_by_id('died_is_approximate').click()
        #the red shading goes away
        self.assertTrue('error' not in self.browser.find_element_by_id('died').get_attribute('class'))

        ##get the current url for use later to make sure page has refreshed
        url = self.browser.current_url

        #she clicks on 'save and continue editing' to save her progress
        self.browser.find_element_by_id('submit_continue').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_continue').click()

        ##wait until page has been reloaded - with an extra long wait time in case it is slow
        self.wait_for(lambda: self.assertTrue(url != self.browser.current_url), 50)

        #she is redirected to a slightly different url which now has the id of the current entry in the address
        #she can still edit the abbreviation and we have an extra author in our database
        self.wait_for(lambda: self.browser.find_element_by_id('abbreviation'))
        self.assertTrue(self.browser.find_element_by_id('abbreviation').is_enabled())
        self.assertTrue(re.compile('^.+?/citations/author/edit/\d+\?_show=\d+$').match(self.browser.current_url))
        self.assertEqual(len(models.Author.objects.all()), 4)

        #Edith adds the century active data
        self.browser.find_element_by_id('century_active').send_keys('5');

        #and saves the record using the 'save and return to author list button' and the new author has appeared in the table
        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Author List' in self.browser.title))
        self.check_rows_in_table('data_table', 5)

        #she realises she has forgotten to add some data so she clicks on the edit link for the new author
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[1].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        #she is returned to the edit page and the data is all visible in the form
        self.wait_for(lambda: self.assertTrue('Add/Edit Author' in self.browser.title))
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('died').get_attribute('value'), '400'), 50)
        self.assertTrue(self.browser.find_element_by_id('died_is_approximate').get_attribute('value'), 'on')
        self.assertTrue(self.browser.find_element_by_id('abbreviation').get_attribute('value'), 'Chrys')
        self.assertTrue(self.browser.find_element_by_id('full_name').get_attribute('value'), 'Iohannes Chrysostomus')
        self.assertTrue(self.browser.find_element_by_id('language').get_attribute('value'), 'grc')

        #abbreviation and language are enabled
        self.assertTrue(self.browser.find_element_by_id('abbreviation').is_enabled())
        self.assertTrue(self.browser.find_element_by_id('language').is_enabled())

        #Edith wants to add the relevant biblindex identifiers to the record
        #she adds one in the box that is visible
        self.browser.find_element_by_id('biblindex_identifiers_0').send_keys('IOHANNES CHRYSOSTOMVS')

        #then she clicks on the plus image to add another box and adds the second one
        self.browser.find_element_by_id('add_biblindex_identifiers').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_biblindex_identifiers').click()
        self.browser.find_element_by_id('biblindex_identifiers_1').send_keys('IOHANNES CHRYSOSTOMVS ?')

        #she clicks to add another box but she doesn't have any more data so she deletes it using the red cross
        self.browser.find_element_by_id('add_biblindex_identifiers').click()
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblindex_identifiers_2')))
        self.browser.find_element_by_id('delete_biblindex_identifiers_2').click()
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('biblindex_identifiers_2')))


        #she clicks on the plus image to add another biblia patristica identifier too but then realises she doesn't have any data
        # she wonders what will happen next time she opens the record - will there be two empty boxes or just one?
        self.browser.find_element_by_id('add_biblia_patristica_identifiers').location_once_scrolled_into_view
        self.browser.find_element_by_id('add_biblia_patristica_identifiers').click()
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('biblia_patristica_identifiers_1')))

        #she also adds a comment and clicks save to return to the author list which has not got any longer as she is editing an existing author
        self.browser.find_element_by_id('comments').send_keys('Edith added this for the Galatians project')

        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Author List' in self.browser.title))
        self.check_rows_in_table('data_table', 5)



        ##now check loading and saving does not produce changes
        ## get existing version of the record
        stored_author = models.Author.objects.get(abbreviation='Chrys')
        stored_author.last_modified_time = 'test'
        stored_author.version_number = 1
        stored_json = JSONRenderer().render(AuthorSerializer(stored_author).data)
        stored = pickle.dumps(stored_json)

        #Edith reloads the record for editing
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[1].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        #there are two biblindex identifiers with data but only one biblia patristica identifier box
        self.wait_for(lambda: self.assertTrue('Add/Edit Author' in self.browser.title), 15)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('biblindex_identifiers_0').get_attribute('value'), 'IOHANNES CHRYSOSTOMVS'), 50)
        self.assertEqual(self.browser.find_element_by_id('biblindex_identifiers_1').get_attribute('value'), 'IOHANNES CHRYSOSTOMVS ?')
        self.assertFalse(self.element_is_on_page('biblindex_identifiers_2'))

        self.assertTrue(self.element_is_on_page('biblia_patristica_identifiers_0'))
        self.assertFalse(self.element_is_on_page('biblia_patristica_identifiers_1'))

        self.browser.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_home').click()

        self.wait_for(lambda: self.assertTrue('Author List' in self.browser.title), 50)
        self.check_rows_in_table('data_table', 5)

        new_author = models.Author.objects.get(abbreviation='Chrys')
        new_author.last_modified_time = 'test'
        new_author.version_number = 1
        new_json = JSONRenderer().render(AuthorSerializer(new_author).data)
        new = pickle.dumps(new_json)

        self.wait_for(lambda: self.assertEqual(stored, new))

        #Edith loads the record again
        table = self.browser.find_element_by_id('data_table')
        rows = table.find_elements_by_tag_name('tr')
        rows[1].find_elements_by_tag_name('td')[-1].find_elements_by_class_name('edit_link')[0].click()

        #she clicks save and add another
        self.wait_for(lambda: self.browser.find_element_by_id('submit_another'))
        self.browser.find_element_by_id('submit_another').location_once_scrolled_into_view
        self.browser.find_element_by_id('submit_another').click()
        self.wait_for(lambda: self.assertTrue(re.compile('^.+?/citations/author/edit/$').match(self.browser.current_url)), 25)
        self.wait_for(lambda: self.browser.find_element_by_id('abbreviation'))
        self.assertEqual(self.browser.find_element_by_id('abbreviation').get_attribute('value'), '')
