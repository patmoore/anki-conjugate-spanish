# -*- coding: utf-8 -*-
import unittest
import inspect
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get, Verb_Dictionary_add, Verb_Dictionary_load
from conjugate_spanish.conjugation_override import Dependent_Standard_Overrides, ConjugationOverride,\
    Radical_Stem_Conjugation_Overrides
Verb_Dictionary_load()
class TestStandardConjugationOverrides(unittest.TestCase):
    def test_gerund_override(self):
        ir = Verb_Dictionary_get(u'ir')
        gerund = ir.conjugate_tense(Tenses.gerund)
        self.assertEqual(gerund, u'yendo', 'ir gerund wrong')
         
    def test_past_part_override(self):
        ir = Verb_Dictionary_get(u'ir')
        for tense in Tenses.past_part_adj:
            pp = ir.conjugate_tense(tense)
            self.assertEqual(pp, u'ido', 'ir past part. wrong')
         
    def test_guir_yo(self):
        distinguir = Verb_Dictionary_get(u'distinguir')
        yo_present = distinguir.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(yo_present, u'distingo', 'guir yo present wrong')
 
    def test_stem_changing_gerund_e2i(self):
        """
        faketir - e:i is explicitly assigned ( fake verb to make it easier to debug ) 
        """
        faketir = Verb("faketir", "", conjugation_overrides="e:i")
#         match = Dependent_Standard_Overrides[u"stem_changing_ir_"+u"e:i"].is_match(faketir)
#         self.assertTrue(match, 'automatch')
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
#         self.assertTrue(fakegir.has_override_applied(u''))
        self.assertIsNotNone(fakegir.conjugation_stems, "fakegir.conjugation_stems")
        gerund = fakegir.conjugate_tense(Tenses.gerund)
        self.assertEqual(gerund, u'fakigiendo', u'e2i gerund wrong='+gerund)
        
    def test_beginning_word_radical_stem_changing_overrides(self):
        """
        """
        oler = Verb(u'oler',"to hear",["o:ue"])
        conjugation = oler.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, u'huelo', "problems with loading manual overrides "+conjugation)
        conjugation = oler.conjugate(Tenses.present_subjective_tense, Persons.first_person_plural)
        self.assertEqual(conjugation, u'olamos', "replacing the beginning vowel back with the infinitive vowel")
     
    def test_that_explicit_override_takes_precedent(self):
        """
        decir is a go verb which must override the default -cir behavior of changing c-> zc
        test to see if a manual override defined as a json object will be correctly applied.
        Make sure for a manual override with None in a override position does not remove a previous override.
        """
        decir = Verb("decir","to say, tell",["go","e:i","-v_cir",
            ConjugationOverride.create_from_json(""u'{"conjugation_stems":{"past":"dij","future":"dir","conditional":"dir"},"conjugations":{"imperative_positive_second":"di"}}')])
        conjugations = decir.conjugate_tense(Tenses.imperative_positive)
        self.assertEqual(conjugations[Persons.second_person_singular], u'di', "problems with loading manual overrides of imperative")
        self.assertEqual(conjugations[Persons.third_person_singular], u'diga', "problems with loading manual overrides of imperative")
        
    def test_go_verb_rules(self):
        """-go verbs:
        in yo present:
        ending stem-consonent -> 'g' +'o' (tener)
        ending stem-vowel -> 'ig' + 'o' (asir)
        ending stem-'c' -> change 'c'->'g' (hacer,decir)
        """
        fakir = Verb(u"fakir", "fake go 1","go")
        conjugation = fakir.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, u"fakgo")
         
        fair = Verb(u"fair", "fake go 1","go")
        conjugation = fair.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, u"faigo")
        
        facer = Verb(u"facer", "fake go 1","go")
        conjugation = facer.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, u"fago")
        
    def test_radical_o2ue__ir_changing(self):
        """
        make sure that the key places of stem changing occur (ir different than er ar verbs)
        """ 
        verb = Verb(u'dormir', u'fake',"o:ue")
        conjugation = verb.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, u'duermo')
        conjugation = verb.conjugate(Tenses.past_tense, Persons.third_person_plural)
        self.assertEqual(conjugation, u'durmieron')
        conjugation = verb.conjugate(Tenses.present_subjective_tense, Persons.first_person_plural)
        self.assertEqual(conjugation, u'durmamos')
        conjugation = verb.conjugate(Tenses.present_subjective_tense, Persons.third_person_plural)
        self.assertEqual(conjugation, u'duerman')
        conjugation = verb.conjugate(Tenses.gerund)
        self.assertEqual(conjugation, u'durmiendo')
        
    def test_uir_verbs(self):
        """ uir verbs have to worry about removing the 'u' before o
        """
        verb = Verb(u'constituir', u"constitute") 
        conjugation = verb.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(u'constituyo', conjugation, u'constituyo !='+conjugation)
