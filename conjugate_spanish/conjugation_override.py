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
    
    def __init__(self, inf_match=None, parents=None, documentation=None, examples=None, key=None, auto_match=True):
        if parents is None:
            self.parent = None
        else:
            _parents = parents if isinstance(parents, list) else [ parents ]
            self.parent = [ Standard_Overrides[parent] if isinstance(parent, six.string_types) else parent for parent in _parents] 
        
        self.inf_match = inf_match
        self.documentation = documentation
        self.examples=examples
        self.key= key if key is not None else inf_match
        self.auto_match = auto_match and inf_match is not None        
        
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
        
    def override_present_stem_changers(self, overrides, documentation=None):
        """
        Special case because occurs so often in spanish
        overrides 1st person singular, 2nd person singular and 3rd person singular and plural
        """
        self.override_tense_stem(tense=Tenses.present_tense, overrides=overrides, persons=Persons.Present_Tense_Stem_Changing_Persons, documentation=documentation)
        
    def override_past_stem_changers(self, overrides, documentation=None):
        """
        Special case because occurs so often in spanish
        overrides 3rd person singular and plural
        """
        self.override_tense_stem(tense=Tenses.past_tense, overrides=overrides, persons=Persons.Past_Tense_Stem_Changing_Persons, documentation=documentation)
    
    def override_tense(self, tense, overrides,persons=None, documentation=None):
        """
        Used for case when the entire tense is very irregular
        """
        self.__overrides(tense, overrides, 'conjugations',persons)
        
    def __get_override(self, tense, person, attr_name):
        overrides = []
        if self.parent is not None:
            for parent in self.parent:
                parent_override = parent.__get_override(tense, parent, attr_name)
                if parent_override is not None:
                    overrides.extend(parent_override)
                                
        if hasattr(self, attr_name):
            self_overrides = getattr(self, attr_name)
            if self_overrides[tense] is not None:
            # some overrides exist for this tense        
                if isinstance(self_overrides[tense], six.string_types):
                    # a single different stem for the entire tense
                    overrides.extend( self_overrides[tense])
                elif self_overrides[tense][person] is not None:
                    # a specific override for the tense/person
                    overrides.extend(self_overrides[tense][person])
            
        return overrides if len(overrides) > 0 else None

    def is_match(self, infinitive):
        if self.inf_match.search(infinitive):
            return True
        else:
            return False

    def apply(self, verb):
        if self.parent is not None:
            for parent in self.parent:
                parent.apply(verb)
            
        for applies in ['conjugations', 'conjugation_stems', 'conjugation_endings']:
            overrides = getattr(self, applies, None)
            if overrides != None:
                for tense, conjugation_override in enumerate(overrides):
                    if conjugation_override is not None:
                        verb._overrides(tense, conjugation_override, applies)
    
def __radical_stem_change(stem, vowel_change, vowels_to):
    # pick off last instance of the vowel.
    # for example:  'elegir' we need to change the last e to an i. 
    # the stem would be 'elej'
    index = stem.rindex(vowel_change)
    if index < 0:
        raise Exception("vowel missing :"+vowel_change)
    changed_stem = stem[:index] + vowels_to + stem[index+1:]
    return changed_stem

Standard_Overrides = {}

"""
RADICAL STEM CHANGE PATTERNS
"""
radical_stem_changes = [
    #including gir 
    [u'e', u'i', u'i'],
    [u'e', u'ie', u'ie'],
    # dormir
    [u'o', u'ue', u'u']
]
for vowel_from, present_vowels_to, past_vowels_to in radical_stem_changes:
    key=vowel_from+':'+present_vowels_to
    if past_vowels_to is None:
        past_vowels_to = present_vowels_to
        
    conjugation_override = ConjugationOverride(key=key,
        documentation='radical stem changing '+key+ "; past tense="+vowel_from+':'+past_vowels_to
        )
    def __make_radical_call(vowel_from, vowels_to):
        return lambda self, stem, **kwargs: __radical_stem_change(stem, vowel_from, vowels_to)
    radical_prstem_call = __make_radical_call(vowel_from, present_vowels_to)
    conjugation_override.override_tense_stem(Tenses.present_tense, __make_radical_call(vowel_from, present_vowels_to), Persons.Present_Tense_Stem_Changing_Persons)
    conjugation_override.override_tense_stem(Tenses.past_tense, __make_radical_call(vowel_from, past_vowels_to), Persons.Past_Tense_Stem_Changing_Persons)
    Standard_Overrides[key] = conjugation_override
    
