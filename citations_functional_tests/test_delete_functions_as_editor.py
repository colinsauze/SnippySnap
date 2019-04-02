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




class DeletionTestsAsEditor(LoggedInFunctionalTest):

    #Tess is a citation Editor so she has no delete permissions

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
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν'
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
            'username': 'tess',
            'password': 'secret',
            'display_name': 'Tess Edition Tester'
            }
        self.tess = self.addCitationEditorUser(credentials)
        self.addBiblicalWorkData()
        self.addProjectData()
        self.p1.edition_transcribers.add(self.tess)

        #she logs in
        self.logUserIn(credentials)
        self.add_data()


    def test_deleteCitation(self):

        #Tess goes to the edit screen for a citation
        self.browser.get('%s/citations/citation/edit/%s' % (self.live_server_url, self.c1.id))
        self.wait_for(lambda: self.assertTrue('Add/Edit Citation' in self.browser.title))
        self.wait_for(lambda: self.assertFalse(self.browser.find_element_by_id('delete').is_displayed()), 50)

        #she doesn't have a delete button
        self.assertFalse(self.browser.find_element_by_id('delete').is_displayed())

        #she tries to access the delete page directly
        self.browser.get('%s/citations/citation/delete/%s' % (self.live_server_url, self.c1.id))
        #but the system doesn't let her get there
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title), 50)

        #she tries to access the api directly
        self.browser.get('%s/api/citations/citation/delete/%s' % (self.live_server_url, self.c1.id))
        self.wait_for(lambda: self.assertTrue('405 Method Not Allowed' in self.browser.find_element_by_tag_name('body').text), 50)

        #she tries to access the author delete page directly
        self.browser.get('%s/citations/author/delete/%s' % (self.live_server_url, self.a1.id))
        #but the system doesn't let her get there
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title), 50)

        #she tries to access the api directly
        self.browser.get('%s/api/citations/author/delete/%s' % (self.live_server_url, self.a1.id))
        self.wait_for(lambda: self.assertTrue('405 Method Not Allowed' in self.browser.find_element_by_tag_name('body').text), 50)

        #she tries to access the work delete page directly
        self.browser.get('%s/citations/work/delete/%s' % (self.live_server_url, self.w1.id))
        #but the system doesn't let her get there
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title), 50)

        #she tries to access the api directly
        self.browser.get('%s/api/citations/work/delete/%s' % (self.live_server_url, self.w1.id))
        self.wait_for(lambda: self.assertTrue('405 Method Not Allowed' in self.browser.find_element_by_tag_name('body').text), 50)

        #she tries to access the edition delete page directly
        self.browser.get('%s/citations/edition/delete/%s' % (self.live_server_url, self.e1.id))
        #but the system doesn't let her get there
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title), 50)

        #she tries to access the api directly
        self.browser.get('%s/api/citations/edition/delete/%s' % (self.live_server_url, self.e1.id))
        self.wait_for(lambda: self.assertTrue('405 Method Not Allowed' in self.browser.find_element_by_tag_name('body').text), 50)

        #she tries to access the series delete page directly
        self.browser.get('%s/citations/series/delete/%s' % (self.live_server_url, self.s1.id))
        #but the system doesn't let her get there
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title), 50)

        #she tries to access the api directly
        self.browser.get('%s/api/citations/series/delete/%s' % (self.live_server_url, self.s1.id))
        self.wait_for(lambda: self.assertTrue('405 Method Not Allowed' in self.browser.find_element_by_tag_name('body').text), 50)

        #she tries to access the onlinecorpus delete page directly
        self.browser.get('%s/citations/onlinecorpus/delete/%s' % (self.live_server_url, self.o1.id))
        #but the system doesn't let her get there
        self.wait_for(lambda: self.assertTrue('403 error' in self.browser.title), 50)

        #she tries to access the api directly
        self.browser.get('%s/api/citations/onlinecorpus/delete/%s' % (self.live_server_url, self.o1.id))
        self.wait_for(lambda: self.assertTrue('405 Method Not Allowed' in self.browser.find_element_by_tag_name('body').text), 50)
