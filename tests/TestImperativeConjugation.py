# -*- coding: utf-8 -*-
import unittest
import inspect
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
from conjugate_spanish.conjugation_override import Dependent_Standard_Overrides
from conjugate_spanish.constants import Persons_Indirect
from conjugate_spanish.standard_endings import Infinitive_Endings
from conjugate_spanish.vowel import Vowels

All_Infinitive_Endings= list(Infinitive_Endings)
All_Infinitive_Endings.append('ír')
class TestImperativeConjugation(unittest.TestCase):
    def test_second_person_singular(self):
        """
        """
        person = Persons.second_person_singular
        for ending in All_Infinitive_Endings:
            fake = Verb.importString('faket'+ending.key,"a fake verb")
            present_subjective_tense = fake.conjugate_tense(Tenses.present_subjective_tense)
            present_tense = fake.conjugate_tense(Tenses.present_tense)
            conjugation = fake.conjugate(Tenses.imperative_positive, person)
            self.assertEqual(conjugation, present_tense[Persons.third_person_singular])
            conjugation = fake.conjugate(Tenses.imperative_negative, person)
            self.assertEqual(conjugation, present_subjective_tense[person])
            
    def test_second_person_plural(self):
        """
        """
        person = Persons.second_person_plural
        for ending in All_Infinitive_Endings:
            fake = Verb.importString('faket'+ending.key,"a fake verb")
            present_subjective_tense = fake.conjugate(Tenses.present_subjective_tense, person)
            conjugation = fake.conjugate(Tenses.imperative_positive,person)
            self.assertEqual(conjugation, fake.inf_verb_string[:-1]+'d')
            conjugation = fake.conjugate(Tenses.imperative_negative,person)
            self.assertEqual(conjugation, present_subjective_tense)
    
    def test_third_first_person(self):
        for person in [Persons.third_person_plural, Persons.third_person_singular, Persons.first_person_plural]:
            for ending in All_Infinitive_Endings:
                fake = Verb.importString('faket'+ending.key,"a fake verb")
                present_subjective_tense = fake.conjugate(Tenses.present_subjective_tense, person)
                conjugation = fake.conjugate(Tenses.imperative_positive, person)
                self.assertEqual(conjugation, present_subjective_tense)
                conjugation = fake.conjugate(Tenses.imperative_negative,person)
                self.assertEqual(conjugation, present_subjective_tense)
            
    
    def test_reflexive_third_person(self):        
        for person in Persons.third_person:
            for ending in All_Infinitive_Endings:
                fake = Verb.importString('faket'+ending.key+'se',"a fake verb")
                present_subjective_tense = fake.conjugate(Tenses.present_subjective_tense,person)
                conjugation = fake.conjugate(Tenses.imperative_positive,person)
                self.assertEqual(conjugation, Vowels.accent_at(present_subjective_tense, 3)+Persons_Indirect[person])
                conjugation = fake.conjugate(Tenses.imperative_negative,person)
                self.assertEqual(conjugation, Vowels.accent_at(present_subjective_tense, 3)+Persons_Indirect[person])
                
        