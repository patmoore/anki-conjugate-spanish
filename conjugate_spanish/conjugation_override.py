# -*- coding: utf-8 -*-
import json
import inspect
from standard_endings import Standard_Conjugation_Endings
from constants import *
"""
Special casing
key: need to allow verbs to opt out of special casing. For example, relucir does not have a c-> j substitution in past tense.
http://www.intro2spanish.com/verbs/listas/master-zco.htm
"""

__all__ = ['ConjugationOverride', 'Standard_Overrides', 'Dependent_Standard_Overrides', 'UniversalAccentFix', '_replace_last_letter_of_stem']

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
    def create_from_json(json_string, key=None):
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
        for applies in ['conjugations', 'conjugation_stems', 'conjugation_endings', 'conjugation_joins']:
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

    def _overrides(self, tenses, overrides, attr_name, persons=None):
        if tenses is None:
            raise Exception("tenses is none")
        for tense in get_iterable(tenses):
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
                    
    def override_tense_stem(self, tenses, overrides,persons=None, documentation=None):
        """
        :overrides:
        """
        self._overrides(tenses, overrides, 'conjugation_stems', persons)
        self.documentation.extend(make_list(documentation))            
                    
    def override_tense_ending(self, tense, overrides,persons=None, documentation=None):
        self._overrides(tense, overrides, 'conjugation_endings',persons)
        self.documentation.extend(make_list(documentation))      
        
    def override_tense_join(self, tense, overrides,persons=None, documentation=None):
        self._overrides(tense, overrides, 'conjugation_joins',persons)
        self.documentation.extend(make_list(documentation))      
        
    def override_present_stem_changers(self, overrides, documentation=None):
        """
        Special case because occurs so often in spanish
        overrides 1st person singular, 2nd person singular and 3rd person singular and plural
        """
        self.override_tense_stem(tenses=Tenses.present_tense, overrides=overrides, persons=Persons.Present_Tense_Stem_Changing_Persons, documentation=documentation)
        
    def override_past_stem_changers(self, overrides, documentation=None):
        """
        Special case because occurs so often in spanish
        overrides 3rd person singular and plural
        """
        self.override_tense_stem(tenses=Tenses.past_tense, overrides=overrides, persons=Persons.Past_Tense_Stem_Changing_Persons, documentation=documentation)
    
    def override_tense(self, tenses, overrides,persons=None, documentation=None):
        """
        Used for case when the entire tense is very irregular
        """
        self._overrides(tenses, overrides, 'conjugations',persons)
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
        if self.inf_match is None:
            raise Exception(self.key+":No inf_match - did you forget to provide an is_match method?")
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
            
        for applies in ['conjugations', 'conjugation_stems', 'conjugation_endings', 'conjugation_joins']:
            overrides = getattr(self, applies, None)
            if overrides != None:
                for tense, conjugation_override in enumerate(overrides):
                    if conjugation_override is not None:
                        verb._overrides(tense, conjugation_override, applies)
    
