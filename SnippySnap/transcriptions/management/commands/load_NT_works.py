from django.core.management.base import BaseCommand, CommandError

from transcriptions.models import Collection
from transcriptions.models import Work
from transcriptions.models import Corpus
from transcriptions.models import Structure

class Command(BaseCommand):

    def handle(self, *args, **options):

        collection_data = {
            'NT': {'identifier': 'NT', 'name': 'The New Testament', 'abbreviation': 'NT'},
            'OT': {'identifier': 'OT', 'name': 'The Old Testament', 'abbreviation': 'OT'}
        }

        for key in collection_data:

            coll = Collection(**collection_data[key])
            # check if we have an existing entry - if so we must ensure we keep the pk as other things link to this
            try:
                existing = Collection.objects.get(identifier=collection_data[key]['identifier'])
                coll.id = existing.id
            except:
                pass
            coll.save()

        corpus_data = {
            'NT_LAT': {'identifier': 'NT_LAT', 'language': 'lat'},
            'NT_GRC': {'identifier': 'NT_GRC', 'language': 'grc'},
        }

        for key in corpus_data:

            c  = Corpus(**corpus_data[key])
            try:
                existing = Corpus.objects.get(identifier=corpus_data[key]['identifier'])
                c.id = existing.id
            except:
                pass
            collection = Collection.objects.get(identifier='NT')
            c.collection = collection
            c.save()



        NT_works_data = {
            'Matt': {'name': 'Matthew', 'abbreviation': 'Matt', 'book_number': 1, 'total_chapters': 28,
                'verses_per_chapter': {'1':25, '2':23, '3':17, '4':25, '5':48, '6':34, '7':29, '8':34, '9':38, '10':42, '11':30, '12':50, '13':58,
                                   '14':36, '15':39, '16':28, '17':27, '18':35, '19':30, '20':34, '21':46, '22':46, '23':39, '24':51, '25':46,
                                   '26':75, '27':66, '28':20}},
            'Mark': {'name': 'Mark', 'abbreviation': 'Mark', 'book_number': 2, 'total_chapters': 16,
                'verses_per_chapter': {'1':45, '2':28, '3':35, '4':41, '5':43, '6':56, '7':37, '8':38, '9':50, '10':52, '11':33, '12':44, '13':37,
                                   '14':72, '15':47, '16':20}},
            'Luke': {'name': 'Luke', 'abbreviation': 'Luke', 'book_number': 3, 'total_chapters': 24,
                'verses_per_chapter': {'1':80, '2':52, '3':38, '4':44, '5':39, '6':49, '7':50, '8':56, '9':62, '10':42, '11':54, '12':59, '13':35,
                                   '14':35, '15':32, '16':31, '17':37, '18':43, '19':48, '20':47, '21':38, '22':71, '23':56, '24':53}},
            'John': {'name': 'John', 'abbreviation': 'John', 'book_number': 4, 'total_chapters': 21,
                'verses_per_chapter': {'1':51, '2':25, '3':36, '4':54, '5':47, '6':71, '7':53, '8':59, '9':41, '10':42, '11':57, '12':50, '13':38,
                                   '14':31, '15':27, '16':33, '17':26, '18':40, '19':42, '20':31, '21':25}},
            'Acts': {'name': 'Acts', 'abbreviation': 'Acts', 'book_number': 5, 'total_chapters': 28,
                'verses_per_chapter': {'1':26, '2':47, '3':26, '4':37, '5':42, '6':15, '7':60, '8':40, '9':43, '10':48, '11':30, '12':25, '13':52,
                                   '14':28, '15':41, '16':40, '17':34, '18':28, '19':41, '20':38, '21':40, '22':30, '23':35, '24':27, '25':27,
                                   '26':32, '27':44, '28':31}},
            'Rom': {'name': 'Romans', 'abbreviation': 'Rom', 'book_number': 6, 'total_chapters': 16,
                'verses_per_chapter': {'1':32, '2':29, '3':31, '4':25, '5':21, '6':23, '7':25, '8':39, '9':33, '10':21, '11':36, '12':21, '13':14,
                                   '14':26, '15':33, '16':27}},
            '1Cor': {'name': '1 Corinthians', 'abbreviation': '1Cor', 'book_number': 7, 'total_chapters': 16,
                'verses_per_chapter': {'1':31, '2':16, '3':23, '4':21, '5':13, '6':20, '7':40, '8':13, '9':27, '10':33, '11':34, '12':31, '13':13,
                                   '14':40, '15':58, '16':24}},
            '2Cor': {'name': '2 Corinthians', 'abbreviation': '2Cor', 'book_number': 8, 'total_chapters': 13,
                'verses_per_chapter': {'1':24, '2':17, '3':18, '4':18, '5':21, '6':18, '7':16, '8':24, '9':15, '10':18, '11':33, '12':21, '13':14}},
            'Gal': {'name': 'Galatians', 'abbreviation': 'Gal', 'book_number': 9, 'total_chapters': 6,
                'verses_per_chapter': {'1':24, '2':21, '3':29, '4':31, '5':26, '6':18}},
            'Eph': {'name': 'Ephesians', 'abbreviation': 'Eph', 'book_number': 10, 'total_chapters': 6,
                'verses_per_chapter': {'1':23, '2':22, '3':21, '4':32, '5':33, '6':24}},
            'Phil': {'name': 'Philippians', 'abbreviation': 'Phil', 'book_number': 11, 'total_chapters': 4,
                'verses_per_chapter': {'1':30, '2':30, '3':21, '4':23}},
            'Col': {'name': 'Colossians', 'abbreviation': 'Col', 'book_number': 12, 'total_chapters': 4,
                'verses_per_chapter': {'1':29, '2':23, '3':25, '4':18}},
            '1Thess': {'name': '1 Thessalonians', 'abbreviation': '1Thess', 'book_number': 13, 'total_chapters': 5,
                'verses_per_chapter': {'1':10, '2':20, '3':13, '4':18, '5':28}},
            '2Thess': {'name': '2 Thessalonians', 'abbreviation': '2Thess', 'book_number': 14, 'total_chapters': 3,
                'verses_per_chapter': {'1':12, '2':17, '3':18}},
            '1Tim': {'name': '1 Timothy', 'abbreviation': '1Tim', 'book_number': 15, 'total_chapters': 6,
                'verses_per_chapter': {'1':20, '2':15, '3':16, '4':16, '5':25, '6':21}},
            '2Tim': {'name': '2 Timothy', 'abbreviation': '2Tim', 'book_number': 16, 'total_chapters': 4,
                'verses_per_chapter': {'1':18, '2':26, '3':17, '4':22}},
            'Titus': {'name': 'Titus', 'abbreviation': 'Titus', 'book_number': 17, 'total_chapters': 3,
                'verses_per_chapter': {'1':16, '2':15, '3':15}},
            'Phlm': {'name': 'Philemon', 'abbreviation': 'Phlm', 'book_number': 18, 'total_chapters': 1,
                'verses_per_chapter': {'1':25}},
            'Heb': {'name': 'Hebrews', 'abbreviation': 'Heb', 'book_number': 19, 'total_chapters': 13,
                'verses_per_chapter': {'1':14, '2':18, '3':19, '4':16, '5':14, '6':20, '7':28, '8':13, '9':28, '10':39, '11':40, '12':29, '13':25}},
            'Jas': {'name': 'James', 'abbreviation': 'Jas', 'book_number': 20, 'total_chapters': 5,
                'verses_per_chapter': {'1':27, '2':26, '3':18, '4':17, '5':20}},
            '1Pet': {'name': '1 Peter', 'abbreviation': '1Pet', 'book_number': 21, 'total_chapters': 5,
                'verses_per_chapter': {'1':25, '2':25, '3':22, '4':19, '5':14}},
            '2Pet': {'name': '2 Peter', 'abbreviation': '2Pet', 'book_number': 22, 'total_chapters': 3,
                'verses_per_chapter': {'1':21, '2':22, '3':18}},
            '1John': {'name': '1 John', 'abbreviation': '1John', 'book_number': 23, 'total_chapters': 5,
                'verses_per_chapter': {'1':10, '2':29, '3':24, '4':21, '5':21}},
            '2John': {'name': '2 John', 'abbreviation': '2John', 'book_number': 24, 'total_chapters': 1,
                'verses_per_chapter': {'1':13}},
            '3John': {'name': '3 John', 'abbreviation': '3John', 'book_number': 25, 'total_chapters': 1,
                'verses_per_chapter': {'1':15}},
            'Jude': {'name': 'Jude', 'abbreviation': 'Jude', 'book_number': 26, 'total_chapters': 1,
                'verses_per_chapter': {'1':25}},
            'Rev': {'name': 'Revelation', 'abbreviation': 'Rev', 'book_number': 27, 'total_chapters': 22,
                'verses_per_chapter': {'1':20, '2':29, '3':22, '4':11, '5':14, '6':17, '7':17, '8':13, '9':21, '10':11, '11':19, '12':17, '13':18,
                                   '14':20, '15':8, '16':21, '17':18, '18':24, '19':21, '20':15, '21':27, '22':21}},
        }



        for entry in NT_works_data:

            work = {
                'identifier' : 'NT_%s' % NT_works_data[entry]['abbreviation'],
                'name': NT_works_data[entry]['name'],
                'sort_value': NT_works_data[entry]['book_number'],
                'abbreviation': NT_works_data[entry]['abbreviation']
            }
            w  = Work(**work)
            try:
                existing = Work.objects.get(identifier='NT_%s' % NT_works_data[entry]['abbreviation'])
                w.id = existing.id
            except:
                pass
            collection = Collection.objects.get(identifier='NT')
            w.collection = collection
            w.save()

            for language in ['GRC', 'LAT']:

                structure = {
                    'abbreviation': NT_works_data[entry]['abbreviation'],
                    'total_chapters': NT_works_data[entry]['total_chapters'],
                    'verses_per_chapter': NT_works_data[entry]['verses_per_chapter'],
                    'position_in_corpus': NT_works_data[entry]['book_number']
                }

                s = Structure(**structure)
                s.work = w
                corpus = Corpus.objects.get(identifier='NT_%s' % language)
                s.corpus = corpus
                existing = Structure.objects.filter(corpus__identifier='NT_%s' % language, work__identifier='NT_%s' % NT_works_data[entry]['abbreviation'])
                if len(existing) == 1:
                    s.id = existing[0].id
                else:
                    pass
                s.save()
