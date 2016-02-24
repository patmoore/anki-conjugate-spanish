# -*- coding: utf-8 -*-
import unittest
import inspect
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get, Verb_Dictionary_add
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
            conjugations = fake.conjugate_tense(Tenses.imperative_positive)
            self.assertEqual(conjugations[person], present_tense[Persons.third_person_singular])
            conjugations = fake.conjugate_tense(Tenses.imperative_negative)
            self.assertEqual(conjugations[person], present_subjective_tense[person])
            
    def test_second_person_plural(self):
        """
        """
        person = Persons.second_person_plural
        for ending in All_Infinitive_Endings:
            fake = Verb(u'faket'+ending,"a fake verb")
            present_subjective_tense = fake.conjugate_tense(Tenses.present_subjective_tense)
            conjugations = fake.conjugate_tense(Tenses.imperative_positive)
            self.assertEqual(conjugations[person], fake.inf_verb_string[:-1]+'d')
            conjugations = fake.conjugate_tense(Tenses.imperative_negative)
            self.assertEqual(conjugations[person], present_subjective_tense[person])
    
    def test_third_first_person(self):
        for person in [Persons.third_person_plural, Persons.third_person_singular, Persons.first_person_plural]:
            for ending in All_Infinitive_Endings:
                fake = Verb(u'faket'+ending,"a fake verb")
                present_subjective_tense = fake.conjugate_tense(Tenses.present_subjective_tense)
                conjugations = fake.conjugate_tense(Tenses.imperative_positive)
                self.assertEqual(conjugations[person], present_subjective_tense[person])
                conjugations = fake.conjugate_tense(Tenses.imperative_negative)
                self.assertEqual(conjugations[person], present_subjective_tense[person])
            
    
    def test_reflexive_third_person(self):        
        for person in Persons.third_person:
            for ending in All_Infinitive_Endings:
                fake = Verb(u'faket'+ending+'se',"a fake verb")
                present_subjective_tense = fake.conjugate_tense(Tenses.present_subjective_tense)
                conjugations = fake.conjugate_tense(Tenses.imperative_positive)
                self.assertEqual(conjugations[person], accent_at(present_subjective_tense[person], 1)+Persons_Indirect[person])
                conjugations = fake.conjugate_tense(Tenses.imperative_negative)
                self.assertEqual(conjugations[person], accent_at(present_subjective_tense[person], 1)+Persons_Indirect[person])
                
        