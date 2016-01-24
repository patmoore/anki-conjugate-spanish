# -*- coding: utf-8 -*-

# These are the standard words (special case)
import codecs
import csv
import six
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

csvfile = codecs.open('./conjugate_spanish/dictionaries/dictionary.csv', mode='r' )
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
    
for fileName, conjugation_override in six.iteritems({u"e2i":u"e:i", u"o2ue": u"o:ue", u"e2ie":u"e:ie"}):
    csvfile = codecs.open('./conjugate_spanish/dictionaries/'+fileName+".csv", mode='r' )
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    try:
        # discard header
    #     csvfile.readline()
        for line in reader:
            try:
                if 'conjugation_overrides' in line and line['conjugation_overrides'] is not None and len(line['conjugation_overrides']) > 0:
                    line['conjugation_overrides'].append(conjugation_override)
                else:
                    line['conjugation_overrides'] = [ conjugation_override ]
                     
                verb = Verb_Dictionary_add(**line)
    #             print repr(verb.conjugate(Tenses.present_tense, Persons.third_person_singular))
    #             c= verb.conjugate_all_tenses()
    #             print repr(c).decode("unicode-escape")
            except Exception as e:
                print e,":error reading ", line            
    except Exception as e:
        print "error reading dictionary.csv"