# -*- coding: utf-8 -*-

import unittest
from conjugate_spanish import Tense, Person, Verb

class TestThirdPersonOnly(unittest.TestCase):
    """
    Used to test for the third person only cases
    """
    def __check(self, verb, stem, inf_ending, prefix_words="", prefix="", reflexive=False, suffix_words="", is_phrase=False):
        self.assertEqual(verb.prefix_words, prefix_words)
        self.assertEqual(verb.prefix, prefix)
        self.assertEqual(verb.stem, stem)
        self.assertEqual(verb.inf_ending, inf_ending)
        self.assertEqual(verb.reflexive, reflexive)
        self.assertEqual(verb.suffix_words, suffix_words)
        self.assertEqual(verb.is_phrase, is_phrase)
        if not is_phrase:
            if reflexive:
                self.assertEqual(verb.inf_verb_string, stem+inf_ending+'se')
            else:
                self.assertEqual(verb.inf_verb_string, stem+inf_ending)
            self.assertEqual(verb.inf_verb_string, verb.full_phrase)
        
    def test_third_only(self):
        verb = Verb.importString('suceder','happen', conjugation_overrides=['3rd_only'])
        results = [
            ['sucede','suceden'],
            ['sucedía','sucedían'],
            ['sucedió','sucedieron'],
            ['sucederá','sucederán'],
            ['sucedería','sucederían'],
            ['suceda','sucedan'],
            ['sucediera','sucedieran'],
            ['suceda','sucedan'],
            ['suceda','sucedan'],
            'sucediendo',
            'sucedido',
            'sucedido'
        ]
        for tense in Tense.all():
            if tense in Tense.Person_Agnostic():
                conjugation_notes = verb.conjugate(tense)
                self.assertEqual(results[tense], conjugation_notes.conjugation)
            else:
                index = 0
                for person in Person.third_person():
                    expected = results[tense][index]
                    conjugation_notes = verb.conjugate(tense, person)
                    self.assertEqual(expected, conjugation_notes.conjugation)
                    index += 1
        
    def test_third_sing_only(self):
        verb = Verb.importString('helar','freeze', conjugation_overrides=['3rd_sing_only',"e:ie"])
        results = [
            'hiela',
            'helaba',
            'heló',
            'helará',
            'helaría',
            'hiele',
            'helara',
            'hiele',
            'hiele',
            'helando',
            'helado'
        ]
        
        for tense in Tense.all():
            for person in [Person.third_person_singular]:
                expected = results[tense]
                conjugation = verb.conjugate(tense, person)
                self.assertEqual(expected, conjugation)
