# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import Tenses
from conjugate_spanish.verb_dictionary import Verb_Dictionary

# note the use_er must be before e_and_o
_conjugation_overrides = ConjugationOverride(parents=[u'oy',u'use_er', u'e_and_o'])
# _conjugation_overrides.override_tense_ending(Tenses.present_tense, u'oy', Persons.first_person_singular)
_conjugation_overrides.override_tense_ending(Tenses.present_tense, [ None, u'ás', u'á', None, None, u'án'], documentation="the accent is needed")
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'estuv', documentation="see tener") 
_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, u'est')
_conjugation_overrides.override_tense_ending(Tenses.present_subjective_tense, [u'é', u'és', u'é', None, None, u'én'], documentation="the accent is needed")
Verb_Dictionary.add(u'estar', conjugation_overrides=_conjugation_overrides, definition="to be")
