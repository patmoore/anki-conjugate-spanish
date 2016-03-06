# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import Tenses,Persons
from conjugate_spanish.verb_dictionary import Verb_Dictionary_add

_conjugation_overrides = ConjugationOverride(parents=[u"go",u"e:ie", u'e_and_o', u'e2d'], key=u"tener")
# _conjugation_overrides.override_tense_stem(Tenses.present_tense, u'ten', Persons.first_person_singular, documentation=u"no e:ie in first person")
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'tuv')
_conjugation_overrides.override_tense(Tenses.imperative_positive, u'ten', Persons.second_person_singular)
Verb_Dictionary_add(u'tener', u'to be', conjugation_overrides=[ u"-e:ie_1sp", u'-pres_sub_inf',_conjugation_overrides])
