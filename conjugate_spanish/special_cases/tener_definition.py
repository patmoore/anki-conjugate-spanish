# -*- coding: utf-8 -*-
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.constants import Tenses,Persons
from conjugate_spanish.verb_dictionary import Verb_Dictionary_add

_conjugation_overrides = ConjugationOverride(parents=[u"go",u"e:ie", u'e_and_o', u'e2d',u'imp_inf_stem_only'], key=u"tener")
_conjugation_overrides.override_tense_stem(Tenses.past_tense, u'tuv')
Verb_Dictionary_add(u'tener', u'to be', conjugation_overrides=[ u"-e:ie_1sp",_conjugation_overrides])
