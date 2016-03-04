# -*- coding: utf-8 -*-
import json
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
    """
    overrides are functions that are bound to the specific verb ( so become instance methods ) 
    They are called:
    { 'tense': tense, 'person': person, 'stem': current_conjugation_stem, 'ending' : current_conjugation_ending }
    overall overrides are called first, then ending overrides, then stem overrides
    
    """    
    def __init__(self, inf_match=None, parents=None, documentation=None, examples=None, key=None, auto_match=None, manual_overrides=None):
        """
        :manual_overrides dict with conjugation_stems, conjugation_endings, conjugations key. values are dicts: tense names as keys; values are arrays or strings
        special case: tense name of 'present_except_nosvos' means present tense overriding just yo, tu, usted, ustedes
        """
        if parents is None:
            self.parent = None
        else:
            _parents = parents if isinstance(parents, list) else [ parents ]
            self.parent = [ Standard_Overrides[parent] if isinstance(parent, six.string_types) else parent for parent in _parents] 
        
        self.inf_match = inf_match
        self.documentation = []
        self.documentation.extend(make_list(documentation))
        self.examples=[]
        self.examples.extend(make_list(examples))
        self.key= key if key is not None else inf_match
        if auto_match is None:
            self.auto_match = inf_match is not None
        else:
            self.auto_match = auto_match  
            
        self.add_manual_overrides(manual_overrides)  
        
    @staticmethod
    def create_from_json(key, json_string):
        if json_string is not None and json_string != u'':
            try:
                manual_overrides = json.loads(json_string, 'utf-8')
            except ValueError as e:
                print("while parsing json manual_overrides to verb_dictionary", repr(e))
                print("manual_overrides="+manual_overrides)        
        conjugation_override = ConjugationOverride(key=key,manual_overrides=manual_overrides) 
        return conjugation_override   
            
    def add_manual_overrides(self, manual_overrides):
        if manual_overrides is None:
            return
        for applies in ['conjugations', 'conjugation_stems', 'conjugation_endings']:
            if applies in manual_overrides:
                overrides = manual_overrides[applies]
                if overrides != None:
                    for tenseStr, conjugation_override in overrides.iteritems():
                        if conjugation_override is not None:
                            if tenseStr == u'present_except_nosvos':
                                tense = Tenses.present_tense
                                persons = Persons.Present_Tense_Stem_Changing_Persons
                                self._overrides(tense, conjugation_override, applies, persons)
                            elif tenseStr == u'future_cond':
                                self._overrides(Tenses.future_tense, conjugation_override, applies)
                                self._overrides(Tenses.conditional_tense, conjugation_override, applies)
                            elif tenseStr == u'imperative_positive_second':
                                self._overrides(Tenses.imperative_positive, conjugation_override, applies, Persons.second_person_singular)
                            elif tenseStr == u'third_past':
                                self._overrides(Tenses.past_tense, conjugation_override, applies, Persons.third_person)
                            else:
                                tense = Tenses.index(tenseStr)
                                persons = None
                                self._overrides(tense, conjugation_override, applies, persons)

    def _overrides(self, tense, overrides, attr_name, persons=None):
        if overrides is None:
            # Not allowed to replace previous overrides
            return
        if not hasattr(self, attr_name):
            self_overrides = [ None ] * len(Tenses)
            setattr(self, attr_name, self_overrides) 
        else:
            self_overrides = getattr(self, attr_name)
            
        if isinstance(overrides, six.string_types) or inspect.isfunction(overrides):
            if tense in Tenses.Person_Agnostic:
                # person is not relevant for gerund and past participle
                self_overrides[tense] = overrides
            elif persons is not None:
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
        """
        :overrides:
        """
        self._overrides(tense, overrides, 'conjugation_stems', persons)
        self.documentation.extend(make_list(documentation))            
                    
    def override_tense_ending(self, tense, overrides,persons=None, documentation=None):
        self._overrides(tense, overrides, 'conjugation_endings',persons)
        self.documentation.extend(make_list(documentation))      
        
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
        self._overrides(tense, overrides, 'conjugations',persons)
        self.documentation.extend(make_list(documentation))      
        
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
            verb.add_applied_override(self.key)
        if self.parent is not None:
            for parent in self.parent:
                verb.process_conjugation_override(parent)
            
        for applies in ['conjugations', 'conjugation_stems', 'conjugation_endings']:
            overrides = getattr(self, applies, None)
            if overrides != None:
                for tense, conjugation_override in enumerate(overrides):
                    if conjugation_override is not None:
                        verb._overrides(tense, conjugation_override, applies)
    
