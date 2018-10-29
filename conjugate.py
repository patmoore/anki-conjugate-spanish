#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from conjugate_spanish.constants import re_compile
from conjugate_spanish import Espanol_Dictionary, Verb, ScreenPrinter
from conjugate_spanish.constants import Tense, Person, IrregularNature
from conjugate_spanish.phrase_printers.csv_printer import CsvPrinter
from conjugate_spanish.phrase_printers.say_printer import SayPrinter
from conjugate_spanish.conjugation_override import Standard_Overrides
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
parser.add_argument('--base','-b', dest='use_as_base_verb', action='store_true',
                    default=False,
                    help='print out the words with supplied base verb (no conjugation unless -c)')
parser.add_argument('--no','-n', dest='no_conjugation', action='store_true',
                    default=None,
                    help='do not conjugate; just list verb')
parser.add_argument('-c', dest='no_conjugation', action='store_false',
                    default=None,
                    help='Conjugate the verb(s)')
parser.add_argument('--noguess', '--ng', dest='guess',
                    action='store_false',
                    default=True,
                    help="If verb is not in the dictionary apply rules to make a guess on conjugation")
parser.add_argument('--fam', dest='force_auto_match', action='store_true',
                    default=False,
                    help='For a word being guessed at force auto_match=True to see what Conjugation overrides would match.')
parser.add_argument('--verbose','-v', dest='verbose',
                    action='store_const',
                    const=1,
                    help='Show how conjugation was determined')
parser.add_argument('--vv', dest='verbose',
                    action='store_const',
                    const=2,
                    help='Show how conjugation was determined')
parser.add_argument('--list-irregulars', '--lir', dest='list_irregularities',
                    action='store_true',
                    default=False)
parser.add_argument('--list-generated','--lg',
                    action='store_true',
                    dest='list_generated',
                    default=False)
parser.add_argument('--conjugation-override-key','-k', dest='conjugation_override_key',
                    type=str)
parser.add_argument('--csv', dest='printer_clazz', action='store_const',
                    const=CsvPrinter,
                    help='print in csv format')
parser.add_argument('--speak','-s', dest="printer_clazz",
                    action='store_const',
                    const=SayPrinter,
                    help="call the 'say' program to speak the spanish")
parser.add_argument('--tenses', dest='tenses', 
                    action=tenseAction,
                    # nargs='*',
                    help='select tenses')

for tense in Tense.all():
    parser.add_argument("--"+tense.short_key, dest='tenses',
                        action='append_const',
                        const=tense,
                        help='Select the {} tense'.format(str(tense))
                        )
parser.add_argument('--persons', dest='persons',
                    action=personAction,
                    help='select persons')
parser.add_argument('--all-persons', dest='persons',
                    action='store_const',
                    const=Person.all(),
                    help='we skip vosotos because that person is not common')

for person in Person.all():
    parser.add_argument("--"+person.short_key, dest='persons',
                        action='append_const',
                        const=person,
                        help='Select the {} person'.format(str(person))
                        )
parser.add_argument('--irregular','-i', dest='irregular_nature',
                    action=irregularAction,
                    help='select minimum irregularity for expansion.')
for irregularNature in IrregularNature.all_except(IrregularNature.base):
    parser.add_argument("--"+irregularNature.short_key, dest='irregular_nature',
                        action='append_const',
                        const=irregularNature,
                        help='Select the {} irregular nature'.format(str(irregularNature))
                        )
args = parser.parse_args()

if args.no_conjugation is None:
    args.no_conjugation = args.use_as_base_verb or args.conjugation_override_key is not None

args.printer_clazz = args.printer_clazz or ScreenPrinter
args.irregular_nature = args.irregular_nature or [IrregularNature.regular]
args.tenses = args.tenses or Tense.all()
args.persons = args.persons or Person.all_except(Person.second_person_plural)
options={
    "verbose": args.verbose or 0
}
verb=None
if args.list_irregularities:
    # this means we only see the standard irregularities
    Standard_Overrides.print_keys_documentation()
    exit

if args.list_generated:
    Espanol_Dictionary.list_generated()
    exit


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
        if phrase is None:
            print("{} not in dictionary".format(key))
            if not args.guess:
                return
            else:
                phrase=Verb.importString(key, force_auto_match=args.force_auto_match)
        if args.no_conjugation:
            print("{} : {} ( {} )".format(phrase.full_phrase, phrase.definition,
                                          phrase.complete_overrides_string))
        elif not phrase.is_phrase:
            printer = args.printer_clazz(phrase, irregular_nature=args.irregular_nature[0], options=options)
            printer.print(tenses=args.tenses, persons=args.persons)
        else:
            print("'{}' is a phrase. (Not conjugated yet)".format(phrase))
    
Espanol_Dictionary.load()

if args.conjugation_override_key:
    args.phrases = Espanol_Dictionary.get_by_irregularity(irregular_nature=IrregularNature.sound_consistence, conjugation_override_key=args.conjugation_override_key )
print_all()
# print(tense.human_readable + ", " + person.human_readable)
# print(phrase.conjugate(tenseIndex, personIndex).full_conjugation)
# print(phrase.conjugation_tracking.get_conjugation_notes(tenseIndex, personIndex))

