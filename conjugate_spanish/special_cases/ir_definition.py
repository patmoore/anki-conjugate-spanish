# -*- coding: utf-8 -*-
from conjugate_spanish import ConjugationOverride, Tenses, Persons, Standard_Conjugation_Endings, Infinitive_Endings
from conjugate_spanish.verb_dictionary import Verb_Dictionary

Past_Tense_IR_CO = ConjugationOverride(parents=[u'unaccent_present_past'])
Past_Tense_IR_CO.override_tense_stem(Tenses.past_tense, u'fu')
# TODO : these next 2 look like a standard override.
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, u'e', Persons.third_person_singular)
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, u'eron', Persons.third_person_plural, documentation=u"missing i")

_ir_conjugation_overrides = ConjugationOverride(parents=[Past_Tense_IR_CO, u'oy', u'yendo'], key=u"ir_irregular")
for person in Persons.all_except(Persons.first_person_singular):
    _ir_conjugation_overrides.override_tense_ending(Tenses.present_tense, Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][person], person)     
_ir_conjugation_overrides.override_tense_stem(Tenses.present_tense, u'v')
_ir_conjugation_overrides.override_tense(Tenses.incomplete_past_tense, [u'iba', u'ibas', u'iba', u'íbamos',u'ibais', u'iban'])
_ir_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, u'vay')
_ir_conjugation_overrides.override_tense(Tenses.imperative_positive, u've', Persons.second_person_singular)
_ir_conjugation_overrides.override_tense(Tenses.imperative_positive, u'vamos', Persons.first_person_plural)
_ir_conjugation_overrides.override_tense_stem(Tenses.Person_Agnostic, u'')
Ir_Definition = Verb_Dictionary.add(u'ir', conjugation_overrides=_ir_conjugation_overrides, definition=u"to go")

# Note: inherit from parent is implicit
_irse_conjugation_overrides = ConjugationOverride(key=u"irse_irregular")
# Also note that the negative is "no nos vayamos" -- we don't have a way to handle that.
_irse_conjugation_overrides.override_tense(Tenses.imperative_positive, u'vámo', Persons.first_person_plural, documentation=u"vámonos only for POSITIVE")
_irse_conjugation_overrides.override_tense(Tenses.imperative_negative, u'nos vayamos', Persons.first_person_plural, documentation=u"no nos vayamos")
_irse_conjugation_overrides.override_tense(Tenses.imperative_positive, u'idos', Persons.second_person_plural, documentation=u"idos only for POSITIVE")
Irse_Definition = Verb_Dictionary.add(u'irse', conjugation_overrides=_irse_conjugation_overrides, definition=u"to go")