# -guir must not pick up a trailing 'u'
__find_last_vowel_re = re.compile(u'^(.*?)(['+AllVowels+'])([^'+AllVowels+']*u?)$', re.UNICODE+re.IGNORECASE)
def __radical_stem_change(stem, vowel_change, vowels_to):
    # pick off last instance of the vowel.
    # for example:  'elegir' we need to change the last e to an i. 
    # the stem would be 'elej'
    match_ = __find_last_vowel_re.match(stem)
    if match_ is None:
        raise Exception("No vowel at all in stem="+stem)
    elif match_.group(2) == vowel_change:
        changed_stem = match_.group(1)+vowels_to+match_.group(3)
    elif match_.group(2) == vowels_to:
        # some other rule resulted in this change already being applied.
        changed_stem = stem
    else:
        # TODO - if another override was applied we shouldn't raise the exception.
        raise Exception(stem+":vowel missing :"+vowel_change)
    
    return changed_stem

def __make_radical_call(vowel_from, vowels_to):
    return lambda self, stem, **kwargs: __radical_stem_change(stem, vowel_from, vowels_to)

Standard_Overrides = {}
def __make_std_override(inf_match=None, parents=None, documentation=None, examples=None, key=None, auto_match=None, manual_overrides=None):
    conjugation_override = ConjugationOverride(inf_match, parents, documentation, examples, key, auto_match, manual_overrides)
    if conjugation_override.key is not None:
        if conjugation_override.key in Standard_Overrides:
            raise Exception("Standard Override already defined for "+conjugation_override.key)
        else:
            Standard_Overrides[conjugation_override.key] = conjugation_override
    return conjugation_override

Dependent_Standard_Overrides = {}
def __make_dep_override(inf_match=None, parents=None, documentation=None, examples=None, key=None, auto_match=None, manual_overrides=None):
    conjugation_override = ConjugationOverride(inf_match, parents, documentation, examples, key, auto_match, manual_overrides)
    if conjugation_override.key is not None:
        if conjugation_override.key in Dependent_Standard_Overrides:
            raise Exception("Dependent_Standard_Overrides already defined for "+conjugation_override.key)
        else:
            Dependent_Standard_Overrides[conjugation_override.key] = conjugation_override
    return conjugation_override
"""
RADICAL STEM CHANGE PATTERNS
http://www.spanishdict.com/topics/show/38
"""
radical_stem_changes = [
    #including gir 
    [u'e', u'i', u'i', u'i'],
    [u'e', u'ie', u'ie', None],
    # dormir
    [u'o', u'ue', u'u', u'u'],
    #adquirir - to acquire     inquirir - to inquire  : only 2 examples
    [u'i', u'ie', None, None],
    #jugar - only example
    [u'u', u'ue', None, None],
    # oler - only example
    [u'o', u'hue', None, None]
]
def __check_for_stem_ir(key, verb):
    if verb.verb_ending_index == Infinitive_Endings.ir_verb:        
        return verb.has_override_applied(key)
    else:
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
    Standard_Overrides[key] = conjugation_override
    if gerund_vowel is not None:
        # http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA5u1NsOEJ
        # but for example, absolver o:ue does not have past tense stem changing
        stem_changing_ir_gerund = __make_dep_override(key=u"stem_changing_ir_"+key,
            auto_match=True,
            examples=[u'dormir'],
            documentation=u"Any -ir verb that has a stem-change in the third person preterite (e->i, or o->u) will have the same stem-change in the gerund form. The -er verb poder also maintains its preterite stem-change in the gerund form."
        )
        stem_changing_ir_gerund.override_tense_stem(Tenses.gerund, __make_radical_call(vowel_from, gerund_vowel))
        stem_changing_ir_gerund.override_tense_stem(Tenses.past_tense, __make_radical_call(vowel_from, past_vowels_to), Persons.Past_Tense_Stem_Changing_Persons)        
        stem_changing_ir_gerund.is_match = six.create_bound_method(__make_check_stem_ir(key), stem_changing_ir_gerund)
        
    
def _replace_last_letter_of_stem(stem, expected_last_letter, new_stem_ending= None):
    truncated_stem = stem[:-1]
    last_letter = stem[-1]
    if expected_last_letter is not None and expected_last_letter != last_letter:
        raise Exception(stem+":wrong stem ending expected:"+expected_last_letter+" got "+last_letter)
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
    documentation=u"-er or -er verbs that have a preceding vowel",
    examples=[u'ir', u'poseer'])
Yendo_Gerund_CO.override_tense_ending(Tenses.gerund, u'yendo')
Standard_Overrides[Yendo_Gerund_CO.key] = Yendo_Gerund_CO

