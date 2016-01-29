# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import Tenses, Persons
from conjugate_spanish.verb_dictionary import Verb_Dictionary_add

_conjugation_overrides = ConjugationOverride(parents=[u'go',u'r_only',""])

# all except 2nd person plural have just h as a stem
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'pud', Persons.all_except(Persons.third_person_singular))
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'hiz', Persons.third_person_singular)
_conjugation_overrides.override_tense_stem(Tenses.future_tense, u'har')
_conjugation_overrides.override_tense_stem(Tenses.future_tense, u'har')
_conjugation_overrides.override_tense_stem(Tenses.imperative_positive, u'haz', Persons.second_person_singular)
Verb_Dictionary_add(u'poner', conjugation_overrides=_conjugation_overrides, definition="to put, to place")

'', '','go,'poner','{"stems":{"past":"pus"}}'