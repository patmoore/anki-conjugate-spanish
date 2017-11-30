#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
import sys
from conjugate_spanish import Espanol_Dictionary
from conjugate_spanish.constants import Tense, Tenses, Persons, Person,\
    IrregularNature
from conjugate_spanish.phrase_printer import ScreenPrinter, CsvPrinter
Espanol_Dictionary.load()
irregular_nature=IrregularNature.radical_stem_change
if len(sys.argv) < 2:
    sorted_keys = list(Espanol_Dictionary.verbDictionary.keys())
    sorted_keys.sort()
    for key in sorted_keys:
        phrase = Espanol_Dictionary.verbDictionary.get(key)
        printer = CsvPrinter(phrase, irregular_nature=irregular_nature)
        printer.print(tenses=Tenses.all)
    exit(0)
    
phrase_str = sys.argv[1]
phrase = Espanol_Dictionary.get(phrase_str)
if phrase is None:
    print(phrase_str+ " : not in dictionary")
    exit(1)

    
if len(sys.argv) < 3:
    printer = ScreenPrinter(phrase, irregular_nature=irregular_nature)
    printer.print()
    exit(0)    

tenseIndex=int(sys.argv[2])
tense = Tenses[tenseIndex]
if len(sys.argv) < 4:
    printer = ScreenPrinter(phrase, irregular_nature=IrregularNature.regular)
    printer.print(tenses=[tense])
    exit(0)

personIndex = int(sys.argv[3])
person = Persons[personIndex]
print(tense.human_readable + ", " + person.human_readable)
print(phrase.conjugate(tenseIndex, personIndex).full_conjugation)
print(phrase.conjugation_tracking.get_conjugation_notes(tenseIndex, personIndex))

