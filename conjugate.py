#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
import sys
from conjugate_spanish import Espanol_Dictionary
from conjugate_spanish.constants import Tense, Tenses, Persons, Person,\
    IrregularNature
from conjugate_spanish.phrase_printer import ScreenPrinter
Espanol_Dictionary.load()
if len(sys.argv) < 2:
#     print("verb tense person")
#     print("tenses=" + str(Tenses))
#     print("persons=" + str(Persons))
    for phrase in Espanol_Dictionary.verbDictionary.values():
        printer = ScreenPrinter(phrase, irregular_nature=IrregularNature.sound_consistence)
        printer.print(tenses=Tenses.all)
    exit(0)
    
phrase_str = sys.argv[1]
phrase = Espanol_Dictionary.get(phrase_str)
printer = ScreenPrinter(phrase, irregular_nature=IrregularNature.sound_consistence)
    
if len(sys.argv) < 3:
    printer.print()
    exit(0)    

tenseIndex=int(sys.argv[2])
tense = Tenses[tenseIndex]
if len(sys.argv) < 4:
    printer.print(tenses=[tense])
    exit(0)

personIndex = int(sys.argv[3])
person = Persons[personIndex]
print(tense.human_readable + ", " + person.human_readable)
print(phrase.conjugate(tenseIndex, personIndex).full_conjugation)
print(phrase.conjugation_tracking.get_conjugation_notes(tenseIndex, personIndex))

