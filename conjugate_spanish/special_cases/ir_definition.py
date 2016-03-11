# -*- coding: utf-8 -*-
from conjugate_spanish import ConjugationOverride, Tenses, Persons, Standard_Conjugation_Endings, Infinitive_Endings
import six
from conjugate_spanish.verb_dictionary import Verb_Dictionary_add
# from conjugate_spanish.verb import Verb

Past_Tense_IR_CO = ConjugationOverride()
Past_Tense_IR_CO.override_tense_stem(Tenses.past_tense, six.u('fu'))
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, six.u('i'), Persons.first_person_singular, documentation="no accent on i")
# TODO : these next 2 look like a standard override.
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, six.u('e'), Persons.third_person_singular)
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, six.u('eron'), Persons.third_person_plural, documentation="missing i")

_ir_conjugation_overrides = ConjugationOverride(parents=[Past_Tense_IR_CO, u'oy', u'yendo'], key="ir_irregular")
for person in Persons.all_except(Persons.first_person_singular):
    _ir_conjugation_overrides.override_tense_ending(Tenses.present_tense, Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][person], person)     
_ir_conjugation_overrides.override_tense_ending(Tenses.present_tense, six.u('ais'), Persons.second_person_plural, documentation="no accent on a")
_ir_conjugation_overrides.override_tense_stem(Tenses.present_tense, six.u('v'))
_ir_conjugation_overrides.override_tense(Tenses.incomplete_past_tense, [six.u('iba'), six.u('ibas'), six.u('iba'), six.u('ibamos'),six.u('ibais'), six.u('iban')])
_ir_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, six.u('vay'))
_ir_conjugation_overrides.override_tense(Tenses.imperative_positive, u've', Persons.second_person_singular)
_ir_conjugation_overrides.override_tense(Tenses.imperative_positive, u'vamos', Persons.first_person_plural)
_ir_conjugation_overrides.override_tense_stem(Tenses.Person_Agnostic, u'')
Ir_Definition = Verb_Dictionary_add(u'ir', conjugation_overrides=_ir_conjugation_overrides, definition="to go")

# Note: inherit from parent is implicit
_irse_conjugation_overrides = ConjugationOverride(key=u"irse_irregular")
# Also note that the negative is "no nos vayamos" -- we don't have a way to handle that.
_irse_conjugation_overrides.override_tense(Tenses.imperative_positive, u'vámo', Persons.first_person_plural, documentation=u"vámonos only for POSITIVE")
Irse_Definition = Verb_Dictionary_add(u'irse', conjugation_overrides=_irse_conjugation_overrides, definition="to go")
