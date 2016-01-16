# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import *
from conjugate_spanish.standard_endings import Irregular_Past_Endings 
from conjugate_spanish.verb import Verb
from conjugate_spanish.verb_dictionary import Verb_Dictionary

_conjugation_overrides = ConjugationOverride()
_conjugation_overrides.override_tense_ending(Tenses.present_tense, u'oy', Persons.first_person_singular)
_conjugation_overrides.override_tense_ending(Tenses.present_tense, [ None, u'ás', u'á', None, None, u'án'], documentation="the accent is needed")
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'estuv', documentation="see tener") 
_conjugation_overrides.override_tense_ending(Tenses.past_tense, Irregular_Past_Endings)
_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, u'est')
_conjugation_overrides.override_tense_ending(Tenses.present_subjective_tense, [u'é', u'és', u'é', None, None, u'én'], documentation="the accent is needed")
Estar_Definition = Verb(u'estar', conjugation_overrides=_conjugation_overrides, definition="to be")
Verb_Dictionary[Estar_Definition.inf_verb_string] = Estar_Definition