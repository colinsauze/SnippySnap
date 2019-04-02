"""Parse TEI transcription file.

Parses documents created using IGNTP XML transcription schema"""


from __future__ import print_function

from lxml import etree
from copy import deepcopy
#from magpy.server.utils import get_mag_path
from transcriptions.yasna_word_parser import YasnaWordParser as WordParser
import re
#import six #we will try to do this without six (but it would be nice if it worked on both) I'm removing to try and make it 3 native
import os
import io



W3NS = '{http://www.w3.org/XML/1998/namespace}%s'
ID_STRING = W3NS % 'id'
FORMAT = 'new'
DEFAULT_NSMAP = {None: 'http://www.tei-c.org/ns/1.0'}


class YasnaParser(object):
    """Parse a TEI file."""
    def __init__(self, file_string, filename=None, corpus='', debug=False,
                 manuscript_id=None, siglum=None,
                 lang=None, document_type=None, private=True, user_id=None):

        #parse the file_string into a tree and get the root
        if file_string == None:
            raise ValueError('file_string provided was None')
        else:
            try:
                self.tree = etree.parse(io.BytesIO(file_string))
            except:
                try:
                    self.tree = etree.parse(io.StringIO(file_string))
                except:
                    raise
        self.root = self.tree.getroot()
        self.file_string = file_string

        #set namespace details (required for functions called below)
        self.nsmap = self._check_for_namespace()
        if 'tei' in self.nsmap:
            self.default_ns = 'tei'
        else:
            self.default_ns = None
        self.schema_prefix = self._check_for_schema()

        #set other simple features
        self.corpus = corpus
        self.private = private
        self._debug = debug
        self.user_id = user_id


        if filename is not None:
            self.source = filename
        else :
            self.source = 'Web Upload'
        if document_type:
            self.document_type = document_type
        else:
            self.document_type = 'unknown'

        #self.identifiers = self._get_identifiers()
        self.siglum = self._get_siglum(siglum)
        self.doc_id = self._get_id(manuscript_id)
        try:
            self.lang = self._get_lang(lang)
        except:
            self.lang = 'ae'




    def _get_siglum(self, siglum):
        """Get Siglum for apparatus, if the user did not supply one
        the siglum is the n attribute on the title element
        with the type attribute document.
        """
        if siglum:
            return siglum
        return self.xpath('title[@type="document"]/@n')[0]

    def _get_id(self, manuscript_id):
        """Get document id.

        The doc id is the key attribute on the title element with
        the type attribute document. If there isn't one it defaults to n attribute

        TODO: check with Hugh on Latin and Coptic key values
        """
        if manuscript_id:
            return manuscript_id
        try:
            return self.xpath('title[@type="document"]/@key')[0]
        except:
            return self.xpath('title[@type="document"]/@n')[0]

    def _get_lang(self, lang):
        """Get an element from a page number string."""
        if lang:
            return lang
        return self.xpath('text/@xml:lang')[0].lower()

    def _check_for_namespace(self):
        """If there is an unnamed default namespace,
        call it tei."""
        nsmap = self.root.nsmap
        if None in nsmap:
            nsmap['tei'] = nsmap.pop(None)
        return nsmap

    def _check_for_schema(self):
        """See if the XML file has a schema, and if so what it is."""
        if self.root.nsmap:
            return "{%s}" % self.root.nsmap[None]
        else:
            return ""
    # not needed for MUYA? - and fails because of lac of type attributes
    # def _get_identifiers(self):
    #     """Get all the alt_identifiers."""
    #     target = '//%saltIdentifier' % self.schema_prefix
    #     identifiers = dict((element.get('type').replace('.', ''),
    #                         list(element)[0].text) for
    #                        element in self.tree.findall(target))
    #     #identifiers['_model'] = 'identifier' onlt needed if embedded validation worked and it doesn't
    #     return identifiers

    def xpath(self, path):
        """Evaluate an xpath expression on the transcript.
        For example:
        transcript.xpath('pb[@n="66v"]')
        """
        if self.default_ns:
            path = './/%s:%s' % (self.default_ns, path)
        return self.root.xpath(path, namespaces=self.nsmap)

