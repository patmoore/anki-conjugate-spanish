# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import *
from conjugate_spanish.standard_endings import Standard_Conjugation_Endings 
from conjugate_spanish.verb_dictionary import Verb_Dictionary
from ir_definition import Past_Tense_IR_CO

def _remove_i(self, tense,person, **kwargs):
    return Standard_Conjugation_Endings[Infinitive_Endings.er_verb][tense][person][1:]

_conjugation_overrides = ConjugationOverride(parents=[Past_Tense_IR_CO, u'oy'])
_conjugation_overrides.override_tense(Tenses.present_tense, [None, u'eres', u'es', u'somos', u'sois', u'son'])
_conjugation_overrides.override_tense_stem(Tenses.incomplete_past_tense, u'er')
_conjugation_overrides.override_tense_stem(Tenses.incomplete_past_tense, u'ér', Persons.first_person_plural)
_conjugation_overrides.override_tense_ending(Tenses.incomplete_past_tense, _remove_i, documentation="no leading i in ending")
_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, u'se')
Verb_Dictionary.add(u'ser', 'to be', conjugation_overrides=_conjugation_overrides)
