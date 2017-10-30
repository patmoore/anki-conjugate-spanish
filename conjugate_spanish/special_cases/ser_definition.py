# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import *
from conjugate_spanish.standard_endings import * 
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
from .ir_definition import Past_Tense_IR_CO

def _remove_i(self, tense,person, **kwargs):
    return Standard_Conjugation_Endings[Infinitive_Endings.er_verb][tense][person][1:]

_conjugation_overrides = ConjugationOverride(parents=[Past_Tense_IR_CO, 'oy'], key="ser")
_conjugation_overrides.override_tense(Tenses.present_tense, [None, 'eres', 'es', 'somos', 'sois', 'son'])
_conjugation_overrides.override_tense_stem(Tenses.incomplete_past_tense, 'er')
_conjugation_overrides.override_tense_stem(Tenses.incomplete_past_tense, 'ér', Persons.first_person_plural)
_conjugation_overrides.override_tense_ending(Tenses.incomplete_past_tense, _remove_i, documentation="no leading i in ending")
_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, 'se')
Verb_Dictionary.add('ser', 'to be', conjugation_overrides=_conjugation_overrides)