#
# #     def _get_page_break_element(self,
# #                                 identifier,
# #                                 kill=False):
# #         """Get an element from a page number string."""
# #         return self.xpath('pb[@xml:id="%s"]' % identifier, kill)
#
#     def get_all_chapters(self):
#         """Get out all the chapters from the element tree"""
#         all_chapters = []
#         chapters = self.tree.findall(
#             '//%sdiv[@type="chapter"]' % self.schema_prefix)
#         for chapter in chapters:
#             # Wrap up TEI
#             # May need to add more for fragment to be valid TEI document
#             root = etree.Element("TEI")
#             root.append(chapter)
#             chapter_dict = {}
#             chapter_dict['text'] = etree.tounicode(
#                 root, pretty_print=True)
#             chapter_dict['number'] = int(chapter.attrib['n'])
#             chapter_dict['identifier'] = \
#                 chapter.attrib[W3NS % 'id']
#             all_chapters.append(chapter_dict)
#         return all_chapters
#
#
#     def find_previous_page_break(self, element):
#         """Find the previous page_break before `element`,
#         useful for knowing what page we are on."""
#         element_list = [el for el in self.tree.iter('%spb' % self.schema_prefix, element.tag)]
#         target_found = False
#         for el in reversed(element_list):
#             if target_found:
#                 if el.tag == '%spb' % self.schema_prefix:
#                     return el
#             if el == element:
#                 target_found = True
#         #if we got here we failed to find any
#         raise StopIteration("Failed to find the previous "
#                             "page break of %s" % etree.tounicode(element))
#
#     @staticmethod
#     def safe_remove(element):
#         """
#         Removes this element from the tree, including its children and
#         text.  The tail text is joined to the previous element or
#         parent.
#         """
#         parent = element.getparent()
#         assert parent is not None
#         if element.tail:
#             previous = element.getprevious()
#             if previous is None:
#                 parent.text = (parent.text or '') + element.tail
#             else:
#                 previous.tail = (previous.tail or '') + element.tail
#         parent.remove(element)
#
#     def get_work_identifier(self):
#         """Get Manuscript Name"""
#         target = '//%sdiv[@type="book"]' % self.schema_prefix
#         work_id = self.tree.find(target)
#         xml_id = work_id.get(ID_STRING)
#         number = work_id.get('n')
#         return xml_id, number
#
#     def get_element_text(self, target_template):
#         """Get some text based on the target."""
#         target = '//%s%s' % (self.schema_prefix, target_template)
#         element = self.tree.find(target)
#         try:
#             return element.text
#         except AttributeError:
#             return None
#
#     def get_document_name(self):
#         """Get document name."""
#         return self.get_element_text('title[@type="document"]')
#
#     def get_attribute_from_target(self,
#                                   target_template,
#                                   attribute):
#         """Get attribute."""
#         target = '//%s%s' % (self.schema_prefix, target_template)
#         element = self.tree.find(target)
#         return element.get(attribute)
#
#     def get_document_number(self):
#         """Get Short document Number from TEI subtitle"""
#         return self.get_attribute_from_target('title[@type="document"]', 'n')
#
#     @staticmethod
#     def get_page_number(xml_id):
#         """Get page number."""
#         return xml_id[1:xml_id.find('-')]
#
#     def get_short_work_name(self):
#         """Get Short Work Name from TEI subtitle"""
#         return self.get_element_text('title[@type="short"]')
#
#     def _get_page_info(self, TEI):
#         pb = TEI.xpath('//tei:pb', namespaces=self.nsmap)[0]
#         page_info = {'corpus': self.corpus}
#         page_info['transcription_ids'] = [self.transcription_id]
#         if self.private:
#             page_info['_model'] = 'private_page'
#             page_info['_id'] = '%s_%s_%s_%s_%s' % (self.corpus,
#                                             self.lang.upper(),
#                                             self.doc_id,
#                                             pb.get(ID_STRING),
#                                             self.user_id)
#             if self.siglum:
#                 page_info['siglum'] = '%s_private' % self.siglum
#         else:
#             page_info['_model'] = 'page'
#             page_info['_id'] = '%s_%s_%s_%s' % (self.corpus,
#                                             self.lang.upper(),
#                                             self.doc_id,
#                                             pb.get(ID_STRING))
#             if self.siglum:
#                 page_info['siglum'] = self.siglum
#         verses = []
#         for verse in TEI.xpath('//tei:ab', namespaces=self.nsmap):
#             if verse.get('n') != None:
#                 if self.private:
#                     verses.append('%s_%s_%s_%s_%s' % (self.corpus,
#                                             self.lang.upper(),
#                                             self.siglum,
#                                             verse.get('n'),
#                                             self.user_id))
#                 else:
#                     verses.append('%s_%s_%s_%s' % (self.corpus,
#                                             self.lang.upper(),
#                                             self.siglum,
#                                             verse.get('n')))
#         page_info['verse_ids'] = verses
#         page_info['long_identifier'] = pb.get('n')
#
#         page_info['xmlid'] = pb.get(ID_STRING)
#         page_info['page_type'] = pb.get('type')
#         page_info['tei'] = etree.tounicode(TEI)
#
#         return page_info
#
#     def _create_new_element(self, tag, attributes, text=None):
#         """  """
#         new = etree.Element('{http://www.tei-c.org/ns/1.0}%s' % tag, nsmap=DEFAULT_NSMAP)
#         if attributes != None:
#             for a in attributes:
#                 new.set(a, attributes[a])
#         if text != None:
#             new.text = text
#         return new
#
#     def _append_element(self, element, parent):
#         """ appends provided element to provided parent
#         and returns pointer to element in the resulting tree """
#         parent.append(element)
#         tag = element.tag[element.tag.rfind('}')+1:]
#         if element.get('n') != None:
#             return parent.xpath('//tei:%s[@n="%s"]' % (tag, element.get('n')), namespaces=self.nsmap)[-1]
#         elif element.get('type') != None:
#             return parent.xpath('//tei:%s[@type="%s"]' % (tag, element.get('type')), namespaces=self.nsmap)[-1]
#         else:
#             return parent.xpath('//tei:%s' % tag, namespaces=self.nsmap)[-1]
#
#     def get_all_pages(self):
#         """ Cats way of dealing with getting pages"""
#         #first check we have pages, if not return empty list
#         if len(self.tree.xpath('//tei:pb', namespaces=self.nsmap)) == 0:
#             return []
#
#         xsl_directory = os.path.join(get_mag_path('transcriptions'), 'xsl')
#         flatten_pages_path = os.path.join(xsl_directory, 'flattenPages.xsl')
#         # there used to be a second xslt that tried to merge adjacent things created by the flattening process but this has now been implemented in python
#
#         first_convertor = etree.parse(flatten_pages_path).getroot()
#
#         stage1 = etree.XSLT(first_convertor)
#         result1 = stage1(self.tree)
#         newtree = etree.fromstring(str(result1))
#
#         pages = []
#         TEI = newtree.xpath('//tei:TEI', namespaces=self.nsmap)[0].attrib
#         text = newtree.xpath('//tei:text', namespaces=self.nsmap)[0].attrib
#         body = newtree.xpath('//tei:body', namespaces=self.nsmap)[0].attrib
#         K = None
#         V = None
#         VText = None
#         B = None
#         page = None
#         current = None
#         columnAdded = False
#         lineAdded = False
#         waiting_for_B = False
#         waiting_for_K = False
#         waiting_for_V = False
#
#
#         #need to fix app tags which will have been multiplied unnecessarily
#         current_app = None
#         current_n = None
#         app_contents_in_waiting = []
#         for elem in newtree.xpath('//tei:body', namespaces=self.nsmap)[0].iterchildren():
#             if elem.tag == '%sapp' % self.schema_prefix and elem.get('part') == 'Y':
#                 if current_app == None:
#                     current_app = elem
#                     current_n = elem.get('n')
#                 else:
#                     if elem.get('n') == current_n:
#                         for item in app_contents_in_waiting:
#                             current_app.append(item)
#                             item.getparent().remove(item)
#                             app_contents_in_waiting = []
#                         for child in elem.iterchildren():
#                             current_app.append(child)
#                         elem.getparent().remove(elem)
#                     else:
#                         for item in app_contents_in_waiting:
#                             current_app.append(item)
#                             item.getparent().remove(item)
#                         curent_app = None
#                         current_n = None
#                         app_contents_in_waiting = []
#             elif elem.tag == '%spb' % self.schema_prefix:
#                 #then we want to break the app
#                 for item in app_contents_in_waiting:
#                     current_app.append(item)
#                     item.getparent().remove(item)
#                 current_app = None
#                 current_n = None
#                 app_contents_in_waiting = []
#             elif elem.tag == '%scb' % self.schema_prefix or elem.tag == '%slb' % self.schema_prefix:
#                 if current_app == None:
#                     pass
#                 else:
#                     app_contents_in_waiting.append(elem)
#                     elem.getparent().remove(elem)
#             else:
#                 for item in app_contents_in_waiting:
#                     current_app.append(item)
#                     item.getparent().remove(item)
#                 curent_app = None
#                 current_n = None
#                 app_contents_in_waiting = []
#
#         #need to fix rdg tags which will have been multiplied unnecessarily
#         for app in newtree.xpath('//tei:app', namespaces=self.nsmap):
#             current_rdg = None
#             current_n = None
#             for elem in app.iterchildren():
#                 if elem.tag == '%srdg' % self.schema_prefix and elem.get('part') == 'Y':
#                     if current_rdg == None:
#                         current_rdg = elem
#                         current_n = elem.get('n')
#                     else:
#                         if elem.get('n') == current_n:
#                             for child in elem.iterchildren():
#                                 current_rdg.append(child)
#                             elem.getparent().remove(elem)
#                         else:
#                             current_rdg = None
#                             current_n = None
#
#
#         for elem in newtree.xpath('//tei:body', namespaces=self.nsmap)[0].iterchildren():
#             if elem.tag == '%spb' % self.schema_prefix:
#                 columnAdded = False
#                 lineAdded = False
#                 if page != None:
#                     pages.append(page)
#                 page = etree.fromstring('<TEI xmlns="http://www.tei-c.org/ns/1.0"></TEI>')
#                 if TEI != None:
#                     for a in TEI:
#                         page.xpath('//tei:TEI', namespaces=self.nsmap)[0].set(a, TEI[a])
#                 newtext = self._create_new_element('text', text)
#                 newbody = self._create_new_element('body', body)
#                 newbody.append(elem)
#                 newtext.append(newbody)
#                 page.append(newtext)
#                 current = page.xpath('//tei:body', namespaces=self.nsmap)[0]
#             elif elem.tag == '%scb' % self.schema_prefix:
#                 current.append(elem)
#                 columnAdded = True
#             elif elem.tag == '%slb' % self.schema_prefix:
#                 current.append(elem)
#                 if columnAdded == True and lineAdded == False:
#                     lineAdded = True
#                     if B != None:
#                         current = self._append_element(self._create_new_element('div', B), current)
#                         waiting_for_B = False
#                     else:
#                         waiting_for_B = True
#                     if K != None:
#                         current = self._append_element(self._create_new_element('div', K), current)
#                         waiting_for_K = False
#                     else:
#                         waiting_for_K = True
#                     if V != None:
#                         current = self._append_element(self._create_new_element('ab', V, text=VText), current)
#                         waiting_for_V = False
#                     else:
#                         waiting_for_V = True
#             elif elem.tag == '%sdiv' % self.schema_prefix:
#                 if elem.get('type') == 'book':
#                     B = elem.attrib
#                     if waiting_for_B == True: #this is the first book on the page to add to current
#                         current = self._append_element(self._create_new_element('div', B), current)
#                         waiting_for_B = False
#                     elif lineAdded == True: #this is the second book on the page so reset current to body
#                         current = page.xpath('//tei:body', namespaces=self.nsmap)[-1]
#                         current = self._append_element(self._create_new_element('div', B), current)
#                 else:
#                     K = elem.attrib
#                     if waiting_for_K == True: #this is the first chapter on the page so add to current
#                         current= self._append_element(self._create_new_element('div', K), current)
#                         waiting_for_K = False
#                     elif lineAdded == True: #then this is the second chapter on the page so make sure current is book
#                         current = page.xpath('//tei:div[@type="book"]', namespaces=self.nsmap)[-1]
#                         current= self._append_element(self._create_new_element('div', K), current)
#             elif elem.tag == '%sab' % self.schema_prefix:
#                 V = elem.attrib
#                 VText = elem.tail
#                 if waiting_for_V == True:
#                     newV = self._create_new_element('ab', V, text=VText)
#                     current = self._append_element(newV, current)
#                     waiting_for_V = False
#                 elif lineAdded == True:
#                     current = current.getparent()
#                     newV = self._create_new_element('ab', V, text=VText)
#                     current = self._append_element(newV, current)
#             elif elem.tag == '%sw' % self.schema_prefix:
#                 #we need to join immediate sibling words with same n value together
#                 if current != None:
#                     if len(current) > 0 and current[-1].tag == '%sw' % self.schema_prefix and current[-1].get('n') == elem.get('n') and elem.get('n') != None:
#                         #need to check if there is just text in the current[-1] word
#                         if len(elem) > 0:
#                             for child in elem.iterchildren():
#                                 current[-1].append(child)
#                         else:
#                             if len(current[-1]) > 0:
#                                 if current[-1][-1].tail != None:
#                                     current[-1][-1].tail = current[-1][-1].tail + elem.text
#                                 else:
#                                     current[-1][-1].tail = elem.text
#                             else:
#                                 current[-1].text = current[-1].text + elem.text
#                     else:
#                         current.append(elem)
#             elif elem.tag == '%sapp' % self.schema_prefix and elem.get('part') == 'Y':
#                 app = elem.attrib
#                 newApp = self._create_new_element('app', app)
#                 for el in elem.iterchildren():
#                     if el.tag == '%srdg' % self.schema_prefix and el.get('part') == 'Y':
#                         rdg = el.attrib
#                         newRdg = self._create_new_element('rdg', rdg)
#                         for e in el.iterchildren():
#                             if e.tag == '%sw' % self.schema_prefix:
#                                 if len(newRdg) > 0 and newRdg[-1].tag == '%sw' % self.schema_prefix and newRdg[-1].get('n') == e.get('n') and e.get('n') != None:
#                                     if len(e) > 0:
#                                         for child in e.iterchildren():
#                                             newRdg[-1].append(child)
#                                     else:
#                                         if len(newRdg[-1]) > 0:
#                                             if newRdg[-1][-1].tail != None:
#                                                 newRdg[-1][-1].tail = newRdg[-1][-1].tail + e.text
#                                             else:
#                                                 newRdg[-1][-1].tail = e.text
#                                         else:
#                                             newRdg[-1].text = current[-1].text + e.text
#                                 else:
#                                     newRdg.append(e)
#                             else:
#                                 newRdg.append(e)
#                         newApp.append(newRdg)
#                     else:
#                         newApp.append(el)
#                 current.append(newApp)
#             elif len(elem.xpath('./ancestor::tei:w', namespaces=self.nsmap)) == 0:
#                 if current != None:
#                     current.append(elem)
#
#         pages.append(page)
# #        pages = self._remove_empty_verses(pages)
#         pages = self._fix_part_attributes(pages)
#
#         JSONpages = []
#         previous_page_id = None
#         for page in pages:
#             JSONpage = self._get_page_info(page)
#             if previous_page_id != None:
#                 JSONpage['previous_page'] = previous_page_id
#             previous_page_id = JSONpage['_id']
#             if len(JSONpages) > 0:
#                 JSONpages[-1]['next_page'] = JSONpage['_id']
#             JSONpages.append(JSONpage)
#         return JSONpages
#
# #     def _remove_empty_verses(self, pages):
# #         if len(pages) > 1:
# #             for page in pages:
# #                 for verse in page.xpath('//tei:ab', namespaces=self.nsmap):
# #                     if
# #         return pages
#
#     def _fix_part_attributes(self, pages):
#         #TODO: step through fixing part attributes where necessary and remove n on reading and app and w
#         #have three trees at any given time
#         current = None
#         previous = None
#         next = None
#         xpaths = {'book': '//tei:div[@type="book"]', 'incipit': '//tei:div[@type="incipit"]',
#                   'chapter': '//tei:div[@type="chapter"]', 'explicit': '//tei:div[@type="explicit"]',
#                   'lection': '//tei:div[@type="lection"]', 'verse': '//tei:ab', 'word': '//tei:w[@part]',
#                   'app': '//tei:app[@part]', 'rdg': '//tei:rdg[@part]'}
#         if len(pages) > 1:
#             for i, page in enumerate(pages):
#                 current = page
#                 if i-1 >= 0:
#                     previous = pages[i-1]
#                 else:
#                     previous = None
#                 if i+1 <len(pages):
#                     next = pages[i+1]
#                 else:
#                     next = None
#                 #to keep this easy to understand we are only changing values in current page
#                 # the surrounding pages are just used to look up data
#                 for key in xpaths:
#                     elems = current.xpath(xpaths[key], namespaces=self.nsmap)
#                     if len(elems) > 0:
#                         if elems[0] == elems[-1]:
#                             if self._is_on_page(elems[0], previous, 'end') and self._is_on_page(elems[0], next, 'start'):
#                                 self._set_part(elems[0], 'M')
#                             elif self._is_on_page(elems[0], previous, 'end'):
#                                 self._set_part(elems[0], 'F')
#                             elif self._is_on_page(elems[0], next, 'start'):
#                                 self._set_part(elems[0], 'I')
#                         else:
#                             if self._is_on_page(elems[0], previous, 'end'):
#                                 self._set_part(elems[0], 'F')
#                             if self._is_on_page(elems[-1], next, 'start'):
#                                 self._set_part(elems[-1], 'I')
#             # remove extranious n's from app, rdg and w
#             for page in pages:
#                 elems = page.xpath('//tei:app[@part]|//tei:rdg[@part]|//tei:w[@part]', namespaces=self.nsmap)
#                 for elem in elems:
#                     try:
#                         del elem.attrib['n']
#                     except:
#                         pass
#
#         return pages
#
#     def _set_part(self, elem, value):
#
#         elem.set('part', value)
#         if elem.tag == '%sw' % self.schema_prefix:
#             for e in elem.xpath('.//*[@part]'):
#                 e.set('part', value)
#
#
#     def _is_on_page(self, elem, page, where):
#         if page == None:
#             return False
#         if where == 'end':
#             index = -1
#         else:
#             index = 0
#         if elem.tag == '%sdiv' % self.schema_prefix:
#             if elem.get('type') == 'book':
#                 if len(page.xpath('//tei:div[@type="book"]', namespaces=self.nsmap)) > 0:
#                     hit = page.xpath('//tei:div[@type="book"]', namespaces=self.nsmap)[index]
#                     if elem.get('n') == hit.get('n'):
#                         return True
#                     else:
#                         return False
#                 else:
#                     return False
#             else:
#                 if len(page.xpath('//tei:div[not(@type="book")]', namespaces=self.nsmap)) > 0:
#                     hit = page.xpath('//tei:div[not(@type="book")]', namespaces=self.nsmap)[index]
#                     if elem.get('n') == hit.get('n'):
#                         return True
#                     else:
#                         return False
#                 else:
#                     return False
#         elif elem.tag == '%sab' % self.schema_prefix:
#             if len(page.xpath('//tei:ab', namespaces=self.nsmap)) > 0:
#                 hit = page.xpath('//tei:ab', namespaces=self.nsmap)[index]
#                 if elem.get('n') == hit.get('n'):
#                     return True
#                 else:
#                     return False
#             else:
#                 return False
#         elif elem.tag == '%sw' % self.schema_prefix: #words have part attributes already from xslt so no need to deal with them all
#             if len(page.xpath('//tei:w[@part]', namespaces=self.nsmap)) > 0:
#                 hit = page.xpath('//tei:w[@part]', namespaces=self.nsmap)[index]
#                 if elem.get('n') == hit.get('n'):
#                     return True
#                 else:
#                     return False
#             else:
#                 return False
#         elif elem.tag == '%sapp' % self.schema_prefix: #words have part attributes already from xslt so no need to deal with them all
#             if len(page.xpath('//tei:app[@part]', namespaces=self.nsmap)) > 0:
#                 hit = page.xpath('//tei:app[@part]', namespaces=self.nsmap)[index]
#                 if elem.get('n') == hit.get('n'):
#                     return True
#                 else:
#                     return False
#             else:
#                 return False
#         elif elem.tag == '%srdg' % self.schema_prefix: #words have part attributes already from xslt so no need to deal with them all
#             if len(page.xpath('//tei:rdg[@part]', namespaces=self.nsmap)) > 0:
#                 hit = page.xpath('//tei:rdg[@part]', namespaces=self.nsmap)[index]
#                 if elem.get('n') == hit.get('n'):
#                     return True
#                 else:
#                     return False
#             else:
#                 return False



