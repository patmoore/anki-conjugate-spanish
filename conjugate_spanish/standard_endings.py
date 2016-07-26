# -*- coding: utf-8 -*-
from .constants import Tenses,Persons,Infinitive_Endings

Standard_Conjugation_Endings = [ [ [] for t in range(len(Tenses)) ] for v in range(len(Infinitive_Endings))]

"""
present tense
""" 
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense] = [
     "o",
     "as",
     "a",
     "amos",
     "áis",
     "an"
    ]  
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_tense] = [
    Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][Persons.first_person_singular],
     'es',
     'e',
     'emos',
     'éis',
     'en'
    ]  
Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_tense] = list(Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_tense])
Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_tense][Persons.first_person_plural] =  'imos'
Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_tense][Persons.second_person_plural] =  'ís'

"""
imperfect tense
"""
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.incomplete_past_tense] = [
     'aba',
     'abas',
     'aba',
     'ábamos',
     'abais',
     'aban'
    ]
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.incomplete_past_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.incomplete_past_tense] = [
     'ía',
     'ías',
     'ía',
     'íamos',
     'íais',
     'ían'
    ]
"""
past tense
"""
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.past_tense] = [
         'é',
         'aste',
         'ó',
        Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][Persons.first_person_plural],
         'asteis',
         'aron' 
    ]
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.past_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.past_tense] =  [
         'í',
         'iste',
         'ió',
        Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_tense][Persons.first_person_plural],
         'isteis',
         'ieron' 
    ]
"""
Future - present tense endings for haber
"""
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.future_tense] = \
    Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.future_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.future_tense] =  [
         'é',
         'ás',
         'á',
         'emos',
         'éis',
         'án' 
    ]
 
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.conditional_tense] = \
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.conditional_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.conditional_tense] = \
    Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.incomplete_past_tense]
 
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_subjective_tense] = list(Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_tense])
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_subjective_tense][Persons.first_person_singular] =  'e'     
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_subjective_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.present_subjective_tense] =\
    list(Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense])
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.present_subjective_tense][Persons.first_person_singular] =  'a'       
 
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.past_subjective_tense] =\
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.past_subjective_tense] = Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.past_subjective_tense] = [
     'ra',
     'ras',
     'ra',
     'ramos',
     'rais',
     'ran'
    ]

"""
Imperative 
"""
for inf in range(len(Infinitive_Endings)):
    Standard_Conjugation_Endings[inf][Tenses.imperative_positive] = [None] * len(Persons)
    Standard_Conjugation_Endings[inf][Tenses.imperative_negative] = [None] * len(Persons)
    
# -ing verb
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.gerund] = 'ando'
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.gerund] = 'iendo'
Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.gerund] = 'iendo'
# -ed verb
Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.past_participle] = \
  Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.adjective] = 'ado'
Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.past_participle] = \
  Standard_Conjugation_Endings[Infinitive_Endings.er_verb][Tenses.adjective] = \
  Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.past_participle] = \
  Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][Tenses.adjective] = 'ido'

