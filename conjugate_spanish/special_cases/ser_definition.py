# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.__init__ import *
from conjugate_spanish.standard_endings import Standard_Conjugation_Endings 
from conjugate_spanish.verb_dictionary import Verb_Dictionary
import six
from conjugate_spanish.verb import Verb
from ir_definition import Past_Tense_IR_CO

def _remove_i(self, tense,person):
    return Standard_Conjugation_Endings[er_verb][tense][person][1:]

_conjugation_overrides = ConjugationOverride(parent=Past_Tense_IR_CO)
_conjugation_overrides.override_tense(present_tense, [u'soy', u'eres', u'es', u'somos', u'sois', u'son'])
_conjugation_overrides.override_tense_stem(incomplete_past_tense, u'er')
_conjugation_overrides.override_tense_stem(incomplete_past_tense, u'ér', first_person_plural)
_conjugation_overrides.override_tense_ending(incomplete_past_tense, _remove_i, documentation="just the leading character is different")
_conjugation_overrides.override_tense_stem(present_subjective_tense, u'se')
Ser_Definition = Verb(six.u('ser'), 'to be', conjugation_overrides=_conjugation_overrides)
Verb_Dictionary[Ser_Definition.inf_verb_string] = Ser_Definition