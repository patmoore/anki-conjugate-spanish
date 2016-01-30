# -*- coding: utf-8 -*-

# These are the standard words (special case)
import codecs
import csv
import six
import json
from verb import Verb
from constants import Persons,Tenses, get_iterable
from conjugation_override import ConjugationOverride

Verb_Dictionary = {}
def Verb_Dictionary_add(inf_ending, definition, conjugation_overrides=None,prefix=None, manual_overrides=None):
    if conjugation_overrides == u'':
        conjugation_overrides = None
    elif isinstance(conjugation_overrides, six.string_types):
        conjugation_overrides = conjugation_overrides.split(",")
            
    if manual_overrides is not None and manual_overrides != u'':
        try:
            manual_overrides = json.loads(manual_overrides, 'utf-8')
        except ValueError as e:
            print "while parsing json manual_overrides to verb_dictionary", repr(e)
            return
        
        conjugation_override = ConjugationOverride(key=inf_ending+"_irregular",manual_overrides=manual_overrides)
    
        if conjugation_overrides is None:
            conjugation_overrides = [conjugation_override]
        else:
            conjugation_overrides.append(conjugation_override)
                                
    verb = Verb(inf_ending, definition,conjugation_overrides=conjugation_overrides)        
    Verb_Dictionary[inf_ending] = verb
#     print "Adding "+verb.inf_verb_string
    return verb

def Verb_Dictionary_get(inf_ending):
    return Verb_Dictionary.get(inf_ending)

import special_cases

for fileName in ['irregulars','dictionary']:
    csvfile = codecs.open('./conjugate_spanish/dictionaries/'+fileName+'.csv', mode='r' )
    reader = csv.DictReader(csvfile, skipinitialspace=True)
    try:
        for line in reader:
            try:
                verb = Verb_Dictionary_add(**line)
    #             print repr(c).decode("unicode-escape")
            except Exception as e:
                print "error reading "+fileName+".csv: ", line, e            
    except Exception as e:
        print "error reading "+fileName+".csv: ", e
    
for fileName, conjugation_override in six.iteritems({u"e2i":u"e:i", u"o2ue": u"o:ue", u"e2ie":u"e:ie"}):
    csvfile = codecs.open('./conjugate_spanish/dictionaries/'+fileName+".csv", mode='r' )
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"',skipinitialspace=True)
    try:
        for line in reader:
            try:
                if 'conjugation_overrides' in line and line['conjugation_overrides'] is not None and len(line['conjugation_overrides']) > 0:
                    line['conjugation_overrides'].append(conjugation_override)
                else:
                    line['conjugation_overrides'] = [ conjugation_override ]
                     
                verb = Verb_Dictionary_add(**line)
    #             print repr(c).decode("unicode-escape")
            except Exception as e:
                print e,":error reading ", line            
    except Exception as e:
        print "error reading dictionary.csv"