#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
import sys
import conjugate_spanish
from conjugate_spanish import Espanol_Dictionary
from conjugate_spanish.constants import Tenses, Persons
Espanol_Dictionary.load()
if len(sys.argv) < 2:
    print("verb tense person")
    exit(0)
    
phrase_str = sys.argv[1]
phrase = Espanol_Dictionary.get(phrase_str)

if len(sys.argv) < 3:
    print(phrase.conjugate_all_tenses())
    exit(0)    

tenseIndex=int(sys.argv[2])
tense = Tenses[tenseIndex]
if len(sys.argv) < 4:
    print(tense)
    print(phrase.conjugate_tense(tenseIndex))
    exit(0)

personIndex = int(sys.argv[3])
person = Persons[personIndex]
print(tense + ", " + person)
print(phrase.conjugate(tenseIndex, personIndex))

