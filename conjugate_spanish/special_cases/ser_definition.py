# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import Tense, Person
from conjugate_spanish.standard_endings import Standard_Conjugation_Endings, Infinitive_Ending
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
from .ir_definition import Past_Tense_IR_CO

def _remove_i(self, conjugation_notes, **kwargs):
    return Standard_Conjugation_Endings[Infinitive_Ending.er_verb][conjugation_notes.tense][conjugation_notes.person][1:]

_conjugation_overrides = ConjugationOverride(parents=[Past_Tense_IR_CO, 'oy'], key="ser")
_conjugation_overrides.override_tense(Tense.present_tense, [None, 'eres', 'es', 'somos', 'sois', 'son'])
_conjugation_overrides.override_tense_stem(Tense.incomplete_past_tense, 'er')
_conjugation_overrides.override_tense_stem(Tense.incomplete_past_tense, 'ér', Person.first_person_plural)
_conjugation_overrides.override_tense_ending(Tense.incomplete_past_tense, _remove_i, documentation="no leading i in ending")
_conjugation_overrides.override_tense_stem(Tense.present_subjective_tense, 'se')
Verb_Dictionary.add('ser', 'to be', conjugation_overrides=_conjugation_overrides)
