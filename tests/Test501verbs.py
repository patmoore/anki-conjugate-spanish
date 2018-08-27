# -*- coding: utf-8 -*-
import unittest
import sys
from conjugate_spanish import Tense, Person, Verb
import io
import csv
from conjugate_spanish.espanol_dictionary import Espanol_Dictionary, Verb_Dictionary
from conjugate_spanish.constants import get_iterable
from conjugate_spanish.standard_endings import Infinitive_Ending
from conjugate_spanish.conjugation_override import Standard_Overrides
MASTER_DIR = './conjugate_spanish/expanded'
Espanol_Dictionary.load()

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.DictReader(unicode_csv_data,
                            dialect=dialect, **kwargs)
    return csv_reader

class Test501verbs(unittest.TestCase):
    def __check(self, verb_string, expected, tenses=Tense.all(), persons=Person.all()):
        verb = Verb_Dictionary.get(verb_string)
        if verb is None:
            raise Exception(verb_string+": no verb")
        errors = {}
        for tense in get_iterable(tenses):
            if tense in Tense.Person_Agnostic():
                key = repr(tense)
                expected_conjugation = expected[key] if expected[key] != '' else None
                conjugation = verb.conjugate(tense, returnAsString=True)
                if expected_conjugation != conjugation:
                    errors[key] = {'expected':expected_conjugation, 'actual':conjugation}
            else:
                for person in get_iterable(persons):
                    key = repr(tense)+'_'+repr(person)
                    expected_conjugation = expected[key] if expected[key] != '' else None
                    conjugation = verb.conjugate(tense,person, returnAsString=True)
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
        with io.open(MASTER_DIR+'/'+source+"-verbs-only.csv", mode='r', encoding="utf-8" ) as csvfile:
            reader = unicode_csv_reader(csvfile, skipinitialspace=True)
            for expected in reader:
                errors = self.__check(expected['full_phrase'], expected)
                if errors is not None:
                    verbs_errors[expected['full_phrase']] = errors                    
        return verbs_errors
    
    def test_a_verb(self):
        source='501verbs'
        verb_string = 'colgar'
        with io.open(MASTER_DIR+'/'+source+"-verbs-only.csv", mode='r', encoding="utf-8" ) as csvfile:
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
#             with io.open(MASTER_DIR+u'/'+source+u"-verbs-only.csv", mode='r', encoding="utf-8" ) as csvfile:
#                 reader = unicode_csv_reader(csvfile, skipinitialspace=True)
#                 for expected in reader:
#                     print(u"\tTesting "+expected['full_phrase'])
#                     errors = self.__check(expected['full_phrase'], expected, Tense.imperative_positive, Person.second_person_plural)
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