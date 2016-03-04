# -*- coding: utf-8 -*-
from __future__ import print_function
# These are the standard words (special case)
import codecs
import traceback
import csv
import six
from verb import Verb

from constants import make_unicode
from conjugation_override import ConjugationOverride

Verb_Dictionary = {}
Verb_Dictionary_By = {}
def Verb_Dictionary_add(phrase, definition, conjugation_overrides=None,base_verb=None, manual_overrides=None, **kwargs):
    if conjugation_overrides == u'':
        conjugation_overrides = None
    elif isinstance(conjugation_overrides, six.string_types):
        conjugation_overrides = conjugation_overrides.split(",")
            
    if manual_overrides is not None and manual_overrides != u'':        
        conjugation_override = ConjugationOverride.create_from_json(phrase+"_irregular",manual_overrides)
    
        if conjugation_overrides is None:
            conjugation_overrides = [conjugation_override]
        else:
            conjugation_overrides.append(conjugation_override)
                                
    verb = Verb(phrase, definition,conjugation_overrides=conjugation_overrides, base_verb=base_verb)  
    if phrase in Verb_Dictionary:
        print(phrase+" already in dictionary")
    else:      
        Verb_Dictionary[verb.full_phrase] = verb
#     print "Adding "+verb.inf_verb_string
    return verb

def Verb_Dictionary_get(phrase):
    return Verb_Dictionary.get(phrase)

def Verb_Dictionary_load():
    import special_cases
    
    for fileNameBase in ['501verbs','501extendedverbs']:
        fileName = './conjugate_spanish/dictionaries/'+fileNameBase+'.csv'
        verbs = []
        Verb_Dictionary_By[fileNameBase] = verbs
        print("reading "+fileName)
        with codecs.open(fileName, mode='r' ) as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            try:
                for line in reader:
                    definition = {u'definition':u''}
                    for key,value in line.iteritems():
                        _value = make_unicode(value)
                        if _value != u'' and _value is not None:
                            definition[make_unicode(key)] = _value 
                    try:
                        verb = Verb_Dictionary_add(**definition)
                        verbs.append(verb.full_phrase)
                        print (verb.full_phrase)
                    except Exception as e:
                        print("error reading "+fileName+": "+ repr(definition)+ repr(e))
                        traceback.print_exc()            
            except Exception as e:
                print("error reading "+fileName+": "+e.message+" line="+repr(line), repr(e))
                traceback.print_exc()

def Verb_Dictionary_export(source):
    with codecs.open('./conjugate_spanish/expanded/'+source+"-expanded.csv", "w", "utf-8-sig") as f:
        for phrase in Verb_Dictionary_By[source]:
            verb = Verb_Dictionary_get(phrase)   
            print("conjugating>>"+verb.full_phrase)     
            f.write(verb.full_phrase+u":"+repr(verb.overrides_applied())+u":"+repr(verb.conjugate_all_tenses())+u"\n")
    
    f.close()