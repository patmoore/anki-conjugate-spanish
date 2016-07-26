# -*- coding: utf-8 -*-
import unittest
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary
from conjugate_spanish.constants import Vowels

class TestBasic(unittest.TestCase):
    """
    Tests to make sure the parts of the verb are parsed out correctly
    """
    def __check(self, verb, stem, inf_ending, prefix_words="", prefix="", reflexive=False, suffix_words="", is_phrase=False):
        self.assertEqual(verb.prefix_words, prefix_words)
        self.assertEqual(verb.prefix, prefix)
        self.assertEqual(verb.stem, stem)
        self.assertEqual(verb.inf_ending, inf_ending)
        self.assertEqual(verb.reflexive, reflexive)
        self.assertEqual(verb.suffix_words, suffix_words)
        self.assertEqual(verb.is_phrase, is_phrase)
        if not is_phrase:
            if reflexive:
                self.assertEqual(verb.full_phrase, stem+inf_ending+'se')
            else:
                self.assertEqual(verb.full_phrase, stem+inf_ending)
        
    def test_self_reference(self):
        verb = Verb("faketer", "fake as always")
        self.assertNotEqual(verb, verb.base_verb)
        self.assertEqual(verb.base_verb_str, None)
        self.__check(verb, "faket", "er")
        
    def test_simple_parsing(self):
        verb = Verb("faketer"," fake definition")
        self.assertFalse(verb.is_phrase)
        self.assertEqual(verb.base_verb_str, None)
        self.assertEqual(verb.full_phrase, "faketer")
        self.__check(verb, "faket", "er")
        
    def test_reflexive_parsing(self):
        verb = Verb("faketerse"," fake definition")
        self.__check(verb, "faket", "er", reflexive=True)
        self.assertEqual(verb.base_verb_str, "faketer")
        verb = Verb("faketer-se"," fake definition")
        self.__check(verb, "faket", "er", reflexive=True)
        self.assertEqual(verb.base_verb_str, "faketer")
        self.assertEqual(verb.full_phrase, "faketerse")
        
    def test_base_verb_parsing(self):
        verb = Verb("abs-faketer-se"," fake definition")
        self.__check(verb, "absfaket", "er", prefix="abs", reflexive=True)
        self.assertEqual(verb.base_verb_str, "faketer")
        self.assertEqual(verb.inf_verb_string, "absfaketer")
        self.assertEqual(verb.full_phrase, "absfaketerse")
        
    def test_phrase_parsing(self):
        # also test for excess spaces and leading spaces
        verb = Verb("  a  absfaketer  de {{inf}}  "," fake definition")
        self.__check(verb, "absfaket", "er", prefix="", reflexive=False, prefix_words="a", suffix_words="de {{inf}}", is_phrase=True)
        self.assertEqual(verb.base_verb_str, "absfaketer")
        self.assertEqual(verb.inf_verb_string, "absfaketer")
        self.assertEqual(verb.full_phrase, "a absfaketer de {{inf}}")

    def test_explicit_accent(self):
        """
        Test to make sure that the u in qu is skipped.
        """
        verb = Verb("acercarse","approach,draw near")
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.third_person_singular)
        self.assertEqual(conjugation, 'acérquese')
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.third_person_plural)
        self.assertEqual(conjugation, 'acérquense')
        
    def test_proper_accent(self):
        """
        make sure the o is accented not the i ( i is a weak vowel )
        """
        verb = Verb('divorciarse','')
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.second_person_singular)
        self.assertEqual('divórciate', conjugation)
        
    def test_accenting_rules(self):
        samples = {
            'divorcia' : ['div', 'o','rc','ia'],
            'divorcian' : ['div', 'o','rc','ian'],
            'divourcia' : ['div', 'ou','rc','ia'],
            'ten' : [ 't','e','n', ''],
            'di' : [ 'd','i','',''],
            'rehuso' : ['r','ehu']
        }
        for word,expected in samples.items():
            match = Vowels.find_accented(word)
            l = [i for i in match.groups()]
            self.assertListEqual(expected, l)
        