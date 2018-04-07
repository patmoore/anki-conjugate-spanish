# -*- coding: utf-8 -*-

import conjugate_spanish
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
from conjugate_spanish.conjugation_override import Standard_Overrides
Verb_Dictionary.load()

Verb_Dictionary.export('501verbs')
Verb_Dictionary.export('501verbs', outputfile='regular', testfn=lambda verb: verb.is_regular)
for override in Standard_Overrides.values():
    filename = override.key.replace(':','2')
    Verb_Dictionary.export('501verbs', outputfile=filename, testfn=lambda verb: verb.has_override_applied(override.key))
def find_print_verb(verb_inf, print_all=False):
    verb = Verb_Dictionary.get(verb_inf)
    if verb is None:
        print(verb_inf+": could not find this verb - not loaded yet?")
    else:
        print(repr(verb.inf_verb_string).decode("unicode-escape"))
        if print_all:
            verb.print_all_tenses()
        else:
            verb.print_irregular_tenses()
        print(repr(verb.overrides_applied()).decode("unicode-escape"))
        print('----------------------')
    
# fivehundredone = [u'desvestir', u'abatir', u'abrasar', u'abrazar', u'abrir', u'absolver', u'tener', u'abstenerse', u'acabar/por', u'advertir',u'caber',u"delinquir"]
# verb_inf = fivehundredone[len(fivehundredone)-1]
# find_print_verb(verb_inf, True)
# 
# for verb_inf in fivehundredone:
#     find_print_verb(verb_inf)
    