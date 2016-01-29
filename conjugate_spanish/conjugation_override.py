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

__all__ = ['ConjugationOverride', 'Standard_Overrides', 'Dependent_Standard_Overrides']

# TODO need a way of adding notes to overrides
class ConjugationOverride():
    
    def __init__(self, inf_match=None, parents=None, documentation=None, examples=None, key=None, auto_match=None, manual_overrides=None):
        if parents is None:
            self.parent = None
        else:
            _parents = parents if isinstance(parents, list) else [ parents ]
            self.parent = [ Standard_Overrides[parent] if isinstance(parent, six.string_types) else parent for parent in _parents] 
        
        self.inf_match = inf_match
        self.documentation = documentation
        self.examples=examples
        self.key= key if key is not None else inf_match
        if auto_match is None:
            self.auto_match = inf_match is not None
        else:
            self.auto_match = auto_match  
            
        self.add_manual_overrides(manual_overrides)      
            
    def add_manual_overrides(self, manual_overrides):
        if manual_overrides is None:
            return
        if 'stems' in manual_overrides and manual_overrides['stems'] is not None:                
            for key, override in manual_overrides['stems'].iteritems():
                tense = Tenses.index(key)
                conjugation_override.override_tense_stem(tense, override)
        if 'endings' in manual_overrides and manual_overrides['endings'] is not None:
            for key, override in manual_overrides['endings'].iteritems():
                tense = Tenses.index(key)
                conjugation_override.override_tense_ending(tense, override)
        if 'conjugations' in manual_overrides and manual_overrides['conjugations'] is not None:
            for key, override in manual_overrides['conjugations'].iteritems():
                tense = Tenses.index(key)
                conjugation_override.override_tense_ending(tense, override)
                
            

    def __overrides(self, tense, overrides, attr_name, persons):
        if not hasattr(self, attr_name):
            self_overrides = [ None ] * len(Tenses)
            setattr(self, attr_name, self_overrides) 
        else:
            self_overrides = getattr(self, attr_name)
            
        if overrides is None or isinstance(overrides, six.string_types) or inspect.isfunction(overrides):
            if persons is not None:
                if self_overrides[tense] is None:
                    self_overrides[tense] = [None] * len(Persons)
                    
                if isinstance(persons, six.integer_types):
                    # a single person has an override
                    self_overrides[tense][persons] = overrides
                else:
                    for person in persons:
                        self_overrides[tense][person] = overrides
            elif tense in Tenses.Person_Agnostic:
                # person is not relevant for gerund and past participle
                self_overrides[tense] = overrides
            else:
                # a single stem for all persons of this tense
                # expand it out to allow for later overrides of specific persons to be applied.
                self_overrides[tense] = [overrides] * len(Persons)
        elif tense in Tenses.Person_Agnostic:
            self_overrides[tense] = overrides
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

    def is_match(self, verb):
        if self.inf_match.search(verb.inf_verb_string):
            return True
        else:
            return False

    def apply(self, verb):
        if self.key:
            # Custom overrides do not always have keys
            verb.appliedOverrides.append(self.key)
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

def __make_radical_call(vowel_from, vowels_to):
    return lambda self, stem, **kwargs: __radical_stem_change(stem, vowel_from, vowels_to)

Standard_Overrides = {}
Dependent_Standard_Overrides = {}
"""
RADICAL STEM CHANGE PATTERNS
"""
radical_stem_changes = [
    #including gir 
    [u'e', u'i', u'i', u'i'],
    [u'e', u'ie', u'ie', None],
    # dormir
    [u'o', u'ue', u'u', u'u']
]
def __check_for_stem_ir(key, verb):
    if verb.verb_ending_index == Infinitive_Endings.ir_verb:        
        for conjugation_override in get_iterable(verb.appliedOverrides):            
            if isinstance(conjugation_override, ConjugationOverride):
                _key = conjugation_override.key
            else:
                _key =conjugation_override
            if _key is not None: # _key is None is always fail.
                if _key == key:
                    return True
    return False
def __make_check_stem_ir(key):
    return lambda self, verb: __check_for_stem_ir(key, verb)

