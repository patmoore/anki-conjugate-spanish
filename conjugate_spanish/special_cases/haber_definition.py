# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import Tenses, Persons, Infinitive_Endings
from conjugate_spanish.verb_dictionary import Verb_Dictionary_add
from conjugate_spanish.standard_endings import Standard_Conjugation_Endings

_conjugation_overrides = ConjugationOverride(parents=[u'r_only', u'e_and_o'])

# all except 2nd person plural have just h as a stem
_conjugation_overrides.override_tense_stem(Tenses.present_tense, u'h', Persons.all_except(Persons.second_person_plural))
_conjugation_overrides.override_tense_ending(Tenses.present_tense, u'e', Persons.first_person_singular)
for person in [ Persons.second_person_singular, Persons.third_person_singular, Persons.third_person_plural]:
    _conjugation_overrides.override_tense_ending(Tenses.present_tense, Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][person], person)
    
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'hub') 
_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, u'hay')
Verb_Dictionary_add(u'haber', conjugation_overrides=_conjugation_overrides, definition="to have (helping verb)")