# -guir must not pick up a trailing 'u'
__find_last_vowel_re = re_compile(u'^(.*?)(['+AllVowels+u'])([^'+AllVowels+u']*u?)$')
def __radical_stem_change(stem, vowel_change, vowels_to):
    # pick off last instance of the vowel.
    # for example:  'elegir' we need to change the last e to an i. 
    # the stem would be 'elej'
    match_ = __find_last_vowel_re.match(stem)
    if match_ is None:
        raise Exception("No vowel at all in stem="+stem)
    elif match_.group(2) == vowels_to:
        # some other rule resulted in this change already being applied.
        changed_stem = stem
    elif match_.group(2) == vowel_change:
        if vowels_to[0] != u'u':
            changed_stem = match_.group(1)+vowels_to+match_.group(3)
        elif match_.group(1) == u'':
            # example oler
            changed_stem = u'h'+vowels_to+match_.group(3)
        elif match_.group(1)[-1] == u'g':
            changed_stem = match_.group(1)+u'ü'+vowels_to[1:]+match_.group(3)
        else:
            changed_stem = match_.group(1)+vowels_to+match_.group(3)
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
    [u'e', u'ie', u'i', u'i'],
    # dormir
    [u'o', u'ue', u'u', u'u'],
    #adquirir - to acquire     inquirir - to inquire  : only 2 examples
    [u'i', u'ie', None, None],
    #jugar - only example
    [u'u', u'ue', None, None]
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
        
    radical_prstem_call = __make_radical_call(vowel_from, present_vowels_to)
    first_person_co = __make_std_override(key=key+u'_1sp',
        documentation='radical stem changing '+key+ "; present tense first person only (allows for this to be turned off) - tener"
        )
    first_person_co.override_tense_stem(Tenses.present_tense, __make_radical_call(vowel_from, present_vowels_to), Persons.first_person_singular)
    conjugation_override = __make_std_override(key=key,
        parents=[first_person_co],
        documentation='radical stem changing '+key+ "; present tense"
        )

    conjugation_override.override_tense_stem(Tenses.present_tense, __make_radical_call(vowel_from, present_vowels_to),
        [Persons.second_person_singular, Persons.third_person_singular, Persons.third_person_plural])

    if gerund_vowel is not None:
        # http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA5u1NsOEJ
        # but for example, absolver o:ue does not have past tense stem changing
        stem_changing_ir_gerund = __make_dep_override(key=key+u"_ir_gerund",
            auto_match=True,
            examples=[u'dormir'],
            documentation=u"Any -ir verb that has a stem-change in the third person preterite (e->i, or o->u) will have the same stem-change in the gerund form. The -er verb poder also maintains its preterite stem-change in the gerund form."
        )
        stem_changing_ir_gerund.override_tense_stem(Tenses.gerund, __make_radical_call(vowel_from, gerund_vowel))
#         stem_changing_ir_gerund.override_tense_stem(Tenses.past_tense, __make_radical_call(vowel_from, past_vowels_to), Persons.Past_Tense_Stem_Changing_Persons)        
        stem_changing_ir_gerund.is_match = six.create_bound_method(__make_check_stem_ir(key), stem_changing_ir_gerund)
    
    if past_vowels_to is not None:
        # http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA5u1NsOEJ
        # but for example, absolver o:ue does not have past tense stem changing
        stem_changing_ir_past = __make_dep_override(key=key+u"_ir_past",
            auto_match=True,
            examples=[u'dormir'],
            documentation=u"Any -ir verb that has a stem-change in the third person preterite (e->i, or o->u) will have the same stem-change in the gerund form. The -er verb poder also maintains its preterite stem-change in the gerund form."
        )
        stem_changing_ir_past.override_tense_stem(Tenses.past_tense, __make_radical_call(vowel_from, past_vowels_to), Persons.third_person)
#         stem_changing_ir_gerund.override_tense_stem(Tenses.past_tense, __make_radical_call(vowel_from, past_vowels_to), Persons.Past_Tense_Stem_Changing_Persons)        
        stem_changing_ir_past.is_match = six.create_bound_method(__make_check_stem_ir(key), stem_changing_ir_gerund)
        
#     if past_vowels_to is not None:
#         nos_vos_present_subjective = __make_dep_override(key=u'stem_changing_past_ir_'+key,
#             documentation=u'nos vos present subjunctive',  examples=[u'dormir',u'morir'],
#             auto_match=True)
#         nos_vos_present_subjective.override_tense_stem(Tenses.past_tense, __make_radical_call(vowel_from, past_vowels_to), [Persons.first_person_plural,Persons.second_person_plural])
#         nos_vos_present_subjective.is_match = six.create_bound_method(__make_check_stem_ir(key), nos_vos_present_subjective)
    
