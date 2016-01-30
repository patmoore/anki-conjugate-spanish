# -*- coding: utf-8 -*-
import conjugate_spanish
from conjugate_spanish.verb_dictionary import Verb_Dictionary_get

def find_print_verb(verb_inf):
    verb = Verb_Dictionary_get(verb_inf)
    print repr(verb.inf_verb_string).decode("unicode-escape")
    verb.print_irregular_tenses()
    print repr(verb.overrides_applied()).decode("unicode-escape")
    print '----------------------'
    
fivehundredone = [u'abatir', u'abrasar', u'abrazar', u'abrir', u'absolver']
verb_inf = fivehundredone[len(fivehundredone)-1]
find_print_verb(verb_inf)

for verb_inf in fivehundredone:
    find_print_verb(verb_inf)
    