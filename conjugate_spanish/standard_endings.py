# -*- coding: utf-8 -*-
from __init__ import *

Standard_Conjugation_Endings = [ [ [] for t in range(len(Tenses)) ] for v in range(len(infinitive_endings))]

"""
present tense
""" 
Standard_Conjugation_Endings[ar_verb][present_tense] = [
    lambda tense, person : u"o",
    lambda tense, person : u"as",
    lambda tense, person : u"a",
    lambda tense, person : u"amos",
    lambda tense, person : u"áis",
    lambda tense, person : u"an"
    ]  
Standard_Conjugation_Endings[er_verb][present_tense] = [
    Standard_Conjugation_Endings[ar_verb][present_tense][first_person_singular],
    lambda tense, person : u'es',
    lambda tense, person : u'e',
    lambda tense, person : u'emos',
    lambda tense, person : u'éis',
    lambda tense, person : u'en'
    ]  
Standard_Conjugation_Endings[ir_verb][present_tense] = list(Standard_Conjugation_Endings[er_verb][present_tense])
Standard_Conjugation_Endings[ir_verb][present_tense][first_person_plural] = lambda tense, person : u'imos'
Standard_Conjugation_Endings[ir_verb][present_tense][second_person_plural] = lambda tense, person : u'ís'

"""
imperfect tense
"""
Standard_Conjugation_Endings[ar_verb][incomplete_past_tense] = [
    lambda tense, person : u'aba',
    lambda tense, person : u'abas',
    lambda tense, person : u'aba',
    lambda tense, person : u'ábamos',
    lambda tense, person : u'abais',
    lambda tense, person : u'aban'
    ]
Standard_Conjugation_Endings[er_verb][incomplete_past_tense] = Standard_Conjugation_Endings[ir_verb][incomplete_past_tense] = [
    lambda tense, person : u'ía',
    lambda tense, person : u'ías',
    lambda tense, person : u'ía',
    lambda tense, person : u'íamos',
    lambda tense, person : u'íais',
    lambda tense, person : u'ían'
    ]
"""
past tense
"""
Standard_Conjugation_Endings[ar_verb][past_tense] = [
        lambda tense, person : u'é',
        lambda tense, person : u'aste',
        lambda tense, person : u'ó',
        Standard_Conjugation_Endings[ar_verb][present_tense][first_person_plural],
        lambda tense, person : u'asteis',
        lambda tense, person : u'aron' 
    ]
Standard_Conjugation_Endings[er_verb][past_tense] = Standard_Conjugation_Endings[ir_verb][past_tense] =  [
        lambda tense, person : u'í',
        lambda tense, person : u'iste',
        lambda tense, person : u'ió',
        Standard_Conjugation_Endings[ir_verb][present_tense][first_person_plural],
        lambda tense, person : u'isteis',
        lambda tense, person : u'ieron' 
    ]
"""
Future - present tense endings for haber
"""
Standard_Conjugation_Endings[ar_verb][future_tense] = \
    Standard_Conjugation_Endings[er_verb][future_tense] = Standard_Conjugation_Endings[ir_verb][future_tense] =  [
        lambda tense, person : u'é',
        lambda tense, person : u'ás',
        lambda tense, person : u'á',
        lambda tense, person : u'emos',
        lambda tense, person : u'éis',
        lambda tense, person : u'án' 
    ]
 
Standard_Conjugation_Endings[ar_verb][conditional_tense] = \
Standard_Conjugation_Endings[er_verb][conditional_tense] = Standard_Conjugation_Endings[ir_verb][conditional_tense] = \
    Standard_Conjugation_Endings[er_verb][incomplete_past_tense]
 
Standard_Conjugation_Endings[ar_verb][present_subjective_tense] = list(Standard_Conjugation_Endings[er_verb][present_tense])
Standard_Conjugation_Endings[ar_verb][present_subjective_tense][first_person_singular] = lambda tense, person : u'e'     
Standard_Conjugation_Endings[er_verb][present_subjective_tense] = Standard_Conjugation_Endings[ir_verb][present_subjective_tense] =\
    list(Standard_Conjugation_Endings[ar_verb][present_tense])
Standard_Conjugation_Endings[er_verb][present_subjective_tense][first_person_singular] = lambda tense, person : u'a'       
 
Standard_Conjugation_Endings[ar_verb][past_subjective_tense] =\
Standard_Conjugation_Endings[er_verb][past_subjective_tense] = Standard_Conjugation_Endings[ir_verb][past_subjective_tense] = [
    lambda tense, person : u'ra',
    lambda tense, person : u'ras',
    lambda tense, person : u'ra',
    lambda tense, person : u'ramos',
    lambda tense, person : u'ráis',
    lambda tense, person : u'ran'
    ]