#-*- coding: utf-8 -*-
"""Word stripper == this one."""
from __future__ import print_function, unicode_literals

#import six

from lxml import etree
from copy import deepcopy
#from bson.errors import InvalidDocument
import sys
import re
import ast


class YasnaWordParser(object):
    """Parse verses into tokenised witnesses."""
    def __init__(self):
        self.namespace = 'http://www.tei-c.org/ns/1.0'


    def prefix(self, tag):
        """Tag with namespace prefix."""
        return '{%s}%s' % (self.namespace, tag)

    def parse_all_verses(self, model='verse'):
        """Connect to the database."""
#         v_collection = self.database.get_collection(model)
#         if self.search == None:
#             verses = v_collection.find()
#         else:
#             verses = v_collection.find(self.search)
#         for verse in verses:
#             transcription_id = verse['transcription_id']
#             if transcription_id not in self.corrector_order:
#                 self.corrector_order[transcription_id] = []
#                 t_collection = self.database.get_collection('transcription')
#                 transcriptions = t_collection.find({'_id': transcription_id})
#                 for transcription in transcriptions:
#                     if 'corrector_order' in transcription:
#                         self.corrector_order[transcription_id] = transcription['corrector_order']
#
#             new_verse = self.parse_verse(verse, self.corrector_order[transcription_id])
#             if 'witnesses' in new_verse:
#                 try:
#                     v_collection.save(new_verse)
#                 except InvalidDocument:
#                     print(new_verse)
#                     print("Failed on verse %s" % new_verse['_id'])
#                     print(new_verse['witnesses'])
#                 else:
#                     sys.stdout.write(".")

    def get_plain_text(self, processed_readings):
        plain_text_readings = []
        for reading in processed_readings:
            plain_text = []
            #this assumes gaps are unimportant and do not need to be recorded - check this is acceptable
            for token in reading['tokens']:
                if 'expanded' in token:
                    plain_text.append(token['expanded'].replace('_', '').replace('[', '').replace(']', ''))
                else:
                    plain_text.append(token['original'].replace('_', '').replace('[', '').replace(']', ''))
            if len(plain_text) > 0:
                text = ' '.join(plain_text)
            else:
                text = ''
            plain_text_readings.append({'reading_text': text, 'id': reading['id'], 'hand': reading['hand'], 'hand_abbreviation': reading['hand_abbreviation']})
        return plain_text_readings


    def parse_verse(self, verse, corrector_order):
        readings = self.get_readings_from_verse(verse, corrector_order)

        processed_readings = self.walk_readings(readings, verse)
        add = False
        for reading in processed_readings:
            if len(reading['tokens']) > 0:
                add = True
        if add == True:
            verse['witnesses'] = processed_readings
            verse['plain_text'] = self.get_plain_text(processed_readings)
        return verse


    def walk_readings(self, readings, verse):
        """Walk all readings."""
        processed_readings = []
        for reading in readings:
            temp = self.walk_reading(
                reading['tokens'],
                verse,
                reading['id'])
            tokens = temp[0]
            details = {'id': reading['id'],
                       'hand': reading['hand'] if 'hand' in reading else 'firsthand',
                       'hand_abbreviation': reading['hand_abbreviation'] if 'hand_abbreviation' in reading else '*',
                       'tokens': tokens}
            if len(temp) > 1:
                details['gap_reading'] = temp[1]
            processed_readings.append(details)
        return processed_readings

    def flatten_texts(self, elem, expand=True):
        """Flatten texts.

        If `expand` is True then nu superlines and <ex> tag
        contents are expanded.
        """

        ignore = [self.prefix('note'), self.prefix('fw'), self.prefix('seg')]

        if not expand:
            ignore.append(self.prefix('ex'))
        result = [(elem.text or "")]
        for sel in elem:
            if sel.tag not in ignore:
                if sel.tag == self.prefix('supplied'):
                    result.append('[%s]' % (self.flatten_texts(sel)))
                elif sel.tag == self.prefix('unclear'):
                    unclear_text = '%s%s' % \
                        ('_'.join(list(self.flatten_texts(sel))), '_')
                    result.append(unclear_text)
                elif sel.tag == self.prefix('gap'):
                    if re.match('^[0-9]+-?[0-9]*$', sel.get('extent')) != None:
                        gap_text = '[%s]' % sel.get('extent')
                    else:
                        gap_text = '[...]'
                    result.append(gap_text)
                else:
                    result.append(self.flatten_texts(sel))
            result.append(sel.tail or '')
        result = re.sub('\s+', '', ''.join(result))
        if (result.find('][') != -1):
            result = re.sub('(\D)\]\[(\D)', '\g<1>\g<2>', result)

        return result



    def walk_reading(self, reading, verse, name):
        """Walk each reading and process the tokens."""
        textual_gap_units = ['verse', 'chapter']
        tokens = []
        word = None
        gap = False
        gap_only = False
        current_gap_unit = ''
        gap_details = ''
        pc_before = []
        pc_after = []
        counter = 2
        #TODO: this should not be hard coded other projects won't use ab - we should just get the first child of t and use that
        if len(reading.xpath('//tei:ab', namespaces={'tei': self.namespace})) > 0:
            reading = reading.xpath('//tei:ab', namespaces={'tei': self.namespace})[0]
            #for element in reading.getchildren():
            for element in reading.iterdescendants():
                if element.tag == self.prefix('w'):
                    if gap and word:
                        word['gap_after'] = True
                        word['gap_details'] = gap_details
                    if len(pc_after) > 0:
                        word['pc_after'] = ''.join(pc_after)
                        pc_after = []
                    if word:
                        tokens.append(word)
                    word = {
                        'verse': reading.get('n'),
                        'index': str(counter),
                        'reading': name,
                        'siglum': verse['siglum']}
                    counter += 2
                    if gap and word['index'] == '2': # only add gap before if it is the first unit
                        word['gap_before'] = True
                        word['gap_before_details'] = gap_details
                    gap_details = ''
                    current_gap_unit = ''
                    gap = False
                    if len(pc_before) > 0:
                        word['pc_before'] = ''.join(pc_before)
                        pc_before = []
                    if len(element.xpath(
                            './/tei:supplied',
                            namespaces={'tei': self.namespace})) > 0:
                        word['supplied'] = True
                    if len(element.xpath('.//tei:unclear',
                                         namespaces={'tei': self.namespace})) > 0:
                        word['unclear'] = True
                    if len(element.xpath('.//tei:abbr[@type="nomSac"]',
                                         namespaces={'tei': self.namespace})) > 0:
                        word['nomSac'] = True
                    if element.get('lemma', None):
                        word['lemma'] = element.get('lemma')
                    word_text = self.flatten_texts(element, expand=False).strip()
                    word['original'] = word_text
                    if 'lemma' in word.keys():
                        word['rule_match'] = [self.prepare_rule_match(word['lemma'])]
                    else:
                        word['rule_match'] = [self.prepare_rule_match(word_text)]
                    expanded_word = self.flatten_texts(
                        element, expand=True).strip()
                    if expanded_word != word_text:
                        word['expanded'] = expanded_word
                        word['rule_match'].append(
                            self.prepare_rule_match(expanded_word))
                    if 'lemma' in word.keys():
                        word['t'] = self.prepare_t(word['lemma'])
                    else:
                        word['t'] = self.prepare_t(expanded_word)
                elif element.tag == self.prefix('gap'):
                    gap = True
                    #if this is the first in a series of gaps
                    #or the currently stored gap is not textual
                    #or the currently stored gap and this gap are both textual
                    if current_gap_unit == '' \
                            or current_gap_unit not in textual_gap_units \
                            or (current_gap_unit in textual_gap_units \
                                and element.get('unit') in textual_gap_units):
                        if element.get('reason') and element.get('reason').lower() == 'witnessend':
                            gap_details = 'lac witness end'
                        elif element.get('reason') and element.get('reason').lower() == 'lacuna':
                            gap_details = 'lac %s %s' % (element.get('extent'),
                                                     element.get('unit'))
                        elif element.get('reason') and element.get('reason').lower() == 'illegible':
                            gap_details = 'ill %s %s' % (element.get('extent'),
                                                     element.get('unit'))
                        else:
                            gap_details = 'gap %s %s' % (element.get('extent'),
                                                     element.get('unit'))
                        current_gap_unit = element.get('unit')
                elif element.tag == self.prefix('pc'):
                    if not word:
                        pc_before.append(self.flatten_texts(element).strip())
                    else:
                        pc_after.append(self.flatten_texts(element).strip())
                elif element.tag == self.prefix('space'):
                    if not word:
                        pc_before.append('<space of %s %s>' % (element.get('unit'),
                                                      element.get('extent')))
                    else:
                        pc_after.append('<space of %s %s>' % (element.get('unit'),
                                                     element.get('extent')))

            if gap and word:
                word['gap_after'] = True
                word['gap_details'] = gap_details
            elif gap:
                gap_only = True
            if len(pc_before) > 0:
                word['pc_before'] = ''.join(pc_before)
            if len(pc_after) > 0:
                word['pc_after'] = ''.join(pc_after)
            if word:
                tokens.append(word)
        if gap_only:
            return [tokens, gap_details]
        else:
            return [tokens]

    def prepare_rule_match(self, data):
        """Prepare the rule match, remove diairesis and apostrophes and make lowercase."""
        return self.lower_greek(
            data.replace(u'ϊ', u'ι').replace(u'ϊ', u'ι').replace(
                u'ϋ', u'υ').replace(u'ϋ', u'υ')).replace('’', '').replace('\'', '')

    def prepare_t(self, data):
        """prepare the t token by removing various unwanted things
        and lowercasing"""
        data = data.replace(u'ϊ', u'ι').replace(u'ϊ', u'ι').replace(
            u'ϋ', u'υ').replace(u'ϋ', u'υ').replace('’', '').replace('\'', '')
        return self.lower_greek(data.replace('[', '').replace(']', '').replace('_', ''))

    @staticmethod
    def lower_greek(data):
        """Lowercase method that supports final sigma."""
        if len(data) > 0:
            newchars = []
            for char in data:
                newchars.append(char.lower())
            if newchars[-1] == u'σ':
                newchars[-1] = u'ς'
            return ''.join(newchars)
        else:
            return data

    def get_hand_for_reading(self, reading, siglum):
        temp = reading.split('_')
        reading_hand = temp[1]
        reading_type = temp[0]
        private = ''
        if siglum.find('_private') != -1:
            siglum = siglum.replace('_private', '')
            private = '_private'
        if reading_type == 'orig':
            return [siglum, '*', private]
            #hand = '%s*%s' % (siglum, private)
        if reading_type == 'alt':
            return [siglum, '%sA' % self.get_corrector_hand(reading_hand), private]
            #hand = '%s%sA%s' % (siglum, self.get_corrector_hand(reading_hand), private)
        if reading_type == 'altZ':
            return [siglum, 'Z', private]
            #hand = '%sZ%s' % (siglum, private)
        if reading_type == 'corr':
            return [siglum, self.get_corrector_hand(reading_hand), private]
            #hand = '%s%s%s' % (siglum, self.get_corrector_hand(reading_hand), private)
        if reading_type in ['variant', 'editorial']:
            return [siglum, '-%s' % reading_hand, private]
            #hand = '%s-%s%s' % (siglum, reading_hand, private)

        # this should never happen but will
        # highlight things that are not being dealt with
        return [siglum, '-%s-%s' % (reading_type, reading_hand), private]
