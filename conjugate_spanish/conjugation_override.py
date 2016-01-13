# -*- coding: utf-8 -*-
import six
import re
import inspect
from __init__ import *

# TODO need a way of adding notes to overrides
class ConjugationOverride():
    
    def __init__(self, inf_match=None, parent=None, documentation=None, examples=None):
        self.parent = parent
        self.inf_match = inf_match
        
    def __overrides(self, tense, overrides, attr_name, persons):
        if not hasattr(self, attr_name):
            self_overrides = [ None ] * len(Tenses)
            setattr(self, attr_name, self_overrides) 
        else:
            self_overrides = getattr(self, attr_name)
            
        if isinstance(overrides, six.string_types) or inspect.isfunction(overrides):
            if persons is not None:
                if self_overrides[tense] is None:
                    self_overrides[tense] = [None] * len(Persons)
                    
                if isinstance(persons, six.integer_types):
                    # a single person has an override
                    self_overrides[tense][persons] = overrides
                else:
                    for person in persons:
                        self_overrides[tense][person] = overrides
            else:
                # a single stem for all persons of this tense
                self_overrides[tense] = [overrides] * len(Persons)
        else:
            # overrides better be a list
            if self_overrides[tense] is None:
                self_overrides[tense] = [None] * len(Persons)
                
            for person, override in enumerate(overrides):
                if override is not None:
                    self_overrides[tense][person] = override
                    
    def override_tense_stem(self, tense, overrides,persons=None, documentation=None):
        self.__overrides(tense, overrides, 'conjugation_stems', persons)
                    
    def override_tense_ending(self, tense, overrides,persons=None, documentation=None):
        self.__overrides(tense, overrides, 'conjugation_endings',persons)
    
    def override_tense(self, tense, overrides,persons=None, documentation=None):
        """
        Used for case when the entire tense is very irregular
        """
        self.__overrides(tense, overrides, 'conjugations',persons)
        
    def __get_override(self, tense, person, attr_name):
        if hasattr(self, attr_name):
            self_overrides = getattr(self, attr_name)
            if self_overrides[tense] is not None:
            # some overrides exist for this tense        
                if isinstance(self_overrides[tense], six.string_types):
                    # a single different stem for the entire tense
                    return self_overrides[tense]
                elif isinstance(self_overrides[tense][person], six.string_types):
                    # a specific override for the tense/person
                    return self_overrides[tense][person]

        if self.parent is not None:
            override = self.parent.__get_override(tense, person, attr_name)
            return override
            
        return None

    def is_match(self, infinitive):
        if self.inf_match.search(infinitive):
            return True
        else:
            return False

    def apply(self, verb):
        for applies in ['conjugations', 'conjugation_stems', 'conjugation_endings']:
            overrides = getattr(self, applies, None)
            if overrides != None:
                for tense, conjugation_override in enumerate(overrides):
                    if conjugation_override is not None:
                        verb._overrides(tense, conjugation_override, applies)
    
Zar_CO = ConjugationOverride(inf_match=re.compile(u'zar$'), 
    documentation='verbs ending in -zar have z -> c before e',
    examples=[six.u('comenzar'), six.u('lanzar')]
    )
Zar_CO.override_tense_stem(past_tense, lambda self, tense, person: self.stem[:-1]+six.u('c'), first_person_singular)
Zar_CO.override_tense_stem(present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('c'))
print Zar_CO.is_match("comenzar")
Gar_CO = ConjugationOverride(inf_match=re.compile(six.u('gar$')), 
    documentation='verbs ending in -gar have g -> gu before e',
    examples=[six.u('pagar')]
    )
Gar_CO.override_tense_stem(past_tense, lambda self, tense, person: self.stem[:-1]+six.u('gu'), first_person_singular)
Gar_CO.override_tense_stem(present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('gu'))
print Gar_CO.is_match(six.u('pagar'))
Car_CO = ConjugationOverride(inf_match=re.compile(six.u('car$')), 
    documentation='verbs ending in -car have c -> qu before e',
    examples=[six.u('tocar')]
    )
