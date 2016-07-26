# -*- coding: utf-8 -*-
import unittest
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary
from conjugate_spanish.constants import Infinitive_Endings, Persons_Indirect

All_Infinitive_Endings= list(Infinitive_Endings)
All_Infinitive_Endings.append('ír')
Verb_Dictionary.load()
#
# complex tener based derivations
#
tener = Verb_Dictionary.get('tener')
# Note: need to add to dictionary in order to do base_string lookup
# TODO : levels of dictionary so we can drop a dictionary
faketener = Verb_Dictionary.add('faketener', "fake tener", base_verb=tener)
faketenerse = Verb_Dictionary.add('faketenerse', "fake tener", base_verb='tener')

# tests double derivatives
# real world example: desacordarse -> acordarse -> acordar
descfaketenerse = Verb_Dictionary.add('descfaketenerse', "fake tener", base_verb=faketenerse)
faketenerse_1 = Verb('faketenerse', "fake tener", base_verb=faketener)

fakeacordar = Verb_Dictionary.add("fakeacordar", "fake acordar", "o:ue")
#derive just because of reflexive/non-reflexive
fakeacordarse = Verb_Dictionary.add("fakeacordarse", "fake acordarse")
descfakeacordarse = Verb_Dictionary.add("descfakeacordarse", "fake acordarse", base_verb=fakeacordarse)

class TestDerivedVerb(unittest.TestCase):
    def test_tener_setup(self):
        tener_ = faketener.base_verb
        self.assertEqual("tener", tener.inf_verb_string)
        self.assertEqual(tener_, tener)                
        self.assertTrue(faketener.is_child(tener_))
        self.assertTrue(faketener.is_child(tener))
        self.assertTrue(faketenerse.is_child(tener_))
        self.assertTrue(faketenerse.is_child(tener))
        self.assertTrue(faketenerse_1.is_child(faketener))
        self.assertTrue(faketenerse_1.is_child(tener_))
        self.assertTrue(faketenerse_1.is_child(tener))
        
    def test_tener_conjugation(self):
        """
        test to make sure that tener is being conjugated correctly
        this tests overriding the stem and conjugation because if this doesn't work the other tests will not work
        """
        conjugation = tener.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual('tengo', conjugation, "Make sure that the override of the first person stem change happens")
        conjugation = tener.conjugate(Tenses.imperative_positive, Persons.second_person_singular)
        self.assertEqual('ten', conjugation, "Make sure that the override of the first person stem change happens")
        conjugation = tener.conjugate(Tenses.imperative_positive, Persons.first_person_plural)
        self.assertEqual('tengamos', conjugation, "Make sure that the override of the first_person_plural stem change happens")
         
    def test_tener_most_tenses_non_reflexive(self):
        """
        all except the imperatives
        """
        conjugations = faketener.conjugate_all_tenses()
        tener_conjugations = tener.conjugate_all_tenses()
        except_tenses = list(Tenses.imperative)
        except_tenses.extend(Tenses.Person_Agnostic)
        most_tenses = Tenses.all_except(except_tenses)        
        for tense in most_tenses:
            for person in Persons.all:
                tail = conjugations[tense][person][4:]
                self.assertEqual(tail, tener_conjugations[tense][person], tail+":tense="+Tenses[tense]+" person="+Persons[person])
                
        for tense in Tenses.Person_Agnostic:
            tail = conjugations[tense][4:]
            self.assertEqual(tail, tener_conjugations[tense], tail+":tense="+Tenses[tense])
            
    def test_tener_most_tenses_reflexive(self):
        """
        all except the imperatives
        """
        tener_conjugations = tener.conjugate_all_tenses()
        except_tenses = list(Tenses.imperative)
        except_tenses.extend(Tenses.Person_Agnostic)
        most_tenses = Tenses.all_except(except_tenses)        
        for tense in most_tenses:
            for person in Persons.all:
                tail = faketenerse.conjugate(tense,person).split(' ')[1][4:]
                self.assertEqual(tail, tener_conjugations[tense][person], tail+":tense="+Tenses[tense]+" person="+Persons[person])
                tail = faketenerse_1.conjugate(tense,person).split(' ')[1][4:]
                self.assertEqual(tail, tener_conjugations[tense][person], tail+":tense="+Tenses[tense]+" person="+Persons[person])
                
        tense = Tenses.gerund             
        tail = faketenerse.conjugate(tense)
        self.assertEqual('faketeniéndose', tail, tail+":tense="+Tenses[tense])
        tail = faketenerse_1.conjugate(tense)
        self.assertEqual('faketeniéndose', tail, tail+":tense="+Tenses[tense])
        
        for tense in Tenses.past_part_adj:             
            tail = faketenerse.conjugate_tense(tense)[4:]
            self.assertEqual(tail, tener_conjugations[tense], tail+":tense="+Tenses[tense])
            tail = faketenerse_1.conjugate_tense(tense)[4:]
            self.assertEqual(tail, tener_conjugations[tense], tail+":tense="+Tenses[tense])

            
    def test_tener_imperatives_non_reflexive(self):
        tener_conjugations = tener.conjugate_all_tenses()
        for tense in Tenses.imperative:
            for person in Persons.all_except([Persons.first_person_singular, Persons.second_person_singular]):
                actual = faketener.conjugate(tense, person)
                tail = actual[4:]
                base = tener_conjugations[tense][person]
                self.assertEqual(tail, base, actual+" "+base+":tense="+Tenses[tense]+" person="+Persons[person])
            actual = faketener.conjugate(Tenses.imperative_positive, Persons.second_person_singular)
            tail = actual[4:]