#     def _get_complex_info(self, target_template):
#         """Get info from within a complex tag."""
#         element = self.tree.find('//%s%s' % (self.schema_prefix,
#                                              target_template))
#         if element is None:
#             return None
#         texts = [item.text for item in element.iter()]
#         for _ in range(texts.count(None)):
#             texts.remove(None)
#         return ' '.join(texts)
#
#     def _create_info_list(self):
#         """Create a list of info."""
#         #info = {'_model': 'info'} only needed if embedded validation worked and it doesn't
#         info = {}
#         info_tags = 'country', 'settlement', 'repository', 'funder', \
#             'textLang', 'origDate', 'origPlace', 'material'
#         info_gen = ((tag, self.get_element_text(tag)) for tag in info_tags)
#         info.update(
#             (key, value) for key, value in info_gen if value is not None)
#         complex_tags = 'respStmt', 'edition', 'publicationStmt', \
#             'condition', 'layout', 'handDesc', 'decoDesc', 'surrogates', \
#             'listBibl', 'projectDesc', 'editorialDecl'
#         complex_gen = ((tag, self._get_complex_info(tag)) for
#                        tag in complex_tags)
#         info.update((key, value) for key, value in complex_gen if
#                     value is not None)
#         return info
#
#     def _get_ms_name(self):
#         """Get long manuscript name."""
#         return self.get_element_text('msName')



    def get_transcription(self):
        """Make transcription object."""
        books = list(set(self.xpath('div[@type="book"]/@n')))
        correctors = None
        if len(self.root.xpath('.//tei:listWit/tei:witness', namespaces=self.nsmap)) > 0:
            correctors = [wit.get(ID_STRING) for wit in self.root.xpath('.//tei:listWit/tei:witness', namespaces=self.nsmap)]
        if len(books) == 1:
            book = books[0]
        else:
            #should raise an error here as this system only supports one book one transcription
            book = ''
        self.book = book
        #we make this for transcription and then overwrite if needed for private_transcription
        transcription = {
            'identifier': '%s_%s_%s_%s' % (self.corpus, self.lang.upper(), self.siglum, self.book),
            'corpus': self.corpus,
            'document_id': self.doc_id,
            'tei': self.file_string,
            'source': self.source,
            'siglum': self.siglum,
            'document_type': self.document_type,
            'language': self.lang,
            'work_id': '%s_%s' % (self.corpus, self.book)
            }
        if correctors != None:
            transcription['corrector_order'] = correctors
        if self.private:
            transcription['siglum'] = '%s_private' % self.siglum
            transcription['identifier'] = '%s_%s_%s_%s_%s' % (self.corpus, self.lang.upper(), self.siglum, self.book, self.user_id)
            transcription['user'] = self.user_id

        self.transcription_id = transcription['identifier'] #used for adding to other models later
        return transcription
