# -*- coding: utf-8 -*-
import unittest

from conjugate_spanish import Tense, Person
from conjugate_spanish.espanol_dictionary import Verb_Dictionary

class TestIr(unittest.TestCase):
    def __check__(self, tense, expected):
        ir = Verb_Dictionary.get("ir")
        for person, expected in expected.items():
            self.assertEqual(expected,ir.conjugate(tense, person, returnAsString=True))

    def test_ir_present_tense(self):
        expected = { Person.first_person_singular: "voy",
                     Person.second_person_singular:"vas",
                     Person.third_person_singular:"va",
                     Person.first_person_plural:"vamos",
                     Person.second_person_plural:"vais",
                     Person.third_person_plural:"van"}
        self.__check__(Tense.present_tense, expected)

    def test_ir_incomplete_past_tense(self):
        expected = { Person.first_person_singular: "iba",
                     Person.second_person_singular:"ibas",
                     Person.third_person_singular:"iba",
                     Person.first_person_plural:"íbamos",
                     Person.second_person_plural:"ibais",
                     Person.third_person_plural:"iban"}
        self.__check__(Tense.incomplete_past_tense, expected)

    def test_ir_past_tense(self):
        expected = { Person.first_person_singular: "fui",
                     Person.second_person_singular:"fuiste",
                     Person.third_person_singular:"fue",
                     Person.first_person_plural:"fuimos",
                     Person.second_person_plural:"fuisteis",
                     Person.third_person_plural:"fueron"}
        self.__check__(Tense.past_tense, expected)

    def test_ir_future_tense(self):
        expected = { Person.first_person_singular: "iré",
                     Person.second_person_singular:"irás",
                     Person.third_person_singular:"irá",
                     Person.first_person_plural:"iremos",
                     Person.second_person_plural:"iréis",
                     Person.third_person_plural:"irán"}
        self.__check__(Tense.future_tense, expected)

    def test_ir_conditional_tense(self):
        expected = { Person.first_person_singular: "iría",
                     Person.second_person_singular:"irías",
                     Person.third_person_singular:"iría",
                     Person.first_person_plural:"iríamos",
                     Person.second_person_plural:"iríais",
                     Person.third_person_plural:"irían"}
        self.__check__(Tense.conditional_tense, expected)

    def test_ir_present_subjective_tense(self):
        expected = { Person.first_person_singular: "vaya",
                     Person.second_person_singular:"vayas",
                     Person.third_person_singular:"vaya",
                     Person.first_person_plural:"vayamos",
                     Person.second_person_plural:"vayáis",
                     Person.third_person_plural:"vayan"}
        self.__check__(Tense.present_subjective_tense, expected)

    def test_ir_past_subjective_tense(self):
        expected = { Person.first_person_singular: "fuera",
                     Person.second_person_singular:"fueras",
                     Person.third_person_singular:"fuera",
                     Person.first_person_plural:"fuéramos",
                     Person.second_person_plural:"fuerais",
                     Person.third_person_plural:"fueran"}
        self.__check__(Tense.past_subjective_tense, expected)

    def test_ir_imperative_positive_tense(self):
        expected = { Person.first_person_singular: None,
                     Person.second_person_singular:"ve",
                     Person.third_person_singular:"vaya",
                     Person.first_person_plural:"vamos",
                     Person.second_person_plural:"id",
                     Person.third_person_plural:"vayan"}
        self.__check__(Tense.imperative_positive, expected)

    def test_ir_imperative_negative_tense(self):
        expected = { Person.first_person_singular: None,
                     Person.second_person_singular:"vayas",
                     Person.third_person_singular:"vaya",
                     Person.first_person_plural:"vayamos",
                     Person.second_person_plural:"vayáis",
                     Person.third_person_plural:"vayan"}
        self.__check__(Tense.imperative_negative, expected)

    def test_ir_tense(self):
        ir = Verb_Dictionary.get("ir")
        self.assertEqual("yendo", ir.conjugate(Tense.gerund, returnAsString=True))
        self.assertEqual("ido", ir.conjugate(Tense.adjective, returnAsString=True))
        self.assertEqual("ido", ir.conjugate(Tense.past_participle, returnAsString=True))