# E2I_CO = ConjugationOverride(
#     key=u'e:i',
#     documentation='radical stem changing e:i')
# E2I_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: __radical_stem_change(stem, u'e', u'i'), Persons.Present_Tense_Stem_Changing_Persons)
# 
# E2IE_CO = ConjugationOverride(key=u'e:ie', documentation="e:ie stem changing verbs")
# E2IE_CO.override_tense_ending(Tenses.present_tense, lambda self, stem, **kwargs: __radical_stem_change(stem, u'e', u'ie'), Persons.Present_Tense_Stem_Changing_Persons)
# Standard_Overrides[E2IE_CO.key] = E2IE_CO

Zar_CO = ConjugationOverride(inf_match=re.compile(u'zar$'), 
    key='zar',
    documentation='verbs ending in -zar have z -> c before e',
    examples=[six.u('comenzar'), six.u('lanzar')]
    )
Zar_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: stem[:-1]+u'c', Persons.first_person_singular)
Zar_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: stem[:-1]+u'c')
Standard_Overrides[Zar_CO.key] = Zar_CO

Gar_CO = ConjugationOverride(inf_match=re.compile(u'gar$'),
    key='gar', 
    documentation='verbs ending in -gar have g -> gu before e',
    examples=[six.u('pagar')]
    )
Gar_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: stem[:-1]+u'gu', Persons.first_person_singular)
Gar_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: stem[:-1]+u'gu')
Standard_Overrides[Gar_CO.key] = Gar_CO

Ger_CO = ConjugationOverride(inf_match=re.compile(u'ger$'),
    key="ger"
    )
Ger_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: stem[:-1] +u'j', documentation=u'g->j before o')
Standard_Overrides[Ger_CO.key] = Ger_CO

Gir_CO = ConjugationOverride(inf_match=re.compile(u'gir$'),
    parents=[Ger_CO, 'e:i'],
    key="gir"
    )
Gir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: stem[:-1] +u'j', documentation=u'g->j before o')
Standard_Overrides[Gir_CO.key] = Gir_CO

Car_CO = ConjugationOverride(inf_match=re.compile(six.u('car$')), 
    key='car',
    documentation='verbs ending in -car have c -> qu before e',
    examples=[six.u('tocar')]
    )
Car_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: stem[:-1]+u'qu', Persons.first_person_singular)
Car_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: stem[:-1]+u'qu')
Standard_Overrides[Car_CO.key] = Car_CO

# http://www.intro2spanish.com/verbs/listas/master-zco.htm
Cir_Cer_After_Vowel_CO = ConjugationOverride(inf_match=re.compile(six.u('[aeiouáéíóú]c[ie]r$')),
    key='v_cer_cir',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
    examples=[six.u('aparecer')]
    )
Cir_Cer_After_Vowel_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: stem[:-1]+u'zc', Persons.first_person_singular)
# Cir_Cer_After_Vowel_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('zc'))
Standard_Overrides[Cir_Cer_After_Vowel_CO.key] = Cir_Cer_After_Vowel_CO
Standard_Overrides['v_cer'] = Cir_Cer_After_Vowel_CO
Standard_Overrides['v_cir'] = Cir_Cer_After_Vowel_CO

Cir_Cer_After_Const_CO = ConjugationOverride(inf_match=re.compile(six.u('[^aeiouáéíóú]c[ie]r$')),
    key='c_cer_cir',
    documentation='verbs ending in -cer or -cir with a preceding constant have c -> z before o',
    examples=[six.u('convencer')]
    )
