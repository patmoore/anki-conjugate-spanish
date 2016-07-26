# -*- coding: utf-8 -*-

import unittest
from conjugate_spanish import Tenses, Persons, Verb

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
        verb = Verb('suceder','happen', conjugation_overrides=['3rd_only'])
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
            'sucedido'
        ]
        for tense in Tenses.all:
            if tense in Tenses.Person_Agnostic:
                conjugation = verb.conjugate(tense)
                self.assertEqual(results[tense], conjugation)
            else:
                for person in Persons.third_person:
                    expected = results[tense][person/3]
                    conjugation = verb.conjugate(tense, person)
                    self.assertEqual(expected, conjugation)
                
        
    def test_third_sing_only(self):
        verb = Verb('helar','freeze', conjugation_overrides=['3rd_sing_only',"e:ie"])
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
        
        for tense in Tenses.all:
            for person in [Persons.third_person_singular]:
                expected = results[tense]
                conjugation = verb.conjugate(tense, person)
                self.assertEqual(expected, conjugation)
