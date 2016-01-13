# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.__init__ import *
from conjugate_spanish.standard_endings import Standard_Conjugation_Endings,Irregular_Past_Endings 
import six
from conjugate_spanish.verb import Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary

_conjugation_overrides = ConjugationOverride()
_conjugation_overrides.override_tense_ending(present_tense, u'oy', first_person_singular)
_conjugation_overrides.override_tense_ending(present_tense, [ None, u'ás', u'á', None, None, u'án'], documentation="the accent is needed")
_conjugation_overrides.override_tense_stem(past_tense, u'estuv', documentation="see tener") 
_conjugation_overrides.override_tense_ending(past_tense, Irregular_Past_Endings)
_conjugation_overrides.override_tense_stem(present_subjective_tense, u'est')
_conjugation_overrides.override_tense_ending(present_subjective_tense, [u'é', u'és', u'é', None, None, u'én'], documentation="the accent is needed")
Estar_Definition = Verb(six.u('estar'), conjugation_overrides=_conjugation_overrides, definition="to be")
Verb_Dictionary[Estar_Definition.inf_verb_string] = Estar_Definition