def _replace_last_letter_of_stem(stem, expected_last_letter, new_stem_ending= None):
    truncated_stem = stem[:-1]
    last_letter = stem[-1]
    if expected_last_letter is not None and expected_last_letter != last_letter:
        # this occurs if another alteration happened first ( for example hacer )
        return stem
#         raise Exception(stem+":wrong stem ending expected:"+expected_last_letter+" got "+last_letter)
    elif new_stem_ending is not None:
        return truncated_stem + new_stem_ending
    else:
        return truncated_stem        
    
def _replace_first_letter_of_ending(ending, expected_first_letter, new_beginning= None):
    truncated_ending = ending[1:]
    first_letter = ending[0]
    if expected_first_letter is not None and expected_first_letter != first_letter:
        # this occurs if another alteration happened first
        return ending
#         raise Exception(ending+":wrong ending expected:"+expected_last_letter+" got "+last_letter)
    elif new_beginning is not None:
        return new_beginning+truncated_ending
    else:
        return truncated_ending   
def _universal_accent_correction(self, stem, ending, **kwargs):
    # if the ending has an accent then we remove the accent on the stem
    if accented_vowel_check.search(stem) and accented_vowel_check.search(ending):
        return [ remove_accent(stem), ending]
    else:
        return [stem, ending]

# explicitly applied at the end
UniversalAccentFix = ConjugationOverride()
UniversalAccentFix.override_tense_join(Tenses.all, _universal_accent_correction, documentation=u"ensure an accented ending overrides an accented stem")
    
STARTS_WITH_E=re_compile(u'^([eé])(.*)$')
STARTS_WITH_I=re_compile(u'^([ii])(.*)$')
STARTS_WITH_O=re_compile(u'^([oó])(.*)$')
ENDS_WITH_B = re_compile(u'^(.*)(b)$')
ENDS_WITH_G = re_compile(u'^(.*)(g)$')
ENDS_WITH_LL_N = re_compile(u"^(.*)(ll|ñ)$")
ENDS_WITH_QU = re_compile(u'^(.*)(qu)$')
ENDS_WITH_R = re_compile(u'^(.*)(r)$')
ENDS_WITH_AC = re_compile(u'^(.*)(ac)$')
ENDS_WITH_OR = re_compile(u'^(.*)(or)$')
ENDS_WITH_OLV = re_compile(u'^(.*)(olv)$')
ENDS_WITH_U=re_compile(u'^(.*[uúü])()$')
ENDS_WITH_C = re_compile(u'^(.*)(c)$')
ENDS_WITH_Z = re_compile(u'^(.*)(z)$')
ENDS_WITH_I = re_compile(u'^(.*)(i)$')
ENDS_WITH_ACCENTED_I = re_compile(u'^(.*)(í)$')
ENDS_WITH_E = re_compile(u'^(.*)(e)$')
ENDS_WITH_VOWEL = re_compile(u'^(.*?['+AllVowels+u'])()$')
STARTS_WITH_NON_I_VOWEL=re_compile(u'^([aeo])(.*)$')
REMOVE_ENDING =re_compile(u'^(.*)()$')
def _check_and_change(stem, ending,
    stem_re=re_compile(u"^(.*)()$"), ending_re=re_compile(u'^()(.*)$'), 
    stem_ending_replacement=None, ending_beginning_replacement=None):
    """
    replaces the stem ending or the ending beginning  if the stem_re.group(2) != u'' and ending_re.group(1) != u''
    otherwise return [stem, ending]
    :param stem_re - a regular expression that has 2 groups. (default always matches)
    :param ending_re - regular expression that has 2 groups.(default always matches)
    :param stem_ending_replacement - if '.' then is no replacement
    :param ending_beginning_replacement - if '.' then is no replacement
    """
    stem_match = stem_re.match(stem)    
    ending_match = ending_re.match(ending)
    result = [stem,ending]
        
    if stem_match is not None and ending_match is not None:
        if stem_ending_replacement is not None:
            result[0] = stem_match.group(1)+stem_ending_replacement
            
        if ending_beginning_replacement is not None:
            result[1] = ending_beginning_replacement+ending_match.group(2) 
    return result

