from .base_logged_in import LoggedInFunctionalTest
from unittest import skip
from citations import models
from selenium.webdriver.support.ui import Select

class LoggingInNoProjectTest(LoggedInFunctionalTest):

    #@skip('timesaving')
    def test_login(self):
        #Edith has decided she rather likes our citation database and decides to
        #get an account so she can do some data entry work
        #The administrators happily oblige her
        credentials = {
            'username': 'edith',
            'password': 'secret'}
        edith = self.addCitationEditorUser(credentials)

        #she logs in
        self.logUserIn(credentials)

        #She goes to the citations database home page and clicks the login link
#         self.browser.get('%s/citations' % self.live_server_url)
#         assert 'Citations Home' in self.browser.title
#         self.browser.find_element_by_link_text('login').click()
#
#         #she enters her username and password and clicks the login button]
#         self.wait_for(lambda: self.assertTrue('ITSEE Login' in self.browser.title))
#         self.browser.find_element_by_id('id_username').send_keys(credentials['username'])
#         self.browser.find_element_by_id('id_password').send_keys(credentials['password'])
#         response = self.browser.find_element_by_id('login_submit_button').click()

        #As she is not yet a member of a project she gets returned to the familiar home page and there is no project stated in the header
        self.wait_for(lambda: self.assertTrue('Citations Home' in self.browser.title))
        self.assertEqual(self.browser.find_element_by_id('project_name').text, '')

        #now she has a logout link
        self.check_for_link_text_value_on_page('logout')


class LoggingInSingleProjectTest(LoggedInFunctionalTest):

    #@skip('timesaving')
    def test_login_with_single_project(self):
         #Edith has decided she rather likes our citation database and decides to
        #get an account so she can do some data entry work
        #The administrators happily oblige her
        #and also add her to the data entry project for Galatians in Greek
        credentials = {
            'username': 'edith',
            'password': 'secret'}
        edith = self.addCitationEditorUser(credentials)
        self.addBiblicalWorkData()
        self.addProjectData()

        self.p1.online_transcribers.add(edith)

        #she logs in
        self.logUserIn(credentials)

        #She goes to the citations database home page and clicks the login link
#         self.browser.get('%s/citations' % self.live_server_url)
#         assert 'Citations Home' in self.browser.title
#         self.browser.find_element_by_link_text('login').click()
#
#         #she enters her username and password and clicks the login button]
#         self.wait_for(lambda: self.assertTrue('ITSEE Login' in self.browser.title))
#         self.browser.find_element_by_id('id_username').send_keys(credentials['username'])
#         self.browser.find_element_by_id('id_password').send_keys(credentials['password'])
#         response = self.browser.find_element_by_id('login_submit_button').click()

        #now when the home page loads she sees that she is logged in under the Galatians project
        self.wait_for(lambda: self.assertTrue('Citations Home' in self.browser.title))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('project_name').text, self.p1.name))


class LoggedInMultipleProjectTest(LoggedInFunctionalTest):

    #@skip('timesaver')
    def test_login_with_multiple_projects(self):
        #Edith would also like to enter some Latin citations of Galatians
        #and also add her to the data entry project for Galatians in Latin as well as Greek
        credentials = {
            'username': 'edith',
            'password': 'secret'}
        edith = self.addCitationEditorUser(credentials)
        self.addBiblicalWorkData()
        self.addProjectData()
        self.p1.online_transcribers.add(edith)

        #The administrators also add Edith to the Latin Galatians project as an online transcriber
        project_data_2 = {'identifier': 'B09_lat',
                        'name': 'Latin Galatians',
                        'biblical_work': self.bw2,
                        'public': True,
                        'language': 'lat',
                        'base_text_siglum': 'vg^st5',
                        'base_text_label': 'Vulgate',
                        'preselects': {'citation' : {'onlinecorpus': 'VLD', 'language': 'lat'},
                                        'edition' : {'language': 'lat'},
                                        'author' : {'language': 'lat'},
                                        'work' : {'language': 'lat'}
                                        },
                        'submit_settings': {'citation' : {'online_transcribers': ['submit_same', 'submit_home', 'submit_continue'],
                                                          'edition_transcribers': ['submit_same', 'submit_home', 'submit_continue']} },
                        'form_settings': {'citation' : {'online_transcribers': ['source_details', 'search_details_div', 'citation_details', 'comments_section', 'status_details'],
                                                        'edition_transcribers': ['source_details', 'citation_details', 'ms_variants_div', 'biblical_catena_div', 'dependencies_div', 'parallels_div', 'comments_section', 'status_details']}},


                        }
        p2 = models.Project.objects.create(**project_data_2)
        p2.online_transcribers.add(edith)

        #she logs in
        self.logUserIn(credentials)

        #she is sent to a page to choose a project
        self.wait_for(lambda: self.assertTrue('Citations Project Select' in self.browser.title))

        #she selects the Latin Galatians project
        project_select = Select(self.browser.find_element_by_id('project'))
        project_select.select_by_visible_text(p2.name)
        self.browser.find_element_by_id('project_select_submit').click()

        #she is now sent to the homepage and the header indicates she is logged into the Latin Galatians project
        self.wait_for(lambda: self.assertEqual('Citations Home', self.browser.title), 50)
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('project_name').text, p2.name))

        #she notices a 'switch project' button has appeared in the footer
        self.assertTrue(self.element_is_on_page('switch_project_button'))

        #she clicks on it and is sent back to the project select page
        self.browser.find_element_by_id('switch_project_button').click()
        self.wait_for(lambda: self.assertTrue('Citations Project Select' in self.browser.title))

        #the Latin Galatians project is selected
        self.assertEqual(int(self.browser.find_element_by_id('project').get_attribute('value')), p2.id)
        #she selects the Greek Galatians project
        project_select = Select(self.browser.find_element_by_id('project'))
        project_select.select_by_visible_text(self.p1.name)
        self.browser.find_element_by_id('project_select_submit').click()

        #she is now sent to the homepage and the header indicates she is logged into the Greek Galatians project
        self.wait_for(lambda: self.assertTrue('Citations Home' in self.browser.title))
        self.wait_for(lambda: self.assertEqual(self.browser.find_element_by_id('project_name').text, self.p1.name))