for vowel_from, present_vowels_to, past_vowels_to, gerund_vowel in radical_stem_changes:
    key=vowel_from+':'+present_vowels_to
    if past_vowels_to is None:
        past_vowels_to = present_vowels_to
        
    conjugation_override = ConjugationOverride(key=key,
        documentation='radical stem changing '+key+ "; past tense="+vowel_from+':'+past_vowels_to
        )

    radical_prstem_call = __make_radical_call(vowel_from, present_vowels_to)
    conjugation_override.override_tense_stem(Tenses.present_tense, __make_radical_call(vowel_from, present_vowels_to), Persons.Present_Tense_Stem_Changing_Persons)
    conjugation_override.override_tense_stem(Tenses.past_tense, __make_radical_call(vowel_from, past_vowels_to), Persons.Past_Tense_Stem_Changing_Persons)        
    Standard_Overrides[key] = conjugation_override
    if gerund_vowel is not None:
        # http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA5u1NsOEJ
        stem_changing_ir_gerund = ConjugationOverride(key=u"stem_changing_ir_"+key,
            auto_match=True,
            documentation=u"Any -ir verb that has a stem-change in the third person preterite (e->i, or o->u) will have the same stem-change in the gerund form. The -er verb poder also maintains its preterite stem-change in the gerund form."
        )
        stem_changing_ir_gerund.override_tense_stem(Tenses.gerund, __make_radical_call(vowel_from, gerund_vowel))

        stem_changing_ir_gerund.is_match  = six.create_bound_method(__make_check_stem_ir(key), stem_changing_ir_gerund)
        Dependent_Standard_Overrides[stem_changing_ir_gerund.key] = stem_changing_ir_gerund 
    
def _replace_last_letter_of_stem(stem, expected_last_letter, new_stem_ending= None):
    truncated_stem = stem[:-1]
    last_letter = stem[-1]
    if expected_last_letter is not None and expected_last_letter != last_letter:
        raise Exception("wrong stem ending expected:"+expected_last_letter+" got "+last_letter)
    elif new_stem_ending is not None:
        return truncated_stem + new_stem_ending
    else:
        return truncated_stem        

"""
==================================================
Gerund  - http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA2iFNsOEI
Whenever an unstressed i appears between two vowels, the spelling always changes to a y, not just in the following gerunds.
"""
Yendo_Gerund_CO = ConjugationOverride(
    inf_match=re.compile(u'[aeiouáéíóú][eéíi]r$', re.UNICODE+re.IGNORECASE),
    key=u'yendo',
    documentation="-er or -er verbs that have a preceding vowel",
    examples=[u'ir', u'poseer'])
Yendo_Gerund_CO.override_tense_ending(Tenses.gerund, u'yendo')
Standard_Overrides[Yendo_Gerund_CO.key] = Yendo_Gerund_CO

Zar_CO = ConjugationOverride(inf_match=re.compile(u'zar$'), 
    key='zar',
    documentation='verbs ending in -zar have z -> c before e',
    examples=[six.u('comenzar'), six.u('lanzar')]
    )
Zar_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'z',u'c'), Persons.first_person_singular)
Zar_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'z',u'c'))
Standard_Overrides[Zar_CO.key] = Zar_CO

Gar_CO = ConjugationOverride(inf_match=re.compile(u'gar$'),
    key='gar', 
    documentation='verbs ending in -gar have g -> gu before e',
    examples=[six.u('pagar')]
    )
Gar_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'g', u'gu'), Persons.first_person_singular)
Gar_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'g',u'gu'))
Standard_Overrides[Gar_CO.key] = Gar_CO

#
# -ger, -gir verbs change g-> j
Ger_CO = ConjugationOverride(inf_match=re.compile(u'ger$'),
    key="ger"
    )
Ger_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'g', u'j'), 
    persons=Persons.first_person_singular,
    documentation=u'g->j before o (present:first person singular) (present subjective) - preserves "g" sound')
Standard_Overrides[Ger_CO.key] = Ger_CO

Gir_CO = ConjugationOverride(inf_match=re.compile(u'gir$'),
    #TODO only if the -gir verb has 'e'
    parents=Ger_CO,
    key="gir"
    )
Standard_Overrides[Gir_CO.key] = Gir_CO

