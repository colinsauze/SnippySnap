from .base import BaseFunctionalTest
    
class HomePageTest(BaseFunctionalTest):
    
    #@skip('timesaver')
    def test_workspace_server_is_running(self):
        #Edith visits the root of the web page and gets a Welcome page
        self.browser.get(self.live_server_url)
        #she sees the Workspace for collaborative editing homepage
        assert 'The Workspace for Collaborative Editing' in self.browser.title
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('THE WORKSPACE FOR COLLABORATIVE EDITING', header_text)
        #which has links to all of the ITSEE tools
        self.check_for_link_href_value_on_page('http://www.itsee.birmingham.ac.uk/ote')
        self.check_for_link_href_value_on_page('http://www.itsee.birmingham.ac.uk/collation')
        self.check_for_link_href_value_on_page('http://www.itsee.birmingham.ac.uk/citations')

        #and all of the ITSEE transcription sites
        
        #TODO: add these checks
        
        #and the contact email address for ITSEE
        self.check_for_link_href_value_on_page('mailto:itsee@contacts.bham.ac.uk')
         
        #TODO: the text of this file should be replaced by the live server version in case anything else has changed - the links were wrong in my local version so it is posisble
        
