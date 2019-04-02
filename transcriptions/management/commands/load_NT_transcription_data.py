import os
import re
import json
from lxml import etree
from django.core.management.base import BaseCommand, CommandError
from transcriptions.transcript_parser import TEIParser
from transcriptions.transcript_parser import LectionaryParser

from transcriptions.models import Work
from transcriptions.models import Transcription
from transcriptions.models import Verse
from transcriptions.models import VerseReading
from transcriptions.models import Corpus


COLLECTION = 'NT'

class Command(BaseCommand):

    def add_transcription_to_database(self, filename, language, collection):
        """Add TEI XML file to the database."""
        print("")
        print("Trying %s" % filename)

        m = re.search('/\d+_([^/]*)\.xml$', filename)

        if m:
            try:
                siglum =  m.group(1)
            except IndexError:
                siglum = None

        document_type = 'unknown'
        if language == 'grc' and siglum:
            indicator = siglum[0]
            if indicator == 'P':
                document_type = 'papyrus'
            elif indicator == 'L':
                document_type = 'lectionary'
            elif indicator == '0':
                document_type = 'majuscule'
            elif re.match('[1-9]', indicator):
                document_type = 'minuscule'

        file_string = open(filename, mode='r', encoding='utf-8').read()
        file_string = file_string.replace("<?xml version='1.0' encoding='utf-8'?>", '')
        #TODO: sort out corpus/collection in the Parser once everything settles down
        if document_type == 'lectionary':
            xml_parser = LectionaryParser(file_string, filename=filename, corpus=collection, document_type=document_type, private=False)
        else:
            xml_parser = TEIParser(file_string, filename=filename, corpus=collection, document_type=document_type, private=False)

        data, private = xml_parser.get_data() #returns a tuple
        siglum = data['transcription']['siglum']

        #TODO: this needs sorting out once we move away from numbers in all systems
        work_id = data['transcription']['work_id']
        book_number = int(work_id.replace('NT_B', ''))
        works = Work.objects.all().filter(collection__abbreviation=collection, sort_value=book_number)
        if len(works) == 1:
            work_id = works[0].id
            del data['transcription']['work_id']
            data['transcription']['work'] = works[0]
            new_identifier = '%s_%s_%s_%s' % (data['transcription']['corpus'], data['transcription']['language'].upper(), data['transcription']['siglum'], works[0].abbreviation)
            print(new_identifier)
            data['transcription']['identifier'] = new_identifier
        else:
            raise


        #TODO: find all transcriptions that match, delete all verses for that transcription
        #make sure you save the existing transcription over the current one (we shouldn't need to delete the transcription just overwrite it)


        print('loading new data')
        current_transcription = Transcription.objects.all().filter(siglum=siglum, language=language, work=work_id)
        if current_transcription.count() > 1:
            raise
        else:
            if current_transcription.count() == 1:
                current_id = current_transcription[0].id
                verses = Verse.objects.all().filter(transcription_identifier=data['transcription']['identifier'])
                verses.delete()
                #TODO: verse_reading also needs deleting - might need model updating too
                data['transcription']['id'] = current_id
            data['transcription']['loading_complete'] = False
            data['transcription']['public'] = True
            corpus = Corpus.objects.all().filter(language=language, collection__abbreviation=collection)
            if len(corpus) == 1:
                data['transcription']['corpus'] = corpus[0]
            else:
                raise


            transcription_object = Transcription(**data['transcription'])
            transcription_object.save()
            for v in data['verses']:
                if 'plain_text' in v:
                    plain_text = v['plain_text']
                    del v['plain_text']
                else:
                    plain_text = []
                v['public'] = True
                v['transcription'] = transcription_object
                del v['transcription_id']
                v['transcription_identifier'] = transcription_object.identifier
                v['work'] = data['transcription']['work']
                del v['work_id']

                if 'duplicate_position' in v:
                    identifier_siglum = '%s-%d' % (v['transcription_siglum'], v['duplicate_position'])
                else:
                    identifier_siglum = v['transcription_siglum']
                if 'incipit' in v and v['incipit'] == True:
                    v['inscriptio'] = True
                    del v['incipit']
                    new_verse_identifier = '%s_%s_%s_%s.inscriptio' % ( collection, v['language'].upper(), identifier_siglum, v['work'].abbreviation)
                    new_context = '%s.inscriptio' % (v['work'].abbreviation)
                elif 'explicit' in v and v['explicit'] == True:
                    v['subscriptio'] = True
                    del v['explicit']
                    new_verse_identifier = '%s_%s_%s_%s.subscriptio' % ( collection, v['language'].upper(), identifier_siglum, v['work'].abbreviation)
                    new_context = '%s.subscriptio' % (v['work'].abbreviation)
                else:
                    new_verse_identifier = '%s_%s_%s_%s.%d.%d' % ( collection, v['language'].upper(), identifier_siglum, v['work'].abbreviation, v['chapter_number'], v['verse_number'])
                    new_context = '%s.%d.%d' % (v['work'].abbreviation, v['chapter_number'], v['verse_number'])

                v['identifier'] = new_verse_identifier
                
                v['context'] = new_context
                verse_object = Verse(**v)
                verse_object.save()
                for plain_text_reading in plain_text:
                    del plain_text_reading['id']
                    plain_text_reading['verse'] = verse_object
                    versereading_object = VerseReading(**plain_text_reading)
                    versereading_object.save()
            transcription_object.loading_complete = True
            transcription_object.save()



    def add_arguments(self, parser):
        parser.add_argument('location', type=str)
        parser.add_argument('language', type=str)
        parser.add_argument( '--corpus', action='store', dest='corpus', help='The corpus the transcription/s should be assigned to.')

    def handle(self, *args, **options):
        location = options['location']
        language = options['language']
        if options['corpus']:
            corpus = options['corpus']
        else:
            corpus = COLLECTION
        if os.path.isfile(location):
            self.add_transcription_to_database(location, language, corpus)
        else:
            for root, directory, files in os.walk(location):
                for filename in files:
                    if filename.endswith('.xml'):
                        self.add_transcription_to_database(os.path.join(root, filename), language, corpus)
