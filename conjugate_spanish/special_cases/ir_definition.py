# -*- coding: utf-8 -*-
from conjugate_spanish import ConjugationOverride, Tense, Person, Standard_Conjugation_Endings, Infinitive_Ending
from conjugate_spanish.espanol_dictionary import Verb_Dictionary

Past_Tense_IR_CO = ConjugationOverride(parents=['unaccent_present_past'])
Past_Tense_IR_CO.override_tense_stem(Tense.past_tense, 'fu')
# TODO : these next 2 look like a standard override.
Past_Tense_IR_CO.override_tense_ending(Tense.past_tense, 'e', Person.third_person_singular)
Past_Tense_IR_CO.override_tense_ending(Tense.past_tense, 'eron', Person.third_person_plural, documentation="missing i")

_ir_conjugation_overrides = ConjugationOverride(parents=[Past_Tense_IR_CO, 'oy', 'yendo'], key="ir_irregular")
for person in Person.all_except(Person.first_person_singular):
    _ir_conjugation_overrides.override_tense_ending(Tense.present_tense, Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.present_tense][person], person)
_ir_conjugation_overrides.override_tense_stem(Tense.present_tense, 'v')
_ir_conjugation_overrides.override_tense(Tense.incomplete_past_tense, ['iba', 'ibas', 'iba', 'íbamos','ibais', 'iban'])
_ir_conjugation_overrides.override_tense_stem(Tense.present_subjective_tense, 'vay')
_ir_conjugation_overrides.override_tense(Tense.imperative_positive, 've', Person.second_person_singular)
_ir_conjugation_overrides.override_tense(Tense.imperative_positive, 'vamos', Person.first_person_plural)
_ir_conjugation_overrides.override_tense_stem(Tense.Person_Agnostic(), '')
Ir_Definition = Verb_Dictionary.add('ir', conjugation_overrides=_ir_conjugation_overrides, definition="to go")

# Note: inherit from parent is implicit
_irse_conjugation_overrides = ConjugationOverride(key="irse_irregular")
# Also note that the negative is "no nos vayamos" -- we don't have a way to handle that.
_irse_conjugation_overrides.override_tense(Tense.imperative_positive, 'vámos', Person.first_person_plural, documentation="vámonos only for POSITIVE")
# _irse_conjugation_overrides.override_tense(Tense.imperative_negative, 'nos vayamos', Person.first_person_plural, documentation="no nos vayamos")
_irse_conjugation_overrides.override_tense(Tense.imperative_positive, 'idos', Person.second_person_plural, documentation="idos only for POSITIVE")
Irse_Definition = Verb_Dictionary.add('irse', conjugation_overrides=_irse_conjugation_overrides, definition="to go (self)")
