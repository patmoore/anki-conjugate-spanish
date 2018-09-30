#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
from conjugate_spanish.constants import re_compile
from conjugate_spanish import Espanol_Dictionary
from conjugate_spanish.constants import Tense, Tense, Person, IrregularNature
from conjugate_spanish.phrase_printer import ScreenPrinter, CsvPrinter
import argparse

# used to avoid having to enter a number ( which is going away anyhow)
# dest - 'destination' key in the namespace.
class EnumAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(EnumAction, self).__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        # get the previous setting.
        prev = getattr(namespace, self.dest) or [] if hasattr(namespace, self.dest) else []
        prev.append(self._enum.index(values))
        setattr(namespace, self.dest, prev)
        
def tenseAction(**kwargs):
    action = EnumAction(**kwargs)
    action._enum = Tense
    return action

def personAction(**kwargs):
    action = EnumAction(**kwargs)
    action._enum = Person
    return action
 
def irregularAction(**kwargs):
    action = EnumAction(**kwargs)
    action._enum = IrregularNature
    return action       

#Haya (hacer), Vaya (Ir), Sepa (Saber), Sea (Ser), Dé (Dar), éste (estar) 

parser = argparse.ArgumentParser(description='Conjugate spanish verbs')
parser.add_argument('phrases', metavar='phrase', type=str, nargs='*',
                    default=None,
                    help='a verb to conjugate')
parser.add_argument('--csv', dest='printer_clazz', action='store_const',
                    const=CsvPrinter, default=ScreenPrinter,
                    help='print in csv format')
parser.add_argument('--tenses', dest='tenses', 
                    action=tenseAction,
                    nargs='*',
                    help='select tenses')
parser.add_argument('--persons', dest='persons',
                    action=personAction,
                    help='select persons')
parser.add_argument('--irregular','-i', dest='irregular_nature',
                    action=irregularAction,
                    help='select minimum irregularity for expansion.')
parser.add_argument('--base','-b', dest='use_as_base_verb', action='store_true',
                    default=False,
                    help='print out the words with supplied base verb')
parser.add_argument('--no','-n', dest='no_conjugation', action='store_true',
                    default=False,
                    help='do not conjugate just list verb')
parser.add_argument('--verbose','-v', dest='verbose',
                    action='store_true',
                    default=False,
                    help='Show how conjugation was determined')
args = parser.parse_args()
args.irregular_nature = args.irregular_nature or [IrregularNature.regular]
args.tenses = args.tenses or Tense.all()
args.persons = args.persons or Person.all()
options={
    "verbose": args.verbose
}
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
    elif args.use_as_base_verb:
        sorted_keys = []
        for phrase in args.phrases:
            sorted_keys.extend(Espanol_Dictionary.get_derived(phrase))
    else:
        sorted_keys = list(args.phrases)
    sorted_keys.sort()
    for key in sorted_keys:
        phrase = Espanol_Dictionary.get(key)
        if not phrase.is_phrase:
            printer = args.printer_clazz(phrase, irregular_nature=args.irregular_nature[0], options=options)
            printer.print(tenses=args.tenses, persons=args.persons)
    
Espanol_Dictionary.load()
print_all()
# print(tense.human_readable + ", " + person.human_readable)
# print(phrase.conjugate(tenseIndex, personIndex).full_conjugation)
# print(phrase.conjugation_tracking.get_conjugation_notes(tenseIndex, personIndex))

