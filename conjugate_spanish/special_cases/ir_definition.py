# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.__init__ import *
from conjugate_spanish.standard_endings import Standard_Conjugation_Endings 
import six
from conjugate_spanish.verb import Verb

_ir_conjugation_overrides = ConjugationOverride()
_ir_conjugation_overrides.override_tense(present_tense, six.u('voy'), first_person_singular) 
_ir_conjugation_overrides.override_tense(present_tense, six.u('vais'), second_person_plural)
_ir_conjugation_overrides.override_tense_stem(present_tense, six.u('v'))
_ir_conjugation_overrides.override_tense_ending(present_tense, Standard_Conjugation_Endings[ar_verb][present_tense])
_ir_conjugation_overrides.override_tense(incomplete_past_tense, [six.u('iba'), six.u('ibas'), six.u('iba'), six.u('ibamos'),six.u('ibais'), six.u('iban')])
_ir_conjugation_overrides.override_tense_stem(past_tense, six.u('fu'))
_ir_conjugation_overrides.override_tense_ending(past_tense, six.u('e'), third_person_singular)
_ir_conjugation_overrides.override_tense_ending(past_tense, six.u('eron'), third_person_plural)
_ir_conjugation_overrides.override_tense_stem(present_subjective_tense, six.u('vay'))
Ir_Definition = Verb(six.u('ir'), _ir_conjugation_overrides)
c= Ir_Definition.conjugate_all_tenses()

print repr(c).decode("unicode-escape")