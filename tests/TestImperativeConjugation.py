# -*- coding: utf-8 -*-
import unittest
import inspect
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary
from conjugate_spanish.conjugation_override import Dependent_Standard_Overrides
from conjugate_spanish.constants import Infinitive_Endings, Persons_Indirect, accent_at

All_Infinitive_Endings= list(Infinitive_Endings)
All_Infinitive_Endings.append(u'ír')
class TestImperativeConjugation(unittest.TestCase):
    def test_second_person_singular(self):
        """
        """
        person = Persons.second_person_singular
        for ending in All_Infinitive_Endings:
            fake = Verb(u'faket'+ending,"a fake verb")
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
            fake = Verb(u'faket'+ending,"a fake verb")
            present_subjective_tense = fake.conjugate(Tenses.present_subjective_tense, person)
            conjugation = fake.conjugate(Tenses.imperative_positive,person)
            self.assertEqual(conjugation, fake.inf_verb_string[:-1]+'d')
            conjugation = fake.conjugate(Tenses.imperative_negative,person)
            self.assertEqual(conjugation, present_subjective_tense)
    
    def test_third_first_person(self):
        for person in [Persons.third_person_plural, Persons.third_person_singular, Persons.first_person_plural]:
            for ending in All_Infinitive_Endings:
                fake = Verb(u'faket'+ending,"a fake verb")
                present_subjective_tense = fake.conjugate(Tenses.present_subjective_tense, person)
                conjugation = fake.conjugate(Tenses.imperative_positive, person)
                self.assertEqual(conjugation, present_subjective_tense)
                conjugation = fake.conjugate(Tenses.imperative_negative,person)
                self.assertEqual(conjugation, present_subjective_tense)
            
    
    def test_reflexive_third_person(self):        
        for person in Persons.third_person:
            for ending in All_Infinitive_Endings:
                fake = Verb(u'faket'+ending+'se',"a fake verb")
                present_subjective_tense = fake.conjugate(Tenses.present_subjective_tense,person)
                conjugation = fake.conjugate(Tenses.imperative_positive,person)
                self.assertEqual(conjugation, accent_at(present_subjective_tense, 3)+Persons_Indirect[person])
                conjugation = fake.conjugate(Tenses.imperative_negative,person)
                self.assertEqual(conjugation, accent_at(present_subjective_tense, 3)+Persons_Indirect[person])
                
        