Zar_CO = __make_std_override(inf_match=re.compile(u'zar$'), 
    key='zar',
    documentation='verbs ending in -zar have z -> c before e',
    examples=[u'comenzar', u'lanzar']
    )
Zar_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'z',u'c'), Persons.first_person_singular)
Zar_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'z',u'c'))

Gar_CO = __make_std_override(inf_match=re.compile(u'gar$'),
    key='gar', 
    documentation='verbs ending in -gar have g -> gu before e',
    examples=[u'pagar']
    )
Gar_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'g', u'gu'), Persons.first_person_singular)
Gar_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'g',u'gu'))

#
# -ger, -gir verbs change g-> j
Ger_CO = __make_std_override(inf_match=re.compile(u'ger$'),
    key="ger"
    )
Gir_CO = __make_std_override(inf_match=re.compile(u'gir$'),
    key="gir"
    )
for co in [ Ger_CO, Gir_CO]:
    co.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'g', u'j'), 
        persons=Persons.first_person_singular,
        documentation=u'g->j before o (present:first person singular) (present subjective) - preserves "g" sound')

# just -egir verbs
E_Gir_CO = __make_std_override(inf_match=re.compile(u'egir$'),
    parents="e:i",
    key=u"e_gir",
    examples=[u'elegir', u'corregir'],
    documentation="gir verbs that have a last stem vowel of e are stem changers ( so exigir is *not* a stem changer)"
)

Car_CO = __make_std_override(inf_match=re.compile(six.u('car$')), 
    key='car',
    documentation='verbs ending in -car have c -> qu before e',
    examples=[six.u('tocar')]
    )
Car_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c',u'qu'), Persons.first_person_singular)
Car_CO.override_tense_stem(Tenses.present_subjective_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c',u'qu'))

# http://www.intro2spanish.com/verbs/listas/master-zco.htm
Cer_After_Vowel_CO = __make_std_override(inf_match=re.compile(six.u('[aeiouáéíóú]cer$')),
    key='v_cer',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
    examples=[six.u('aparecer')]
    )
Cir_After_Vowel_CO = __make_std_override(inf_match=re.compile(six.u('[aeiouáéíóú]cir$')),
    key='v_cir',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o')
for co in [ Cer_After_Vowel_CO, Cir_After_Vowel_CO]:
    co.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c',u'zc'), Persons.first_person_singular)

Cer_After_Const_CO = __make_std_override(inf_match=re.compile(six.u('[^aeiouáéíóú]cer$')),
    key='c_cer',
    documentation='verbs ending in -cer or -cir with a preceding constant have c -> z before o',
    examples=[u'convencer']
    )
Cir_After_Const_CO = __make_std_override(inf_match=re.compile(six.u('[^aeiouáéíóú]cir$')),
    key='c_cir',
    documentation='verbs ending in -cer or -cir with a preceding constant have c -> z before o',
    examples=[u'convencer']
    )
for co in [ Cer_After_Const_CO, Cir_After_Const_CO ]:
    co.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem,u'c',u'z'), Persons.first_person_singular)

I2Y_PastTense_CO = __make_std_override(
    key=u'i2y',
    documentation="uir verbs, -aer, -eer, -oír, and -oer verbs: past tense (accented i, third person i->y) (triple vowels) http://www.studyspanish.com/verbs/lessons/pretortho.htm"
)
I2Y_PastTense_CO.override_tense_ending(Tenses.past_tense, lambda self, ending, **kwargs: accent_at(ending, 0), Persons.all_except(Persons.third_person))
I2Y_PastTense_CO.override_tense_ending(Tenses.past_tense, lambda self, ending, **kwargs: u'y' + ending[1:], Persons.third_person,
    documentation=u"change i to y")
    
Uir_CO = __make_std_override(inf_match=re.compile(six.u('[^qg]uir$'), re.IGNORECASE+re.UNICODE),
    parents=I2Y_PastTense_CO,
    key="uir",
    documentation='-uir but NOT quir nor guir verbs. Add a y before inflection except 1st/2nd plurals',
    examples=[u'incluir', u'construir', u'contribuir']
    )
Uir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: stem + u'y', Persons.Present_Tense_Stem_Changing_Persons)

Guir_CO = __make_std_override(inf_match=re.compile(six.u('guir$'), re.IGNORECASE+re.UNICODE),
    key='guir'
    )
# drop u in 1st person present
Guir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs:_replace_last_letter_of_stem(stem,u'u'), Persons.first_person_singular)