#
#     def get_document(self):
#         """Get all the metadata about the document."""
#         manuscript = {
#             'identifiers': self.identifiers,
#             'info': self._create_info_list(),
#             'corpus': self.corpus,
#             }
#         if self.private:
#             manuscript['_model'] = 'private_manuscript'
#             manuscript['_id'] = '%s_%s_%s_%s' % (self.corpus, self.lang.upper(), self.doc_id, self.user_id)
#             if self.siglum:
#                 manuscript['siglum'] = '%s_private' % self.siglum
#         else:
#             manuscript['_model'] = 'manuscript'
#             manuscript['_id'] = '%s_%s_%s' % (self.corpus, self.lang.upper(), self.doc_id)
#             if self.siglum:
#                 manuscript['siglum'] = self.siglum
#         manuscript['transcription_ids'] = [self.transcription_id]
#         long_name = self._get_ms_name()
#         if long_name:
#             manuscript['long_name'] = long_name
#         return manuscript
#
#     def _get_page_for_verse(self,
#                             n_value):
#         """Get page from verse n value."""
#         verse = self.tree.find('.//%sab[@%s="%s"]' % (self.schema_prefix,
#                                                       'n',
#                                                       n_value))
#         try:
#             page_break = self.find_previous_page_break(verse)
#         except StopIteration:
#             # Not on a page
#             return None
#         try:
#             return page_break.attrib[ID_STRING]
#         except:
#             return page_break.attrib['n']
#         return None