Use_Er_Conjugation_In_Past = __make_std_override(key=u'use_er',
    documentation=u'some verbs', examples= [u'andar'])
Use_Er_Conjugation_In_Past.override_tense_ending(Tenses.past_tense, lambda self, tense, person, **kwargs: Standard_Conjugation_Endings[Infinitive_Endings.er_verb][tense][person])
    
"""
==================================================
Gerund  - http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA2iFNsOEI
Whenever an unstressed i appears between two vowels, the spelling always changes to a y, not just in the following gerunds.
Note: eír verbs are not included
"""
Yendo_Gerund_CO = __make_std_override(
    key=u'yendo',
    documentation=u"-er or -er verbs that have a preceding vowel",
    examples=[u'ir', u'poseer'])
def _yendo_(self,stem,ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_VOWEL, STARTS_WITH_I, ending_beginning_replacement=u'y')
    return result
Yendo_Gerund_CO.override_tense_join(Tenses.gerund, _yendo_)

def _zar_check(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_Z,STARTS_WITH_E,u'c')
    return result

Zar_CO = __make_std_override(inf_match=re_compile(u'zar$'), 
    key='zar',
    documentation='verbs ending in -zar have z -> c before e',
    examples=[u'comenzar', u'lanzar']
    )
Zar_CO.override_tense_join(Tenses.past_tense, _zar_check, Persons.first_person_singular)
Zar_CO.override_tense_join(Tenses.present_subjective_tense, _zar_check)

def _gar_check(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_G,STARTS_WITH_E,u'gu')
    return result
    
Gar_CO = __make_std_override(inf_match=re_compile(u'gar$'),
    key='gar', 
    documentation='verbs ending in -gar have g -> gu before e',
    examples=[u'pagar']
    )
Gar_CO.override_tense_join(Tenses.past_tense, _gar_check, Persons.first_person_singular)
Gar_CO.override_tense_join(Tenses.present_subjective_tense, _gar_check)

#
# -ger, -gir verbs change g-> j
def _geir_check(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_G,STARTS_WITH_O,u'j')
    return result
    
Ger_CO = __make_std_override(inf_match=re_compile(u'ger$'),
    key="ger"
    )
Gir_CO = __make_std_override(inf_match=re_compile(u'gir$'),
    key="gir"
    )
for co in [ Ger_CO, Gir_CO]:
    co.override_tense_join(Tenses.present_tense, _geir_check, 
        persons=Persons.first_person_singular,
        documentation=u'g->j before o (present:first person singular) (present subjective) - preserves "g" sound')

# just -egir verbs
E_Gir_CO = __make_std_override(inf_match=re_compile(u'egir$'),
    parents=u"e:i",
    key=u"e_gir",
    examples=[u'elegir', u'corregir'],
    documentation=u"gir verbs that have a last stem vowel of e are stem changers ( so exigir is *not* a stem changer)"
)

# ========================================================================
def _car_check(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_C,STARTS_WITH_E,u'qu')
    return result

Car_CO = __make_std_override(inf_match=re_compile(six.u('car$')), 
    key='car',
    documentation='verbs ending in -car have c -> qu before e',
    examples=[six.u('tocar')]
    )
Car_CO.override_tense_join(Tenses.past_tense, _car_check, Persons.first_person_singular)
Car_CO.override_tense_join(Tenses.present_subjective_tense, _car_check)

# ========================================================================
# http://www.intro2spanish.com/verbs/listas/master-zco.htm
def _v_ceir_check(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_C,STARTS_WITH_O,u'zc')
    return result    
Cer_After_Vowel_CO = __make_std_override(inf_match=re_compile(u'['+AllVowels+u']cer$'),
    key='v_cer',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
    examples=[six.u('aparecer')]
    )
