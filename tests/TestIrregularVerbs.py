# -*- coding: utf-8 -*-
import unittest
from conjugate_spanish.espanol_dictionary import Espanol_Dictionary
from conjugate_spanish.constants import Tenses, Persons
Espanol_Dictionary.load()
class TestIrregularVerbs(unittest.TestCase):
    def test_ser(self):
        verb = Espanol_Dictionary.get("ser")
        conjugation = verb.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, "soy")
        
    def test_derived_reflexive(self):
        """
        ducharse - derived from duchar 
        """
        verb = Espanol_Dictionary.get("ducharse")
        conjugation = verb.conjugate(Tenses.incomplete_past_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, "me duchaba")
        
    def test_derived_twice_reflexive(self):
        """
        despedirse - derived from despedir which is derived from pedir
        """
        verb = Espanol_Dictionary.get("despedirse")
        conjugation = verb.conjugate(Tenses.incomplete_past_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, "me despedía")

    def test_derived_twice_reflexive_second_person_plural(self):
        """
        despedirse - derived from despedir which is derived from pedir
        """
        verb = Espanol_Dictionary.get("despedirse")
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.second_person_plural)
        self.assertEqual(conjugation, "despedíos")
        
    def test_correct_accent_derived_ends_in(self):
        """
        despedirse - derived from despedir which is derived from pedir
        """
        verb = Espanol_Dictionary.get("obtener")
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.second_person_singular)
        self.assertEqual(conjugation, "obtén")
        verb = Espanol_Dictionary.get("deshacer")
        conjugation = verb.conjugate(Tenses.imperative_positive, Persons.second_person_singular)
        self.assertEqual(conjugation, "deshaz")