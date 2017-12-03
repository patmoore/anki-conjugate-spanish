#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
import sys
import re
from conjugate_spanish.constants import re_compile
from conjugate_spanish import Espanol_Dictionary
from conjugate_spanish.constants import Tense, Tenses, Persons, Person,\
    IrregularNature
from conjugate_spanish.phrase_printer import ScreenPrinter, CsvPrinter
Espanol_Dictionary.load()
options={}
irregular_nature=IrregularNature.radical_stem_change
if len(sys.argv) < 2:
    sorted_keys = list(Espanol_Dictionary.verbDictionary.keys())
    sorted_keys.sort()
    for key in sorted_keys:
        phrase = Espanol_Dictionary.verbDictionary.get(key)
        if not phrase.is_phrase:
            printer = CsvPrinter(phrase, irregular_nature=irregular_nature, options=options)
            printer.print(tenses=Tenses.all)
    exit(0)
    
arg_str = sys.argv[1]
accent_a = re_compile("'a")
arg_str = re.sub(accent_a, 'á', arg_str)
accent_e = re_compile("'e")
arg_str = re.sub(accent_e, 'é', arg_str)
accent_i = re_compile("'i")
arg_str = re.sub(accent_i, 'í', arg_str)
accent_o = re_compile("'o")
arg_str = re.sub(accent_o, 'ó', arg_str)
accent_u = re_compile("'u")
arg_str = re.sub(accent_u, 'ú', arg_str)
umlaut_u = re_compile("~u")
arg_str = re.sub(umlaut_u, 'ü', arg_str)
ny = re_compile("~n")
phrase_str = re.sub(ny, 'ñ', arg_str)
phrase = Espanol_Dictionary.get(phrase_str)
if phrase is None:
    print(phrase_str+ " : not in dictionary")
    exit(1)

    
if len(sys.argv) < 3:
    printer = ScreenPrinter(phrase, irregular_nature=irregular_nature, options=options)
    printer.print()
    exit(0)    

tenseIndex=int(sys.argv[2])
tense = Tenses[tenseIndex]
if len(sys.argv) < 4:
    printer = ScreenPrinter(phrase, irregular_nature=IrregularNature.regular, options=options)
    printer.print(tenses=[tense])
    exit(0)

personIndex = int(sys.argv[3])
person = Persons[personIndex]
print(tense.human_readable + ", " + person.human_readable)
print(phrase.conjugate(tenseIndex, personIndex).full_conjugation)
print(phrase.conjugation_tracking.get_conjugation_notes(tenseIndex, personIndex))

