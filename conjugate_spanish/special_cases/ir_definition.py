# -*- coding: utf-8 -*-
from conjugate_spanish import ConjugationOverride, Tenses, Persons, Standard_Conjugation_Endings, Infinitive_Endings
from conjugate_spanish.espanol_dictionary import Verb_Dictionary

Past_Tense_IR_CO = ConjugationOverride(parents=['unaccent_present_past'])
Past_Tense_IR_CO.override_tense_stem(Tenses.past_tense, 'fu')
# TODO : these next 2 look like a standard override.
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, 'e', Persons.third_person_singular)
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, 'eron', Persons.third_person_plural, documentation="missing i")

_ir_conjugation_overrides = ConjugationOverride(parents=[Past_Tense_IR_CO, 'oy', 'yendo'], key="ir_irregular")
for person in Persons.all_except(Persons.first_person_singular):
    _ir_conjugation_overrides.override_tense_ending(Tenses.present_tense, Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][person], person)     
_ir_conjugation_overrides.override_tense_stem(Tenses.present_tense, 'v')
_ir_conjugation_overrides.override_tense(Tenses.incomplete_past_tense, ['iba', 'ibas', 'iba', 'íbamos','ibais', 'iban'])
_ir_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, 'vay')
_ir_conjugation_overrides.override_tense(Tenses.imperative_positive, 've', Persons.second_person_singular)
_ir_conjugation_overrides.override_tense(Tenses.imperative_positive, 'vamos', Persons.first_person_plural)
_ir_conjugation_overrides.override_tense_stem(Tenses.Person_Agnostic, '')
Ir_Definition = Verb_Dictionary.add('ir', conjugation_overrides=_ir_conjugation_overrides, definition="to go")

# Note: inherit from parent is implicit
_irse_conjugation_overrides = ConjugationOverride(key="irse_irregular")
# Also note that the negative is "no nos vayamos" -- we don't have a way to handle that.
_irse_conjugation_overrides.override_tense(Tenses.imperative_positive, 'vámo', Persons.first_person_plural, documentation="vámonos only for POSITIVE")
_irse_conjugation_overrides.override_tense(Tenses.imperative_negative, 'nos vayamos', Persons.first_person_plural, documentation="no nos vayamos")
_irse_conjugation_overrides.override_tense(Tenses.imperative_positive, 'idos', Persons.second_person_plural, documentation="idos only for POSITIVE")
Irse_Definition = Verb_Dictionary.add('irse', conjugation_overrides=_irse_conjugation_overrides, definition="to go")
