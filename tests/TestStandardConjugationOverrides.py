# -*- coding: utf-8 -*-
import unittest
import inspect
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get, Verb_Dictionary_add
from conjugate_spanish.conjugation_override import Dependent_Standard_Overrides

class TestStandardConjugationOverrides(unittest.TestCase):
    def test_gerund_override(self):
        ir = Verb_Dictionary_get(u'ir')
        gerund = ir.conjugate_tense(Tenses.gerund)
        self.assertEqual(gerund, u'yendo', 'ir gerund wrong')
         
    def test_past_part_override(self):
        ir = Verb_Dictionary_get(u'ir')
        gerund = ir.conjugate_tense(Tenses.past_participle)
        self.assertEqual(gerund, u'ido', 'ir past part. wrong')
         
    def test_guir_yo(self):
        distinguir = Verb_Dictionary_get(u'distinguir')
        yo_present = distinguir.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(yo_present, u'distingo', 'guir yo present wrong')
 
    def test_stem_changing_gerund_e2i(self):
        """
        faketir - e:i is explicitly assigned ( fake verb to make it easier to debug ) 
        """
        faketir = Verb("faketir", "", conjugation_overrides="e:i")
        match = Dependent_Standard_Overrides[u"stem_changing_ir_"+u"e:i"].is_match(faketir)
        self.assertTrue(match, 'automatch')
        self.assertIsNotNone(faketir.conjugation_stems, "faketir.conjugation_stems")
        self.assertTrue(inspect.ismethod(faketir.conjugation_stems[9][0]), "is method")
        self.assertFalse(inspect.isfunction(faketir.conjugation_stems[9][0]), "is function")
        gerund = faketir.conjugate_tense(Tenses.gerund)
        self.assertEqual(gerund, u'fakitiendo', 'e2i gerund wrong')
        
    def test_stem_changing_gerund_implicit_e2i(self):
        """
        fakegir - e:i is implicitly assigned: gir have stem changing by default
        """
        fakegir = Verb(u'fakegir', "")
        conjugation_overrides = fakegir.appliedOverrides
        self.assertIsNotNone(fakegir.conjugation_stems, "fakegir.conjugation_stems")
        gerund = fakegir.conjugate_tense(Tenses.gerund)
        self.assertEqual(gerund, u'fakigiendo', 'e2i gerund wrong')
        
    def test_manual_overrides(self):
        """
        test to see if a manual override defined as a json object will be correctly applied.
        Make sure for a manual override with None in a override position does not remove a previous override.
        """
        oler = Verb_Dictionary_add(u'oler',"to hear","pres_sub_inf",None,'{"conjugation_stems":{"present_except_nosvos":"huel"}}')
        conjugations = oler.conjugate_all_tenses()
        self.assertEqual(conjugations[Tenses.present_tense][Persons.first_person_singular], u'huelo', "problems with loading manual overrides ")
        self.assertEqual(conjugations[Tenses.present_subjective_tense][Persons.first_person_plural], u'olamos', "problems with using predefined overrides with manual overrides")
     
    def test_that_explicit_override_takes_precedent(self):
        """
        decir is a go verb which must override the default -cir behavior of changing c-> zc
        """
        decir = Verb_Dictionary_add("decir","to say, tell","go,e:i,-v_cir",None,'{"conjugation_stems":{"present":["di"],"past":"dij","future":"dir","conditional":"dir"},"conjugations":{"imperative positive":[null, "di"]}}')
        conjugations = decir.conjugate_all_tenses()
        self.assertEqual(conjugations[Tenses.imperative_positive][Persons.second_person_singular], u'di', "problems with loading manual overrides of imperative")
        self.assertEqual(conjugations[Tenses.imperative_positive][Persons.third_person_singular], u'diga', "problems with loading manual overrides of imperative")
