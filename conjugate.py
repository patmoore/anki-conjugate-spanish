#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
import sys
import conjugate_spanish
from conjugate_spanish import Espanol_Dictionary
from conjugate_spanish.constants import Tense, Tenses, Persons, Person
Espanol_Dictionary.load()
if len(sys.argv) < 2:
#     print("verb tense person")
#     print("tenses=" + str(Tenses))
#     print("persons=" + str(Persons))
    for verb in Espanol_Dictionary.verbDictionary.values():
        verb.conjugate_all_tenses()
    exit(0)
    
phrase_str = sys.argv[1]
phrase = Espanol_Dictionary.get(phrase_str)

def print_tense(tense, conjugations):
    print(tense.human_readable+ "(" 
      + str(tense._value_) + "):")
    if tense in Tenses.Person_Agnostic:
        print('\t' + conjugations, phrase.conjugation_tracking.get_conjugation_notes(tense))
    else:
        print('\t', end='')
        for person in Person:
            print(person.human_readable + "(" 
              + str(person._value_) + "):", end=' ')
            
            if conjugations[person] is None:
                print("---", end='; ')
            else:    
                print(conjugations[person], end='; ')
                print(phrase.conjugation_tracking.get_conjugation_notes(tense, person))
    print()
    
if len(sys.argv) < 3:
    conjugations = phrase.conjugate_all_tenses()
    for tense in Tense:
        print_tense(tense, conjugations[tense])
    print(phrase.conjugation_tracking)
    exit(0)    

tenseIndex=int(sys.argv[2])
tense = Tenses[tenseIndex]
if len(sys.argv) < 4:
    conjugation = phrase.conjugate_tense(tenseIndex)
    print_tense(tense, conjugation)
    exit(0)

personIndex = int(sys.argv[3])
person = Persons[personIndex]
print(tense.human_readable + ", " + person.human_readable)
print(phrase.conjugate(tenseIndex, personIndex))
print(phrase.conjugation_tracking.get_conjugation_notes(tenseIndex, personIndex))

