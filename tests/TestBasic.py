# -*- coding: utf-8 -*-
import unittest
from conjugate_spanish.constants import Tense, Person, Reflexive
from conjugate_spanish.vowel import Vowels
from conjugate_spanish.verb import Verb

class TestBasic(unittest.TestCase):
    """
    Tests to make sure the parts of the verb are parsed out correctly
    """
    def __check(self, verb, stem, inf_ending, prefix_words="", prefix="", reflexive=Reflexive.not_reflexive, suffix_words="", is_phrase=False):
        self.assertEqual(verb.prefix_words, prefix_words)
        self.assertEqual(verb.prefix, prefix)
        self.assertEqual(verb.stem, stem)
        self.assertEqual(verb.inf_ending, inf_ending)
        self.assertEqual(verb.reflexive, reflexive)
        self.assertEqual(verb.suffix_words, suffix_words)
        self.assertEqual(verb.is_phrase, is_phrase)
        if not is_phrase:
            if reflexive != Reflexive.not_reflexive:
                self.assertEqual(verb.full_phrase, stem+inf_ending+'se')
            else:
                self.assertEqual(verb.full_phrase, stem+inf_ending)
            
    def test_self_reference(self):
        """
        Make sure that a verb does not claim itself as its own base_verb - it would cause infinit loops
        """
        verb = Verb.importString("faketer", "fake as always")
        self.assertNotEqual(verb, verb.base_verb)
        self.assertEqual(verb.base_verb_string, None)
        self.__check(verb, "faket", "er")
        
    def test_simple_parsing(self):
        verb = Verb.importString("faketer"," fake definition")
        self.assertFalse(verb.is_phrase)
        self.assertEqual(verb.base_verb_string, None)
        self.assertEqual(verb.root_verb_string, None)
        self.assertEqual(verb.full_phrase, "faketer")
        self.__check(verb, "faket", "er")
        
    def test_reflexive_parsing(self):
        verb = Verb.importString("faketerse"," fake definition")
        self.__check(verb, "faket", "er", reflexive=Reflexive.reflexive)
        self.assertEqual(verb.base_verb_string, "faketer")
        verb = Verb.importString("faketer-se"," fake definition")
        self.__check(verb, "faket", "er", reflexive=Reflexive.base_reflexive)
        self.assertEqual(verb.base_verb_string, "faketerse")
        self.assertEqual(verb.root_verb_string, "faketer")
        self.assertEqual(verb.full_phrase, "faketerse")
        
    def test_base_verb_parsing(self):
        verb = Verb.importString("abs-faketer-se"," fake definition")
        self.__check(verb, "absfaket", "er", prefix="abs", reflexive=Reflexive.base_reflexive)
        self.assertEqual(verb.base_verb_string, "faketerse")
        self.assertEqual(verb.root_verb_string, "faketer")
        self.assertEqual(verb.inf_verb_string, "absfaketer")
        self.assertEqual(verb.full_phrase, "absfaketerse")
        
    def test_phrase_parsing(self):
        # also test for excess spaces and leading spaces
        # also test for cases like 'inter-cambiar'        
        verb = Verb.importString("  a  inter-faketer deber de {{inf}}  "," fake definition")
        self.__check(verb, "interfaket", "er", prefix="inter", reflexive=Reflexive.not_reflexive, prefix_words="a", suffix_words="deber de {{inf}}", is_phrase=True)
        self.assertEqual(verb.base_verb_string, "interfaketer")
        self.assertEqual(verb.root_verb_string, "faketer")
        self.assertEqual(verb.inf_verb_string, "interfaketer")
        self.assertEqual(verb.full_phrase, "a interfaketer deber de {{inf}}")
        
        verb = Verb.importString("  a interfaketer /deber/ en {{inf}}  "," fake definition")
        self.__check(verb, "deb", "er", prefix="", reflexive=Reflexive.not_reflexive, prefix_words="a interfaketer", suffix_words="en {{inf}}", is_phrase=True)
        self.assertEqual(verb.base_verb_string, "deber")
        self.assertEqual(verb.root_verb_string, "deber")
        self.assertEqual(verb.inf_verb_string, "deber")
        self.assertEqual(verb.full_phrase, "a interfaketer deber en {{inf}}")

    def test_explicit_accent(self):
        """
        Test to make sure that the u in qu is skipped.
        """
        verb = Verb.importString("acercarse","approach,draw near")
        conjugation_notes = verb.conjugate(Tense.imperative_positive, Person.third_person_singular)
        self.assertEqual(conjugation_notes.conjugation, 'acérquese')
        conjugation_notes = verb.conjugate(Tense.imperative_positive, Person.third_person_plural)
        self.assertEqual(conjugation_notes.conjugation, 'acérquense')
        
    def test_proper_accent_1(self):
        """
        make sure the o is accented not the i ( i is a weak vowel )
        """
        verb = Verb.importString('divorciarse','')
        self.assertEqual(verb.base_verb_string, "divorciar")
        self.assertEqual(verb.root_verb_string, "divorciar")
        self.assertEqual(verb.inf_verb_string, "divorciar")
        conjugation_notes = verb.conjugate(Tense.imperative_positive, Person.second_person_singular)
        self.assertEqual('divórciate', conjugation_notes.conjugation)
        
    def test_proper_accent_2(self):
        """
        make sure the o is accented not the i ( i is a weak vowel )
        """
        verb = Verb.importString('limpiarse','')
        self.assertEqual(verb.base_verb_string, "limpiar")
        self.assertEqual(verb.root_verb_string, "limpiar")
        self.assertEqual(verb.inf_verb_string, "limpiar")
        conjugation_notes = verb.conjugate(Tense.imperative_positive, Person.second_person_singular)
        self.assertEqual('límpiate', conjugation_notes.conjugation)
        
    def test_proper_accent_3(self):
        """
        make sure the o is accented not the i ( i is a weak vowel )
        """
        verb = Verb.importString('enviar','', conjugation_overrides="iar")
        self.assertEqual(verb.base_verb_string, None)
        self.assertEqual(verb.root_verb_string, "enviar")
        self.assertEqual(verb.inf_verb_string, "enviar")
        conjugation_notes = verb.conjugate(Tense.imperative_positive, Person.second_person_singular)
        self.assertEqual('envía', conjugation_notes.conjugation)
    def test_proper_accent_4(self):
        """
        make sure the o is accented not the i ( i is a weak vowel )
        """
        verb = Verb.importString('erguirse','', conjugation_overrides="e:i")
        self.assertEqual(verb.base_verb_string, "erguir")
        self.assertEqual(verb.root_verb_string, "erguir")
        self.assertEqual(verb.inf_verb_string, "erguirse")
        conjugation_notes = verb.conjugate(Tense.imperative_positive, Person.second_person_singular)
        self.assertEqual('írguete', conjugation_notes.conjugation)
        
    def test_accenting_rules(self):
        samples = {
            'divorcia' : ['div', 'o','rc','ia'],
            'divorcian' : ['div', 'o','rc','ian'],
            'divourcia' : ['div', 'ou','rc','ia'],
            'ten' : [ 't','e','n', ''],
            'di' : [ 'd','i','',''],
            'rehuso' : ['r','ehu','s','o']
        }
        for word,expected in samples.items():
            match = Vowels.find_accented(word)
            l = [i for i in match.groups()]
            self.assertListEqual(expected, l)
        