Past_Yo_Ud_Irr_CO = __make_std_override(key=u'e_and_o', 
    documentation=u"Some irregular verbs have past tense changes yo: 'e' and usted has 'o' (no accent) (this includes -ducir verbs)",
    examples=[u'estar', u'tener', u'traducir'])
Past_Yo_Ud_Irr_CO.override_tense_ending(Tenses.past_tense, u'e', Persons.first_person_singular)
Past_Yo_Ud_Irr_CO.override_tense_ending(Tenses.past_tense, u'o', Persons.third_person_singular)

Ducir_CO = __make_std_override(inf_match=re.compile(u'd[úu]cir$', re.IGNORECASE+re.UNICODE),
    key='ducir',
    parents=u'e_and_o',
    documentation=six.u('verbs ending in -ducir are also irregular in the past tense'),
    examples=[six.u('producir'), six.u('aducir')]
    )
Ducir_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c', u'j'), documentation=u'past tense is special case c-> j')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'eron', Persons.third_person_plural, documentation=u'normally ieron')

Eir_CO = __make_std_override(inf_match=re.compile(u'eír$', re.IGNORECASE+re.UNICODE),
    #pattern does not include the unaccented i.
    key=u"eír",
    documentation=u"eír verbs have accent on i in the infinitive",
    examples = [u'reír', u'freír']
    )
Eir_CO.override_present_stem_changers(lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'e', u'í'), 
        documentation="replace stem ending e with accented í")
Eir_CO.override_tense_ending(Tenses.present_tense, lambda self, **kwargs: u'ímos', documentation="accent on the i", persons=Persons.first_person_plural)
Eir_CO.override_past_stem_changers(lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'e'), documentation="remove the e from the stem")

Ei_r_CO = __make_std_override(inf_match=re.compile(u'eir$'),
    parents=Eir_CO,
    key=u'eir',
    documentation=u"eir ending usually has accent i but just in case, but separate than the 'correct' case")
# -aer, -eer, -oír, and -oer
for suffix in [ u'aer', u'eer', u'oír', u'oer'] :
    co = __make_std_override(inf_match=re.compile(suffix+u'$'),
        # the i2y pattern that can be automatically assigned to eer verbs
        key=suffix,
        parents=[I2Y_PastTense_CO],
        documentation=suffix+u" verbs"
        )

"""
http://www.spanish411.net/Spanish-Preterite-Tense.asp
"-ñir" or "-llir" use "-ó" and "-eron" endings instead of "-ió" and "-ieron" because they already have a "y" sound in their stems:
"""
LL_N_CO = __make_std_override(inf_match=re.compile(u'(ll|ñ)[eií]r$'),
    key=u"ll_ñ",
    examples=[u'tañer', u'reñir'],
    documentation=u"If the stem of -er or -ir verbs ends in ll or ñ, -iendo changes to -endo. (Since ll and ñ already have an i sound in them, it is not necessary to add it to the gerund ending.)")
LL_N_CO.override_tense_ending(Tenses.gerund, u'endo')
LL_N_CO.override_tense_ending(Tenses.past_tense, u'ó', Persons.third_person_singular, documentation="Note that this o is accented (other std overrides use an unaccented o")
LL_N_CO.override_tense_ending(Tenses.past_tense, u'eron', Persons.third_person_plural, documentation="Note that this o is accented (other std overrides use an unaccented o")

Iar_CO = __make_std_override(inf_match=re.compile(u'iar$', re.IGNORECASE+re.UNICODE),
    auto_match=False,
    key=u'iar',
    documentation=u'some iar verbs accent the i so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-iar-with-i-ii.htm\
     http://www.intro2spanish.com/verbs/listas/master-iar.htm',
    examples=[u'confiar',u'criar',u'desviar',u'enfriar',u'esquiar'])
Iar_CO.override_present_stem_changers(lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'i', u'í'))

Uar_CO = __make_std_override(inf_match=re.compile(u'[^g]uar$', re.IGNORECASE+re.UNICODE),
    auto_match=False,
    key=u'uar',
    documentation=u'some uar verbs accent the u so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-uar-with-u-uu.htm')
Uar_CO.override_present_stem_changers(lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'u', u'ú'))

Guar_CO = __make_std_override(inf_match=re.compile(u'guar$', re.IGNORECASE+re.UNICODE),
    key=u'guar',
    examples=[u'averiguar'],
    documentation=u'guar verbs need a umlaut/dieresis ü to keep the u sound so we pronounce gu like gw which keeps it consistent with the infinitive sound http://www.spanish411.net/Spanish-Preterite-Tense.asp')