#             print repr(tail).decode("unicode-escape") 
            self.assertEqual("tén", tail)

    def test_tener_imperatives_reflexive_special_case(self):
        """
        Tests for the case where tener based verbs have 2nd person singular 'ten' as the base ( accents are applied to the 'ten' )
        Also tests the multiple level of derivation case (faketenserse -> faketener -> tener )
        """
        expected_positive = [ None, 'faketente', 'faketéngase', 'faketengámonos', 'faketeneos',  'faketénganse']
        expected_negative = [ None, 'te faketengas', 'faketéngase', 'faketengámonos', 'os faketengáis',  'faketénganse']
        for tense in Tenses.imperative:
            expected = expected_negative if tense == Tenses.imperative_negative else expected_positive
            for person in Persons.all_except([Persons.first_person_singular]):                
                actual = faketenerse.conjugate(tense, person)
                self.assertEqual(expected[person], actual, expected[person]+" != "+actual+":tense="+Tenses[tense]+" person="+Persons[person])
                actual = faketenerse_1.conjugate(tense, person)
                self.assertEqual(expected[person], actual, expected[person]+" != "+actual+":tense="+Tenses[tense]+" person="+Persons[person])

    def test_tener_multiple_ancestors_imperative(self):
        """
        Tests for the case where tener based verbs have 2nd person singular 'ten' as the base ( accents are applied to the 'ten' )
        Also tests the multiple level of derivation case (faketenserse -> faketener -> tener )
        """
        expected_positive = [ None, 'descfaketente', 'descfaketéngase', 'descfaketengámonos', 'descfaketeneos',  'descfaketénganse']
        expected_negative = [ None, 'te descfaketengas', 'descfaketéngase', 'descfaketengámonos', 'os descfaketengáis',  'descfaketénganse']
        for tense in Tenses.imperative:
            expected = expected_negative if tense == Tenses.imperative_negative else expected_positive
            for person in Persons.all_except([Persons.first_person_singular]):                
                actual = descfaketenerse.conjugate(tense, person)
                self.assertEqual(expected[person], actual, expected[person]+" != "+actual+":tense="+Tenses[tense]+" person="+Persons[person])
        
    def test_acordar_multiple_ancestors(self):
        """
        tests the multiple level of derivation case (faketenserse -> faketener -> tener )
        """
        expected_positive = [ None, 'descfakeacuérdate', 'descfakeacuérdese', 'descfakeacordémonos', 'descfakeacordaos',  'descfakeacuérdense']
        expected_negative = [ None, 'te descfakeacuerdes', 'descfakeacuérdese', 'descfakeacordémonos', 'os descfakeacordéis',  'descfakeacuérdense']
        for tense in Tenses.imperative:
            expected = expected_negative if tense == Tenses.imperative_negative else expected_positive
            for person in Persons.all_except([Persons.first_person_singular]):                
                actual = descfakeacordarse.conjugate(tense, person)
                self.assertEqual(expected[person], actual, expected[person]+" != "+actual+":tense="+Tenses[tense]+" person="+Persons[person])
