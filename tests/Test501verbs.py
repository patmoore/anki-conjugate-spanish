# -*- coding: utf-8 -*-
import unittest
from conjugate_spanish import Tenses, Persons, Verb
import codecs
import csv
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
from conjugate_spanish.constants import Infinitive_Endings, Persons_Indirect,\
    get_iterable
from conjugate_spanish.conjugation_override import Standard_Overrides
MASTER_DIR = './conjugate_spanish/expanded'
Verb_Dictionary.load()

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.DictReader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)

    for row in csv_reader:
        line = {}
        for key,value in row.items():
            line[str(key,'utf-8')] = str(value,'utf-8')
        yield line
        # decode UTF-8 back to Unicode, cell by cell:
#         yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        encoded = line.encode('utf-8')
        yield encoded
        
class Test501verbs(unittest.TestCase):
    def __check(self, verb_string, expected, tenses=Tenses.all, persons=Persons.all):
        verb = Verb_Dictionary.get(verb_string)
        if verb is None:
            raise Exception(verb_string+": no verb")
        errors = {}
        for tense in get_iterable(tenses):
            if tense in Tenses.Person_Agnostic:
                key = Tenses[tense]
                expected_conjugation = expected[key] if expected[key] != '' else None
                conjugation = verb.conjugate(tense)
                if expected_conjugation != conjugation:
                    errors[key] = {'expected':expected_conjugation, 'actual':conjugation}
            else:
                for person in get_iterable(persons):
                    key = Tenses[tense]+'_'+Persons[person]
                    expected_conjugation = expected[key] if expected[key] != '' else None
                    conjugation = verb.conjugate(tense,person)
                    if expected_conjugation != conjugation:
                        errors[key] = {'expected':expected_conjugation, 'actual':conjugation}
        if len(errors) > 0:
            errors['appliedOverrides'] = verb.appliedOverrides
            return errors
           #  self.assertFalse(True, verb.full_phrase+repr(errors))
        else:
            return None
        
    def _check_verbs(self, source):
        verbs_errors = {}
        with codecs.open(MASTER_DIR+'/'+source+"-verbs-only.csv", mode='rb', encoding="utf-8" ) as csvfile:
            reader = unicode_csv_reader(csvfile, skipinitialspace=True)
            for expected in reader:
                errors = self.__check(expected['full_phrase'], expected)
                if errors is not None:
                    verbs_errors[expected['full_phrase']] = errors                    
        return verbs_errors
    
    def test_a_verb(self):
        source='501verbs'
        verb_string = 'colgar'
        with codecs.open(MASTER_DIR+'/'+source+"-verbs-only.csv", mode='rb', encoding="utf-8" ) as csvfile:
            reader = unicode_csv_reader(csvfile, skipinitialspace=True)
            for expected in reader:
                if expected['full_phrase'] == verb_string:
                    errors = self.__check(expected['full_phrase'], expected)
                    if errors is not None:
                        self.assertFalse(True, verb_string+repr(errors))
                    break

#     def test_std_overrides(self):
#         for source in Standard_Overrides.keys():
#             print(u">>>>>>>Testing "+source)
#             source = source.replace(u':',u'2')
#             with codecs.open(MASTER_DIR+u'/'+source+u"-verbs-only.csv", mode='rb', encoding="utf-8" ) as csvfile:
#                 reader = unicode_csv_reader(csvfile, skipinitialspace=True)
#                 for expected in reader:
#                     print(u"\tTesting "+expected['full_phrase'])
#                     errors = self.__check(expected['full_phrase'], expected, Tenses.imperative_positive, Persons.second_person_plural)
#                     if errors is not None:
#                         self.assertFalse(True, expected['full_phrase']+repr(errors))
                        
            

#     def test_regular_verbs(self):
#         source=u'501verbs-regular'
#         verbs_errors = self._check_verbs(source)
#         if len(verbs_errors) > 0:
#             for full_phrase, errors in verbs_errors.iteritems():
#                 print(full_phrase, repr(errors))
#                 
#     def test_irregular_verbs(self):
#         source=u'501verbs-irregular'
#         verbs_errors = self._check_verbs(source)
#         if len(verbs_errors) > 0:
#             for full_phrase, errors in verbs_errors.iteritems():
#                 print(full_phrase, repr(errors))
#                 
#     def test_master_verbs(self):
#         source=u'501verbs-master'
#         verbs_errors = self._check_verbs(source)
#         if len(verbs_errors) > 0:
#             for full_phrase, errors in verbs_errors.iteritems():
#                 print(full_phrase, repr(errors))