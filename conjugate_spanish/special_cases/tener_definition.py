# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import Tenses,Persons
from conjugate_spanish.verb_dictionary import Verb_Dictionary_add

_conjugation_overrides = ConjugationOverride(parents=[u"go",u"e:ie", u'e_and_o', u'e2d'], key="tener_irregular")
_conjugation_overrides.override_tense_stem(Tenses.present_tense, u'ten', Persons.first_person_singular, documentation="no e:ie in first person")
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'tuv')
_conjugation_overrides.override_tense(Tenses.imperative_positive, u'ten', Persons.second_person_singular)
Verb_Dictionary_add(u'tener', u'to be', conjugation_overrides=_conjugation_overrides)