#    def get_plain_text(self, ab_element):




    def get_verse_details(self, ab_element, context_info):

        verse_info = {'tei': etree.tounicode(ab_element),
                      'document_type': self.document_type,
                      'document_id': self.doc_id,
                      'work_id': '%s_%s' % (self.corpus, self.book)
                      }

        if context_info in ['incipit', 'explicit']:
            context = context_info
            verse_info[context] = True
            verse_info['reference'] = context
        else:
            #matcher = r'B(?P<book_number>\d+)K(?P<chapter_number>\d+)V(?P<verse_number>\d+)'
            matcher = r'(?P<book>\w+)(?P<chapter_number>\d+).(?P<verse_number>\d+)'
            match_object = re.match(matcher, context_info)
            try:
                info_dict = match_object.groupdict()
            except AttributeError:
                print(("Failed with:", context_info))
                raise
            info_dict['book'] = info_dict['book']
            info_dict['chapter_number'] = int(info_dict['chapter_number'])
            info_dict['verse_number'] = int(info_dict['verse_number'])

            verse_info['chapter_number'] = info_dict['chapter_number']
            verse_info['verse_number'] = info_dict['verse_number']
            context = '%s.%02d.%02d' % (info_dict['book'], info_dict['chapter_number'], info_dict['verse_number'])
            verse_info['reference'] = ab_element.get('n')

        verse_info['context'] = context
        if not ab_element.get(W3NS % 'lang'):
            verse_info['language'] = self.lang
        else:
            verse_info['language'] = ab_element.get(W3NS % 'lang')
        verse_info['identifier'] = '%s_%s_%s_%s' % (self.corpus,
                                             self.lang.upper(),
                                             self.siglum,
                                             context)
        verse_info['transcription_id'] = self.transcription_id
        verse_info['transcription_siglum'] = self.siglum

        if self.siglum:
            verse_info['siglum'] = self.siglum
        # print(verse_info)
        # input()
        return verse_info


    def get_all_verses(self,
                       model='verse', pages=False):
        """Get info about verses from TEI."""

        verse_target = './/%sdiv/%sab' % (self.schema_prefix, self.schema_prefix)
        ab_elements = self.tree.findall(verse_target)

        verses = []

        for index, ab_element in enumerate(ab_elements):

            #basic context data - should never need to be overwritten
            verse_info = {'index': index}
            parent = ab_element.getparent()
            context = None

            if parent.get('type') == 'chapter':
                context = ab_element.get('n')
            elif parent.get('type') == 'incipit':
                context = 'incipit'
            elif parent.get('type') == 'explicit':
                context = 'explicit'
            #add in the more specific xml extracted data
            verse_details = self.get_verse_details(ab_element, context)
            if verse_details == None:
                continue
            else:
                verse_info.update(verse_details)
            #get page details if we asked for them
            if pages:
                page = self._get_page_for_verse(verse_info['n'])
                if page:
                    verse_info['page'] = page
                else:
                    verse_info['note'] = "The verse is not on a page."
                    verse_info['page'] = None

            verses.append(verse_info)
        #check for duplicates
        verses = self.check_duplicate_verses(verses)

        #because we keep changing the sigla and id of verses in cases where we have more than one
        #it is safer to just add the private markers right at the end once we are done with any changes
        #that have to be made
        if self.private:
            for verse in verses:
                if verse['siglum']:
                    verse['siglum'] = '%s_private' % verse['siglum']
                verse['identifier'] = '%s_%s' % (verse['identifier'], self.user_id)
                #I think by using the assigned self.transcription_id I have already sorted this out - check though
                #verse['transcription_id'] = '%s_%s' % (verse['transcription_id'], self.user_id)
        return verses

    def check_duplicate_verses(self, verses):
        multiple_counts = {}
        processed_verse_ids = []
        for verse in verses:
            if verse['identifier'] in processed_verse_ids:
                if verse['identifier'] in multiple_counts.keys():
                    multiple_counts[verse['identifier']] += 1
                else:
                    multiple_counts[verse['identifier']] = 2
                verse['siglum'] = '%s-%s' % (self.siglum, multiple_counts[verse['identifier']])
                verse['duplicate_position'] = multiple_counts[verse['identifier']]
                verse['identifier'] = '%s_%s_%s-%s_%s' % (
                                                        self.corpus,
                                                        self.lang.upper(),
                                                        self.siglum,
                                                        multiple_counts[verse['identifier']],
                                                        verse['context']
                                                        )

            processed_verse_ids.append(verse['identifier'])
        #now check whether we need to add -1 to any of the sigla
        if len(multiple_counts.keys()) > 0:
            for i, verse in enumerate(verses):
                if verse['identifier'] in multiple_counts.keys():
                    verse['identifier'] = '%s_%s_%s-1_%s' % (
                                                            self.corpus,
                                                            self.lang.upper(),
                                                            self.siglum,
                                                            verse['context']
                                                            )
                    verse['siglum'] = '%s-1' % verse['siglum']
                    verse['duplicate_position'] = 1
        return verses
