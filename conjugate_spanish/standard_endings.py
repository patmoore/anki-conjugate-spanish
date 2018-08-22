# -*- coding: utf-8 -*-
from .constants import *

class Infinitive_Ending(BaseConst):
    ar_verb = (0, 'ar', '-ar')
    er_verb = (1, 'er', '-er')
    ir_verb = (2, 'ir', '-ir')
    a_ir_verb = (2, 'ír', '-ír')
    def get_standard_conjugation_ending(self, conjugation_notes, verb_ending_index):
        """
        verb_ending_index - eliminate asap - this should be the code ( but not certain how the ír verbs are handled) 
        """
        if conjugation_notes.tense in Tense.Person_Agnostic():
            return Standard_Conjugation_Endings[verb_ending_index][conjugation_notes.tense]
        else:
            return Standard_Conjugation_Endings[verb_ending_index][conjugation_notes.tense][conjugation_notes.person]

Standard_Conjugation_Endings = [ [ [] for t in range(len(Tense)) ] for v in range(len(Infinitive_Ending))]

"""
present tense
""" 
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.present_tense] = [
     "o",
     "as",
     "a",
     "amos",
     "áis",
     "an"
    ]  
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.present_tense] = [
    Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.present_tense][Person.first_person_singular],
     'es',
     'e',
     'emos',
     'éis',
     'en'
    ]  
Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.present_tense] = list(Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.present_tense])
Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.present_tense][Person.first_person_plural] =  'imos'
Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.present_tense][Person.second_person_plural] =  'ís'

"""
imperfect tense
"""
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.incomplete_past_tense] = [
     'aba',
     'abas',
     'aba',
     'ábamos',
     'abais',
     'aban'
    ]
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.incomplete_past_tense] = Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.incomplete_past_tense] = [
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
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.past_tense] = [
         'é',
         'aste',
         'ó',
        Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.present_tense][Person.first_person_plural],
         'asteis',
         'aron' 
    ]
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.past_tense] = Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.past_tense] =  [
         'í',
         'iste',
         'ió',
        Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.present_tense][Person.first_person_plural],
         'isteis',
         'ieron' 
    ]
"""
Future - present tense endings for haber
"""
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.future_tense] = \
    Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.future_tense] = Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.future_tense] =  [
         'é',
         'ás',
         'á',
         'emos',
         'éis',
         'án' 
    ]
 
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.conditional_tense] = \
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.conditional_tense] = Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.conditional_tense] = \
    Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.incomplete_past_tense]
 
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.present_subjective_tense] = list(Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.present_tense])
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.present_subjective_tense][Person.first_person_singular] =  'e'
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.present_subjective_tense] = Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.present_subjective_tense] =\
    list(Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.present_tense])
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.present_subjective_tense][Person.first_person_singular] =  'a'
 
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.past_subjective_tense] =\
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.past_subjective_tense] = Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.past_subjective_tense] = [
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
for inf in range(len(Infinitive_Ending)):
    Standard_Conjugation_Endings[inf][Tense.imperative_positive] = [None] * len(Person)
    Standard_Conjugation_Endings[inf][Tense.imperative_negative] = [None] * len(Person)
    
# -ing verb
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.gerund] = 'ando'
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.gerund] = 'iendo'
Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.gerund] = 'iendo'
# -ed verb
Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.past_participle] = \
  Standard_Conjugation_Endings[Infinitive_Ending.ar_verb][Tense.adjective] = 'ado'
Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.past_participle] = \
  Standard_Conjugation_Endings[Infinitive_Ending.er_verb][Tense.adjective] = \
  Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.past_participle] = \
  Standard_Conjugation_Endings[Infinitive_Ending.ir_verb][Tense.adjective] = 'ido'