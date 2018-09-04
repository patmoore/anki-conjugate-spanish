# -*- coding: utf-8 -*-
import unittest

from conjugate_spanish import Tense, Person
from conjugate_spanish.espanol_dictionary import Espanol_Dictionary, Verb_Dictionary
Espanol_Dictionary.load()

class TestEstar(unittest.TestCase):
    def __check__(self, tense, expected):
        estar = Verb_Dictionary.get("estar")
        for person, expected in expected.items():
            self.assertEqual(expected,estar.conjugate(tense, person, returnAsString=True))

    def test_estar_present_tense(self):
        expected = { Person.first_person_singular: "estoy",
                     Person.second_person_singular:"estás",
                     Person.third_person_singular:"está",
                     Person.first_person_plural:"estamos",
                     Person.second_person_plural:"estáis",
                     Person.third_person_plural:"están"}
        self.__check__(Tense.present_tense, expected)

    def test_estar_incomplete_past_tense(self):
        expected = { Person.first_person_singular: "estaba",
                     Person.second_person_singular:"estabas",
                     Person.third_person_singular:"estaba",
                     Person.first_person_plural:"estábamos",
                     Person.second_person_plural:"estabais",
                     Person.third_person_plural:"estaban"}
        self.__check__(Tense.incomplete_past_tense, expected)

    def test_estar_past_tense(self):
        expected = { Person.first_person_singular: "estuve",
                     Person.second_person_singular:"estuviste",
                     Person.third_person_singular:"estuvo",
                     Person.first_person_plural:"estuvimos",
                     Person.second_person_plural:"estuvisteis",
                     Person.third_person_plural:"estuvieron"}
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
        expected = { Person.first_person_singular: "esté",
                     Person.second_person_singular:"estés",
                     Person.third_person_singular:"esté",
                     Person.first_person_plural:"estemos",
                     Person.second_person_plural:"estéis",
                     Person.third_person_plural:"estén"}
        self.__check__(Tense.present_subjective_tense, expected)

    def test_estar_past_subjective_tense(self):
        expected = { Person.first_person_singular: "estuviera",
                     Person.second_person_singular:"estuvieras",
                     Person.third_person_singular:"estuviera",
                     Person.first_person_plural:"estuviéramos",
                     Person.second_person_plural:"estuvierais",
                     Person.third_person_plural:"estuvieran"}
        self.__check__(Tense.past_subjective_tense, expected)

    def test_estar_imperative_positive_tense(self):
        expected = { Person.first_person_singular: None,
                     Person.second_person_singular:"está",
                     Person.third_person_singular:"esté",
                     Person.first_person_plural:"estemos",
                     Person.second_person_plural:"estad",
                     Person.third_person_plural:"estén"}
        self.__check__(Tense.imperative_positive, expected)

    def test_estar_imperative_negative_tense(self):
        expected = { Person.first_person_singular: None,
                     Person.second_person_singular:"estés",
                     Person.third_person_singular:"esté",
                     Person.first_person_plural:"estemos",
                     Person.second_person_plural:"estéis",
                     Person.third_person_plural:"estén"}
        self.__check__(Tense.imperative_negative, expected)

    def test_estar_tense(self):
        estar = Verb_Dictionary.get("estar")
        self.assertEqual("estando", estar.conjugate(Tense.gerund, returnAsString=True))
        self.assertEqual("estado", estar.conjugate(Tense.adjective, returnAsString=True))
        self.assertEqual("estado", estar.conjugate(Tense.past_participle, returnAsString=True))