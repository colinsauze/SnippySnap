from .base_logged_in import LoggedInFunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from rest_framework.renderers import JSONRenderer
from citations.serializers import CitationSerializer
from citations import models
from transcriptions import models as transcription_models
import re
import pickle
import json
import time
from unittest import skip
from django.utils import timezone




class DeletionTests(LoggedInFunctionalTest):

    #Edith is a citation Manager so she has deletion permissions


    def add_data(self):
        ##add data specifically designed to test deletion relations properly

        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc'
                   }
        self.a1 = models.Author.objects.create(**a1_data)
        a2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA2',
                   'full_name': 'Test Author 2',
                   'language': 'grc'
                   }
        self.a2 = models.Author.objects.create(**a2_data)
        a3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA3',
                   'full_name': 'Test Author 3',
                   'language': 'grc'
                   }
        self.a3 = models.Author.objects.create(**a3_data)


        w1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW1',
                   'author': self.a1,
                   'title': 'Test Work 1',
                   'language': 'grc'
                   }
        self.w1 = models.Work.objects.create(**w1_data)
        w2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW2',
                   'author': self.a2,
                   'title': 'Test Work 2',
                   'language': 'grc',
                   'clavis': '1234'
                   }
        self.w2 = models.Work.objects.create(**w2_data)
        w3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW3',
                   'author': self.a2,
                   'title': 'Test Work 3',
                   'language': 'grc',
                   'clavis': '1235',
                   }
        self.w3 = models.Work.objects.create(**w3_data)
        self.w3.other_possible_authors.add(self.a1)

        s1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TS1',
                   'title': 'Test Series 1'
                   }
        self.s1 = models.Series.objects.create(**s1_data)
        s2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TS2',
                   'title': 'Test Series 2'
                   }
        self.s2 = models.Series.objects.create(**s2_data)

        o1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TO1',
                   'title': 'Test Onlinecorpus 1'
                   }
        self.o1 = models.OnlineCorpus.objects.create(**o1_data)
        o2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TO2',
                   'title': 'Test Onlinecorpus 2'
                   }
        self.o2 = models.OnlineCorpus.objects.create(**o2_data)

        e1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': self.w1,
                   'editor': 'Migne',
                   'series': self.s1,
                   'year': '1906',
                   'volume': '6',
                   'onlinecorpus': self.o1
                   }
        self.e1 = models.Edition.objects.create(**e1_data)

        e2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': self.w1,
                   'series': self.s1,
                   'editor': 'Jones',
                   'year': '1997'
                   }
        self.e2 = models.Edition.objects.create(**e2_data)


        c1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e2,
                   'biblical_work': self.bw2,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων'
                   }
        self.c1 = models.Citation.objects.create(**c1_data)


        c2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'John.1.1',
                   'biblical_reference_sortable': 4001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e1,
                   'biblical_work': self.bw1,
                   'onlinecorpus': self.o1,
                   'status': 'deprecated but flagged',
                   'citation_text': 'και αρνῃ μεν το θεος ην ο λογος'
                   }
        self.c2 = models.Citation.objects.create(**c2_data)

        c3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw2,
                   'onlinecorpus': self.o1,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν'
                   }
        self.c3= models.Citation.objects.create(**c3_data)

        pc1_data = {'created_by': 'ben',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e1,
                   'biblical_work': self.bw2,
                   'onlinecorpus': self.o1,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν',
                   'project': self.p1,
                   'copied_to_private_time': timezone.now(),
                   }
        self.pc1= models.PrivateCitation.objects.create(**pc1_data)

        pc2_data = {'created_by': 'ben',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'edition': self.e1,
                   'biblical_work': self.bw2,
                   'onlinecorpus': self.o1,
                   'status': 'live',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν',
                   'project': self.p1,
                   'copied_to_private_time': timezone.now(),
                   }
        self.pc2= models.PrivateCitation.objects.create(**pc2_data)

        d1_data = {'relation_type': 'same_as',
                   'author': self.a2,
                   'work': self.w2,
                   'work_reference': '15.3',
                   'citation': self.c1
                   }
        self.d1 = models.Dependency.objects.create(**d1_data)

        d2_data = {'relation_type': 'same_as',
                   'author': self.a1,
                   'work': self.w1,
                   'work_reference': '15.1',
                   'citation': self.c3
                   }
        self.d2 = models.Dependency.objects.create(**d2_data)

        pd1_data = {'relation_type': 'same_as',
                   'author': self.a1,
                   'work': self.w1,
                   'work_reference': '15.2',
                   'citation': self.pc1
                   }
        self.pd1 = models.PrivateDependency.objects.create(**pd1_data)

    #she logs into the system
    def setUp(self):
        self.browser = webdriver.Firefox()

        credentials = {
            'username': 'edith',
            'password': 'secret',
            'display_name': 'Edith Tester'
            }
        self.edith = self.addCitationManagerUser(credentials)

        self.addBiblicalWorkData()
        self.addProjectData()
        self.p1.edition_transcribers.add(self.edith)

        #she logs in
        self.logUserIn(credentials)
        self.add_data()

    def test_deleteCitation(self):

        #Edith goes to the edit screen for a citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''))

        #she clicks on the delete button
        self.browser.find_element_by_id('delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete').click()
        self.wait_for(lambda: self.assertTrue('Delete Citation' in self.browser.title), 50)

        #there is a table on the screen
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('dependency_table')))
        #there is a list containing the citation that she has asked to delete
        self.assertTrue(self.element_is_on_page('citation_list'))
        #The citation's string representation is shown
        citlist = self.browser.find_element_by_id('citation_list')
        list_items = citlist.find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.c1.__str__())

        #There is a button to delete it
        self.assertTrue(self.element_is_on_page('delete_citation_%d' % self.c1.id))
        #when Edith clicks on the string representation of the citation she is taken to the details to check it is the correct one
        links = self.browser.find_elements_by_tag_name('a')

        for link in links:
            if link.text == self.c1.__str__():
                link.click()

        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Citation'))
        #the url is correct
        self.assertIn('/citations/citation/%s' % self.c1.id, self.browser.current_url)
        #there is a table showing the citation
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        ##wait for page to load
        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Delete Citation'), 50)

        #she clicks to cancel and returns to the list of citations
        self.browser.find_element_by_id('cancel_delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('cancel_delete').click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #she clicks back and is returned to the deltion page
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Citation' in self.browser.title), 50)

        #she clicks to delete the only item on the page and is returned to the citation list
        self.browser.find_element_by_id('delete_citation_%d' % self.c1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_citation_%d' % self.c1.id).click()
        self.wait_for(lambda: self.assertTrue('Citation List' in self.browser.title), 50)

        #the item is no longer in the database
        self.assertFalse(models.Citation.objects.filter(pk=self.c1.id).exists())
        #and the others are
        self.assertTrue(models.Citation.objects.filter(pk=self.c2.id).exists())
        self.assertTrue(models.Citation.objects.filter(pk=self.c3.id).exists())

        #the dependency associated with the deleted citation has also been deleted
        self.assertFalse(models.Dependency.objects.filter(pk=self.d1.id).exists())
        #the other is still there
        self.assertTrue(models.Dependency.objects.filter(pk=self.d2.id).exists())
        #the work and edition linked to the deleted citation are still in the database
        self.assertTrue(models.Work.objects.filter(pk=self.w1.id).exists())
        self.assertTrue(models.Edition.objects.filter(pk=self.e2.id).exists())

    def test_deleteSeries(self):
        #The only dependency for series is Edition
        #Deleting a series does not require the edition to be deleted just the reference to it
        #This is allowed even if the affected edition is referenced in citations in either public or private projects
        #Edith goes to the edit screen for a series
        self.browser.get('%s/citations/series/edit/%s' % (self.live_server_url, self.s1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Series' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('abbreviation').get_attribute('value'), ''))

        #she clicks on the delete button
        self.browser.find_element_by_id('delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete').click()
        self.wait_for(lambda: self.assertTrue('Delete Series' in self.browser.title), 50)

        #there is a table on the screen
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('dependency_table')))

        #there is a list containing the series that she has asked to delete
        self.assertTrue(self.element_is_on_page('series_list'))
        #The series' string representation is shown
        list_items = self.browser.find_element_by_id('series_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.s1.__str__())
        #There is a button to delete it
        self.assertTrue(self.element_is_on_page('delete_series_%d' % self.s1.id))
        self.browser.save_screenshot('delete_series.png')
        #there is another list containing the two edition that will be affected by deleting this series
        #and each has a delete button
        self.assertTrue(self.element_is_on_page('edition_list'))
        list_items = self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')
        self.assertEqual(len(list_items), 2)
        self.assertTrue(self.e2.__str__() in list_items[0].text)
        self.assertTrue(self.element_is_on_page('delete_edition_%d' % self.e2.id))
        self.assertTrue(self.e1.__str__() in list_items[1].text)
        self.assertTrue(self.element_is_on_page('delete_edition_%d' % self.e1.id))

        #Edith tried to disobey the rules and delete the series without deleting the edition reference
        self.browser.find_element_by_id('delete_series_%d' % self.s1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_series_%d' % self.s1.id).click()

        #she gets an error message saying the the series can't be deleted while the dependencies still exist
        self.wait_for(lambda: self.assertTrue(self.browser.find_element_by_id('error')))
        self.assertTrue('It was not possible to delete this series as there are other database entries that are dependent upon it.' in self.browser.find_element_by_id('error').get_attribute('innerHTML'))

        #she closes the error message
        self.browser.find_element_by_id('error_close').click()

        #she checks one of the links for the edition
        self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')[1].find_element_by_tag_name('a').click()

        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Edition'))
        #the url is correct
        self.assertIn('/citations/edition/%s' % self.e1.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Series' in self.browser.title))

        #she clicks on the button to delete the series reference in the edition she looked at
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).click()

        #the page reloads and the second edition is no longer visible
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')), 1), 50)

        ##this should set the series to null but keep the edition itself
        ##and not change the online corpus (I'm checking this because it is a required field in the serializer)
        ##also check that the last modified has been updated and other things are the same
        edition1 = models.Edition.objects.get(id=self.e1.id)
        self.assertEqual(edition1.series, None)
        self.assertEqual(edition1.onlinecorpus, self.o1)
        self.assertEqual(edition1.last_modified_by, 'Edith Tester')
        self.assertEqual(edition1.created_by, 'cat')

        #she deletes the reference in the second edition
        self.browser.find_element_by_id('delete_edition_%d' % self.e2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_edition_%d' % self.e2.id).click()

        #the page reloads and there are no visible edition
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('edition_list')), 50)
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('series_list')), 50)

        #she clicks on the button to delete the series
        self.browser.find_element_by_id('delete_series_%d' % self.s1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_series_%d' % self.s1.id).click()

        #she is redirected to the list of series
        self.wait_for(lambda: self.assertTrue('Series List' in self.browser.title), 50)
        #there is only one series in the table now (plus a header row)
        self.check_rows_in_table('data_table', 2)
        #the series she has deleted no longer exists in the database
        self.assertFalse(models.Series.objects.filter(pk=self.s1.id).exists())


    def test_deleteOnlinecorpus(self):

        #Edith goes to the edit screen for an online corpus
        self.browser.get('%s/citations/onlinecorpus/edit/%s' % (self.live_server_url, self.o1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Onlinecorpus' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('abbreviation').get_attribute('value'), ''))

        #she clicks on the delete button
        self.browser.find_element_by_id('delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete').click()
        self.wait_for(lambda: self.assertTrue('Delete Onlinecorpus' in self.browser.title), 50)

        #there is a warning that says that this online corpus is referenced in a private citation that the current user does not have permission to delete
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('private_dependency_warning')))

        #there is a table of dependencies
        self.assertTrue(self.element_is_on_page('dependency_table'))

        #there is a list containing the online corpus that she has asked to delete
        self.assertTrue(self.element_is_on_page('onlinecorpus_list'))
        #The series' string representation is shown
        list_items = self.browser.find_element_by_id('onlinecorpus_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.o1.__str__())
        #There is no button to delete it because of the dependencies
        self.assertFalse(self.element_is_on_page('delete_onlinecorpus_%d' % self.o1.id))

        #there is another list containing the edition that will be affected by deleting this onlinecorpus
        #it has a delete button
        self.assertTrue(self.element_is_on_page('edition_list'))
        list_items = self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')
        self.assertEqual(len(list_items), 1)
        self.assertTrue(self.e1.__str__() in list_items[0].text)
        self.assertTrue(self.element_is_on_page('delete_edition_%d' % self.e1.id))

        #there is another list containing the citations that will be affected by deleting this onlinecorpus
        #they both have delete buttons
        self.assertTrue(self.element_is_on_page('citation_list'))
        list_items2 = self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')
        self.wait_for(lambda: self.assertEqual(len(list_items2), 2), 50)
        self.assertEqual(self.c2.__str__(), list_items2[0].text)
        self.assertTrue(self.element_is_on_page('delete_citation_%d' % self.c2.id))
        self.assertEqual(self.c3.__str__(), list_items2[1].text)
        self.assertTrue(self.element_is_on_page('delete_citation_%d' % self.c3.id))

        #she checks one of the links for the edition
        self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')[0].find_element_by_tag_name('a').click()

        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Edition'))
        #the url is correct
        self.assertIn('/citations/edition/%s' % self.e1.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Onlinecorpus' in self.browser.title))


        #she checks one of the links for one of the citations
        self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')[1].find_element_by_tag_name('a').click()

        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Citation'))
        #the url is correct
        self.assertIn('/citations/citation/%s' % self.c3.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Onlinecorpus' in self.browser.title))

        #she deletes the two references in the citations
        #she clicks on the button to delete the online corpus reference in the edition she looked at
        self.browser.find_element_by_id('delete_citation_%d' % self.c3.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_citation_%d' % self.c3.id).click()

        #the page reloads and the second edition is no longer visible
        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')), 1), 50)

        ##this should set the onlinecorpus to null but keep the edition itself
        ##also check that the last modified has been updated and other things are the same
        cit = models.Citation.objects.get(id=self.c3.id)
        self.assertEqual(cit.onlinecorpus, None)
        self.assertEqual(cit.last_modified_by, 'Edith Tester')
        self.assertEqual(cit.created_by, 'cat')

        #she deletes the reference in the second edition
        self.browser.find_element_by_id('delete_citation_%d' % self.c2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_citation_%d' % self.c2.id).click()

        #the page reloads and there are no visible edition
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('citation_list')), 50)
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('edition_list')), 50)

        #she deletes the online corpus reference in the edition
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).click()

        #the page reloads and the edition list is no longer visible
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('edition_list')), 50)
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('onlinecorpus_list')), 50)

        ##this should set the online corpus to null but keep the edition itself
        ##and not change the series (I'm checking this because it is a required field in the serializer)
        ##also check that the last modified has been updated and other things are the same
        edition1 = models.Edition.objects.get(id=self.e1.id)
        self.assertEqual(edition1.series, self.s1)
        self.assertEqual(edition1.onlinecorpus, None)
        self.assertEqual(edition1.last_modified_by, 'Edith Tester')
        self.assertEqual(edition1.created_by, 'cat')

        #she can't delete the online corpus itself as there is no button (due to dependencies in private citations)
        self.assertFalse(self.element_is_on_page('delete_onlinecorpus_%d' % self.o1.id))

        #she can see the full details by clicking on the link
        self.browser.find_element_by_id('onlinecorpus_list').find_elements_by_tag_name('li')[0].find_element_by_tag_name('a').click()
        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Onlinecorpus'))
        #the url is correct
        self.assertIn('/citations/onlinecorpus/%s' % self.o1.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))


    def test_deleteEdition(self):
        ##The only possible dependencies for edition are  references in citations (or private citations)
        ##the citations themselves do not need deleting just the reference to the edition
        ##the presence of a reference in a private citation will prevent the edition from being deleted
        #Edith goes to the edit screen for an edition
        self.browser.get('%s/citations/edition/edit/%s' % (self.live_server_url, self.e1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Edition' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''))

        #she clicks on the delete button
        self.browser.find_element_by_id('delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete').click()
        self.wait_for(lambda: self.assertTrue('Delete Edition' in self.browser.title), 50)

        #there is a warning that says that this edition is referenced in a private citation that the current user does not have permission to delete
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('private_dependency_warning')))

        #there is a table on the screen
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('dependency_table')))

        #there is a list containing the edition that she has asked to delete
        self.assertTrue(self.element_is_on_page('edition_list'))
        #The edition's string representation is shown
        list_items = self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.e1.__str__())
        #There is no button to delete it
        self.assertFalse(self.element_is_on_page('delete_edition_%d' % self.e1.id))

        #there is another list containing the two edition that will be affected by deleting this series
        #and each has a delete button
        self.assertTrue(self.element_is_on_page('citation_list'))
        list_items = self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')
        self.assertEqual(len(list_items), 1)
        self.assertEqual(self.c2.__str__(), list_items[0].text)
        self.assertTrue(self.element_is_on_page('delete_citation_%d' % self.c2.id))

        #she checks one of the links for the edition
        self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')[0].find_element_by_tag_name('a').click()

        self.wait_for(lambda: self.assertEqual(self.browser.title, 'Citation'))
        #the url is correct
        self.assertIn('/citations/citation/%s' % self.c2.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Edition' in self.browser.title))

        #she clicks on the button to delete the series reference in the edition she looked at
        self.browser.find_element_by_id('delete_citation_%d' % self.c2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_citation_%d' % self.c2.id).click()

        #the page reloads and there are no visible citations
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('citation_list')), 50)
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('edition_list')), 50)

        ##this should set the edition reference to null but keep the citation
        ##also check that the last modified has been updated and other things are the same
        cit = models.Citation.objects.get(id=self.c2.id)
        self.assertEqual(cit.edition, None)
        self.assertEqual(cit.last_modified_by, 'Edith Tester')
        self.assertEqual(cit.created_by, 'cat')

        #Edith consults with the owner of the private citation that has a reference to this edition
        #the owner of the citation deleted the references
        self.pc1.edition = None
        self.pc1.save()
        self.pc2.edition = None
        self.pc2.save()

        #Next time Edith loads the page there are no dependencies and there is a button to delete the edition
        self.browser.get('%s/citations/edition/delete/%s' % (self.live_server_url, self.e1.id))
        self.wait_for(lambda: self.assertTrue('Delete Edition' in self.browser.title))
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('citation_list')), 50)
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('edition_list')), 50)
        self.assertTrue(self.element_is_on_page('delete_edition_%d' % self.e1.id))

        #she clicks on the button to delete the edition
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).click()

        #she is redirected to the list of edition
        self.wait_for(lambda: self.assertTrue('Edition List' in self.browser.title), 50)
        #there is only one edition in the table now (plus a header row)
        self.check_rows_in_table('data_table', 2)
        #the edition she has deleted no longer exists in the database
        self.assertFalse(models.Edition.objects.filter(pk=self.e1.id).exists())

    def test_deleteWork(self):

        self.browser.get('%s/citations/work/edit/%s' % (self.live_server_url, self.w1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Work' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('author').get_attribute('value'), ''))

        #she clicks on the delete button
        self.browser.find_element_by_id('delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete').click()
        self.wait_for(lambda: self.assertTrue('Delete Work' in self.browser.title), 50)

        #there is a warning to say that this work is referenced in private citations/private dependencies which the current user cannot delete
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('private_dependency_warning')))

        #there is a table on the screen
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('dependency_table')))

        #there is a list containing the work that she has asked to delete
        self.assertTrue(self.element_is_on_page('work_list'))
        #The work's string representation is shown
        list_items = self.browser.find_element_by_id('work_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.w1.__str__())
        #There is no button to delete it
        self.assertFalse(self.element_is_on_page('delete_work_%d' % self.w1.id))

        #there is a list containing the edition of this work
        self.assertTrue(self.element_is_on_page('edition_list'))
        #The edition's string representation is shown
        list_items = self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.e2.__str__())
        self.assertEqual(list_items[1].text, self.e1.__str__())
        #the first has a delete button
        self.assertTrue(self.element_is_on_page('delete_edition_%d' % self.e2.id))
        #the second doesn't as this edition is referenced in a private citation
        self.assertFalse(self.element_is_on_page('delete_edition_%d' % self.e1.id))

        #there is another list containing the citations of this work
        self.assertTrue(self.element_is_on_page('citation_list'))
        #The citation's string representation is shown
        list_items = self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.c2.__str__())
        self.assertEqual(list_items[1].text, self.c1.__str__())
        #they both have delete buttons
        self.assertTrue(self.element_is_on_page('delete_citation_%d' % self.c2.id))
        self.assertTrue(self.element_is_on_page('delete_citation_%d' % self.c1.id))

        #there is a final list containing the dependency that involves this work
        #it has a delete button
        self.assertTrue(self.element_is_on_page('dependency_list'))
        list_items = self.browser.find_element_by_id('dependency_list').find_elements_by_tag_name('li')
        self.assertEqual(len(list_items), 1)
        self.assertTrue(self.element_is_on_page('delete_dependency_%d' % self.d2.id))

        #there is a link to the citation containing the dependency, she clicks on it
        list_items[0].find_element_by_tag_name('a').click()

        #she is taken to the citation
        self.wait_for(lambda: self.assertTrue('Citation' in self.browser.title))
        #the url is correct
        self.assertIn('/citations/citation/%s' % self.c3.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Work' in self.browser.title))

        #she deletes the dependency
        self.browser.find_element_by_id('delete_dependency_%d' % self.d2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_dependency_%d' % self.d2.id).click()

        #the page reloads and the dependency list is no longer visible
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('dependency_list')), 25)
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('citation_list')))


        #the citation is still in the database but the dependency has been deleted
        self.assertTrue(models.Citation.objects.filter(pk=self.c3.id).exists())
        self.assertFalse(models.Dependency.objects.filter(pk=self.d2.id).exists())

        #she moves on the the citations themselves.
        #she clicks on the link for the first citation and that takes her to the details
        list_items = self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')
        list_items[0].find_element_by_tag_name('a').click()

        #she is taken to the citation
        self.wait_for(lambda: self.assertTrue('Citation' in self.browser.title))
        #the url is correct
        self.assertIn('/citations/citation/%s' % self.c2.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Work' in self.browser.title))

        #she deletes the first citation
        self.browser.find_element_by_id('delete_citation_%d' % self.c2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_citation_%d' % self.c2.id).click()

        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')), 1))

        #she deletes the second citation
        self.browser.find_element_by_id('delete_citation_%d' % self.c1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_citation_%d' % self.c1.id).click()

        #there are no more citations
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('citation_list')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('edition_list')))

        #she deletes the edition that can be deleted
        self.browser.find_element_by_id('delete_edition_%d' % self.e2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_edition_%d' % self.e2.id).click()

        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')), 1))

        #she clicks on the link to check the edition details
        list_items = self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')
        list_items[0].find_element_by_tag_name('a').click()

        #she is taken to the edition
        self.wait_for(lambda: self.assertTrue('Edition' in self.browser.title))
        #the url is correct
        self.assertIn('/citations/edition/%s' % self.e1.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #the final two items cannot be deleted because of dependencies with private citations
        #Edith negotiates with the owner of the citations and the edition reference are deleted from them
        self.pc1.edition = None
        self.pc1.save()
        self.pc2.edition = None
        self.pc2.save()

        #she reloads the page
        self.browser.get('%s/citations/work/delete/%s' % (self.live_server_url, self.w1.id))
        #the remaining edition now has a delete button
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_edition_%d' % self.e1.id)))
        #she clicks it
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).click()

        #the page reloads and there are no edition
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('edition_list')))
        #the work list is still there and there is still no delete button
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('work_list')))
        self.assertFalse(self.element_is_on_page('delete_work_%d' % self.w1.id))

        #Edith goes back to the work page while she sorts the other private citations out
        self.browser.get('%s/citations/work/' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title))

        #Edith does more negotiation with the owner of the private citations
        #the citation from this work is deleted from the database
        models.PrivateCitation.objects.filter(pk=self.pc2.id).delete()

        #she reloads the page
        self.browser.get('%s/citations/work/delete/%s' % (self.live_server_url, self.w1.id))
        #the work still has no delete button
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('delete_work_%d' % self.w1.id)))

        #she also asks for the dependency involving this work is deleted which it is
        models.PrivateDependency.objects.filter(pk=self.pd1.id).delete()

        #now when she reloads the page the work does have a delete button
        self.browser.get('%s/citations/work/delete/%s' % (self.live_server_url, self.w1.id))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_work_%d' % self.w1.id)))

        #she clicks the button to delete the work
        self.browser.find_element_by_id('delete_work_%d' % self.w1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_work_%d' % self.w1.id).click()

        #she is redirected to the list of edition
        self.wait_for(lambda: self.assertTrue('Work List' in self.browser.title), 50)
        #there are now only two works in the table now (plus a header row)
        self.check_rows_in_table('data_table', 3)
        #the work she has deleted no longer exists in the database
        self.assertFalse(models.Work.objects.filter(pk=self.w1.id).exists())


    def test_deleteAuthor(self):

        self.browser.get('%s/citations/author/edit/%s' % (self.live_server_url, self.a1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Author' in self.browser.title))
        self.wait_for(lambda: self.assertNotEqual(self.browser.find_element_by_id('abbreviation').get_attribute('value'), ''))

        #she clicks on the delete button
        self.browser.find_element_by_id('delete').location_once_scrolled_into_view
        self.browser.find_element_by_id('delete').click()
        self.wait_for(lambda: self.assertTrue('Delete Author' in self.browser.title), 150)

        #there is a warning to say that this author is referenced in private citations/private dependencies which the current user cannot delete
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('private_dependency_warning')))

        #there is a table on the screen
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('dependency_table')))

        #there is a list containing the author that she has asked to delete
        self.assertTrue(self.element_is_on_page('author_list'))
        #The author's string representation is shown
        list_items = self.browser.find_element_by_id('author_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.a1.__str__())
        #There is no button to delete it
        self.assertFalse(self.element_is_on_page('delete_author_%d' % self.a1.id))

        #there is a list containing the works by this author
        self.assertTrue(self.element_is_on_page('work_list'))
        #The works's string representation is shown
        list_items = self.browser.find_element_by_id('work_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.w1.__str__())
        #the work does not have a delete button as it is also involved in a private citation
        self.assertFalse(self.element_is_on_page('delete_work_%d' % self.w1.id))

        #there is a list containing possible works by this author
        self.assertTrue(self.element_is_on_page('possible_work_list'))
        #The works's string representation is shown
        list_items = self.browser.find_element_by_id('possible_work_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.w3.__str__())
        #the work has a delete button as this does not affect private citations
        self.assertTrue(self.element_is_on_page('delete_work_%d_author_%d' % (self.w3.id, self.a1.id)))

        #there is a list containing the edition of this work
        self.assertTrue(self.element_is_on_page('edition_list'))
        #The edition's string representation is shown
        list_items = self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')
        self.assertTrue(self.e2.__str__() in list_items[0].text)
        self.assertTrue(self.e1.__str__() in list_items[1].text)
        #the first has a delete button
        self.assertTrue(self.element_is_on_page('delete_edition_%d' % self.e2.id))
        #the second doesn't as this edition is referenced in a private citation
        self.assertFalse(self.element_is_on_page('delete_edition_%d' % self.e1.id))

        #there is another list containing the citations of this work
        self.assertTrue(self.element_is_on_page('citation_list'))
        #The citations's string representation is shown
        list_items = self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')
        self.assertEqual(list_items[0].text, self.c2.__str__())
        self.assertEqual(list_items[1].text, self.c1.__str__())
        #they both have delete buttons
        self.assertTrue(self.element_is_on_page('delete_citation_%d' % self.c2.id))
        self.assertTrue(self.element_is_on_page('delete_citation_%d' % self.c1.id))

        #there is a final list containing the dependency that involves this work
        #it has a delete button
        self.assertTrue(self.element_is_on_page('dependency_list'))
        list_items = self.browser.find_element_by_id('dependency_list').find_elements_by_tag_name('li')
        self.assertEqual(len(list_items), 1)
        self.assertTrue(self.element_is_on_page('delete_dependency_%d' % self.d2.id))

        #there is a link to the citation containing the dependency, she clicks on it
        self.assertTrue(self.c3.__str__() in list_items[0].text)
        list_items[0].find_element_by_tag_name('a').click()

        #she is taken to the citation
        self.wait_for(lambda: self.assertTrue('Citation' in self.browser.title))
        #the url is correct
        self.assertIn('/citations/citation/%s' % self.c3.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Author' in self.browser.title))

        #she deletes the dependency
        self.browser.find_element_by_id('delete_dependency_%d' % self.d2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_dependency_%d' % self.d2.id).click()

        #the page reloads and the dependency list is no longer visible
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('dependency_list')), 25)
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('citation_list')), 75)

        #the citation is still in the database but the dependency has been deleted
        self.assertTrue(models.Citation.objects.filter(pk=self.c3.id).exists())
        self.assertFalse(models.Dependency.objects.filter(pk=self.d2.id).exists())

        #she moves on the the citations themselves.
        #she clicks on the link for the first citation and that takes her to the details
        list_items = self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')
        list_items[0].find_element_by_tag_name('a').click()

        #she is taken to the citation
        self.wait_for(lambda: self.assertTrue('Citation' in self.browser.title))
        #the url is correct
        self.assertIn('/citations/citation/%s' % self.c2.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Author' in self.browser.title))

        #she deletes the first citation
        self.browser.find_element_by_id('delete_citation_%d' % self.c2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_citation_%d' % self.c2.id).click()

        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('citation_list').find_elements_by_tag_name('li')), 1))

        #she deletes the second citation
        self.browser.find_element_by_id('delete_citation_%d' % self.c1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_citation_%d' % self.c1.id).click()

        #there are no more citations
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('citation_list')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('edition_list')))

        #she deletes the edition that can be deleted
        self.browser.find_element_by_id('delete_edition_%d' % self.e2.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_edition_%d' % self.e2.id).click()

        self.wait_for(lambda: self.assertEqual(len(self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')), 1))

        #she clicks on the link to check the edition details
        list_items = self.browser.find_element_by_id('edition_list').find_elements_by_tag_name('li')
        list_items[0].find_element_by_tag_name('a').click()

        #she is taken to the edition
        self.wait_for(lambda: self.assertTrue('Edition' in self.browser.title))
        #the url is correct
        self.assertIn('/citations/edition/%s' % self.e1.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #the final two items cannot be deleted because of dependencies with private citations
        #Edith negotiates with the owner of the citations and the edition reference are deleted from them
        self.pc1.edition = None
        self.pc1.save()
        self.pc2.edition = None
        self.pc2.save()

        #she reloads the page
        self.browser.get('%s/citations/author/delete/%s' % (self.live_server_url, self.a1.id))
        #the remaining edition now has a delete button
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_edition_%d' % self.e1.id)))
        #she clicks it
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_edition_%d' % self.e1.id).click()

        #the page reloads and there are no edition
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('edition_list')))
        #the work list is still there and there is still no delete button
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('work_list')))
        self.assertFalse(self.element_is_on_page('delete_work_%d' % self.w1.id))
        #the author list is still there and there is still no delete button
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('author_list')))
        self.assertFalse(self.element_is_on_page('delete_author_%d' % self.a1.id))

        #possible author
        #she clicks on the link to see the deails of the work for which this author might be a posisble author
        list_items = self.browser.find_element_by_id('possible_work_list').find_elements_by_tag_name('li')
        list_items[0].find_element_by_tag_name('a').click()

        #she is taken to the work
        self.wait_for(lambda: self.assertTrue('Work' in self.browser.title))
        #the url is correct
        self.assertIn('/citations/work/%s' % self.w3.id, self.browser.current_url)
        #there is a table showing the edition
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('data_instance_table')))

        #she clicks back
        self.browser.execute_script("window.history.go(-1)")
        self.wait_for(lambda: self.assertTrue('Delete Author' in self.browser.title))

        #Edith deletes the possible work
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_work_%d_author_%d' % (self.w3.id, self.a1.id))))
        self.browser.find_element_by_id('delete_work_%d_author_%d' % (self.w3.id, self.a1.id)).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_work_%d_author_%d' % (self.w3.id, self.a1.id)).click()


        #there are no more possible works but the work list is still there
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('possible_work_list')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('work_list')))
        self.browser.save_screenshot('author.png')

        #the author itself is still in the database
        self.assertTrue(models.Author.objects.filter(pk=self.a1.id).exists())
        #so is the work
        self.assertTrue(models.Work.objects.filter(pk=self.w3.id).exists())
        #but he reference to the author in the work has been removed
        self.assertFalse(models.Work.objects.all().filter(pk=self.w3.id, other_possible_authors__id = self.a1.id).exists())


        #Edith goes back to the author page while she sorts the other private citations out
        self.browser.get('%s/citations/author/' % self.live_server_url)
        self.wait_for(lambda: self.assertTrue('Author List' in self.browser.title))

        #Edith does more negotiation with the owner of the private citations
        #the citation from this work is deleted from the database
        models.PrivateCitation.objects.filter(pk=self.pc2.id).delete()

        #she reloads the page
        self.browser.get('%s/citations/author/delete/%s' % (self.live_server_url, self.a1.id))
        #the work still has no delete button
        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('delete_work_%d' % self.w1.id)))


        #she also asks for the dependency involving this work is deleted which it is
        models.PrivateDependency.objects.filter(pk=self.pd1.id).delete()

        #now when she reloads the page the work does have a delete button
        self.browser.get('%s/citations/author/delete/%s' % (self.live_server_url, self.a1.id))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('delete_work_%d' % self.w1.id)))

        #she clicks the button to delete the work
        self.browser.find_element_by_id('delete_work_%d' % self.w1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_work_%d' % self.w1.id).click()

        self.wait_for(lambda: self.assertFalse(self.element_is_on_page('work_list')))
        self.wait_for(lambda: self.assertTrue(self.element_is_on_page('author_list')))

        #as all the private dependencies have been resolved already and all of the others have been deleted the author now has a delete button
        #she clicks the button to delete the author
        self.browser.find_element_by_id('delete_author_%d' % self.a1.id).location_once_scrolled_into_view
        self.browser.find_element_by_id('delete_author_%d' % self.a1.id).click()

        #she is redirected to the list of authors
        self.wait_for(lambda: self.assertTrue('Author List' in self.browser.title), 50)
        #there are now only two authors in the table now (plus a header row)
        self.check_rows_in_table('data_table', 3)
        #the author she has deleted no longer exists in the database
        self.assertFalse(models.Author.objects.filter(pk=self.a1.id).exists())