#TODO is it just -egir verbs or do we allow for consonents between the e and the -gir? 
E_Gir_CO = ConjugationOverride(inf_match=re.compile(u'e[^aiou]*gir$'),
    parents="e:i",
    key=u"e_gir",
    examples=[u'elegir', u'corregir'],
    documentation="gir verbs that have a last stem vowel of e are stem changers ( so exigir is *not* a stem changer)"
)
Standard_Overrides[E_Gir_CO.key] = E_Gir_CO

Car_CO = ConjugationOverride(inf_match=re.compile(six.u('car$')), 
    key='car',
    documentation='verbs ending in -car have c -> qu before e',
    examples=[six.u('tocar')]
    )
Car_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c',u'qu'), Persons.first_person_singular)
Car_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c',u'qu'))
Standard_Overrides[Car_CO.key] = Car_CO

# http://www.intro2spanish.com/verbs/listas/master-zco.htm
Cir_Cer_After_Vowel_CO = ConjugationOverride(inf_match=re.compile(six.u('[aeiouáéíóú]c[ie]r$')),
    key='v_cer_cir',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
    examples=[six.u('aparecer')]
    )
Cir_Cer_After_Vowel_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c',u'zc'), Persons.first_person_singular)
# Cir_Cer_After_Vowel_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, tense, person: self.stem[:-1]+six.u('zc'))
Standard_Overrides[Cir_Cer_After_Vowel_CO.key] = Cir_Cer_After_Vowel_CO
Standard_Overrides['v_cer'] = Cir_Cer_After_Vowel_CO
Standard_Overrides['v_cir'] = Cir_Cer_After_Vowel_CO

Cir_Cer_After_Const_CO = ConjugationOverride(inf_match=re.compile(six.u('[^aeiouáéíóú]c[ie]r$')),
    key='c_cer_cir',
    documentation='verbs ending in -cer or -cir with a preceding constant have c -> z before o',
    examples=[six.u('convencer')]
    )
Cir_Cer_After_Const_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem,u'c',u'z'), Persons.first_person_singular)
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
Guir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs:_replace_last_letter_of_stem(stem,u'u'), Persons.first_person_singular)
Standard_Overrides[Guir_CO.key]=Guir_CO

Ducir_CO = ConjugationOverride(inf_match=re.compile(u'd[úu]cir$', re.IGNORECASE+re.UNICODE),
    key='ducir',
    parents=Cir_Cer_After_Vowel_CO,
    documentation=six.u('verbs ending in -ducir are also irregular in the past tense'),
    examples=[six.u('producir'), six.u('aducir')]
    )
Ducir_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c', u'j'), documentation=u'past tense is special case c-> j')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'e', Persons.first_person_singular, documentation=u'first person past is e instead of i')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'o', Persons.third_person_singular, documentation=u'normally ió')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'eron', Persons.third_person_plural, documentation=u'normally ieron')
Standard_Overrides[Ducir_CO.key]=Ducir_CO

Eir_CO = ConjugationOverride(inf_match=re.compile(u'eír$'),
    #pattern does not include the unaccented i.
    key=u"eír",
    documentation=u"eír verbs have accent on i in the infinitive",
    examples = [u'reír', u'freír']
    )
Eir_CO.override_present_stem_changers(lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'e', u'í'), 
        documentation="replace stem ending e with accented í")
Eir_CO.override_tense_ending(Tenses.present_tense, lambda self, **kwargs: u'ímos', documentation="accent on the i", persons=Persons.first_person_plural)
Eir_CO.override_past_stem_changers(lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'e'), documentation="remove the e from the stem")

Standard_Overrides[Eir_CO.key]=Eir_CO

Ei_r_CO = ConjugationOverride(inf_match=re.compile(u'eir$'),
    parents=Eir_CO,
    key=u'eir',
    documentation=u"eir ending usually has accent i but just in case, but separate than the 'correct' case")
Standard_Overrides[Ei_r_CO.key]=Ei_r_CO

Eer_CO = ConjugationOverride(inf_match=re.compile(u'eer$'),
    # the i2y pattern that can be automatically assigned to eer verbs
    key=u"eer",
    parents=[I2Y_PastTense_CO],
    documentation=u"eer verbs",
    examples = [u'creer']
    )
Standard_Overrides[Eer_CO.key]=Eer_CO

