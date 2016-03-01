import unittest
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get, Verb_Dictionary_add
from conjugate_spanish.constants import Infinitive_Endings, Persons_Indirect

class TestBasic(unittest.TestCase):
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
                self.assertEqual(verb.inf_verb_string, stem+inf_ending+u'se')
            else:
                self.assertEqual(verb.inf_verb_string, stem+inf_ending)
            self.assertEqual(verb.inf_verb_string, verb.full_phrase)
        
    def test_self_reference(self):
        verb = Verb("faketer", "fake as always")
        self.assertNotEqual(verb, verb.base_verb)
        self.assertEqual(verb.base_verb_str, None)
        self.__check(verb, u"faket", u"er")
        
    def test_simple_parsing(self):
        verb = Verb(u"faketer",u" fake definition")
        self.assertFalse(verb.is_phrase)
        self.assertEqual(verb.base_verb_str, None)
        self.assertEqual(verb.full_phrase, u"faketer")
        self.__check(verb, u"faket", u"er")
        
    def test_reflexive_parsing(self):
        verb = Verb(u"faketerse"," fake definition")
        self.__check(verb, u"faket", u"er", reflexive=True)
        self.assertEqual(verb.base_verb_str, u"faketer")
        verb = Verb(u"faketer-se"," fake definition")
        self.__check(verb, u"faket", u"er", reflexive=True)
        self.assertEqual(verb.base_verb_str, u"faketer")
        self.assertEqual(verb.full_phrase, u"faketerse")
        
    def test_base_verb_parsing(self):
        verb = Verb(u"abs-faketer-se"," fake definition")
        self.__check(verb, u"absfaket", u"er", prefix=u"abs", reflexive=True)
        self.assertEqual(verb.base_verb_str, u"faketer")
        self.assertEqual(verb.inf_verb_string, u"absfaketerse")
        self.assertEqual(verb.full_phrase, u"absfaketerse")
        
    def test_phrase_parsing(self):
        # also test for excess spaces and leading spaces
        verb = Verb(u"  a  absfaketer  de {{inf}}  "," fake definition")
        self.__check(verb, u"absfaket", u"er", prefix=u"", reflexive=False, prefix_words=u"a", suffix_words=u"de {{inf}}", is_phrase=True)
        self.assertEqual(verb.base_verb_str, u"absfaketer")
        self.assertEqual(verb.inf_verb_string, u"absfaketer")
        self.assertEqual(verb.full_phrase, u"a absfaketer de {{inf}}")
