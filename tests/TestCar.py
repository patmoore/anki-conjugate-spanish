# -*- coding: utf-8 -*-
import unittest
from conjugate_spanish.constants import Tense, Person, Reflexive
from conjugate_spanish.vowel import Vowels, WordTokenizer
from conjugate_spanish.verb import Verb

fakacar = Verb.importString("fakacar")
fakacarse = Verb.importString("fakacarse", base_verb=fakacar)
faklcar = Verb.importString("faklcar")
faklcarse = Verb.importString("faklcarse", base_verb=faklcar)
#
# Test -car verbs
class TestCar(unittest.TestCase):
    def test_vowel_car(self):
        self.assertEqual(fakacar.appliedOverrides,["car"])
        conjugation_notes = fakacar.conjugate(Tense.past_tense, Person.first_person_singular)
        self.assertEqual("fakaqué", conjugation_notes.full_conjugation)
    def test_vowel_carse(self):
        self.assertEqual(fakacarse.base_verb.appliedOverrides,["car"])
    def test_consonant_car(self):
        self.assertEqual(faklcar.appliedOverrides,["car"])
        conjugation_notes = faklcar.conjugate(Tense.past_tense, Person.first_person_singular)
        self.assertEqual("faklqué", conjugation_notes.full_conjugation)
    def test_consonant_carse(self):
        self.assertIsNotNone(faklcarse.base_verb_string)
        self.assertEqual(faklcarse.base_verb.appliedOverrides,["car"])