Cir_After_Vowel_CO = __make_std_override(inf_match=re_compile(u'['+AllVowels+u']cir$'),
    key='v_cir',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o')
for co in [ Cer_After_Vowel_CO, Cir_After_Vowel_CO]:
    co.override_tense_join(Tenses.present_tense, _v_ceir_check, Persons.first_person_singular)

def _c_ceir_check(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_C,STARTS_WITH_O,u'z')
    return result    
Cer_After_Const_CO = __make_std_override(inf_match=re_compile(u'[^'+AllVowels+u']cer$'),
    key='c_cer',
    documentation='verbs ending in -cer or -cir with a preceding consonant have c -> z before o',
    examples=[u'convencer']
    )
Cir_After_Const_CO = __make_std_override(inf_match=re_compile(u'[^'+AllVowels+u']cir$'),
    key='c_cir',
    documentation='verbs ending in -cer or -cir with a preceding consonant have c -> z before o',
    examples=[u'convencer']
    )
for co in [ Cer_After_Const_CO, Cir_After_Const_CO ]:
    co.override_tense_join(Tenses.present_tense, _c_ceir_check, Persons.first_person_singular)
# ========================================================================
# http://www.studyspanish.com/verbs/lessons/pretortho.htm

def __i2y_past_3rd_i_check(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_VOWEL,
        STARTS_WITH_I, ending_beginning_replacement=u'y')
    if result[0] == stem and result[1] == ending:
        # if no change remore the i in the ending (traer)
        result = _check_and_change(stem, ending, ending_re=STARTS_WITH_I,ending_beginning_replacement=u'')
    return result

I2Y_PastTense_CO = __make_std_override(
    key=u'i2y',
    documentation="uir verbs, -aer, -eer, -oír, and -oer verbs: past tense (accented i, third person i->y) \
    IF the stem is still ending in a vowel \
    AND the ending hasn't already been changed (e_and_o) \
    IF the stem has been changed to a non-vowel ( traer ) then the i is dropped in third person\
    (triple vowels) http://www.studyspanish.com/verbs/lessons/pretortho.htm"
)
I2Y_PastTense_CO.override_tense_join(Tenses.past_tense, __i2y_past_3rd_i_check, Persons.third_person, documentation=u"change i to y or remove i if stem doesn't end in vowel")
def _accent_i_check(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_VOWEL,
        STARTS_WITH_I, ending_beginning_replacement=u'í')
    return result
Accent_All_But_3_PastTense_CO = __make_std_override(key=u'accent_i_past', 
    documentation=u'-aer, -eer, -oír, and -oer verbs: past tense (accented i,for 1st,2nd persons) if stem still ends in a vowel'
    )
Accent_All_But_3_PastTense_CO.override_tense_join(Tenses.past_tense, _accent_i_check, Persons.all_except(Persons.third_person),
    documentation=u"change i to accented i")
Accent_I_PastParticipleAdjective_CO = __make_std_override(key=u'accent_i_pp_adj', 
    documentation=u'-aer, -eer, -oír, and -oer verbs: past participle and adjective tense (accented i) if stem still ends in a vowel'
    )
Accent_I_PastParticipleAdjective_CO.override_tense_join(Tenses.past_part_adj, _accent_i_check,
    documentation=u"change i to accented i")

I_I_CO = __make_std_override(key="i_i_remove",
    documentation=u'remove duplicate i where the stem would end in an i and the ending would start with an i. past tense reír',
    examples= [u'reír'])
def _i_i_remove(self,stem,ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_I, STARTS_WITH_I, ending_beginning_replacement=u'')
    return result
I_I_CO.override_tense_join(Tenses.past_tense, _i_i_remove, Persons.third_person)
I_I_CO.override_tense_join(Tenses.gerund, _i_i_remove)
def _uir_present_check(self, stem, ending, **kwargs):
    """
    insert a 'y' between stem (if it still ends in a u) and any ending that starts in a vowel that is not 'i'
    """
    result = _check_and_change(stem, ending, ENDS_WITH_U, STARTS_WITH_NON_I_VOWEL, u'y')
    return result
Uir_CO = __make_std_override(inf_match=re_compile(six.u('[^qg]uir$')),
    parents=[I2Y_PastTense_CO], 
    key="uir",
    documentation='-uir but NOT quir nor guir verbs. Add a y before inflection except 1st/2nd plurals',
    examples=[u'incluir', u'construir', u'contribuir']
    )
#make sure the -u is still there and hasn't been removed by some other rule.
Uir_CO.override_tense_join(Tenses.present_tense, _uir_present_check, Persons.Present_Tense_Stem_Changing_Persons)

Guir_CO = __make_std_override(inf_match=re_compile(six.u('guir$')),
    key='guir'
    )
# drop u in 1st person present
Guir_CO.override_tense_stem(Tenses.present_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem,u'u'), 
    Persons.first_person_singular)

