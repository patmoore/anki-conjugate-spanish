# -*- coding: utf-8 -*-
import unittest

from conjugate_spanish import Tense, Person
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
Verb_Dictionary.add("ir", "go",conjugation_overrides="oy,yendo,unaccent_present_past", manual_overrides='{"conjugation_stems":{"present":"v","past":"fu","present_subjective":"vay"},"conjugation_endings":{"present":[null,"as","a","amos","ais","an"],"past":[null,null,"e",null,null,"eron"]},"conjugations":{"incomplete_past":["iba", "ibas", "iba", "íbamos","ibais", "iban"],"imperative_positive":[null, "ve", null, "vamos", null, null]}}')
Verb_Dictionary.add("irse", "go (self)",manual_overrides='{"conjugations":{"imperative_negative":[null, null, "se vaya", "nos vayamos", null, "se vayan"],"imperative_positive":[null, null,null,null,"idos",null]}}')
class TestIr(unittest.TestCase):
    ir_expected = {
        Tense.present_tense:
             {Person.first_person_singular: "voy",
                Person.second_person_singular: "vas",
                Person.third_person_singular: "va",
                Person.first_person_plural: "vamos",
                Person.second_person_plural: "vais",
                Person.third_person_plural: "van"},
        Tense.incomplete_past_tense:
            {Person.first_person_singular: "iba",
             Person.second_person_singular: "ibas",
             Person.third_person_singular: "iba",
             Person.first_person_plural: "íbamos",
             Person.second_person_plural: "ibais",
             Person.third_person_plural: "iban"},
        Tense.past_tense:
            {Person.first_person_singular: "fui",
             Person.second_person_singular: "fuiste",
             Person.third_person_singular: "fue",
             Person.first_person_plural: "fuimos",
             Person.second_person_plural: "fuisteis",
             Person.third_person_plural: "fueron"},
        Tense.future_tense:
            {Person.first_person_singular: "iré",
             Person.second_person_singular: "irás",
             Person.third_person_singular: "irá",
             Person.first_person_plural: "iremos",
             Person.second_person_plural: "iréis",
             Person.third_person_plural: "irán"},
        Tense.conditional_tense:
            {Person.first_person_singular: "iría",
             Person.second_person_singular: "irías",
             Person.third_person_singular: "iría",
             Person.first_person_plural: "iríamos",
             Person.second_person_plural: "iríais",
             Person.third_person_plural: "irían"},
        Tense.present_subjective_tense:
            {Person.first_person_singular: "vaya",
             Person.second_person_singular: "vayas",
             Person.third_person_singular: "vaya",
             Person.first_person_plural: "vayamos",
             Person.second_person_plural: "vayáis",
             Person.third_person_plural: "vayan"},
        Tense.past_subjective_tense:
            {Person.first_person_singular: "fuera",
             Person.second_person_singular: "fueras",
             Person.third_person_singular: "fuera",
             Person.first_person_plural: "fuéramos",
             Person.second_person_plural: "fuerais",
             Person.third_person_plural: "fueran"},
        Tense.imperative_positive:
            {Person.first_person_singular: None,
             Person.second_person_singular: "ve",
             Person.third_person_singular: "vaya",
             Person.first_person_plural: "vamos",
             Person.second_person_plural: "id",
             Person.third_person_plural: "vayan"},
        Tense.imperative_negative:
            {Person.first_person_singular: None,
             Person.second_person_singular: "vayas",
             Person.third_person_singular: "vaya",
             Person.first_person_plural: "vayamos",
             Person.second_person_plural: "vayáis",
             Person.third_person_plural: "vayan"}
    }
    def __irse_check__(self, tense, expected):
        irse = Verb_Dictionary.get("irse")
        for person, expected in expected.items():
            irse_expected = None if expected is None else person.indirect_pronoun+ " "+ expected
            self.assertEqual(irse_expected,irse.conjugate(tense, person, returnAsString=True), "Irse : tense {} Person {} ".format(str(tense), str(person)))

    def __check__(self, tense, expected):
        ir = Verb_Dictionary.get("ir")
        for person, expected in expected.items():
            self.assertEqual(expected,ir.conjugate(tense, person, returnAsString=True), "Ir tense {} Person {} ".format(str(tense), str(person)))

    def test_ir_present_tense(self):
        self.__check__(Tense.present_tense, TestIr.ir_expected[Tense.present_tense])
        self.__irse_check__(Tense.present_tense, TestIr.ir_expected[Tense.present_tense])

    def test_ir_incomplete_past_tense(self):
        self.__check__(Tense.incomplete_past_tense, TestIr.ir_expected[Tense.incomplete_past_tense])
        self.__irse_check__(Tense.incomplete_past_tense, TestIr.ir_expected[Tense.incomplete_past_tense])

    def test_ir_past_tense(self):
        self.__check__(Tense.past_tense, TestIr.ir_expected[Tense.past_tense])
        self.__irse_check__(Tense.past_tense, TestIr.ir_expected[Tense.past_tense])

    def test_ir_future_tense(self):
        self.__check__(Tense.future_tense, TestIr.ir_expected[Tense.future_tense])
        self.__irse_check__(Tense.future_tense, TestIr.ir_expected[Tense.future_tense])

    def test_ir_conditional_tense(self):
        self.__check__(Tense.conditional_tense, TestIr.ir_expected[Tense.conditional_tense])
        self.__irse_check__(Tense.conditional_tense, TestIr.ir_expected[Tense.conditional_tense])

    def test_ir_present_subjective_tense(self):
        self.__check__(Tense.present_subjective_tense, TestIr.ir_expected[Tense.present_subjective_tense])
        self.__irse_check__(Tense.present_subjective_tense, TestIr.ir_expected[Tense.present_subjective_tense])

    def test_ir_past_subjective_tense(self):
        self.__check__(Tense.past_subjective_tense, TestIr.ir_expected[Tense.past_subjective_tense])
        self.__irse_check__(Tense.past_subjective_tense, TestIr.ir_expected[Tense.past_subjective_tense])

    def test_ir_imperative_positive_tense(self):
        tense = Tense.imperative_positive
        self.__check__(tense, TestIr.ir_expected[tense])
        expected = {
            Person.first_person_singular: None,
            Person.second_person_singular: "vete",
            Person.third_person_singular: "váyase",
            Person.first_person_plural: "vámonos",
            Person.second_person_plural: "idos",
            Person.third_person_plural: "váyanse"
        }
        irse = Verb_Dictionary.get("irse")
        for person, expected in expected.items():
            self.assertEqual(expected,irse.conjugate(tense, person, returnAsString=True), "Irse tense {} Person {} ".format(str(tense), str(person)))


    def test_ir_imperative_negative_tense(self):
        self.__check__(Tense.imperative_negative, TestIr.ir_expected[Tense.imperative_negative])
        self.__irse_check__(Tense.imperative_negative, TestIr.ir_expected[Tense.imperative_negative])

    def test_ir_tense(self):
        ir = Verb_Dictionary.get("ir")
        self.assertEqual("yendo", ir.conjugate(Tense.gerund, returnAsString=True))
        self.assertEqual("ido", ir.conjugate(Tense.adjective, returnAsString=True))
        self.assertEqual("ido", ir.conjugate(Tense.past_participle, returnAsString=True))