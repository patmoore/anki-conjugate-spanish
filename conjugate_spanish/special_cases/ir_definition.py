# -*- coding: utf-8 -*-
from conjugate_spanish import * 
import six
from conjugate_spanish.verb_dictionary import Verb_Dictionary_add
# from conjugate_spanish.verb import Verb

Past_Tense_IR_CO = ConjugationOverride()
Past_Tense_IR_CO.override_tense_stem(Tenses.past_tense, six.u('fu'))
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, six.u('i'), Persons.first_person_singular, documentation="no accent on i")
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, six.u('e'), Persons.third_person_singular)
Past_Tense_IR_CO.override_tense_ending(Tenses.past_tense, six.u('eron'), Persons.third_person_plural, documentation="missing i")

_ir_conjugation_overrides = ConjugationOverride(parents=[Past_Tense_IR_CO, u'oy', u'yendo'])
for person in Persons.all_except(Persons.first_person_singular):
    _ir_conjugation_overrides.override_tense_ending(Tenses.present_tense, Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][person], person)     
_ir_conjugation_overrides.override_tense_ending(Tenses.present_tense, six.u('ais'), Persons.second_person_plural, documentation="no accent on a")
_ir_conjugation_overrides.override_tense_stem(Tenses.present_tense, six.u('v'))
_ir_conjugation_overrides.override_tense(Tenses.incomplete_past_tense, [six.u('iba'), six.u('ibas'), six.u('iba'), six.u('ibamos'),six.u('ibais'), six.u('iban')])
_ir_conjugation_overrides.override_tense_stem(Tenses.present_subjective_tense, six.u('vay'))
_ir_conjugation_overrides.override_tense_stem(Tenses.past_participle, u'')
_ir_conjugation_overrides.override_tense_stem(Tenses.gerund, u'')
Ir_Definition = Verb_Dictionary_add(u'ir', conjugation_overrides=_ir_conjugation_overrides, definition="to go")
Irse_Definition = Verb_Dictionary_add(u'irse', conjugation_overrides=_ir_conjugation_overrides, definition="to go")
