# -*- coding: utf-8 -*-
import unittest
import inspect
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get, Verb_Dictionary_add
from conjugate_spanish.conjugation_override import Dependent_Standard_Overrides
from conjugate_spanish.constants import Infinitive_Endings, Persons_Indirect, accent_at

All_Infinitive_Endings= list(Infinitive_Endings)
All_Infinitive_Endings.append(u'ír')
faketener = Verb_Dictionary_add(u'faketener', "fake tener", base_verb=u'tener')
tener = Verb_Dictionary_get(u'tener')
class TestDerivedVerb(unittest.TestCase):
    def test_setup(self):
        tener_ = faketener.base_verb
        self.assertEqual("tener", tener.inf_verb_string)
        self.assertEqual(tener_, tener)
        
    def test_most_tenses(self):
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
            
    def test_imperatives(self):
        conjugations = faketener.conjugate_all_tenses()
        tener_conjugations = tener.conjugate_all_tenses()
        for tense in Tenses.imperative:
            for person in Persons.all_except([Persons.first_person_singular, Persons.second_person_singular]):
                tail = conjugations[tense][person][4:]
                base = tener_conjugations[tense][person]
                self.assertEqual(tail, base, tail+" "+base+":tense="+Tenses[tense]+" person="+Persons[person])
                
            tail = conjugations[Tenses.imperative_positive][Persons.second_person_singular][4:]
#             print repr(tail).decode("unicode-escape") 
            self.assertEqual(u"tén", tail)