#
#     def _has_columns(self, page):
#         """
#         Count the columns.
#
#         """
#         page_tei_element = etree.fromstring(page['tei'])
#         tree = page_tei_element.getroottree()
#         column_breaks = tree.findall('//%scb' % self.schema_prefix)
#
#         number_of_column_breaks = len(column_breaks)
#         if not number_of_column_breaks:
#             return False
#         else:
#             return True
#
#     def _column_post_process(self, tree):
#         """
#         Count the columns and remove the first column break.
#         """
#         column_breaks = tree.findall('//%scb' % self.schema_prefix)
#         number_of_column_breaks = len(column_breaks)
#
#         if number_of_column_breaks:
#             if number_of_column_breaks == 6:
#                 print(etree.tostring(column_breaks[0]))
#             first_cb = column_breaks[0]
#             self.safe_remove(first_cb)
#             root = tree.getroot()
#             tei = etree.tounicode(root, pretty_print=True)
#             return tei, number_of_column_breaks
#         return None, 0
#
#     def update_html(self, instance):
#         """Create a cached HTML fragment."""
#         tei = instance['tei']
#         number_of_columns = 0
#         columised_page = None
#
#         if self._has_columns(instance):
#             if isinstance(tei, six.text_type):
#                 # This is the old one
#                 #tei_element = etree.fromstring(tei.encode('utf8'))
#                 # This is the new one
#                 tei_element = etree.fromstring(tei)
#             else:
#                 tei_element = etree.fromstring(tei)
#             tree = tei_element.getroottree()
#
#             columised_page, number_of_columns = \
#                 self._column_post_process(tree)
#             if columised_page:
#                 tei = columised_page
#             instance['columns'] = number_of_columns
#
#         try:
#             tei_element = etree.XML(tei)
#         except ValueError:
#             tei_element = etree.XML(tei.encode('utf8'))
#
#         if columised_page:
#             xml_stylesheet = \
#                 '/srv/itsee/apps/xsl/IGNTP-4columns.xsl'
#         else:
#             xml_stylesheet = \
#                 '/srv/itsee/apps/xsl/IGNTP-columns.xsl'
#
#         xslt_root = etree.parse(xml_stylesheet)
#         transform = etree.XSLT(xslt_root)
#         html_string = six.text_type(transform(tei_element))[22:]
#         html_string = convert_spans(html_string, number_of_columns)
#
#         instance['html'] = html_string
#         return instance
#
#     def get_ab_details(self, ab_element):
#         verse_info = {'tei': etree.tounicode(ab_element,
#                                                  pretty_print=True),
#                       'document_type': self.document_type,
#                       'document_id': self.doc_id,
#                       'corpus': self.corpus,}
#         if not ab_element.get(W3NS % 'lang'):
#             verse_info['language'] = self.lang
#         else:
#             verse_info['language'] = ab_element.get(W3NS % 'lang')
#         verse_info['transcription_siglum'] = self.siglum
#         if self.siglum:
#             verse_info['siglum'] = self.siglum
#         return verse_info

    def _get_unique_verses(self, verses):
        references = []
        for verse in verses:
            references.append(verse['reference'])
        return len(set(references))

    def get_data(self):
        """Get all manuscript data."""
        data = {}
        data['transcription'] = self.get_transcription()