Car_CO.override_tense_stem(past_tense, lambda self, tense, person: self.stem[:-1]+six.u('qu'), first_person_singular)
Car_CO.override_tense_stem(present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('qu'))

# http://www.intro2spanish.com/verbs/listas/master-zco.htm
Cir_Cer_After_Vowel_CO = ConjugationOverride(inf_match=re.compile(six.u('[aeiouáéíóú]c[ie]r$')),
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
    examples=[six.u('aparecer')]
    )
Cir_Cer_After_Vowel_CO.override_tense_stem(present_tense, lambda self, tense, person: self.stem[:-1]+six.u('zc'), first_person_singular)
# Cir_Cer_After_Vowel_CO.override_tense_stem(present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('zc'))

Cir_Cer_After_Const_CO = ConjugationOverride(inf_match=re.compile(six.u('[^aeiouáéíóú]c[ie]r$')),
    documentation='verbs ending in -cer or -cir with a preceding constant have c -> z before o',
    examples=[six.u('convencer')]
    )
Cir_Cer_After_Const_CO.override_tense_stem(present_tense, lambda self, tense, person: self.stem[:-1]+six.u('z'), first_person_singular)
# Cir_Cer_After_Const_CO.override_tense_stem(present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('z'))

Uir_CO = ConjugationOverride(inf_match=re.compile(six.u('[^q]uir$'), re.I),
    documentation='-uir but NOT quir verbs. Add a y before inflection except 1st/2nd plurals',
    examples=[six.u('incluir'), six.u('construir')]
    )

Guir_CO = ConjugationOverride(inf_match=re.compile(six.u('guir$'), re.I),
    parent=Uir_CO
    )
Ucir_CO = ConjugationOverride(inf_match=re.compile(six.u('[úu]cir$')),
    parent=Cir_Cer_After_Vowel_CO,
    documentation=six.u('')
    )

Ducir_CO = ConjugationOverride(inf_match=re.compile(six.u('d[úu]cir$')),
    parent=Ucir_CO,
    documentation=six.u('verbs ending in -ducir are also irregular in the past tense'),
    examples=[six.u('producir'), six.u('aducir')]
    )

"""
Special casing
key: need to allow verbs to opt out of special casing. For example, relucir does not have a c-> j substitution in past tense.
"""
Special_Changes = [
    {
        'key': 'v_cr',        
        '__doc__': 'verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
        '__examples__': 'http://www.intro2spanish.com/verbs/listas/master-zco.htm',                
        'inf_ending': re.compile(u'[aeiouáéíóú]c[ie]r$'),
        # tocar - example
        'conjugation_ending' : re.compile(u'^[oó]'),
        'conjugation': lambda stem, ending: stem[:-1] + u'zc' + ending
    },
    {
        '__doc__': 'verbs ending in -cer or -cir with preceding constant have c -> z before o',
        '__examples__': r'convencer',                
        'inf_ending': re.compile(u'[^aeiouáéíóú]c[ie]r$'),
        'conjugation_ending' : re.compile(u'^[oó]'),
        'conjugation': lambda stem, ending: stem[:-1] + u'z'+ ending,
    },

    {
        'key' : u'ucir_present',
        'inf_ending': re.compile(u'ucir'),
        
    },
    {
        '__doc__':'verbs ending in -ducir are also irregular in the past tense',
        '__examples__': 'introducir, traducir',
        'inf_ending': re.compile(u'ducir'),
        'override': {
            'tense': past_tense,
            'conjugation': [
                
                ]
        }
    }
]

Ducir = re.compile(six.u('d[úu]cir$'))
# (includes -ducir rules ) 
Ucir = re.compile(six.u('[úu]cir$'))
#
Guir = re.compile(six.u('guir'))
Uir = re.compile(six.u('[^q]uir$'))

#TODO: does this include ucir words?
Cer_Cir_With_Vowel = re.compile(u'[aeiouáéíóú]c[ie]r$')

Cer_Cir_Without_Vowel = re.compile(u'[^aeiouáéíóú]c[ie]r$')

Ger_Gir = re.compile(six.u('g[ei]r$'))

__all__ = [ConjugationOverride]
