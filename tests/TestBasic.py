# -*- coding: utf-8 -*-
import unittest
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get, Verb_Dictionary_add
from conjugate_spanish.constants import Vowels

class TestBasic(unittest.TestCase):
    """
    Tests to make sure the parts of the verb are parsed out correctly
    """
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
        self.assertEqual(verb.inf_verb_string, u"absfaketer")
        self.assertEqual(verb.full_phrase, u"absfaketerse")
        
    def test_phrase_parsing(self):
        # also test for excess spaces and leading spaces
        verb = Verb(u"  a  absfaketer  de {{inf}}  "," fake definition")
        self.__check(verb, u"absfaket", u"er", prefix=u"", reflexive=False, prefix_words=u"a", suffix_words=u"de {{inf}}", is_phrase=True)
        self.assertEqual(verb.base_verb_str, u"absfaketer")
        self.assertEqual(verb.inf_verb_string, u"absfaketer")
        self.assertEqual(verb.full_phrase, u"a absfaketer de {{inf}}")

    def test_explicit_accent(self):
        """
        Test to make sure that the u in qu is skipped.
        """
        verb = Verb(u"acercarse",u"approach,draw near")
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.third_person_singular)
        self.assertEqual(conjugation, u'acérquese')
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.third_person_plural)
        self.assertEqual(conjugation, u'acérquense')
        
    def test_proper_accent(self):
        """
        make sure the o is accented not the i ( i is a weak vowel )
        """
        verb = Verb(u'divorciarse',u'')
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.second_person_singular)
        self.assertEqual(u'divórciate', conjugation)
        
    def test_accenting_rules(self):
        samples = {
            u'divorcia' : [u'div', u'o',u'rc',u'ia'],
            u'divorcian' : [u'div', u'o',u'rc',u'ian'],
            u'divourcia' : [u'div', u'ou',u'rc',u'ia'],
            u'ten' : [ u't',u'e',u'n', u''],
            u'di' : [ u'd',u'i',u'',u''],
            u'rehuso' : [u'r',u'ehu']
        }
        for word,expected in samples.iteritems():
            match = Vowels.find_accented(word)
            l = [i for i in match.groups()]
            self.assertListEqual(expected, l)
        