Quir_CO = __make_std_override(inf_match=re_compile(six.u('quir$')),
    key='quir',
    examples= [u'delinquir'],
    documentation=u'drop qu in first person and replace with c (sound preserving)'
    )
def _quir_(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_QU, STARTS_WITH_O,
        stem_ending_replacement=u'c')
    return result
Quir_CO.override_tense_join(Tenses.present_tense, _quir_, Persons.first_person_singular)

Past_Yo_Ud_Irr_CO = __make_std_override(key=u'e_and_o', 
    documentation=u"Some irregular verbs have past tense changes yo: 'e' and usted has 'o' (no accent) (this includes -ducir verbs)",
    examples=[u'estar', u'tener', u'traducir'])
Past_Yo_Ud_Irr_CO.override_tense_ending(Tenses.past_tense, u'e', Persons.first_person_singular)
Past_Yo_Ud_Irr_CO.override_tense_ending(Tenses.past_tense, u'o', Persons.third_person_singular)

Ducir_CO = __make_std_override(inf_match=re_compile(u'd[úu]cir$'),
    key='ducir',
    parents=u'e_and_o',
    documentation=six.u('verbs ending in -ducir are also irregular in the past tense'),
    examples=[six.u('producir'), six.u('aducir')]
    )
Ducir_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'c', u'j'), documentation=u'past tense is special case c-> j')
Ducir_CO.override_tense_ending(Tenses.past_tense, u'eron', Persons.third_person_plural, documentation=u'normally ieron')

Eir_CO = __make_std_override(inf_match=re_compile(u'eír$'),
    #pattern does not include the unaccented i.
    key=u"eír",
    parents=["e:i", Accent_All_But_3_PastTense_CO, Accent_I_PastParticipleAdjective_CO, I_I_CO],
    documentation=u"eír verbs have accent on i in the infinitive",
    examples = [u'reír', u'freír']
    )
def _eir_present_tense_first_plural(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_E, STARTS_WITH_I, ending_beginning_replacement=u'í')
    return result
def _eir_present_tense_most(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_I, STARTS_WITH_NON_I_VOWEL, stem_ending_replacement=u'í')
    return result
def _eir_present_sub_tense_first_plural(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_ACCENTED_I, STARTS_WITH_NON_I_VOWEL, stem_ending_replacement=u'i')
    return result
Eir_CO.override_tense_join(Tenses.present_tense, _eir_present_tense_most, documentation="replace i (after stem change) with accented í", persons=Persons.all_except(Persons.first_person_plural))
Eir_CO.override_tense_join(Tenses.present_tense, _eir_present_tense_first_plural, documentation="accent on the i", persons=Persons.first_person_plural)
Eir_CO.override_tense_join(Tenses.present_subjective_tense, _eir_present_sub_tense_first_plural, documentation="remove accent on the i", persons=Persons.first_person_plural)

