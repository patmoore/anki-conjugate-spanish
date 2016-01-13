# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.__init__ import *
from conjugate_spanish.standard_endings import Standard_Conjugation_Endings 
import six
from conjugate_spanish.verb import Verb
from ir_definition import Past_Tense_IR_CO

def _remove_i(self, tense,person):
    return self.conjugate_ending(tense, person) + Standard_Conjugation_Endings[er_verb][tense][1:]

_conjugation_overrides = ConjugationOverride(parent=Past_Tense_IR_CO)
_conjugation_overrides.override_tense(present_tense, [six.u('soy'), six.u('eres'), six.u('es'), six.u('somos'), six.u('sois'), six.u('son')])
_conjugation_overrides.override_tense_stem(incomplete_past_tense, six.u('er'))
_conjugation_overrides.override_tense_ending(incomplete_past_tense, _remove_i, documentation="just the leading character is different")
_conjugation_overrides.override_tense_stem(present_subjective_tense, six.u('se'))
Ser_Definition = Verb(six.u('ser'), _conjugation_overrides)
c= Ser_Definition.conjugate_all_tenses()
 
print repr(c).decode("unicode-escape")