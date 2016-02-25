# -*- coding: utf-8 -*-
from __future__ import print_function
# These are the standard words (special case)
import codecs
import csv
import six
import json
from verb import Verb

from constants import Persons, Tenses, get_iterable
from conjugation_override import ConjugationOverride

Verb_Dictionary = {}
def Verb_Dictionary_add(inf_ending, definition, conjugation_overrides=None,base_verb=None, manual_overrides=None, **kwargs):
    if conjugation_overrides == u'':
        conjugation_overrides = None
    elif isinstance(conjugation_overrides, six.string_types):
        conjugation_overrides = conjugation_overrides.split(",")
            
    if manual_overrides is not None and manual_overrides != u'':
        try:
            manual_overrides = json.loads(manual_overrides, 'utf-8')
        except ValueError as e:
            print("while parsing json manual_overrides to verb_dictionary", repr(e))
            print("manual_overrides="+manual_overrides)
            return
        
        conjugation_override = ConjugationOverride(key=inf_ending+"_irregular",manual_overrides=manual_overrides)
    
        if conjugation_overrides is None:
            conjugation_overrides = [conjugation_override]
        else:
            conjugation_overrides.append(conjugation_override)
                                
    verb = Verb(inf_ending, definition,conjugation_overrides=conjugation_overrides, base_verb=base_verb)        
    Verb_Dictionary[inf_ending] = verb
#     print "Adding "+verb.inf_verb_string
    return verb

def Verb_Dictionary_get(inf_ending):
    return Verb_Dictionary.get(inf_ending)

def Verb_Dictionary_load():
    import special_cases
    
    for fileNameBase in ['irregulars','dictionary']:
        fileName = './conjugate_spanish/dictionaries/'+fileNameBase+'.csv'
        print("reading "+fileName)
        csvfile = codecs.open(fileName, mode='r' )
        reader = csv.DictReader(csvfile, skipinitialspace=True)
        try:
            for line in reader:
                try:
                    verb = Verb_Dictionary_add(**line)
        #             print repr(c).decode("unicode-escape")
                except Exception as e:
                    print("error reading "+fileName+": "+ line+ e)            
        except Exception as e:
            print("error reading "+fileName+": "+e.message+" line="+line)
