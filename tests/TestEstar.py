# -*- coding: utf-8 -*-
import unittest

from conjugate_spanish import Tense, Person
from conjugate_spanish.espanol_dictionary import Verb_Dictionary

class TestEstar(unittest.TestCase):
    def __check__(self, tense, expected):
        estar = Verb_Dictionary.get("estar")
        for person, expected in expected.items():
            self.assertEqual(expected,estar.conjugate(tense, person, returnAsString=True))

    def test_estar_present_tense(self):
        expected = { Person.first_person_singular: "soy",
                     Person.second_person_singular:"eres",
                     Person.third_person_singular:"es",
                     Person.first_person_plural:"somos",
                     Person.second_person_plural:"sois",
                     Person.third_person_plural:"son"}
        self.__check__(Tense.present_tense, expected)

    def test_estar_incomplete_past_tense(self):
        expected = { Person.first_person_singular: "era",
                     Person.second_person_singular:"eras",
                     Person.third_person_singular:"era",
                     Person.first_person_plural:"éramos",
                     Person.second_person_plural:"erais",
                     Person.third_person_plural:"eran"}
        self.__check__(Tense.incomplete_past_tense, expected)

    def test_estar_past_tense(self):
        expected = { Person.first_person_singular: "fui",
                     Person.second_person_singular:"fuiste",
                     Person.third_person_singular:"fue",
                     Person.first_person_plural:"fuimos",
                     Person.second_person_plural:"fuisteis",
                     Person.third_person_plural:"fueron"}
        self.__check__(Tense.past_tense, expected)

    def test_estar_future_tense(self):
        expected = { Person.first_person_singular: "estaré",
                     Person.second_person_singular:"estarás",
                     Person.third_person_singular:"estará",
                     Person.first_person_plural:"estaremos",
                     Person.second_person_plural:"estaréis",
                     Person.third_person_plural:"estarán"}
        self.__check__(Tense.future_tense, expected)

    def test_estar_conditional_tense(self):
        expected = { Person.first_person_singular: "estaría",
                     Person.second_person_singular:"estarías",
                     Person.third_person_singular:"estaría",
                     Person.first_person_plural:"estaríamos",
                     Person.second_person_plural:"estaríais",
                     Person.third_person_plural:"estarían"}
        self.__check__(Tense.conditional_tense, expected)

    def test_estar_present_subjective_tense(self):
        expected = { Person.first_person_singular: "sea",
                     Person.second_person_singular:"seas",
                     Person.third_person_singular:"sea",
                     Person.first_person_plural:"seamos",
                     Person.second_person_plural:"seáis",
                     Person.third_person_plural:"sean"}
        self.__check__(Tense.present_subjective_tense, expected)

    def test_estar_past_subjective_tense(self):
        expected = { Person.first_person_singular: "fuera",
                     Person.second_person_singular:"fueras",
                     Person.third_person_singular:"fuera",
                     Person.first_person_plural:"fuéramos",
                     Person.second_person_plural:"fuerais",
                     Person.third_person_plural:"fueran"}
        self.__check__(Tense.past_subjective_tense, expected)

    def test_estar_imperative_positive_tense(self):
        expected = { Person.first_person_singular: None,
                     Person.second_person_singular:"sé",
                     Person.third_person_singular:"sea",
                     Person.first_person_plural:"seamos",
                     Person.second_person_plural:"sed",
                     Person.third_person_plural:"sean"}
        self.__check__(Tense.imperative_positive, expected)

    def test_estar_imperative_negative_tense(self):
        expected = { Person.first_person_singular: None,
                     Person.second_person_singular:"seas",
                     Person.third_person_singular:"sea",
                     Person.first_person_plural:"seamos",
                     Person.second_person_plural:"seáis",
                     Person.third_person_plural:"sean"}
        self.__check__(Tense.imperative_negative, expected)

    def test_estar_tense(self):
        estar = Verb_Dictionary.get("estar")
        self.assertEqual("siendo", estar.conjugate(Tense.gerund, returnAsString=True))
        self.assertEqual("sido", estar.conjugate(Tense.adjective, returnAsString=True))
        self.assertEqual("sido", estar.conjugate(Tense.past_participle, returnAsString=True))