Cir_Cer_After_Const_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: stem[:-1]+u'z', Persons.first_person_singular)
# Cir_Cer_After_Const_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('z'))
Standard_Overrides[Cir_Cer_After_Const_CO.key] = Cir_Cer_After_Const_CO
Standard_Overrides['v_cer'] = Cir_Cer_After_Const_CO
Standard_Overrides['v_cir'] = Cir_Cer_After_Const_CO

I2Y_PastTense_CO = ConjugationOverride(
    key=u'i2y',
    documentation="uir verbs and eer verbs"
)
I2Y_PastTense_CO.override_tense_ending(Tenses.past_tense, u'yó', Persons.third_person_singular)
I2Y_PastTense_CO.override_tense_ending(Tenses.past_tense, u'yeron', Persons.third_person_plural)
Standard_Overrides[I2Y_PastTense_CO.key] = I2Y_PastTense_CO
    
Uir_CO = ConjugationOverride(inf_match=re.compile(six.u('[^qg]uir$'), re.I),
    parents=I2Y_PastTense_CO,
    key="uir",
    documentation='-uir but NOT quir nor guir verbs. Add a y before inflection except 1st/2nd plurals',
    examples=[u'incluir', u'construir', u'contribuir']
    )
Uir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: stem + u'y', Persons.Present_Tense_Stem_Changing_Persons)
Standard_Overrides[Uir_CO.key]=Uir_CO

Guir_CO = ConjugationOverride(inf_match=re.compile(six.u('guir$'), re.I),
    key='guir'
    )
# drop u in 1st person present
Guir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs:stem[:-1], Persons.first_person_singular)
Standard_Overrides[Guir_CO.key]=Guir_CO

Ducir_CO = ConjugationOverride(inf_match=re.compile(u'd[úu]cir$', re.IGNORECASE+re.UNICODE),
    key='ducir',
    parents=Cir_Cer_After_Vowel_CO,
    documentation=six.u('verbs ending in -ducir are also irregular in the past tense'),
    examples=[six.u('producir'), six.u('aducir')]
    )
Ducir_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: stem[:-1] + u'j', documentation=u'past tense is special case c-> j')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'e', Persons.first_person_singular, documentation=u'first person past is e instead of i')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'o', Persons.third_person_singular, documentation=u'normally ió')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'eron', Persons.third_person_plural, documentation=u'normally ieron')
Standard_Overrides[Ducir_CO.key]=Ducir_CO

Eir_CO = ConjugationOverride(inf_match=re.compile(u'e[ií]r$'),
    #pattern includes without the accent as well because user may forget the accent.
    key="eir",
    documentation="eír verbs have accent on i in the infinitive",
    examples = [u'reír', u'freír']
    )
Eir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: stem[:-1] + u'í', Persons.Present_Tense_Stem_Changing_Persons)
Eir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: stem[:-1], Persons.Past_Tense_Stem_Changing_Persons, documentation="remove the e from the stem")
Standard_Overrides[Eir_CO.key]=Eir_CO
Standard_Overrides["eír"]=Eir_CO

Eer_CO = ConjugationOverride(inf_match=re.compile(u'eer$'),
    # the i2y pattern that can be automatically assigned to eer verbs
    key="eer",
    parents=I2Y_PastTense_CO,
    documentation="eer verbs",
    examples = [u'creer']
    )
# optional

Iar_CO = ConjugationOverride(inf_match=re.compile(u'iar$', re.IGNORECASE+re.UNICODE),
    auto_match=False,
    key=u'iar',
    documentation=u'some iar verbs accent the i so that it is not weak in the yo form')
Iar_CO.override_tense_ending(Tenses.present_tense, u'\u0301' + Standard_Conjugation_Endings[Infinitive_Endings.ar_verb][Tenses.present_tense][Persons.first_person_singular], Persons.first_person_singular)
Standard_Overrides[Iar_CO.key] = Iar_CO

Go_CO = ConjugationOverride(key=u'go', documentation="go verbs")
Go_CO.override_tense_ending(Tenses.present_tense, u"go", Persons.first_person_singular, documentation="go verb")
Standard_Overrides[Go_CO.key] = Go_CO

