import unittest
from conjugate_spanish import Tenses, Persons, Verb
import codecs
import csv
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get, Verb_Dictionary_add,Verb_Dictionary_load
from conjugate_spanish.constants import Infinitive_Endings, Persons_Indirect
Verb_Dictionary_load()
def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.DictReader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)

    for row in csv_reader:
        line = {}
        for key,value in row.iteritems():
            line[unicode(key,'utf-8')] = unicode(value,'utf-8')
        yield line
        # decode UTF-8 back to Unicode, cell by cell:
#         yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        encoded = line.encode('utf-8')
        yield encoded
        
class Test501verbs(unittest.TestCase):
    def __check(self, verb_string, expected):
        verb = Verb_Dictionary_get(verb_string)
        errors = {}
        for tense in [Tenses.past_tense]:
            if tense in Tenses.Person_Agnostic:
                key = Tenses[tense]
                expected_conjugation = expected[key] if expected[key] != u'' else None
                conjugation = verb.conjugate(tense)
                if expected_conjugation != conjugation:
                    errors[key] = {'expected':expected_conjugation, 'actual':conjugation}
            else:
                for person in [Persons.third_person_plural]:# Persons.all:
                    key = Tenses[tense]+u'_'+Persons[person]
                    expected_conjugation = expected[key] if expected[key] != u'' else None
                    conjugation = verb.conjugate(tense,person)
                    if expected_conjugation != conjugation:
                        errors[key] = {'expected':expected_conjugation, 'actual':conjugation}
        if len(errors) > 0:
            self.assertFalse(True, verb.full_phrase+repr(errors))
        
    def test_a_verb(self):
        source=u'501verbs'
        verb = u'traer'
        with codecs.open('./tests/'+source+"-verbs-only.csv", mode='rb', encoding="utf-8" ) as csvfile:
            reader = unicode_csv_reader(csvfile, skipinitialspace=True)
            for expected in reader:
                if expected['full_phrase'] == verb:
                    self.__check(expected['full_phrase'], expected)
                    break
                
#     def test_all_verbs(self):
#         source=u'501verbs'
#         with codecs.open('./tests/'+source+"-verbs-only.csv", mode='rb', encoding="utf-8" ) as csvfile:
#             reader = unicode_csv_reader(csvfile, skipinitialspace=True)
#             for expected in reader:
#                 self.__check(expected['full_phrase'], expected)