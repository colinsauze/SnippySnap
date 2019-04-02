import sys
import time
from itsee_functional_tests.base import BaseFunctionalTest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from citations import models
from transcriptions import models as transcription_models

class FunctionalTest(BaseFunctionalTest):

    def addBiblicalWorkData(self):

        collection_data = {
            'identifier': 'NT',
            'name': 'The New Testament',
            'abbreviation': 'NT'
        }

        self.collection = transcription_models.Collection.objects.create(**collection_data)


        grc_corpus_data = {
            'identifier': 'NT_GRC',
            'collection': self.collection,
            'language': 'grc',
        }
        self.grc_corpus = transcription_models.Corpus.objects.create(**grc_corpus_data)

        lat_corpus_data = {
            'identifier': 'NT_LAT',
            'collection': self.collection,
            'language': 'lat',
        }
        self.lat_corpus = transcription_models.Corpus.objects.create(**lat_corpus_data)


        biblical_work_data = {'identifier': 'NT_John',
                              'sort_value': 4,
                              'name': 'John',
                              'collection': self.collection,
                              'abbreviation': 'John'
                              }
        self.bw1 = transcription_models.Work.objects.create(**biblical_work_data)


        biblical_work_data_2 = {'identifier': 'NT_Gal',
                              'sort_value': 9,
                              'name': 'Galatians',
                              'collection': self.collection,
                              'abbreviation': 'Gal'
                              }
        self.bw2 = transcription_models.Work.objects.create(**biblical_work_data_2)

        structure_data = {
            'work': self.bw2,
            'corpus': self.grc_corpus,
            'position_in_corpus': 9,
            'total_chapters': 2,
            'verses_per_chapter': {1: 2, 2: 2},
            'abbreviation': 'Gal'
        }
        self.structure = transcription_models.Structure.objects.create(**structure_data)

    def addTestData(self):

        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA1',
                   'full_name': 'Test Author 1',
                   'language': 'grc',
                   'version_number': 1,
                   }
        self.a1 = models.Author.objects.create(**a1_data)
        a2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA2',
                   'full_name': 'Test Author 2',
                   'language': 'grc',
                   'version_number': 1,
                   }
        self.a2 = models.Author.objects.create(**a2_data)
        a3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TA3',
                   'full_name': 'Test Author 3',
                   'language': 'lat',
                   'version_number': 1,
                   }
        self.a3 = models.Author.objects.create(**a3_data)


        w1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW1',
                   'author': self.a1,
                   'title': 'Test Work 1',
                   'language': 'grc',
                   'version_number': 1,
                   }
        self.w1 = models.Work.objects.create(**w1_data)
        w2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW2',
                   'author': self.a2,
                   'title': 'Test Work 2',
                   'language': 'grc',
                   'clavis': '1234',
                   'version_number': 1,
                   }
        self.w2 = models.Work.objects.create(**w2_data)

        s1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TS1',
                   'title': 'Test Series 1',
                   'version_number': 1,
                   }
        self.s1 = models.Series.objects.create(**s1_data)
        s2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TS2',
                   'title': 'Test Series 2',
                   'version_number': 1,
                   }
        self.s2 = models.Series.objects.create(**s2_data)

        e1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': self.w2,
                   'editor': 'Migne',
                   'series': self.s1,
                   'year': '1906',
                   'volume': '6',
                   'version_number': 1,
                   }
        self.e1 = models.Edition.objects.create(**e1_data)
        e2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': self.w2,
                   'editor': 'Jones',
                   'year': '1997',
                   'version_number': 1,
                   }
        self.e2 = models.Edition.objects.create(**e2_data)

        o1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TO1',
                   'title': 'Test Onlinecorpus 1',
                   'version_number': 1,
                   }
        self.o1 = models.OnlineCorpus.objects.create(**o1_data)
        o2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TO2',
                   'title': 'Test Onlinecorpus 2',
                   'version_number': 1,
                   }
        self.o2 = models.OnlineCorpus.objects.create(**o2_data)

        self.addBiblicalWorkData()

        c1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'biblical_reference': 'John.1.1',
                   'biblical_reference_sortable': 4001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw1,
                   'status': 'live',
                   'citation_text': 'και αρνῃ μεν το θεος ην ο λογος',
                   'version_number': 1,
                   }
        self.c1 = models.Citation.objects.create(**c1_data)

        c2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'Gal.1.1',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw2,
                   'status': 'deprecated but flagged',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν',
                   'version_number': 1,

                   }
        self.c2 = models.Citation.objects.create(**c2_data)
