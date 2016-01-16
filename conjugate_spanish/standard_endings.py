# -*- coding: utf-8 -*-
import copy
from constants import *

Standard_Conjugation_Endings = [ [ [] for t in range(len(Tenses)) ] for v in range(len(Infinitive_Endings))]

"""
present tense
""" 
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense] = [
     u"o",
     u"as",
     u"a",
     u"amos",
     u"áis",
     u"an"
    ]  
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_tense] = [
    Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][Persons.first_person_singular],
     u'es',
     u'e',
     u'emos',
     u'éis',
     u'en'
    ]  
Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_tense] = list(Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_tense])
Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_tense][Persons.first_person_plural] =  u'imos'
Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_tense][Persons.second_person_plural] =  u'ís'

"""
imperfect tense
"""
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.incomplete_past_tense] = [
     u'aba',
     u'abas',
     u'aba',
     u'ábamos',
     u'abais',
     u'aban'
    ]
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.incomplete_past_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.incomplete_past_tense] = [
     u'ía',
     u'ías',
     u'ía',
     u'íamos',
     u'íais',
     u'ían'
    ]
"""
past tense
"""
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.past_tense] = [
         u'é',
         u'aste',
         u'ó',
        Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][Persons.first_person_plural],
         u'asteis',
         u'aron' 
    ]
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.past_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.past_tense] =  [
         u'í',
         u'iste',
         u'ió',
        Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_tense][Persons.first_person_plural],
         u'isteis',
         u'ieron' 
    ]
"""
Future - present tense endings for haber
"""
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.future_tense] = \
    Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.future_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.future_tense] =  [
         u'é',
         u'ás',
         u'á',
         u'emos',
         u'éis',
         u'án' 
    ]
 
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.conditional_tense] = \
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.conditional_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.conditional_tense] = \
    Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.incomplete_past_tense]
 
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_subjective_tense] = list(Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_tense])
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_subjective_tense][Persons.first_person_singular] =  u'e'     
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_subjective_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_subjective_tense] =\
    list(Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense])
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_subjective_tense][Persons.first_person_singular] =  u'a'       
 
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.past_subjective_tense] =\
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.past_subjective_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.past_subjective_tense] = [
     u'ra',
     u'ras',
     u'ra',
     u'ramos',
     u'rais',
     u'ran'
    ]

Irregular_Past_Endings = copy.deepcopy(Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.past_tense])
Irregular_Past_Endings[Persons.first_person_singular] = u'e'
Irregular_Past_Endings[Persons.third_person_singular] = u'o'