LL_N_CO = ConjugationOverride(inf_match=re.compile(u'(ll|ñ)[eií]r$'),
    key=u"ll_ñ",
    documentation=u"If the stem of -er or -ir verbs ends in ll or ñ, -iendo changes to -endo. (Since ll and ñ already have an i sound in them, it is not necessary to add it to the gerund ending.)")
LL_N_CO.override_tense_ending(Tenses.gerund, u'endo')
Standard_Overrides[LL_N_CO.key]=LL_N_CO

# These endings must be explicitly added
def __accent_stem_last(self, stem, **kwargs):
    return stem + u'\u0301'

Iar_CO = ConjugationOverride(inf_match=re.compile(u'iar$', re.IGNORECASE+re.UNICODE),
    auto_match=False,
    key=u'iar',
    documentation=u'some iar verbs accent the i so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-iar-with-i-ii.htm')
Iar_CO.override_present_stem_changers(__accent_stem_last)
Standard_Overrides[Iar_CO.key] = Iar_CO

Uar_CO = ConjugationOverride(inf_match=re.compile(u'[^g]uar$', re.IGNORECASE+re.UNICODE),
    auto_match=False,
    key=u'uar',
    documentation=u'some uar verbs accent the u so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-uar-with-u-uu.htm')
Uar_CO.override_present_stem_changers(__accent_stem_last)
Standard_Overrides[Uar_CO.key] = Uar_CO

Go_CO = ConjugationOverride(key=u'go', documentation="go verbs")
Go_CO.override_tense_ending(Tenses.present_tense, u"go", Persons.first_person_singular, documentation="go verb")
Standard_Overrides[Go_CO.key] = Go_CO

Oy_CO = ConjugationOverride(key=u'oy', documentation="oy verbs")
Oy_CO.override_tense_ending(Tenses.present_tense, u"oy", Persons.first_person_singular, documentation="oy verb")
Standard_Overrides[Oy_CO.key] = Oy_CO

Past_Yo_Ud_Irr_CO = ConjugationOverride(key=u'e_and_o', 
    documentation=u"Some irregular verbs have past tense changes yo: 'e' and usted has 'o'",
    examples=[u'estar', u'tener'])
Past_Yo_Ud_Irr_CO.override_tense_ending(Tenses.past_tense, u'e', Persons.first_person_singular)
Past_Yo_Ud_Irr_CO.override_tense_ending(Tenses.past_tense, u'o', Persons.third_person_singular)
Standard_Overrides[Past_Yo_Ud_Irr_CO.key] = Past_Yo_Ud_Irr_CO

Infinitive_Stems_E2D = ConjugationOverride(key=u'e2d', documentation="Future Tense/Conditional Tense:Some verbs convert the -er ending infinitive stem to a 'd'",
        examples=[u'tener'])
Infinitive_Stems_E2D.override_tense_stem(Tenses.future_tense, lambda self, stem, **kwargs: stem[:-2] + u'dr')
Infinitive_Stems_E2D.override_tense_stem(Tenses.conditional_tense, lambda self, stem, **kwargs: stem[:-2] + u'dr')
Standard_Overrides[Infinitive_Stems_E2D.key]=Infinitive_Stems_E2D

Infinitive_Stems_R_Only = ConjugationOverride(key=u'r_only', documentation="Future Tense/Conditional Tense:Some verbs remove the vowel in the infinitive ending to a r",
        examples=[u'haber'])
Infinitive_Stems_R_Only.override_tense_stem(Tenses.future_tense, lambda self, stem, **kwargs: stem[:-2] + u'r')
Infinitive_Stems_R_Only.override_tense_stem(Tenses.conditional_tense, lambda self, stem, **kwargs: stem[:-2] + u'r')
Standard_Overrides[Infinitive_Stems_R_Only.key]=Infinitive_Stems_R_Only

Present_Subjective_Infinitive = ConjugationOverride(key='pres_sub_inf',
     documentation="Some verbs use the infinitive stem as the present subjective stem for nosotros/vosotros",
     examples=[u"querer", u"oler"])
Present_Subjective_Infinitive.override_tense_stem(Tenses.present_subjective_tense, lambda self, **kwargs: self.stem, Persons.all_except(Persons.Present_Tense_Stem_Changing_Persons))
Standard_Overrides[Present_Subjective_Infinitive.key] = Present_Subjective_Infinitive

# Third person only conjugations