#        document = self.get_document()
        verses = self.get_all_verses(pages=False)
        word_parser = WordParser()
        corrector_order = None
        if 'corrector_order' in data['transcription']:
            corrector_order = self.doctor_corrector_order(data['transcription']['corrector_order'])
        for verse in verses:
            verse = word_parser.parse_verse(verse, corrector_order)
#         pages = self.get_all_pages()
#         for page in pages:
#             self.update_html(page)

#        data['manuscript'] = document
        data['verses'] = verses
        data['transcription']['total_verses'] = len(data['verses'])
        data['transcription']['total_unique_verses'] = self._get_unique_verses(data['verses'])
#        data['pages'] = pages
        return (data, self.private)

    def get_data_online(self):
        """Get all manuscript data."""
        data = {}
        data['transcription'] = self.get_transcription()
        # document = self.get_document()
        verses = self.get_all_verses(pages=False)
        # if self.incipit_explicit:
        #     verses.extend(self.get_incipit_explicit())
        word_parser = WordParser()
        corrector_order = None
        if 'corrector_order' in data['transcription']:
            corrector_order = self.doctor_corrector_order(data['transcription']['corrector_order'])
        for verse in verses:
            verse = word_parser.parse_verse(verse, corrector_order)
#         pages = self.get_all_pages()
#         for page in pages:
#             self.update_html(page)
#
#         data['manuscript'] = document
        data['verses'] = verses
        data['transcription']['total_verses'] = len(data['verses'])
        data['transcription']['total_unique_verses'] = self._get_unique_verses(data['verses'])