#             hand = '%s-%s-%s%s' % (siglum,
#                                  reading_type,
#                                  reading_hand, private)
#        return hand

    def get_corrector_hand(self, hand_name):
        if hand_name == 'firsthand':
            return 'C*'
        elif hand_name == 'corrector' or hand_name == 'unspecified':
            return 'C'
        elif hand_name == 'secunda_manu':
            return 'Csm'
        elif hand_name == 'manu_recentissima':
            return 'Csm'
        else:
            return hand_name.replace('corrector', 'C')

#     def get_corrector_hand(self, hand_name, siglum):
#         private = ''
#         if siglum.find('_private') != -1:
#             siglum = siglum.replace('_private', '')
#             private = '_private'
#         if hand_name == 'firsthand':
#             hand = '%sC*%s' % (siglum, private)
#         elif hand_name == 'corrector' or hand_name == 'unspecified':
#             hand = '%sC%s' % (siglum, private)
#         elif hand_name == 'secunda_manu':
#             hand = '%sCsm%s' % (siglum, private)
#         elif hand_name == 'manu_recentissima':
#             hand = '%sCsm%s' % (siglum, private)
#         else:
#             hand = '%s%s%s' % (siglum, hand_name.replace('corrector', 'C'), private)
#         return hand

    def get_readings_from_verse(self, verse, corrector_order):
        """Get the readings."""
        # Remove linebreaks
        tei = verse['tei']
        text = tei.replace(u'\n', u'')
        try:
            tei_element = etree.XML(text)
        except ValueError:
            tei_element = etree.XML(text.encode('utf8'))

        # If there are app tags, split them into readings
        app_tags = tei_element.findall(self.prefix('app'))
        if not app_tags:
            try:
                return [{"id": verse['siglum'],
                         'tokens': tei_element}]
            except KeyError:
                print("Died on verse", verse, tei_element)
                raise

        else:
            hands = []
            for rdg in tei_element.xpath('.//tei:rdg', namespaces={'tei': self.namespace}):
                hand = '%s_%s' % (rdg.get('type'), rdg.get('hand'))
                rdg.set('siglum', hand)
                hands.append(hand)
            hands = list(set(hands))
            compiled_readings = {}
            for z, app in enumerate(app_tags):
                # Pull out the readings
                # For each reading:
                # replace the whole app tag with the contents of the reading
                # name each reading according to the hand
                readings = app.findall(self.prefix('rdg'))
                for hand in hands:
                    found = False
                    if hand in compiled_readings:
                        compiled_reading = compiled_readings[hand]
                    else:
                        compiled_reading = deepcopy(tei_element)
                    try:
                        app_tag = compiled_reading.xpath('//tei:app', namespaces={'tei': self.namespace})[z]
                    except:
                        # TODO give relevant exception type(s)
                        pass
                    else:
                        app_index = compiled_reading.index(app_tag)
                        readings = app.findall(self.prefix('rdg'))
                        try:
                            i = corrector_order.index(hand)
                        except:
                            i = -1
                        while i >= 0 and found == False:
                            for reading in readings:
                                if reading.get('siglum') == corrector_order[i] \
                                        and (corrector_order[i].split('_')[0] != 'alt' \
                                             or hand == corrector_order[i]):
                                    match = reading
                                    found = True
                                    break
                            i -= 1
                        if found == True: #then we have the reading of the hand we are in
                            for i, child in enumerate(match.getchildren()):
                                app_tag.getparent().insert(app_index + 1 + i, deepcopy(child))
                        else:
                            print('no hand found')
                            reading = app_tag.xpath('.//tei:rdg[@type="orig"]', namespaces={'tei': self.namespace})
                            if len(reading) > 0:
                                for i, child in enumerate(reading[0].getchildren()):
                                    app_tag.getparent().insert(app_index + 1 + i, deepcopy(child))
                            else:
                                reading = app_tag.xpath('.//tei:rdg[@type="editorial"]', namespaces={'tei': self.namespace})
                                if len(reading) > 0:
                                    for i, child in enumerate(reading[0].getchildren()):
                                        app_tag.getparent().insert(app_index + 1 + i, deepcopy(child))
                                else:
                                    print(verse['_id'])
                                    print('no reading found')
                        compiled_readings[hand] = compiled_reading

            for hand in compiled_readings.keys():
                apps = compiled_readings[hand].xpath(
                            '//tei:app', namespaces={'tei': self.namespace})
                for app in apps:
                    app.getparent().remove(app)
            return [{"id": ''.join(self.get_hand_for_reading(identifier, verse['siglum'])),
                     'hand': identifier.split('_')[1],
                     'hand_abbreviation': self.get_hand_for_reading(identifier, verse['siglum'])[1],
                     'tokens': tokens} for
                    identifier, tokens in compiled_readings.items()]


