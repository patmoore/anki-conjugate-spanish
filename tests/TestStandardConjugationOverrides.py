# -*- coding: utf-8 -*-
import unittest
import inspect
from conjugate_spanish import Tenses, Persons, Verb
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
from conjugate_spanish.conjugation_override import Dependent_Standard_Overrides, ConjugationOverride,\
    Radical_Stem_Conjugation_Overrides
# Verb_Dictionary.load()
class TestStandardConjugationOverrides(unittest.TestCase):
    def test_gerund_override(self):
        ir = Verb_Dictionary.get('ir')
        gerund = ir.conjugate_tense(Tenses.gerund)
        self.assertEqual(gerund, 'yendo', 'ir gerund wrong')
         
    def test_past_part_override(self):
        ir = Verb_Dictionary.get('ir')
        for tense in Tenses.past_part_adj:
            pp = ir.conjugate_tense(tense)
            self.assertEqual(pp, 'ido', 'ir past part. wrong')
         
    def test_guir_yo(self):
        distinguir = Verb.importString('distinguir','')
        yo_present = distinguir.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(yo_present, 'distingo', 'guir yo present wrong')
 
    def test_stem_changing_gerund_e2i(self):
        """
        faketir - e:i is explicitly assigned ( fake verb to make it easier to debug ) 
        """
        faketir = Verb.importString("faketir", "", conjugation_overrides="e:i")
#         match = Dependent_Standard_Overrides[u"stem_changing_ir_"+u"e:i"].is_match(faketir)
#         self.assertTrue(match, 'automatch')
        self.assertIsNotNone(faketir.conjugation_stems, "faketir.conjugation_stems")
        self.assertTrue(inspect.ismethod(faketir.conjugation_stems[9][0]), "is method")
        self.assertFalse(inspect.isfunction(faketir.conjugation_stems[9][0]), "is function")
        gerund = faketir.conjugate_tense(Tenses.gerund)
        self.assertEqual(gerund, 'fakitiendo', 'e2i gerund wrong')
        
    def test_stem_changing_gerund_implicit_e2i(self):
        """
        fakegir - e:i is implicitly assigned: gir have stem changing by default
        """
        fakegir = Verb.importString('fakegir', "")
#         self.assertTrue(fakegir.has_override_applied(u''))
        self.assertIsNotNone(fakegir.conjugation_stems, "fakegir.conjugation_stems")
        gerund = fakegir.conjugate_tense(Tenses.gerund)
        self.assertEqual(gerund, 'fakigiendo', 'e2i gerund wrong='+gerund)
        
    def test_beginning_word_radical_stem_changing_overrides(self):
        """
        """
        oler = Verb.importString('oler',"to hear",["o:ue"])
        conjugation = oler.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, 'huelo', "problems with loading manual overrides "+conjugation)
        conjugation = oler.conjugate(Tenses.present_subjective_tense, Persons.first_person_plural)
        self.assertEqual(conjugation, 'olamos', "replacing the beginning vowel back with the infinitive vowel")
     
    def test_that_explicit_override_takes_precedent(self):
        """
        decir is a go verb which must override the default -cir behavior of changing c-> zc
        test to see if a manual override defined as a json object will be correctly applied.
        Make sure for a manual override with None in a override position does not remove a previous override.
        """
        decir = Verb.importString("decir","to say, tell",["go","e:i","-v_cir",
            ConjugationOverride.create_from_json(""'{"conjugation_stems":{"past":"dij","future":"dir","conditional":"dir"},"conjugations":{"imperative_positive_second":"di"}}')])
        conjugations = decir.conjugate_tense(Tenses.imperative_positive)
        self.assertEqual(conjugations[Persons.second_person_singular], 'di', "problems with loading manual overrides of imperative")
        self.assertEqual(conjugations[Persons.third_person_singular], 'diga', "problems with loading manual overrides of imperative")
        
    def test_go_verb_rules(self):
        """-go verbs:
        in yo present:
        ending stem-consonent -> 'g' +'o' (tener)
        ending stem-vowel -> 'ig' + 'o' (asir)
        ending stem-'c' -> change 'c'->'g' (hacer,decir)
        """
        fakir = Verb.importString("fakir", "fake go 1","go")
        conjugation = fakir.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, "fakgo")
         
        fair = Verb.importString("fair", "fake go 1","go")
        conjugation = fair.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, "faigo")
        
        facer = Verb.importString("facer", "fake go 1","go")
        conjugation = facer.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, "fago")
        
    def test_radical_o2ue__ir_changing(self):
        """
        make sure that the key places of stem changing occur (ir different than er ar verbs)
        """ 
        verb = Verb.importString('dormir', 'fake',"o:ue")
        conjugation = verb.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual(conjugation, 'duermo')
        conjugation = verb.conjugate(Tenses.past_tense, Persons.third_person_plural)
        self.assertEqual(conjugation, 'durmieron')
        conjugation = verb.conjugate(Tenses.present_subjective_tense, Persons.first_person_plural)
        self.assertEqual(conjugation, 'durmamos')
        conjugation = verb.conjugate(Tenses.present_subjective_tense, Persons.third_person_plural)
        self.assertEqual(conjugation, 'duerman')
        conjugation = verb.conjugate(Tenses.gerund)
        self.assertEqual(conjugation, 'durmiendo')
        
    def test_uir_verbs(self):
        """ uir verbs have to worry about removing the 'u' before o
        """
        verb = Verb.importString('constituir', "constitute") 
        conjugation = verb.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual('constituyo', conjugation, 'constituyo !='+conjugation)
        
    def test_u_u_verbs(self):
        """
        uar verbs have a u:ú stem change
        """
        verb = Verb.importString('continuar', 'continue')
        conjugation = verb.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual('continúo', conjugation, 'continúo !='+ conjugation)
        conjugation = verb.conjugate(Tenses.present_subjective_tense, Persons.first_person_singular)
        self.assertEqual('continúe', conjugation, 'continúe !='+ conjugation)
        
    def test_complex_verbs(self):
        """
        e:i verbs have a u:ú stem change
        """
        verb = Verb.importString('venir', 'come',["-e:ie_1sp",'e:ie','e:ie_past_all','go','e2d',"e_and_o"])
        radical_stem = Radical_Stem_Conjugation_Overrides['e:ie']
        self.assertTrue(verb.has_override_applied(radical_stem.key))
        self.assertFalse(verb.has_override_applied(radical_stem.first_person_conjugation_override.key))
        self.assertTrue(verb.has_override_applied(radical_stem.stem_changing_ir_past_all.key))
        conjugation = verb.conjugate(Tenses.present_tense, Persons.first_person_singular)
        self.assertEqual('vengo', conjugation, 'vengo !='+ conjugation)
        conjugation = verb.conjugate(Tenses.present_tense, Persons.second_person_singular)
        self.assertEqual('vienes', conjugation, 'vienes !='+ conjugation)
        
        conjugation = verb.conjugate(Tenses.past_tense, Persons.first_person_singular)
        self.assertEqual('vine', conjugation, 'vine !='+ conjugation)
        conjugation = verb.conjugate(Tenses.past_tense, Persons.third_person_singular)
        self.assertEqual('vino', conjugation, 'vino !='+ conjugation)
