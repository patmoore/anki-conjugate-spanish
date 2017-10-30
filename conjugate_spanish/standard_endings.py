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
        if conjugation_notes.tense in Tenses.Person_Agnostic:
            return Standard_Conjugation_Endings[verb_ending_index][conjugation_notes.tense]
        else:
            return Standard_Conjugation_Endings[verb_ending_index][conjugation_notes.tense][conjugation_notes.person]
    
class Infinitive_Endings_(BaseConsts_):
    ar_verb = Infinitive_Ending.ar_verb
    er_verb = Infinitive_Ending.er_verb
    ir_verb = Infinitive_Ending.ir_verb
    
         
     
Infinitive_Endings = Infinitive_Endings_(
    [Infinitive_Ending.ar_verb, 
         Infinitive_Ending.er_verb, 
         Infinitive_Ending.ir_verb])

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