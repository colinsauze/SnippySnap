"""Handlers for transcriptions."""

from functools import partial
import json
import re
import os
import base64
from urllib import unquote
#for python3 needs to be from urllub.parse import unquote

from lxml import etree

from magpy.server.utils import get_mag_path
import tornado.web
import requests
from bson import json_util
from transcriptions.transcriptparser import TEIParser
from transcriptions.transcriptparser import LectionaryParser
from transcriptions.words import WordParser
from magpy.server.auth import AuthenticationMixin, WhoAmIMixin, \
    permission_required
from magpy.server.database import DatabaseMixin, ValidationMixin
from magpy.server.instances import InstanceLoader

class ValidationHandler(tornado.web.RequestHandler,
                          DatabaseMixin,
                          AuthenticationMixin,
                          ValidationMixin,
                          WhoAmIMixin):
    
    def process_error_log(self, log):
        errors = []
        for i in range(0, len(log)):
            error = str(log[i])
            error = error.replace('<string>:', 'Error in line ').replace('{http://www.tei-c.org/ns/1.0}', '').replace('0:ERROR:SCHEMASV:SCHEMAV_ELEMENT_CONTENT:', '')
            errors.append(error)
        return errors
    
    
    @tornado.web.asynchronous
    def post(self):
        filename = self.get_argument('file_name', None)
        base64file = self.get_argument('src', None)
        if base64file != None:
            meta, content = base64file.split(',', 1)
            ext_m = re.match("data:.*?/(.*?);base64", meta)
            if not ext_m:
                raise ValueError("Can't parse base64 file data ({})".format(meta))
            real_content = base64.b64decode(content)
        else:
            real_content = self.get_argument('xml', None)
            real_content = unquote(real_content)
        try:
            tree = etree.fromstring(real_content);
        except:
            raise tornado.web.HTTPError(415, "the file was not well formed xml")
         
        #now validate against our schema
        schema_directory = os.path.join(get_mag_path('transcriptions'), 'schema')
        schema = etree.XMLSchema(etree.parse(os.path.join(schema_directory, 'TEI-NTMSS.xsd')))

        result = schema.validate(tree)
        log = schema.error_log
        results = {}
        if result == False:
            results['valid'] = False
            results['errors'] = self.process_error_log(log)    
            results['filename'] = filename
        else:
            results['valid'] = True
            results['filename'] = filename
            
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(results))
        self.finish()


#TODO: finish validation checks (working for delete need to be added for create)

