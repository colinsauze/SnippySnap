from django.test import TestCase
from django.utils import timezone
from django.db.models import Q
from citations import models
from citations import views
from transcriptions import models as transcription_models
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.http import HttpRequest
import urllib
import json


class DeleteHelperTests(TestCase):

    def setUp(self):

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
                   'language': 'lat'
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
        self.w1.other_possible_authors.add(self.a2)
        self.w1.save()

        w2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'abbreviation': 'TW2',
                   'author': self.a2,
                   'title': 'Test Work 2',
                   'language': 'grc',
                   'clavis': '1234'
                   }
        self.w2 = models.Work.objects.create(**w2_data)

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

        e1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': self.w2,
                   'editor': 'Migne',
                   'series': self.s1,
                   'year': '1906',
                   'volume': '6'
                   }
        self.e1 = models.Edition.objects.create(**e1_data)
        e2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'work': self.w2,
                   'editor': 'Jones',
                   'year': '1997'
                   }
        self.e2 = models.Edition.objects.create(**e2_data)

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

        # biblical_work_data = {'identifier': 'NT_GRC_John',
        #                       'book_number': 4,
        #                       'name': 'John',
        #                       'corpus': 'NT',
        #                       'language': 'grc',
        #                       'abbreviation': 'John'
        #                       }
        biblical_work_data = {'identifier': 'NT_John',
                              'sort_value': 4,
                              'name': 'John',
                              'corpus': 'NT',
                              'abbreviation': 'John'
                              }
        self.bw1 = transcription_models.Work.objects.create(**biblical_work_data)

        # biblical_work_data_2 = {'identifier': 'NT_GRC_Gal',
        #                       'book_number': 9,
        #                       'name': 'Galatians',
        #                       'abbreviation': 'Gal',
        #                       'corpus': 'NT',
        #                       'language': 'grc',
        #                       'total_chapters': 2,
        #                       'verses_per_chapter': {1: 2, 2: 2}
        #                       }
        biblical_work_data_2 = {'identifier': 'NT_Gal',
                              'sort_value': 9,
                              'name': 'Galatians',
                              'abbreviation': 'Gal',
                              'corpus': 'NT'
                              }
        self.bw2 = transcription_models.Work.objects.create(**biblical_work_data_2)

        c1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w1,
                   'edition':self.e1,
                   'biblical_reference': 'B04K01V01',
                   'biblical_reference_sortable': 4001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw1,
                   'status': 'live',
                   'citation_text': 'και αρνῃ μεν το θεος ην ο λογος',
                   }
        self.c1 = models.Citation.objects.create(**c1_data)
        dependency = {'author': self.a2, 'work': self.w2}
        self.d1 = models.Dependency.objects.create(**dependency)
        self.c1.dependencies.add(self.d1)
        self.c1.save()
        c2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'language': 'grc',
                   'work': self.w2,
                   'biblical_reference': 'B09K01V01',
                   'biblical_reference_sortable': 9001001,
                   'chapter': 1,
                   'verse': 1,
                   'biblical_work': self.bw2,
                   'status': 'deprecated but flagged',
                   'citation_text': 'Παῦλος ἀπόστολος οὐκ ἀπ᾿ ἀνθρώπων, οὐδὲ δι᾿ ἀνθρώπου, ἀλλὰ διὰ Ἰησοῦ Χριστοῦ, καὶ Θεοῦ πατρὸς τοῦ ἐγείραντος αὐτὸν ἐκ νεκρῶν',
                   'onlinecorpus': self.o1
                   }
        self.c2 = models.Citation.objects.create(**c2_data)


    def test_getRelations(self):

        relations = views.getRelations('author', self.a2)
        self.assertEqual(len(relations['works']), 1)
        self.assertEqual(len(relations['possible_works']), 1)
        self.assertEqual(len(relations['editions']), 2)
        self.assertEqual(len(relations['citations']), 1)
        self.assertEqual(len(relations['dependencies']), 1)

        relations = views.getRelations('work', self.w2)
        self.assertEqual(len(relations['editions']), 2)
        self.assertEqual(len(relations['citations']), 1)
        self.assertEqual(len(relations['dependencies']), 1)

        relations = views.getRelations('edition', self.e1)
        self.assertEqual(len(relations['citations']), 1)

        relations = views.getRelations('series', self.s1)
        self.assertEqual(len(relations['editions']), 1)

        relations = views.getRelations('onlinecorpus', self.o1)
        self.assertEqual(len(relations['editions']), 0)
        self.assertEqual(len(relations['citations']), 1)

        relations = views.getRelations('citations', self.c1)
        self.assertEqual(relations, {})
