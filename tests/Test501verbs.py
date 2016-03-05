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
#     return csv_reader
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
    def __check(self, verb, stem, inf_ending, prefix_words=u"", prefix=u"", reflexive=False, suffix_words=u"", is_phrase=False):
        self.assertEqual(verb.prefix_words, prefix_words)
        self.assertEqual(verb.prefix, prefix)
        self.assertEqual(verb.stem, stem)
        self.assertEqual(verb.inf_ending, inf_ending)
        self.assertEqual(verb.reflexive, reflexive)
        self.assertEqual(verb.suffix_words, suffix_words)
        self.assertEqual(verb.is_phrase, is_phrase)
        if not is_phrase:
            if reflexive:
                self.assertEqual(verb.full_phrase, stem+inf_ending+u'se')
            else:
                self.assertEqual(verb.full_phrase, stem+inf_ending)
        
    def test_all_verbs(self):
        source=u'501verbs'
        with codecs.open('./conjugate_spanish/expanded/'+source+"-verbs-only.csv", mode='rb', encoding="utf-8" ) as csvfile:
            reader = unicode_csv_reader(csvfile, skipinitialspace=True)
            for line in reader:
                verb = Verb_Dictionary_get(line['full_phrase'])
                for tense in Tenses.all_except(Tenses.Person_Agnostic):
                    for person in Persons.all:
                        key = Tenses[tense]+u'_'+Persons[person]
                        expected = line[key] if line[key] != u'' else None
                        conjugation = verb.conjugate(tense,person)
                        self.assertEqual(conjugation, expected)