#     def parse_ntvmr_readings(self, data, context):
#         json = []
#         document_id = data.get('docid')
#         siglum = data.get('ganum')
#         readings = data.text.split('|')
#         for i in range(0, len(readings), 2):
#             if readings[i] == '':
#                 hand = siglum
#             elif re.match('[1-9]*', readings[i]) != None:
#                 hand = siglum + 'C' + readings[i]
#             else :
#                 hand = siglum + readings[i]
#             text = readings[i+1]
#             json.append({'id': hand, 'tokens': self.walk_ntvmr_reading(text, context, siglum, hand)})
#         return json
#
#     def walk_ntvmr_reading(self, reading_text, context, siglum, hand):
#         tokens = []
#         counter = 2
#         words = []
#         word = []
#         punctuation = [';', '.', '·', ',', ':', '†']
#         temp = re.split('((?:^|\s)\{gap[^}]*?\}(?:$|\s))', reading_text)
#         for t in temp:
#             if re.match('^\s*\{gap[^}]*?\}\s*$', t) != None:
#                 words.append(t.strip())
#             elif t.find('{') == -1:
#                 words.extend(t.replace('][', '').split())
#             else:
#                 for l in t:
#                     if l == ' ' and not inGap:
#                         words.append(''.join(word).replace('][', ''))
#                         word = []
#                     elif l == '{':
#                         word.append(l)
#                         inGap = True
#                     elif l == '}':
#                         word.append(l)
#                         inGap = False
#                     elif not inGap:
#                         word.append(l)
#                 if len(word) > 0:
#                     words.append(''.join(word).replace('][', ''))
#         word = None
#         gap = False
#         gap_details = ''
#         for w in words:
#             if re.match('^\s*\{gap[^}]*?\}\s*$', w) != None:
#                 gap = True
#                 if w.find('witnessEnd') != -1:
#                     gap_details = 'lac witness end'
#                 else:
#                     try:
#                         e = re.search('extent="([^"])"', w)
#                         u = re.search('unit="([^"])"', w)
#                         gap_details = 'lac %s %s' % (e.group(1), u.group(1))
#                     except:
#                         gap_details = 'lac unknown'
#             else:
#                 if word:
#                     tokens.append(word)
#                     word = None
#                 original = w.replace('̅', '')
#                 pc_before = []
#                 pre = True
#                 pc_after = []
#                 post = False
#                 orig = []
#                 for c in original:
#                     if c in punctuation:
#                         if pre:
#                             pc_before.append(c)
#                         elif post:
#                             pc_after.append(c)
#                     else:
#                         orig.append(c)
#                         pre = False
#                         post = True
#                 extags = re.compile('\([^(]\)')
#                 word_text = extags.sub('', ''.join(orig))
#                 word = {'verse': context,
#                          'siglum': siglum,
#                          'reading': hand,
#                          'index': str(counter),
#                          'original': word_text}
#                 word['rule_match'] = [self.prepare_rule_match(word_text)]
#                 expanded_word = ''.join(orig).replace(u'¯', u'ν')
#                 if expanded_word != word_text:
#                     word['expanded'] = expanded_word
#                     word['rule_match'].append(self.prepare_rule_match(expanded_word))
#                 word['t'] = self.prepare_t(expanded_word)
#                 if len(pc_before) > 0:
#                     word['pc_before'] = ''.join(pc_before)
#                 if len(pc_after) > 0:
#                     word['pc_after'] = ''.join(pc_after)
#                 if gap:
#                     word['gap_before'] = True
#                     word['gap_details'] = gap_details
#                 gap_details = ''
#                 gap = False
#                 if '̅' in w:
#                     word['nomSac'] = True
#                 if '_' in w:
#                     word['unclear'] = True
#                 if '[' in w:
#                     word['supplied'] = True
#                 #print(token)
#                 counter += 2
#         if gap and word:
#             word['gap_after'] = True
#             word['gap_details'] = gap_details
#         return tokens


if __name__ == "__main__":
    PARSER = WordParser()
    PARSER.parse_verse(basic_verse = {'context': 'B02K1V1',
                       'book_number': 2,
                       'chapter_number': 1,
                       'verse_number': 1,
                       'siglum': '01',
                        'document_id': '20001'})