#         data['pages'] = pages
        return data

    #adds in alt hands which is a specific way of doing things for the ECM
    def doctor_corrector_order(self, corrector_order):
        new_corrector_order = []
        for hand in corrector_order:
            if hand == 'firsthand':
                new_corrector_order.extend(['orig_firsthand', 'corr_firsthand', 'alt_firsthand'])
            else:
                new_corrector_order.extend(['corr_%s' % hand, 'alt_%s' % hand])
        return new_corrector_order




def open_spans(html):
    """Make the column library happy."""
    return html.replace(
        '<span class="colBreak"/>',
        '<span class="colBreak"></span>')


def convert_four(html):
    """Convert four columns."""
    html = html.replace('cssfirstcolumnwidth', '21')
    html = html.replace(
        '<span class="colBreak"/>',
        '</div>\n<div class="gutter" style="display: block; '
        'position: absolute; left: 21%; top: 0px; width: 5%;'
        ' bottom: 0px;"></div><div class="column" style="dis'
        'play: block; position: absolute; left: 26%; top: 0p'
        'x; width: 21%; bottom: 0px;">', 1)

    html = html.replace(
        '<span class="colBreak"/>',
        '</div>\n<div class="gutter" style="display: block; '
        'position: absolute; left: 47%; top: 0px; width:'
        ' 5%; bottom: 0px;"></div><div class="column" st'
        'yle="display: block; position: absolute; left: '
        '52%; top: 0px; width: 21%; bottom: 0px;">', 1)
    html = html.replace(
        '<span class="colBreak"/>',
        '</div>\n<div class="gutter" style="display: block; '
        'position: absolute; left: 73%; top: 0px; width:'
        ' 5%; bottom: 0px;"></div><div class="column" st'
        'yle="display: block; position: absolute; left: '
        '78%; top: 0px; width: 21%; bottom: 0px;">', 1)
    return html


def convert_three(html):
    """Convert three columns."""
    html = html.replace('cssfirstcolumnwidth', '30')
    html = html.replace(
        '<span class="colBreak"/>',
        '</div>\n<div class="gutter" style="display: block; '
        'position: absolute; left: 30%; top: 0px; width:'
        ' 5%; bottom: 0px;"></div><div class="column" st'
        'yle="display: block; position: absolute; left: '
        '35%; top: 0px; width: 30%; bottom: 0px;">', 1)
    html = html.replace(
        '<span class="colBreak"/>',
        '</div>\n<div class="gutter" style="display: block; '
        'position: absolute; left: 65%; top: 0px; width:'
        ' 5%; bottom: 0px;"></div><div class="column" st'
        'yle="display: block; position: absolute; left: '
        '70%; top: 0px; width: 30%; bottom: 0px;">', 1)
    return html


def convert_two(html):
    """Convert two columns."""
    html = html.replace('cssfirstcolumnwidth', '47')
    html = html.replace(
        '<span class="colBreak"/>',
        '</div>\n<div class="gutter" style="display: block; '
        'position: absolute; left: 47%; top: 0px; width:'
        ' 5%; bottom: 0px;"></div><div class="column" st'
        'yle="display: block; position: absolute; left: '
        '52%; top: 0px; width: 47%; bottom: 0px;">', 1)
    return html


def convert_spans(html, number_of_columns):
    """Implement columns ourselves."""
    if number_of_columns == 4:
        return convert_four(html)
    if number_of_columns == 3:
        return convert_three(html)
    if number_of_columns == 2:
        return convert_two(html)
    if number_of_columns == 1:
        return html
    if number_of_columns == 0:
        return html
    print(number_of_columns, "columns")
    assert False, "Too many columns."