class TranscriptionIndexHandler(tornado.web.RequestHandler,
                          DatabaseMixin,
                          AuthenticationMixin,
                          ValidationMixin,
                          WhoAmIMixin):

    @tornado.web.asynchronous
    def post(self):       
        base64file = self.get_argument('src', None)
        if base64file != None:
            meta, content = base64file.split(',', 1)
            ext_m = re.match("data:.*?/(.*?);base64", meta)
            if not ext_m:
                raise ValueError("Can't parse base64 file data ({})".format(meta))
            xml_string = base64.b64decode(content)
        else:
            xml_string = self.get_argument('xml', None)
            xml_string = unquote(xml_string)
        try:
            tree = etree.fromstring(xml_string)
        except:
            raise tornado.web.HTTPError(415, "the file was not well formed xml")
        
        #now validate against our schema
        schema_directory = os.path.join(get_mag_path('transcriptions'), 'schema')
        schema = etree.XMLSchema(etree.parse(os.path.join(schema_directory, 'TEI-NTMSS.xsd')))
        result = schema.validate(tree)

        if result == False:
            raise tornado.web.HTTPError(415, "the file did not validate with the TEI-NTMSS schema")
        
        #else we have a valid XML file so we can continue to indexing
        
        project_id = self.get_argument('project_id', None) 
        book = tree.xpath('//tei:div[@type="book"]/@n', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        corpus = self.get_argument('corpus', None)
        transcription_id = self.get_argument('transcription_id', None)
        transcription_id_created = False
        if transcription_id is None:
            siglum = tree.xpath('//tei:title[@type="document"]/@n', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
            language = tree.xpath('//tei:text/@xml:lang', namespaces={'tei': 'http://www.tei-c.org/ns/1.0', 
                                                                      'xml': 'http://www.w3.org/XML/1998/namespace'})[0]                                                                                                                
            transcription_id = '%s_%s_%s_%s' % (corpus.upper(), language.upper(), siglum, book)
            transcription_id_created = True
            
        public_flag = self.get_argument('public', None)
        if not public_flag:
            public_flag = False
        elif public_flag == 'true':
            public_flag = True
        else:
            public_flag = False
        if corpus is None:
            corpus = 'unknown'    
        
        self.get_user(transcription_id, project_id, corpus.upper(), xml_string, public_flag, book, transcription_id_created)

    @tornado.web.asynchronous
    def get_user(self, transcription_id, project_id, corpus, xml_string, public_flag, book, transcription_id_created):
        success = partial(self.get_projects, 
                          transcription_id=transcription_id,
                          project_id=project_id,
                          corpus=corpus,
                          xml_string=xml_string,
                          public_flag=public_flag,
                          book=book,
                          transcription_id_created=transcription_id_created)
        return self.who_am_i(success)
    
    #add in a check for project
    def get_projects(self, user, error, transcription_id, project_id, corpus, xml_string, public_flag, book, transcription_id_created):
        #chose spec based on type
        if public_flag == True:
            spec = {'_id': project_id, 'published_transcription_managers' : {'$in': [user['_id']]}}
        else:
            if transcription_id_created:
                transcription_id = '%s_%s' % (transcription_id, user['_id'])
            spec = {'_id': project_id, 'transcription_managers' : {'$in': [user['_id']]}}
        
        success = partial(self.check_project_permissions,
                          user=user,
                          transcription_id=transcription_id,
                          project_id=project_id,
                          corpus=corpus,
                          xml_string=xml_string,
                          public_flag=public_flag,
                          book=book)
        projects = self.get_collection('editing_project')
        projects.find(spec=spec).to_list(callback=success) 
    
    #check project permissions    
    def check_project_permissions(self, projects, error, user, transcription_id, project_id, corpus, xml_string, public_flag, book):
        #if we are not working in a project just check we can write to private_transcription
        #set public_flag to false just to check - no writing to public if you are not in a project!
        if not project_id:
            public_flag = False
            return self.check_database_permissions(user, transcription_id, corpus, xml_string, public_flag, book)
        #if you are in a project make sure you check public or private permissions as detailed in the project settings
        for project in projects:
            if public_flag == True:
                if 'published_transcription_managers' in project and user['_id'] in project['published_transcription_managers']:
                    if 'witnesses' in project and transcription_id in project['witnesses']:
                        return self.check_database_permissions(user, transcription_id, corpus, xml_string, public_flag, book)  
                    else:
                        raise tornado.web.HTTPError(403, 'this transcription is not listed in the list of witnesses for this project. It must be added to the project before it can be indexed.')
            else:
                if 'transcription_managers' in project and user['_id'] in project['transcription_managers']:
                    print(project['witnesses'])
                    if 'witnesses' in project and transcription_id in project['witnesses']:
                        return self.check_database_permissions(user, transcription_id, corpus, xml_string, public_flag, book)
                    else:
                        raise tornado.web.HTTPError(403, 'this transcription is not listed in the list of witnesses for this project. It must be added to the project before it can be indexed.')
        raise tornado.web.HTTPError(403)
     
    @tornado.web.asynchronous
    def check_database_permissions(self, user, transcription_id, corpus, xml_string, public_flag, book):
        """If the user can delete transcriptions, then go on to delete method below."""
        if public_flag == True:
            permissions = {'transcription': ['delete', 'create'], 'verse': ['delete', 'create'],
                       'page': ['create'], 'manuscript': ['create']}
        else:
            permissions = {'private_transcription': ['delete', 'create'], 'private_verse': ['delete', 'create'],
                       'private_page': ['create'], 'private_manuscript': ['create']}
        
        success = partial(self.get_existing_transcription,
                          user_id = user['_id'],
                          transcription_id = transcription_id,
                          corpus=corpus,
                          xml_string=xml_string,
                          public_flag=public_flag,
                          book=book)
        self.check_permissions(success, permissions=permissions)
    
    def get_existing_transcription(self, permissions_response, user_id, transcription_id, corpus, xml_string, public_flag, book):
        authenticated, missing_permissions = permissions_response
        if authenticated:
            success = partial(self.delete_existing_transcription, 
                               transcription_id=transcription_id,
                               corpus=corpus,
                               xml_string=xml_string,
                               user_id=user_id,
                               public_flag=public_flag,
                               book=book)      
            if public_flag == True:
                spec = {'_id': transcription_id, 'book_string': book}
                coll = self.get_collection('transcription')
                coll.find(spec=spec).to_list(callback=success)
            else:
                spec = {'_id': transcription_id, 'book_string': book, 'user_id': user_id}
                coll = self.get_collection('private_transcription')
                coll.find(spec=spec).to_list(callback=success)
        else:
            raise tornado.web.HTTPError(403, 'missing permissions: %s' % missing_permissions)
        

    def delete_existing_transcription(self, transcriptions, error, user_id, transcription_id, corpus, xml_string, public_flag, book):
        source = self.get_argument('file_location', None)
        if len(transcriptions) > 0:
            source = transcriptions[0]['source']
        callback = partial(self.get_data_from_transcription, 
                                transcription_id=transcription_id,
                                corpus=corpus,
                                xml_string=xml_string,
                                user_id=user_id,
                                public_flag=public_flag,
                                book=book,
                                source=source)      
        if public_flag == True:
            coll = self.get_collection('transcription')
            coll.remove({'_id': transcription_id, 'book_string': book}, callback=callback)
        else:
            coll = self.get_collection('private_transcription')
            coll.remove({'_id': transcription_id, 'book_string': book, 'user': user_id}, callback=callback)

        
    @tornado.web.asynchronous
    def get_data_from_transcription(self, response, error, transcription_id, corpus, xml_string, user_id, public_flag, book, source):
        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        self.set_header('Content-Disposition',  'inline;')
        self.write(transcription_id)
        self.finish()

        document_type = self.get_argument('document_type', None)
        if document_type is None:
            document_type = 'unknown'
            
        if public_flag == True:
            private_boolean = False
        else:
            private_boolean = True
        #if a parser has been specified use it
        tei_parser = self.get_argument('tei_parser', None)
        if tei_parser:
            if tei_parser == 'TEIParser':
                parser = TEIParser(source, corpus, xml_string, document_type=document_type.lower(),  private=private_boolean, user_id=user_id)
            if tei_parser == 'LectionaryParser':
                parser = LectionaryParser(source, corpus, xml_string, document_type=document_type.lower(),  private=private_boolean, user_id=user_id)
        #if not make a choice based on document type
        else:
            if document_type == 'lectionary':
                parser = LectionaryParser(source, corpus, xml_string, document_type=document_type.lower(),  private=private_boolean, user_id=user_id)
            else:
                parser = TEIParser(source, corpus, xml_string, document_type=document_type.lower(),  private=private_boolean, user_id=user_id)
        data = parser.get_data_online()
        siglum = data['manuscript']['siglum']
        self.delete_verses(data, siglum, user_id, public_flag, book)
        
    def delete_verses(self, data, siglum, user_id, public_flag, book):
        callback = partial(self.add_data,
                           data=data,
                           user_id=user_id,
                           public_flag=public_flag,
                           book=book)
        if public_flag == True:
            coll = self.get_collection('verse')
            coll.remove({'siglum': siglum, 'book_string': book}, callback=callback)            
        else:
            coll = self.get_collection('private_verse')
            coll.remove({'siglum': siglum, 'book_string': book, 'user': user_id}, callback=callback)
            
    #TODO: this really should also delete pages if we are going to add pages but we don't use pages at the moment so I am removing the page and MS uploading
    #I don't think the pages are even being created properly
    #this is one to come back too.
        
    #models are embedded in data so this doesn't need to care
    def add_data(self, response, error, data, user_id, public_flag, book):
        loader = InstanceLoader(validation=False)
#         data['manuscript']['user'] = user_id
#         loader.add_instance(data['manuscript'])
#         for page in data['pages']:
#             page['user'] = user_id
#         loader.add_instances(data['pages'])
        for verse in data['verses']:
            verse['user'] = user_id
        loader.add_instances(data['verses'])
        data['transcription']['user'] = user_id
        data['transcription']['identifier_string'] = data['transcription']['_id'].replace('_%s' % user_id, '')
        loader.add_instance(data['transcription'])
        

class GetTranscriptionHandler(tornado.web.RequestHandler,
                          DatabaseMixin):
    
    @tornado.web.asynchronous
    def get(self):
        tid = self.get_argument('id', None)
        callback = partial(self.getTEITranscription)  
        print(tid)
        spec = {'_id': tid}
        coll = self.get_collection('transcription')
        coll.find(spec=spec).to_list(callback=callback)
    
    @tornado.web.asynchronous
    def getTEITranscription(self, transcriptions, error):
        if len(transcriptions) == 0:
            raise tornado.web.HTTPError(404, "Not Found")
        self.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.write(transcriptions[0]['tei'])
        self.finish()
        