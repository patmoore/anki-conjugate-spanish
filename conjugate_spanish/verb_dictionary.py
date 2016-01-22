# -*- coding: utf-8 -*-

# These are the standard words (special case)
import codecs
import csv
from verb import Verb
from constants import Persons,Tenses

Verb_Dictionary = {}
def Verb_Dictionary_add(inf_ending, definition, conjugation_overrides=None,prefix=None):
    try:
        verb = Verb(inf_ending, definition,conjugation_overrides=conjugation_overrides)
    except Exception as e:
        print "while adding to verb_dictionary", repr(e)
        
    Verb_Dictionary[inf_ending] = verb
    return verb


import special_cases

csvfile = codecs.open('./conjugate_spanish/dictionary.csv', mode='r' )
reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
try:
    # discard header
#     csvfile.readline()
    for line in reader:
        try:
            verb = Verb_Dictionary_add(**line)
#             print repr(verb.conjugate(Tenses.present_tense, Persons.third_person_singular))
#             c= verb.conjugate_all_tenses()
#             print repr(c).decode("unicode-escape")
        except Exception as e:
            print "error reading dictionary.csv: ", line            
except Exception as e:
    print "error reading dictionary.csv"