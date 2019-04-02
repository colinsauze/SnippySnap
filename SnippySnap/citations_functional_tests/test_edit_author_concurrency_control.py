from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from rest_framework.renderers import JSONRenderer
from citations.serializers import AuthorSerializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from citations import models
import re
import pickle
import time

class AddAndEditAuthorConcurrencyControl(LoggedInFunctionalTest):
    #Tess is a citation Editor for the Greek Galatians project
    #Edith is a citation manager

    def element_is_on_page(self, browser, element_id):
        try:
            browser.find_element_by_id(element_id)
            return True
        except NoSuchElementException:
            return False

    def setUp(self):
        self.browser1 = webdriver.Firefox()
        self.browser2 = webdriver.Firefox()

    def tearDown(self):
        ContentType.objects.clear_cache() #necessary for content type problems in add_citation_manager_permissions
        self.browser1.quit()
        self.browser2.quit()

    def logUsersIn(self, credentials):
        ## I can't find a simple way of logging a user in so we need to do it the long way for now
        #She goes to the citations database home page and clicks the login link
        self.browser1.get('%s/citations' % self.live_server_url)
        assert 'Citations Home' in self.browser1.title
        self.browser1.find_element_by_link_text('login').click()

        self.wait_for(lambda: self.assertTrue('ITSEE Login' in self.browser1.title))
        self.browser1.find_element_by_id('id_username').send_keys(credentials[0]['username'])
        self.browser1.find_element_by_id('id_password').send_keys(credentials[0]['password'])
        self.browser1.find_element_by_id('login_submit_button').click()
        self.wait_for(lambda: self.assertFalse('ITSEE Login' in self.browser1.title))

        ## I can't find a simple way of logging a user in so we need to do it the long way for now
        #She goes to the citations database home page and clicks the login link
        self.browser2.get('%s/citations' % self.live_server_url)
        assert 'Citations Home' in self.browser2.title
        self.browser2.find_element_by_link_text('login').click()

        self.wait_for(lambda: self.assertTrue('ITSEE Login' in self.browser2.title))
        self.browser2.find_element_by_id('id_username').send_keys(credentials[1]['username'])
        self.browser2.find_element_by_id('id_password').send_keys(credentials[1]['password'])
        self.browser2.find_element_by_id('login_submit_button').click()
        self.wait_for(lambda: self.assertFalse('ITSEE Login' in self.browser2.title))

    def setUp(self):
        self.browser1 = webdriver.Firefox()
        self.browser2 = webdriver.Firefox()

        ## add some citations to work with
        self.addTestData()
        credentials1 = {
            'username': 'tess',
            'password': 'secret'}

        credentials2 = {
            'username': 'edith',
            'password': 'secret'}

        g2 = Group(name='citation_managers')
        g2.save()
        self.add_citation_manager_permissions(g2)

        self.tess = User.objects.create_user(**credentials1)
        self.tess.groups.add(g2)
        self.tess.save()
        self.edith = User.objects.create_user(**credentials2)
        self.edith.groups.add(g2)
        self.edith.save()

        self.addProjectData()
        self.p1.online_transcribers.add(self.edith)
        self.p1.online_transcribers.add(self.tess)

        self.logUsersIn([credentials1, credentials2])

    def test_concurrencyControl(self):
        #Tess has been promoted to a citation manager
        #Edith and Tess are both editing citation authors at the same time.
        #They both load the first author
        ## Tess' browser
        self.browser1.get('%s/citations/author/edit/%s' % (self.live_server_url, self.a1.id))
        ## Wait until data is loaded
        self.wait_for(lambda: self.assertTrue(self.browser1.find_element_by_id('full_name').get_attribute('value'), 'Test Author 1'))
        ## Edith's browser
        self.browser2.get('%s/citations/author/edit/%s' % (self.live_server_url, self.a1.id))
        ## Wait until data is loaded
        self.wait_for(lambda: self.assertTrue(self.browser2.find_element_by_id('full_name').get_attribute('value'), 'Test Author 1'))

        #Tess makes a change to the data and saves
        self.browser1.find_element_by_id('full_name').send_keys('Iohannes Chrysostomus')
        #she then clicks save
        self.browser1.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser1.find_element_by_id('submit_home').click()
        self.wait_for(lambda: self.assertTrue('Author List' in self.browser1.title))

        #Edith makes a change to the data and saves
        self.browser2.find_element_by_id('full_name').send_keys('John Chrysostomus')
        #she then clicks save
        self.browser2.find_element_by_id('submit_home').location_once_scrolled_into_view
        self.browser2.find_element_by_id('submit_home').click()
        #she gets a warning message to say that she cannot save
        self.assertTrue(self.element_is_on_page(self.browser2, 'error'))
