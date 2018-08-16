#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
from conjugate_spanish.constants import re_compile
from conjugate_spanish import Espanol_Dictionary
from conjugate_spanish.constants import Tense, Tenses, Persons,\
    IrregularNature, IrregularNatures
from conjugate_spanish.phrase_printer import ScreenPrinter, CsvPrinter
import argparse

class EnumAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(EnumAction, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        prev = getattr(namespace, self.dest) if hasattr(namespace, self.dest) else []
        prev +=  self._enum.index(int(values))
        setattr(namespace, self.dest, prev)
        
def tenseAction(**kwargs):
    action = EnumAction(**kwargs)
    action._enum = Tenses
    return action

def personAction(**kwargs):
    action = EnumAction(**kwargs)
    action._enum = Persons
    return action
 
def irregularAction(**kwargs):
    action = EnumAction(**kwargs)
    action._enum = IrregularNatures
    return action       

#Haya (hacer), Vaya (Ir), Sepa (Saber), Sea (Ser), Dé (Dar), éste (estar) 

parser = argparse.ArgumentParser(description='Conjugate spanish verbs')
parser.add_argument('phrases', metavar='phrase', type=str, nargs='*',
                    default=None,
                    help='a verb to conjugate')
parser.add_argument('--printer', dest='printer_clazz', action='store_const',
                    const=CsvPrinter, default=ScreenPrinter,
                    help='print in csv format')
parser.add_argument('--tenses', dest='tenses', 
                    action=tenseAction,
                    nargs='*',
                    default=Tenses.all,
                    help='select tenses')
parser.add_argument('--persons', dest='persons',
                    action=personAction,
                    default=Persons.all,
                    help='select persons')
parser.add_argument('--irregular', dest='irregular_nature', 
                    action=irregularAction,
                    default=IrregularNatures.regular,
                    help='select minimum irregularity for expansion.')
args = parser.parse_args()


options={}
verb=None

spanishize_array = [
        [ re_compile("'a"), 'á'],
        [ re_compile("'e"), 'é'],
        [ re_compile("'i"), 'í'],
        [ re_compile("'o"), 'ó'],
        [ re_compile("'u"), 'ú'],
        [ re_compile("~u"), 'ü'],
        [ re_compile("~n"), 'ñ']
    ]

def spanishize(phrase):
    result = phrase
    for operation, replacement in spanishize_array:
        result = re.sub(operation, replacement, result)
    return result

def print_all():
    if args.phrases is None:
        sorted_keys = list(Espanol_Dictionary.verbDictionary.keys())
    else:
        sorted_keys = list(args.phrases)
    sorted_keys.sort()
    for key in sorted_keys:
        phrase = Espanol_Dictionary.get(key)
        if not phrase.is_phrase:
            printer = args.printer_clazz(phrase, irregular_nature=args.irregular_nature, options=options)
            printer.print(tenses=args.tenses, persons=args.persons)
    
Espanol_Dictionary.load()
print_all()
# print(tense.human_readable + ", " + person.human_readable)
# print(phrase.conjugate(tenseIndex, personIndex).full_conjugation)
# print(phrase.conjugation_tracking.get_conjugation_notes(tenseIndex, personIndex))

