# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import Tenses,Persons
from conjugate_spanish.verb_dictionary import Verb_Dictionary_add

_conjugation_overrides = ConjugationOverride(parents=["go","e:ie"])
_conjugation_overrides.override_tense_stem(Tenses.present_tense, u'ten', Persons.first_person_singular, documentation="no e:ie in first person")
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'tuv')
_conjugation_overrides.override_tense_ending(Tenses.past_tense, u'e', Persons.first_person_singular)
_conjugation_overrides.override_tense_ending(Tenses.past_tense, u'o', Persons.third_person_singular)
_conjugation_overrides.override_tense_stem(Tenses.future_tense, u'tendr')
_conjugation_overrides.override_tense_stem(Tenses.conditional_tense, u'tendr')
Verb_Dictionary_add(u'tener', u'to be', conjugation_overrides=_conjugation_overrides)
