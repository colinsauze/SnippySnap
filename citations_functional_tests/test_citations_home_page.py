from itsee_functional_tests.base import BaseFunctionalTest
from unittest import skip
from django.contrib.auth.models import User
from django.test import RequestFactory
from citations import views
from django.test import Client

class CitationsHomePageTest(BaseFunctionalTest):

    #@skip('timesaver')
    def test_citations_are_available_and_homepage_has_correct_links(self):
        #Edith decides to visit the citations homepage
        self.browser.get('%s/citations' % self.live_server_url)

        #she notices that the page title is 'Citations Home'
        assert 'Citations Home' in self.browser.title

        #She notices a login link
        self.check_for_link_text_value_on_page('login')
        #she clicks on the link and it takes her to a login page with input boxes for username and password
        self.browser.find_element_by_link_text('login').click()
        self.wait_for(lambda: self.assertTrue(
                                              self.browser.find_element_by_id('id_username') and self.browser.find_element_by_id('id_password')
                                            ))
        #as she doesn't have an account in the system Edith clicks the cancel button
        self.browser.find_element_by_id('cancel_button').click()
        #which takes her back to the citations homepage
        self.wait_for(lambda: self.assertTrue('Citations Home' in self.browser.title))

        #Even without logging in she sees she has three options to start exploring the data she can either
        #view Latin citations
        self.check_for_link_href_value_on_page("%s/citations/citation?language=lat" % self.live_server_url)
        #view Greek citations
        self.check_for_link_href_value_on_page("%s/citations/citation?language=grc" % self.live_server_url)
        #or search the citations
        self.check_for_link_href_value_on_page("%s/citations/search" % self.live_server_url)

        #She decides not to explore further just now and instead gets on with the ironing