Ei_r_CO = __make_std_override(inf_match=re_compile(u'eir$'),
    parents=Eir_CO,
    key=u'eir',
    documentation=u"eir ending usually has accent i but just in case, but separate than the 'correct' case")
# -aer, -eer, -oír, and -oer
for suffix in [ u'aer', u'eer', u'oír', u'oer'] :
    co = __make_std_override(inf_match=re_compile(suffix+u'$'),
        # the i2y pattern that can be automatically assigned to eer verbs
        key=suffix,
        parents=[Yendo_Gerund_CO, I2Y_PastTense_CO, Accent_All_But_3_PastTense_CO, Accent_I_PastParticipleAdjective_CO], 
        documentation=suffix+u" verbs"
        )

#separate o and e with a 'y'
def _oir_present_tense(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_VOWEL, STARTS_WITH_E, ending_beginning_replacement=u'ye')
    return result
Standard_Overrides[u'oír'].override_tense_join(Tenses.present_tense,_oir_present_tense, 
    [Persons.second_person_singular, Persons.third_person_singular, Persons.third_person_plural])
def _oir_present_nos(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_VOWEL, STARTS_WITH_I, ending_beginning_replacement=u'í')
    return result
Standard_Overrides[u'oír'].override_tense_join(Tenses.present_tense,_oir_present_nos, Persons.first_person_plural)

"""
http://www.spanish411.net/Spanish-Preterite-Tense.asp
"-ñir" or "-llir" use "-ó" and "-eron" endings instead of "-ió" and "-ieron" because they already have a "y" sound in their stems:
"""
def _ll_n_check(self, stem, ending, **kwargs):
    # remove the i if ends in ñ or ll (sound preservation)
    result = _check_and_change(stem, ending, ENDS_WITH_LL_N, STARTS_WITH_I, ending_beginning_replacement=u'')
    return result
LL_N_CO = __make_std_override(inf_match=re_compile(u'(ll|ñ)[eií]r$'),
    key=u"ll_ñ",
    examples=[u'tañer', u'reñir'],
    documentation=u"If the stem of -er or -ir verbs ends in ll or ñ, -iendo changes to -endo. (Since ll and ñ already have an i sound in them, it is not necessary to add it to the gerund ending.)")
LL_N_CO.override_tense_join(Tenses.gerund, _ll_n_check)
LL_N_CO.override_tense_join(Tenses.past_tense, _ll_n_check, Persons.third_person)

Iar_CO = __make_std_override(inf_match=re_compile(u'iar$'),
    auto_match=False,
    key=u'iar',
    documentation=u'some iar verbs accent the i so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-iar-with-i-ii.htm\
     http://www.intro2spanish.com/verbs/listas/master-iar.htm',
    examples=[u'confiar',u'criar',u'desviar',u'enfriar',u'esquiar'])
Iar_CO.override_present_stem_changers(lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'i', u'í'))

Uar_CO = __make_std_override(inf_match=re_compile(u'[^g]uar$'),
    auto_match=False,
    key=u'uar',
    documentation=u'some uar verbs accent the u so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-uar-with-u-uu.htm')
Uar_CO.override_present_stem_changers(lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'u', u'ú'))

Guar_CO = __make_std_override(inf_match=re_compile(u'guar$'),
    key=u'guar',
    examples=[u'averiguar'],
    documentation=u'guar verbs need a umlaut/dieresis ü to keep the u sound so we pronounce gu like gw which keeps it consistent with the infinitive sound http://www.spanish411.net/Spanish-Preterite-Tense.asp')
Guar_CO.override_tense_stem(Tenses.past_tense, lambda self, stem, **kwargs: _replace_last_letter_of_stem(stem, u'u', u'ü'), Persons.first_person_singular,
    documentation="preserves sound in infinitive")

#>>>>>>> TODO: check to see of all -go verbs use just stem in imperative 2nd person, salir, tener,poner
def __go(self, stem, **kwargs):
    if stem[-1:] in AllVowels:
        return stem +u'ig'
    elif stem[-1:] == u'c':
        # hacer is example
        return stem[:-1]+u'g'
    else:
        return stem +u'g'
