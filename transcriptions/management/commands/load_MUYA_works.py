from django.core.management.base import BaseCommand, CommandError

from transcriptions.models import Collection
from transcriptions.models import Work
from transcriptions.models import Corpus
from transcriptions.models import Structure

class Command(BaseCommand):

    def handle(self, *args, **options):

        collection_data = {
            'AV': {'identifier': 'AV', 'name': 'Avetsa', 'abbreviation': 'AV'}
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
            'AV_AE': {'identifier': 'AV_AE', 'language': 'ae'},
        }

        for key in corpus_data:

            c  = Corpus(**corpus_data[key])
            try:
                existing = Corpus.objects.get(identifier=corpus_data[key]['identifier'])
                c.id = existing.id
            except:
                pass
            collection = Collection.objects.get(identifier='AV')
            c.collection = collection
            c.save()

        MUYA_works_data = {
            'Y': {'name': 'Yasna', 'abbreviation': 'Y', 'book_number': 2, 'total_chapters': 6,
                'verses_per_chapter': {'3': 25, '4': 26, '5': 6, '6': 21, '7': 28, '8': 9}},
            'YiR': {'name': 'Rapihwin', 'abbreviation': 'YiR', 'book_number': 2, 'total_chapters': 6,
                'verses_per_chapter': {'3': 25, '4': 26, '5': 6, '6': 21, '7': 28, '8': 9}},
            'VS': {'name': 'Vivevdad', 'abbreviation': 'VS', 'book_number': 2, 'total_chapters': 6,
                'verses_per_chapter': {'3': 25, '4': 26, '5': 6, '6': 21, '7': 28, '8': 9}},
            'VytS': {'name': 'Vistasp Yast', 'abbreviation': 'VytS', 'book_number': 2, 'total_chapters': 6,
                'verses_per_chapter': {'3': 25, '4': 26, '5': 6, '6': 21, '7': 28, '8': 9}}
        }

        for entry in MUYA_works_data:

            work = {
                'identifier' : 'AV_%s' % MUYA_works_data[entry]['abbreviation'],
                'name': MUYA_works_data[entry]['name'],
                'sort_value': MUYA_works_data[entry]['book_number'],
                'abbreviation': MUYA_works_data[entry]['abbreviation']
            }
            w  = Work(**work)
            try:
                existing = Work.objects.get(identifier='AV_%s' % MUYA_works_data[entry]['abbreviation'])
                w.id = existing.id
            except:
                pass
            collection = Collection.objects.get(identifier='AV')
            w.collection = collection
            w.save()

            for language in ['AE']:

                structure = {
                    'abbreviation': MUYA_works_data[entry]['abbreviation'],
                    'total_chapters': MUYA_works_data[entry]['total_chapters'],
                    'verses_per_chapter': MUYA_works_data[entry]['verses_per_chapter'],
                    'position_in_corpus': MUYA_works_data[entry]['book_number']
                }

                s = Structure(**structure)
                s.work = w
                corpus = Corpus.objects.get(identifier='AV_%s' % language)
                s.corpus = corpus
                existing = Structure.objects.filter(corpus__identifier='AV_%s' % language, work__identifier='AV_%s' % MUYA_works_data[entry]['abbreviation'])
                if len(existing) == 1:
                    s.id = existing[0].id
                else:
                    pass
                s.save()