Guar_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'u', u'ü'), Persons.first_person_singular,
    documentation="preserves sound in infinitive")

#>>>>>>> TODO: check to see of all -go verbs use just stem in imperative 2nd person, salir, tener,poner
Go_CO = __make_std_override(key=u'go', documentation="go verbs")
Go_CO.override_tense_ending(Tenses.present_tense, u"go", Persons.first_person_singular, documentation="go verb")
IGo_CO = __make_std_override(key=u'igo', documentation="go verbs", examples=[u'caer'])
IGo_CO.override_tense_ending(Tenses.present_tense, u"igo", Persons.first_person_singular, documentation="igo verb")

Oy_CO = __make_std_override(key=u'oy', documentation="oy verbs")
Oy_CO.override_tense_ending(Tenses.present_tense, u"oy", Persons.first_person_singular, documentation="oy verb")

Infinitive_Stems_E2D = __make_std_override(key=u'e2d', documentation="Future Tense/Conditional Tense:Some verbs convert the -er ending infinitive stem to a 'd'",
        examples=[u'tener'])
Infinitive_Stems_E2D.override_tense_stem(Tenses.future_tense, lambda self, stem, **kwargs: stem[:-2] + u'dr')
Infinitive_Stems_E2D.override_tense_stem(Tenses.conditional_tense, lambda self, stem, **kwargs: stem[:-2] + u'dr')

Infinitive_Stems_R_Only = __make_std_override(key=u'r_only', documentation="Future Tense/Conditional Tense:Some verbs remove the vowel in the infinitive ending to a r",
        examples=[u'haber'])
Infinitive_Stems_R_Only.override_tense_stem(Tenses.future_tense, lambda self, stem, **kwargs: stem[:-2] + u'r')
Infinitive_Stems_R_Only.override_tense_stem(Tenses.conditional_tense, lambda self, stem, **kwargs: stem[:-2] + u'r')

Present_Subjective_Infinitive = __make_dep_override(key='pres_sub_inf',
     documentation="radical stem changing -ar,-er verbs use the infinitive stem as the present subjective stem for nosotros/vosotros",
     auto_match=True,
     examples=[u"querer", u"oler",u"acordar"])
Present_Subjective_Infinitive.override_tense_stem(Tenses.present_subjective_tense, lambda self, **kwargs: self.stem, Persons.all_except(Persons.Present_Tense_Stem_Changing_Persons))
def __check_radical_stem_change_present_sub(self, verb):
    if verb.verb_ending_index in [Infinitive_Endings.er_verb, Infinitive_Endings.ar_verb]:
        applied = False
        for key in [u'o:ue', u'e:ie', u'e:i']:
            applied |= verb.has_override_applied(key)
        return applied
    else:
        return False        
Present_Subjective_Infinitive.is_match = six.create_bound_method(__check_radical_stem_change_present_sub, Present_Subjective_Infinitive)

# TODO: Need to check for reflexive verb
# Ir_Reflexive_Accent_I_CO = __make_std_override(u'[ií]r$', key="imp_accent_i", 
#     documentation="Second person plural, reflexive positive, ir verbs accent the i: Vestíos! (get dressed!) ",
#     examples=[u'vestirse'])
# Ir_Reflexive_Accent_I_CO.override_tense_stem(Tenses.imperative_positive, persons=Persons.second_person_plural,
#     documentation="Second person plural, reflexive positive, ir verbs accent the i: Vestíos! (get dressed!) ",
#     overrides=lambda self, **kwargs: remove_accent(self.stem) + u'ír'
#     )
# Third person only conjugations

def __block_conjugation(self, options, **kwargs):
    force_conjugation = pick(options, 'force_conjugation', False)
    if force_conjugation:
        conjugation = self._conjugate_stem_and_endings(options=options, **kwargs)
        return conjugation
    else:
        return None
    
Third_Person_Only_CO = __make_std_override(key='3rd_only', examples=[u'gustar'])
for tense in Tenses.all_except(Tenses.Person_Agnostic):
    Third_Person_Only_CO.override_tense(tense=tense, overrides=__block_conjugation, persons=Persons.all_except(Persons.third_person), documentation="third person only verbs don't conjugate for any other person")

Third_Person_Singular_Only_CO = __make_std_override(key='3rd_sing_only', examples=[u'helar'])
for tense in Tenses.all_except(Tenses.Person_Agnostic):
    Third_Person_Singular_Only_CO.override_tense(tense=tense, overrides=__block_conjugation, persons=Persons.all_except(Persons.third_person_singular), documentation="third person singular only verbs don't conjugate for any other person (weather)")
