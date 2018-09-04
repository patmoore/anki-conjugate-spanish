# -*- coding: utf-8 -*-
import unittest

from conjugate_spanish import Tense, Person
from conjugate_spanish.espanol_dictionary import Verb_Dictionary

class TestSer(unittest.TestCase):
    def __check__(self, tense, expected):
        ser = Verb_Dictionary.get("ser")
        for person, expected in expected.items():
            self.assertEqual(expected,ser.conjugate(tense, person, returnAsString=True), "person {} tense {}".format(str(person), str(tense)))

    def test_ser_present_tense(self):
        expected = { Person.first_person_singular: "soy",
                     Person.second_person_singular:"eres",
                     Person.third_person_singular:"es",
                     Person.first_person_plural:"somos",
                     Person.second_person_plural:"sois",
                     Person.third_person_plural:"son"}
        self.__check__(Tense.present_tense, expected)

    def test_ser_incomplete_past_tense(self):
        expected = { Person.first_person_singular: "era",
                     Person.second_person_singular:"eras",
                     Person.third_person_singular:"era",
                     Person.first_person_plural:"éramos",
                     Person.second_person_plural:"erais",
                     Person.third_person_plural:"eran"}
        self.__check__(Tense.incomplete_past_tense, expected)

    def test_ser_past_tense(self):
        expected = { Person.first_person_singular: "fui",
                     Person.second_person_singular:"fuiste",
                     Person.third_person_singular:"fue",
                     Person.first_person_plural:"fuimos",
                     Person.second_person_plural:"fuisteis",
                     Person.third_person_plural:"fueron"}
        self.__check__(Tense.past_tense, expected)

    def test_ser_future_tense(self):
        expected = { Person.first_person_singular: "seré",
                     Person.second_person_singular:"serás",
                     Person.third_person_singular:"será",
                     Person.first_person_plural:"seremos",
                     Person.second_person_plural:"seréis",
                     Person.third_person_plural:"serán"}
        self.__check__(Tense.future_tense, expected)

    def test_ser_conditional_tense(self):
        expected = { Person.first_person_singular: "sería",
                     Person.second_person_singular:"serías",
                     Person.third_person_singular:"sería",
                     Person.first_person_plural:"seríamos",
                     Person.second_person_plural:"seríais",
                     Person.third_person_plural:"serían"}
        self.__check__(Tense.conditional_tense, expected)

    def test_ser_present_subjective_tense(self):
        expected = { Person.first_person_singular: "sea",
                     Person.second_person_singular:"seas",
                     Person.third_person_singular:"sea",
                     Person.first_person_plural:"seamos",
                     Person.second_person_plural:"seáis",
                     Person.third_person_plural:"sean"}
        self.__check__(Tense.present_subjective_tense, expected)

    def test_ser_past_subjective_tense(self):
        expected = { Person.first_person_singular: "fuera",
                     Person.second_person_singular:"fueras",
                     Person.third_person_singular:"fuera",
                     Person.first_person_plural:"fuéramos",
                     Person.second_person_plural:"fuerais",
                     Person.third_person_plural:"fueran"}
        self.__check__(Tense.past_subjective_tense, expected)

    def test_ser_imperative_positive_tense(self):
        expected = { Person.first_person_singular: None,
                     Person.second_person_singular:"sé",
                     Person.third_person_singular:"sea",
                     Person.first_person_plural:"seamos",
                     Person.second_person_plural:"sed",
                     Person.third_person_plural:"sean"}
        self.__check__(Tense.imperative_positive, expected)

    def test_ser_imperative_negative_tense(self):
        expected = { Person.first_person_singular: None,
                     Person.second_person_singular:"seas",
                     Person.third_person_singular:"sea",
                     Person.first_person_plural:"seamos",
                     Person.second_person_plural:"seáis",
                     Person.third_person_plural:"sean"}
        self.__check__(Tense.imperative_negative, expected)

    def test_ser_tense(self):
        ser = Verb_Dictionary.get("ser")
        self.assertEqual("siendo", ser.conjugate(Tense.gerund, returnAsString=True))
        self.assertEqual("sido", ser.conjugate(Tense.adjective, returnAsString=True))
        self.assertEqual("sido", ser.conjugate(Tense.past_participle, returnAsString=True))