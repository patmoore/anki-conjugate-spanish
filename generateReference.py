# -*- coding: utf-8 -*-
from __future__ import print_function
import conjugate_spanish
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get,Verb_Dictionary_load,Verb_Dictionary_export
Verb_Dictionary_load()
Verb_Dictionary_export('501verbs')
def find_print_verb(verb_inf, print_all=False):
    verb = Verb_Dictionary_get(verb_inf)
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
    
fivehundredone = [u'desvestir', u'abatir', u'abrasar', u'abrazar', u'abrir', u'absolver', u'tener', u'abstenerse', u'acabar/por', u'advertir',u'caber',u"delinquir"]
verb_inf = fivehundredone[len(fivehundredone)-1]
find_print_verb(verb_inf, True)

for verb_inf in fivehundredone:
    find_print_verb(verb_inf)
    