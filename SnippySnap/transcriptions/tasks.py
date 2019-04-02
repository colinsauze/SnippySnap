from celery import shared_task
from lxml import etree
from django.contrib.auth.models import User
from transcriptions import models
from transcriptions.transcript_parser import TEIParser
from transcriptions.transcript_parser import LectionaryParser
from transcriptions.word_parser import WordParser

#TODO: change this so it does not delete the original due to relations in projects etc.
#ln 17 and 22
@shared_task
def index_transcription(xml_string, corpus, document_type=None, tei_parser=None, username=None, transcription_id=None, project_id=None, public_flag=False):

    #delete from appropriate repo
    if not public_flag:
        try:
            #NB this trusts transcription_id to identify the user where required. I think this is okay because of public/private flag
            models.PrivateTranscription.objects.get(identifier=transcription_id).delete()
        except:
            print('no private transcription to delete')
    else:
        try:
            models.Transcription.objects.get(identifier=transcription_id).delete()
        except:
            print('no transcription to delete')
    #now we have deleted everything that needs deleting
    if public_flag == True:
        private_boolean = False
    else:
        private_boolean = True
    source = 'Web upload'
    #if a parser has been specified use it
    if tei_parser:
        if tei_parser == 'TEIParser':
            parser = TEIParser(xml_string, corpus=corpus, filename=source, document_type=document_type.lower(),  private=private_boolean, user_id=username)
        if tei_parser == 'LectionaryParser':
            parser = LectionaryParser(xml_string, corpus=corpus, filename=source, document_type=document_type.lower(),  private=private_boolean, user_id=username)
    #if not make a choice based on document type
    else:
        if document_type == 'lectionary':
            parser = LectionaryParser(xml_string, corpus=corpus, filename=source, document_type=document_type.lower(),  private=private_boolean, user_id=username)
        else:
            parser = TEIParser(xml_string, corpus=corpus, filename=source, document_type=document_type.lower(),  private=private_boolean, user_id=username)
    data = parser.get_data_online()
    user = User.objects.get(username=username)

    print('data processing complete')
    print('loading new data')
    data['transcription']['loading_complete'] = False
    data['transcription']['user'] = user

    transcription_object = models.PrivateTranscription(**data['transcription'])
    transcription_object.save()
    for v in data['verses']:
        v['transcription'] = transcription_object
        v['user'] = user
        del v['transcription_id']
        try:
            del v['plain_text']
        except:
            pass
        verse_object = models.PrivateVerse(**v)

        verse_object.save()
    transcription_object.loading_complete = True
    transcription_object.save()
