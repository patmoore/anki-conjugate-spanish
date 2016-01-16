# -*- coding: utf-8 -*-
import six
import re
import inspect
from standard_endings import Standard_Conjugation_Endings
from constants import *
"""
Special casing
key: need to allow verbs to opt out of special casing. For example, relucir does not have a c-> j substitution in past tense.
http://www.intro2spanish.com/verbs/listas/master-zco.htm
"""

__all__ = ['ConjugationOverride', 'Standard_Overrides']

# TODO need a way of adding notes to overrides
class ConjugationOverride():
    
    def __init__(self, inf_match=None, parent=None, documentation=None, examples=None, key=None, auto_match=True):
        self.parent = parent
        self.inf_match = inf_match
        self.documentation = documentation
        self.examples=examples
        self.key= key if key is not None else inf_match
        self.auto_match = auto_match        
        
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
                # expand it out to allow for later overrides of specific persons to be applied.
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
        if self.parent is not None:
            self.parent.apply(verb)
            
        for applies in ['conjugations', 'conjugation_stems', 'conjugation_endings']:
            overrides = getattr(self, applies, None)
            if overrides != None:
                for tense, conjugation_override in enumerate(overrides):
                    if conjugation_override is not None:
                        verb._overrides(tense, conjugation_override, applies)
    
Standard_Overrides = {}
Zar_CO = ConjugationOverride(inf_match=re.compile(u'zar$'), 
    key='zar',
    documentation='verbs ending in -zar have z -> c before e',
    examples=[six.u('comenzar'), six.u('lanzar')]
    )
Zar_CO.override_tense_stem(Tenses.past_tense, lambda self, tense, person: self.stem[:-1]+six.u('c'), Persons.first_person_singular)
Zar_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('c'))
Standard_Overrides[Zar_CO.key] = Zar_CO

Gar_CO = ConjugationOverride(inf_match=re.compile(six.u('gar$')),
    key='gar', 
    documentation='verbs ending in -gar have g -> gu before e',
    examples=[six.u('pagar')]
    )
Gar_CO.override_tense_stem(Tenses.past_tense, lambda self, tense, person: self.stem[:-1]+six.u('gu'), Persons.first_person_singular)
Gar_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('gu'))
Standard_Overrides[Gar_CO.key] = Gar_CO

Ger_Gir_CO = ConjugationOverride(inf_match=re.compile(u'g[ei]r$'),
    key="ger_gir"
    )
Ger_Gir_CO.override_tense_stem(Tenses.present_tense, lambda self, tense, person: self.stem[:-1] +u'j', documentation=u'g->j before ')
Standard_Overrides[Ger_Gir_CO.key] = Ger_Gir_CO
Standard_Overrides[u'ger'] = Ger_Gir_CO
Standard_Overrides[u'gir'] = Ger_Gir_CO

Car_CO = ConjugationOverride(inf_match=re.compile(six.u('car$')), 
    key='car',
    documentation='verbs ending in -car have c -> qu before e',
    examples=[six.u('tocar')]
    )
Car_CO.override_tense_stem(Tenses.past_tense, lambda self, tense, person: self.stem[:-1]+six.u('qu'), Persons.first_person_singular)
Car_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('qu'))
Standard_Overrides[Car_CO.key] = Car_CO

# http://www.intro2spanish.com/verbs/listas/master-zco.htm
Cir_Cer_After_Vowel_CO = ConjugationOverride(inf_match=re.compile(six.u('[aeiouáéíóú]c[ie]r$')),
    key='v_cer_cir',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
    examples=[six.u('aparecer')]
    )
Cir_Cer_After_Vowel_CO.override_tense_stem(Tenses.present_tense, lambda self, tense, person: self.stem[:-1]+six.u('zc'), Persons.first_person_singular)
# Cir_Cer_After_Vowel_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('zc'))
Standard_Overrides[Cir_Cer_After_Vowel_CO.key] = Cir_Cer_After_Vowel_CO
Standard_Overrides['v_cer'] = Cir_Cer_After_Vowel_CO
Standard_Overrides['v_cir'] = Cir_Cer_After_Vowel_CO

Cir_Cer_After_Const_CO = ConjugationOverride(inf_match=re.compile(six.u('[^aeiouáéíóú]c[ie]r$')),
    key='c_cer_cir',
    documentation='verbs ending in -cer or -cir with a preceding constant have c -> z before o',
    examples=[six.u('convencer')]
    )
Cir_Cer_After_Const_CO.override_tense_stem(Tenses.present_tense, lambda self, tense, person: self.stem[:-1]+six.u('z'), Persons.first_person_singular)
# Cir_Cer_After_Const_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('z'))
Standard_Overrides[Cir_Cer_After_Const_CO.key] = Cir_Cer_After_Const_CO
Standard_Overrides['v_cer'] = Cir_Cer_After_Const_CO
Standard_Overrides['v_cir'] = Cir_Cer_After_Const_CO

Uir_CO = ConjugationOverride(inf_match=re.compile(six.u('[^qg]uir$'), re.I),
    key="uir",
    documentation='-uir but NOT quir nor guir verbs. Add a y before inflection except 1st/2nd plurals',
    examples=[u'incluir', u'construir', u'contribuir']
    )
Uir_CO.override_tense_ending(Tenses.present_tense, lambda self, tense,person: u'y' + Standard_Conjugation_Endings[Infinitive_Endings.ir_verb][tense][person], Persons.Present_Tense_Stem_Changing_Persons)
Uir_CO.override_tense_ending(Tenses.past_tense, u'yó', Persons.third_person_singular)
Uir_CO.override_tense_ending(Tenses.past_tense, u'yeron', Persons.third_person_plural)
Standard_Overrides[Uir_CO.key]=Uir_CO

Guir_CO = ConjugationOverride(inf_match=re.compile(six.u('guir$'), re.I),
    key='guir'
    )
# drop u in 1st person present
Guir_CO.override_tense_stem(Tenses.present_tense, lambda self, tense, person:self.stem[:-1], Persons.first_person_singular)
Standard_Overrides[Guir_CO.key]=Guir_CO

Ducir_CO = ConjugationOverride(inf_match=re.compile(u'd[úu]cir$', re.IGNORECASE+re.UNICODE),
    key='ducir',
    parent=Cir_Cer_After_Vowel_CO,
    documentation=six.u('verbs ending in -ducir are also irregular in the past tense'),
    examples=[six.u('producir'), six.u('aducir')]
    )
Ducir_CO.override_tense_stem(Tenses.past_tense, lambda self, tense, person: self.stem[:-1] + u'j', documentation=u'past tense is special case c-> j')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'e', Persons.first_person_singular, documentation=u'first person past is e instead of i')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'o', Persons.third_person_singular, documentation=u'normally ió')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'eron', Persons.third_person_plural, documentation=u'normally ieron')
Standard_Overrides[Ducir_CO.key]=Ducir_CO

Iar_CO = ConjugationOverride(inf_match=re.compile(u'iar$', re.IGNORECASE+re.UNICODE),
    auto_match=False,
    key=u'iar',
    documentation=u'some iar verbs accent the i so that it is not weak in the yo form')
Iar_CO.override_tense_ending(Tenses.present_tense, u'\u0301' + Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][Persons.first_person_singular], Persons.first_person_singular)
Standard_Overrides[Iar_CO.key] = Iar_CO