Go_CO = __make_std_override(key=u'go', documentation="go verbs -ig if last stem letter is vowel", examples=[u'caer'])
Go_CO.override_tense_stem(Tenses.present_tense, __go, Persons.first_person_singular, documentation="go verb")

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

Past_Participle_To = __make_std_override(key=u'ppto')
Past_Participle_To.override_tense_ending(Tenses.past_part_adj, u'to')
def _olver_(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_OLV,
        stem_ending_replacement=u'uel')
    return result
Past_Participle_Olver = __make_std_override(key=u"pp_olver",
    parents=[Past_Participle_To],
    documentation=u"past participle that has a olver -to ending rather than the normal -ado, -ando",
    examples=[u'absolver', u'resolver', u'volver'])
Past_Participle_Olver.override_tense_join(Tenses.past_part_adj, _olver_)
def _abrir_(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_R,
        stem_ending_replacement=u'ier')
    return result
Past_Participle_Rir = __make_std_override(key=u"pp_rir",
    parents=[Past_Participle_To],
    documentation=u"past participle that has a -rir -to ending rather than the normal -ado, -ando",
    examples=[u'abrir', u'cubrir'])
Past_Participle_Rir.override_tense_join(Tenses.past_part_adj, _abrir_)
def _morir_(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_OR,
        stem_ending_replacement=u'uer')
    return result
Past_Participle_Orir = __make_std_override(key=u"pp_orir",
    parents=[Past_Participle_To],
    documentation=u"past participle that has a olver -to ending rather than the normal -ado, -ando",
    examples=[u'morir'])
Past_Participle_Orir.override_tense_join(Tenses.past_part_adj, _morir_)
def _cribir_(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending, ENDS_WITH_B,
        stem_ending_replacement=u'')
    return result
Past_Participle_Cribir = __make_std_override(key=u"pp_cribir",
    inf_match=re_compile(u'cribir$'),
    parents=[Past_Participle_To],
    documentation=u"past participle that has a cribir -to ending rather than the normal -ado, -ando",
    examples=[u'escribir',u'transcribir',u'inscribir', u'describir' ])
Past_Participle_Cribir.override_tense_join(Tenses.past_part_adj, _cribir_)
def _ver_(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending,
        stem_ending_replacement=u'is')
    return result
Past_Participle_Ver = __make_std_override(key=u"pp_ver",
    parents=[Past_Participle_To],
    documentation=u"past participle that has a ver -to ending rather than the normal -ado, -ando",
    examples=[u'ver'])
Past_Participle_Ver.override_tense_join(Tenses.past_part_adj, _ver_)
def _acer_(self, stem, ending, **kwargs):
    result = _check_and_change(stem, ending,
        ENDS_WITH_AC, REMOVE_ENDING,
        stem_ending_replacement=u'',
        ending_beginning_replacement=u'echo')
    return result
Past_Participle_Acer = __make_std_override(key=u"pp_acer",
    documentation=u"past participle that has a acer -to ending rather than the normal -ado, -ando",
    examples=[u'hacer', u'satisfacer'])
Past_Participle_Acer.override_tense_join(Tenses.past_part_adj, _acer_)
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
Third_Person_Only_CO.override_tense(tenses=Tenses.all_except(Tenses.Person_Agnostic), overrides=__block_conjugation, persons=Persons.all_except(Persons.third_person), documentation="third person only verbs don't conjugate for any other person")

Third_Person_Singular_Only_CO = __make_std_override(key='3rd_sing_only', examples=[u'helar'])
Third_Person_Singular_Only_CO.override_tense(tenses=Tenses.all_except(Tenses.Person_Agnostic), overrides=__block_conjugation, persons=Persons.all_except(Persons.third_person_singular), documentation="third person singular only verbs don't conjugate for any other person (weather)")
