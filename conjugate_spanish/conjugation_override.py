# -*- coding: utf-8 -*-
import json
import inspect
from .standard_endings import *
from .constants import *
from .conjugation_tracking import ConjugationNotes
from .vowel import Vowels
from string import Template
from conjugate_spanish.constants import IrregularNature
import types
from .utils import cs_error
"""
Special casing
key: need to allow verbs to opt out of special casing. For example, relucir does not have a c-> j substitution in past tense.
http://www.intro2spanish.com/verbs/listas/master-zco.htm
"""

__all__ = ['ConjugationOverride', 'Standard_Overrides', 'Dependent_Standard_Overrides', 'UniversalAccentFix', '_replace_last_letter_of_stem']

class Standard_Overrides_(dict):
    EXCLUDED = Template("Excluded (${conjugation_documentation})")
    INCLUDED = Template("${conjugation_documentation}")
    def __init__(self):
        pass
    
    def human_documentation(self, conjugation_overrides):
        documentation =[]
        if conjugation_overrides is not None:
            for conjugation_override in get_iterable(conjugation_overrides):
                documentation.append(self.human_conjugation_override(conjugation_override))
        return documentation
    
    def human_conjugation_override(self, conjugation_override_string):
        if conjugation_override_string is None or conjugation_override_string == '':
            return None
        
        if conjugation_override_string[0] == '-':
            lookup_key = conjugation_override_string[1:]
            conjugation = self.get(lookup_key)         
            return conjugation_override_string+": Excluded ("+";".join(conjugation.documentation)+")"
        else:
            lookup_key = conjugation_override_string
            conjugation = self.get(lookup_key)         
            return conjugation_override_string+":"+";".join(conjugation.documentation)            
    
Standard_Overrides = Standard_Overrides_()

def make_std_override(inf_match=None, parents=None, documentation=None, examples=None, key=None, auto_match=None, manual_overrides=None, irregular_nature=None):
    conjugation_override = ConjugationOverride(inf_match, parents, documentation, examples, key, auto_match, manual_overrides, irregular_nature)
    conjugation_override.add_std()
    return conjugation_override

Dependent_Standard_Overrides = {}
def make_dep_override(inf_match=None, parents=None, documentation=None, examples=None, key=None, auto_match=None, manual_overrides=None, irregular_nature=None):
    conjugation_override = ConjugationOverride(inf_match, parents, documentation, examples, key, auto_match, manual_overrides, irregular_nature)
    if conjugation_override.key is not None:
        if conjugation_override.key in Dependent_Standard_Overrides:
            raise Exception("Dependent_Standard_Overrides already defined for "+conjugation_override.key)
        else:
            Dependent_Standard_Overrides[conjugation_override.key] = conjugation_override
    return conjugation_override
# TODO need a way of adding notes to overrides

class ConjugationOverrideProperty(BaseConst):
    conjugations = (0, 'conjugations', 'conjugations')
    conjugation_stems = (1, 'conjugation_stems', 'conjugation_stems')
    conjugation_endings = (2, 'conjugation_endings', 'conjugation_endings')
    conjugation_joins = (3, 'conjugation_joins', 'conjugation_joins')

class ConjugationOverride(object):
    """
    TODO -- make conjugation a pipeline.
    Conjugation options: here because I want to explore a conjugation pipeline by removing from Verb.
    """
    FORCE_CONJUGATION = 'force_conjugation'
    REFLEXIVE_OVERRIDE = 'reflexive_override'
    
    """
    overrides are functions that are bound to the specific verb ( so become instance methods ) 
    They are called:
    { 'tense': tense, 'person': person, 'stem': current_conjugation_stem, 'ending' : current_conjugation_ending }
    overall overrides are called first, then ending overrides, then stem overrides
    
    """    
    def __init__(self, inf_match=None, parents=None, documentation=None, examples=None, key=None, auto_match=None, manual_overrides=None, irregular_nature=None):
        """
        :manual_overrides dict with conjugation_stems, conjugation_endings, conjugations key. values are dicts: tense names as keys; values are arrays or strings
        special case: tense name of 'present_except_nosvos' means present tense overriding just yo, tu, usted, ustedes
        """        
        self.inf_match = inf_match
        self.documentation =make_list(documentation)
        if parents is None:
            self._parents = None
        else:
            _parents = make_list(parents)
            self._parents = [ Standard_Overrides[parent] if isinstance(parent, str) else parent for parent in _parents] 
#             for parent in self.parents:
#                 self.documentation.extend([parent.key+" :"+parent_documentation for parent_documentation in parent.documentation])                                       
        
        self.examples=make_list(examples)
        self.key= key if key is not None else inf_match
        if auto_match is None:
            self.auto_match = inf_match is not None
        else:
            self.auto_match = auto_match  
        self.manual_overrides = manual_overrides
        self.add_manual_overrides(manual_overrides)  
        self.irregular_nature = irregular_nature
        
    @staticmethod
    def create_from_json(json_string, key=None):
        if isinstance(json_string, str) and json_string != '':
            try:
                manual_overrides = json.loads(make_unicode(json_string))
            except ValueError as e:
                print("while parsing json manual_overrides "+ json_string + " to verb_dictionary", repr(e))
                raise       
        conjugation_override = ConjugationOverride(key=key,manual_overrides=manual_overrides) 
        return conjugation_override   
            
    def add_manual_overrides(self, manual_overrides):
        if manual_overrides is None:
            return
        for conjugationOverrideProperty in ConjugationOverrideProperty.all():
            applies = conjugationOverrideProperty.key
            if applies in manual_overrides:
                overrides = manual_overrides[applies]
                if overrides != None:
                    for tenseStr, conjugation_override in overrides.items():
                        if conjugation_override is not None:
                            if tenseStr == 'present_except_nosvos':
                                tense = Tense.present_tense
                                persons = Person.Present_Tense_Stem_Changing_Persons()
                                self._overrides(tense, conjugation_override, applies, persons)
                            elif tenseStr == 'future_cond':
                                self._overrides(Tense.future_tense, conjugation_override, applies)
                                self._overrides(Tense.conditional_tense, conjugation_override, applies)
                            elif tenseStr == 'imperative_positive_second':
                                self._overrides(Tense.imperative_positive, conjugation_override, applies, Person.second_person_singular)
                            elif tenseStr == 'third_past':
                                self._overrides(Tense.past_tense, conjugation_override, applies, Person.third_person())
                            else:
                                tense = Tense.index(tenseStr)
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
                self_overrides = [ None ] * len(Tense)
                setattr(self, attr_name, self_overrides) 
            else:
                self_overrides = getattr(self, attr_name)
                
            if isinstance(overrides, str) or inspect.isfunction(overrides):
                if tense in Tense.Person_Agnostic():
                    # person is not relevant for gerund and past participle
                    self_overrides[tense] = overrides
                elif persons is not None:
                    if self_overrides[tense] is None:
                        self_overrides[tense] = [None] * len(Person)
                        
                    if isinstance(persons, Person):
                        # a single person has an override
                        self_overrides[tense][persons] = overrides
                    else:
                        for person in persons:
                            self_overrides[tense][person] = overrides
                else:
                    # a single stem for all persons of this tense
                    # expand it out to allow for later overrides of specific persons to be applied.
                    self_overrides[tense] = [overrides] * len(Person.all())
            elif tense in Tense.Person_Agnostic():
                self_overrides[tense] = overrides
            else:
                # overrides better be a list
                if self_overrides[tense] is None:
                    self_overrides[tense] = [None] * len(Person.all())
                    
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
        
    def override_past_stem_changers(self, overrides, documentation=None):
        """
        Special case because occurs so often in spanish
        overrides 3rd person singular and plural
        """
        self.override_tense_stem(tenses=Tense.past_tense, overrides=overrides, persons=Person.Past_Tense_Stem_Changing_Persons(), documentation=documentation)
    
    def override_tense(self, tenses, overrides,persons=None, documentation=None):
        """
        Used for case when the entire tense is very irregular
        """
        self._overrides(tenses, overrides, 'conjugations',persons)
        self.documentation.extend(make_list(documentation))      
        
    def __get_override(self, tense, person, attr_name):
        overrides = []
        if self.has_parents:
            for parent in self.parents:
                parent_override = parent.__get_override(tense, parent, attr_name)
                if parent_override is not None:
                    overrides.extend(parent_override)
                                
        if hasattr(self, attr_name):
            self_overrides = getattr(self, attr_name)
            if self_overrides[tense] is not None:
            # some overrides exist for this tense        
                if isinstance(self_overrides[tense], str):
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
        """
        Called by Conjugation_Override as an override is applied
        """        
        def __convert_to_self_function(override): 
            if override is None:
                return None           
            elif inspect.isfunction(override) or inspect.ismethod(override):
                boundfunc = types.MethodType(override, self)
                return boundfunc
            elif isinstance(override, str):
                return override                        
            else:
                cs_error("Override must be function or string not"+type(override),tense)    
        if self.has_parents:
            for parent in self.parents:
                verb.process_conjugation_override(parent)
            
        for conjugationOverrideProperty in ConjugationOverrideProperty.all():
            applies = conjugationOverrideProperty.key
            overrides = getattr(self, applies, None)
            if overrides != None:
                for tense, conjugation_override in enumerate(overrides):
                    if conjugation_override is not None:
                        ## temporary code while we collapse overriding so it is not exploded 
                        # for each verb.
                        if isinstance(conjugation_override, list):
                            overrides_ = [ __convert_to_self_function(co) for co in conjugation_override ] 
                        elif tense in Tense.Person_Agnostic():
                            overrides_ = __convert_to_self_function(conjugation_override)
                        else:
                            cs_error("something else")
                        verb._overrides(tense, overrides_, applies)
                        
    def add_std(self):
        if self.key is not None:
            if self.key in Standard_Overrides:
                raise Exception("Standard Override already defined for "+self.key)
            else:
                Standard_Overrides[self.key] = self
    
    @property
    def has_parents(self):
        return self.parents is not None and len(self.parents) > 0 
    
    @property
    def parents(self):        
        return self._parents

    def __repr__(self):
        return "ConjugationOverride(inf_match={0}, parents={1}, documentation={2}, examples={3}, key={4}, auto_match={5}, manual_overrides={6}, irregular_nature={7})".format(self.inf_match, self.parents, self.documentation, self.examples, self.key, self.auto_match, self.manual_overrides, self.irregular_nature)
    
Radical_Stem_Conjugation_Overrides = {} 
class Radical_Stem_Conjugation_Override(ConjugationOverride):
    def __init__(self, inf_stem_vowel, present_stem_vowels=None, beginning_word_vowels=None,
        past_stem_vowels = None,
        past_stem_persons=Person.third_person(),
        inf_match=None, parents=None, documentation=None, examples=None, auto_match=None, manual_overrides=None,
        ):
        if past_stem_vowels is None:
            past_stem_vowels = present_stem_vowels[0] 
        if present_stem_vowels is None:
            key = inf_stem_vowel+':p_'+past_stem_vowels
        else:
            key = inf_stem_vowel+':'+present_stem_vowels
        
        super(Radical_Stem_Conjugation_Override, self).__init__(inf_match, parents, documentation, examples, key, auto_match, manual_overrides, irregular_nature=IrregularNature.standard_irregular)

        def __make_radical_call(vowels_from, vowels_to, beginning_word_vowels_to=None, beginning_word_vowels_from=None):
            # Note: even for i-> transitions this is needed to ensure correct accents on the result.
            # -guir/-quir must not pick up a trailing 'u' as the 'last' vowel
            regex = re_compile('^(.*?)('+Vowels.re_any_string(vowels_from)+'|'+Vowels.re_any_string(vowels_to)+')?('+Vowels.consonants+'*(qu|gu)?)$')
            if beginning_word_vowels_from is not None:
                # huelo needs to be checked for 'hue' before looking for 'ue'
                regexes = [ re_compile('^()('+Vowels.re_any_string(beginning_word_vowels_from)+')('+Vowels.consonants+'*(qu|gu)?)$'), regex]
            else:
                regexes = [regex]
            def __radical_stem_change(self, conjugation_notes, **kwargs):
                # pick off last instance of the vowel.
                # for example:  'elegir' we need to change the last e to an i. 
                # the stem would be 'elej'
                for regex in regexes:
                    match_ = regex.match(conjugation_notes.core_verb)
                    if match_ is None:
                        continue
                    elif match_.group(2) == '':
                        self.__raise(msg=key+':vowels being looked for were not the last ones. '+conjugation_notes.core_verb, **kwargs)
                    
                    elif match_.group(1) == '':
                        # modifying beginning of word. ( ir, errar, erguir )
                        if beginning_word_vowels_to is not None:
                            changed_stem = beginning_word_vowels_to + match_.group(3)
                        else:
                            changed_stem = vowels_to + match_.group(3)
                    else:
                        if vowels_to[0] == 'u' and match_.group(1)[-1] == 'g':
                            # o -> ue before a g requires üe so that the u is pronounced.
                            changed_stem = match_.group(1)+'ü'+vowels_to[1:]+match_.group(3)
                        else:
                            changed_stem = match_.group(1)+vowels_to+match_.group(3)
                    
                    conjugation_notes.change(operation='rad_vowels',
                                            irregular_nature=IrregularNature.radical_stem_change,
                                            core_verb=changed_stem)
                    return
                self.__raise(msg=key+":No vowels in stem=u"+conjugation_notes.core_verb,**kwargs)
            return __radical_stem_change
        self.inf_stem_vowel = inf_stem_vowel
        self.present_stem_vowels = present_stem_vowels
        self.beginning_word_vowels = beginning_word_vowels
        self.past_stem_vowels = past_stem_vowels
        
        infinitive_to_past_tense = __make_radical_call(inf_stem_vowel, past_stem_vowels, beginning_word_vowels_to=beginning_word_vowels)
        if self.present_stem_vowels is not None:
            infinitive_to_present_tense = __make_radical_call(inf_stem_vowel, self.present_stem_vowels, beginning_word_vowels_to=beginning_word_vowels)
            # used to change present subjective 1st/2nd person plural
            present_tense_to_past_tense = __make_radical_call(self.present_stem_vowels, self.past_stem_vowels, beginning_word_vowels_from=beginning_word_vowels)
            present_tense_to_infinitive = __make_radical_call(self.present_stem_vowels, self.inf_stem_vowel, beginning_word_vowels_from=beginning_word_vowels)
            first_person_co_key = key+'_1sp'
            self.first_person_conjugation_override = make_std_override(key=first_person_co_key,
                documentation='radical stem changing '+key+ "; present tense first person only (allows for this to be turned off) - tener"
            )
            self.first_person_conjugation_override.override_tense_stem(Tense.present_tense, infinitive_to_present_tense, Person.first_person_singular)
            self.most_present_tense = make_std_override(key=key+'_present',
                parents=[self.first_person_conjugation_override],
                documentation='radical stem changing '+key+ "; present tense"
                )
        
            self.most_present_tense.override_tense_stem(Tense.present_tense, infinitive_to_present_tense,
                [Person.second_person_singular, Person.third_person_singular, Person.third_person_plural])
            # TODO - check to see if the first_person stem radical change has been applied. before doing a revert ( tener ) 
            self.nos_vos_present_subjective_ir = make_std_override(key=key+'_pres_sub_nos_vos_ir',
                documentation='stem changing ir verbs that actually applied the stem change in the yo-present use the 3rd past tense vowel',  examples=['dormir','morir']
            )
            self.nos_vos_present_subjective_ir.override_tense_stem(Tense.present_subjective_tense, present_tense_to_past_tense, [Person.first_person_plural,Person.second_person_plural])
            self.nos_vos_present_subjective_ar = make_std_override(key=key+'_pres_sub_nos_vos',
                documentation='stem changing ar,er verbs use the infinitive vowel. ir verbs that do not apply the stem change in the yo-present use the infinitive vowel',  examples=['dormir','morir']
            )
            self.nos_vos_present_subjective_ar.override_tense_stem(Tense.present_subjective_tense, present_tense_to_infinitive, [Person.first_person_plural,Person.second_person_plural])

        # http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA5u1NsOEJ
        # but for example, absolver o:ue does not have past tense stem changing
        self.stem_changing_ir_gerund = make_std_override(key=key+"_ir_gerund",
            examples=['dormir'],
            documentation="Any -ir verb that has a stem-change in the third person preterite (e->i, or o->u) will have the same stem-change in the gerund form.\
             The -er verb poder also maintains its preterite stem-change in the gerund form.\
             http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA5u1NsOEJ"
        )
        self.stem_changing_ir_gerund.override_tense_stem(Tense.gerund, infinitive_to_past_tense)
        # http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA5u1NsOEJ
        # but for example, absolver o:ue does not have past tense stem changing
        self.stem_changing_ir_past = make_std_override(key=key+"_past_3rd",
            examples=['dormir'],
            documentation="Any -ir verb that has a stem-change in the third person preterite (e->i, or o->u) will have the same stem-change in the gerund form. The -er verb poder also maintains its preterite stem-change in the gerund form."
        )
        self.stem_changing_ir_past.override_tense_stem(Tense.past_tense, infinitive_to_past_tense, past_stem_persons)
        
        self.add_std() # bad if we are running a web site but this makes the below code work
        self.stem_changing_ir_past_all = make_std_override(key=key+"_past_all",
            examples=['venir','poder','predecir'],
            parents=[self.key,self.stem_changing_ir_gerund],
            documentation="Some -ir verbs apply the stem-change to all preterite (must be manually applied)"
        )
        self.stem_changing_ir_past_all.override_tense_stem(Tense.past_tense, infinitive_to_past_tense, Person.all())
        
        self.conjugation_overrides = [ None ] * len(Infinitive_Ending)
        if self.present_stem_vowels is not None:
            for ending in Infinitive_Ending.all():
                self.conjugation_overrides[ending] = [self.first_person_conjugation_override, self.most_present_tense ]
        else:
            for ending in Infinitive_Ending.all():
                self.conjugation_overrides[ending] = [ ]            

        self.conjugation_overrides[Infinitive_Ending.ir_verb].extend([self.stem_changing_ir_gerund, self.stem_changing_ir_past])
            
    def apply(self, verb):
        conjugation_overrides = self.conjugation_overrides[verb.verb_ending_index]
        for conjugation_override in conjugation_overrides:
            verb.process_conjugation_override(conjugation_override)
        if verb.verb_ending_index == Infinitive_Ending.ir_verb and verb.has_override_applied(self.first_person_conjugation_override.key):
            verb.process_conjugation_override(self.nos_vos_present_subjective_ir)
        else:
            verb.process_conjugation_override(self.nos_vos_present_subjective_ar)
            
    @classmethod
    def make(cls, inf_stem_vowel, present_stem_vowels=None, past_stem_vowels=None, past_stem_persons=Person.third_person(), beginning_word_vowels=None):
        conjugation_override = Radical_Stem_Conjugation_Override(inf_stem_vowel=inf_stem_vowel, present_stem_vowels=present_stem_vowels, 
            past_stem_vowels=past_stem_vowels,
            beginning_word_vowels=beginning_word_vowels)
        # really should be here -- but we don't have to worry about adding an object to a global before init completes for this program so f*ck it
#         conjugation_override.add_std()
        Radical_Stem_Conjugation_Overrides[conjugation_override.key] = conjugation_override 

"""
RADICAL STEM CHANGE PATTERNS
http://www.spanishdict.com/topics/show/38
"""
Radical_Stem_Conjugation_Override.make(inf_stem_vowel='e', present_stem_vowels='i')
Radical_Stem_Conjugation_Override.make(inf_stem_vowel='e', present_stem_vowels='ie', beginning_word_vowels='ye')
Radical_Stem_Conjugation_Override.make(inf_stem_vowel='o', present_stem_vowels='ue', beginning_word_vowels='hue')
#adquirir - to acquire     inquirir - to inquire  : only 2 examples
Radical_Stem_Conjugation_Override.make(inf_stem_vowel='i', present_stem_vowels='ie')
#jugar - only example
Radical_Stem_Conjugation_Override.make(inf_stem_vowel='u', present_stem_vowels='ue')
# [^qg]uar verbs act like radical stem changers
Radical_Stem_Conjugation_Override.make(inf_stem_vowel='u', present_stem_vowels='ú')
# iar verbs
Radical_Stem_Conjugation_Override.make(inf_stem_vowel='i', present_stem_vowels='í')
# hacer and satisfacer
Radical_Stem_Conjugation_Override.make(inf_stem_vowel='a', past_stem_vowels='i', past_stem_persons=Person.all())

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
    
def _universal_accent_correction(self, conjugation_notes, **kwargs):
    # if the ending has an accent then we remove the accent on the stem
    if Vowels.accented_vowel_check.search(conjugation_notes.core_verb) and Vowels.accented_vowel_check.search(conjugation_notes.ending):
        conjugation_notes.change(operation='_universal_accent_correction',
                                 irregular_nature=IrregularNature.regular,
                                  core_verb=Vowels.remove_accent(conjugation_notes.core_verb))

# explicitly applied at the end
UniversalAccentFix = ConjugationOverride()
UniversalAccentFix.override_tense_join(Tense.all(), _universal_accent_correction, documentation="ensure an accented ending overrides an accented stem")
    
STARTS_WITH_E=re_compile('^([eé])(.*)$')
STARTS_WITH_I=re_compile('^([ii])(.*)$')
STARTS_WITH_O=re_compile('^([oó])(.*)$')
ENDS_WITH_B = re_compile('^(.*)(b)$')
ENDS_WITH_G = re_compile('^(.*)(g)$')
ENDS_WITH_LL_N = re_compile("^(.*)(ll|ñ)$")
ENDS_WITH_QU = re_compile('^(.*)(qu)$')
ENDS_WITH_R = re_compile('^(.*)(r)$')
ENDS_WITH_AC = re_compile('^(.*)(ac)$')
ENDS_WITH_OR = re_compile('^(.*)(or)$')
ENDS_WITH_OLV = re_compile('^(.*)(olv)$')
ENDS_WITH_U=re_compile('^(.*)([uúü])$')
ENDS_WITH_C = re_compile('^(.*)(c)$')
ENDS_WITH_Z = re_compile('^(.*)(z)$')
ENDS_WITH_I = re_compile('^(.*)(i)$')
ENDS_WITH_ACCENTED_I = re_compile('^(.*)(í)$')
ENDS_WITH_E = re_compile('^(.*)(e)$')
# -ir verbs in vosotros imperitive positive need to have accented i
ENDS_WITH_ID_OR_IR = re_compile('^(.*)([ií][rd])$')
ENDS_WITH_VOWEL = re_compile('^(.*?'+Vowels.all_group+')()$')
STARTS_WITH_NON_I_VOWEL=re_compile('^([aeo])(.*)$')
REMOVE_ENDING =re_compile('^(.*)()$')
def _check_and_change(conjugation_notes,
    stem_re=re_compile("^(.*)()$"), ending_re=re_compile('^()(.*)$'), 
    stem_ending_replacement=None, ending_beginning_replacement=None,
    operation='_check_and_change',
    irregular_nature=IrregularNature.sound_consistence):
    """
    replaces the stem ending or the ending beginning  if the stem_re.group(2) != u'' and ending_re.group(1) != u''
    otherwise return [stem, ending]
    :param stem_re - a regular expression that has 2 groups. (default always matches)
    :param ending_re - regular expression that has 2 groups.(default always matches)
    :param stem_ending_replacement - if '.' then is no replacement
    :param ending_beginning_replacement - if '.' then is no replacement
    """
    stem_match = stem_re.match(conjugation_notes.core_verb)    
    ending_match = ending_re.match(conjugation_notes.ending)
    changes = { }
    if stem_match is not None and ending_match is not None:
        if stem_ending_replacement is not None:
            changes['core_verb'] = stem_match.group(1)+stem_ending_replacement
            
        if ending_beginning_replacement is not None:
            changes['ending'] = ending_beginning_replacement+ending_match.group(2) 
        conjugation_notes.change(operation=operation,
                                 irregular_nature=irregular_nature,
                                  **changes)
        return True
    return False

Use_Er_Conjugation_In_Past = make_std_override(key='use_er',
    documentation='some -ar verbs use -er conjugation in past tense', examples= ['andar','estar'])
Use_Er_Conjugation_In_Past.override_tense_ending(Tense.past_tense,
      lambda self, conjugation_notes, **kwargs: conjugation_notes.change(
          operation='use_er',
          irregular_nature=IrregularNature.rare,
          ending=Standard_Conjugation_Endings[Infinitive_Ending.er_verb][conjugation_notes.tense][conjugation_notes.person]))
    
"""
==================================================
Gerund  - http://www.spanishdict.com/answers/100043/spanish-gerund-form#.VqA2iFNsOEI
Whenever an unstressed i appears between two vowels, the spelling always changes to a y, not just in the following gerunds.
Note: eír verbs are not included
"""
Yendo_Gerund_CO = make_std_override(
    key='yendo',
    documentation="-er or -er verbs that have a preceding vowel",
    examples=['ir', 'poseer'])
def _yendo_(self,conjugation_notes, **kwargs):
    if conjugation_notes.core_verb == '': #ir
        _check_and_change(conjugation_notes, ending_re=STARTS_WITH_I, ending_beginning_replacement='y', operation=self.key)
    else:
        _check_and_change(conjugation_notes, ENDS_WITH_VOWEL, STARTS_WITH_I, ending_beginning_replacement='y', operation=self.key)
Yendo_Gerund_CO.override_tense_join(Tense.gerund, _yendo_)

def _zar_check(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_Z,STARTS_WITH_E,'c', operation=self.key)
Zar_CO = make_std_override(inf_match=re_compile('zar$'), 
    key='zar',
    documentation='verbs ending in -zar have z -> c before e',
    examples=['comenzar', 'lanzar'],
    irregular_nature=IrregularNature.sound_consistence
    )
Zar_CO.override_tense_join(Tense.past_tense, _zar_check, Person.first_person_singular)
Zar_CO.override_tense_join(Tense.present_subjective_tense, _zar_check)

def _gar_check(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_G,STARTS_WITH_E,'gu', operation=self.key)
    
Gar_CO = make_std_override(inf_match=re_compile('gar$'),
    key='gar', 
    documentation='verbs ending in -gar have g -> gu before e',
    examples=['pagar'],
    irregular_nature=IrregularNature.sound_consistence
    )
Gar_CO.override_tense_join(Tense.past_tense, _gar_check, Person.first_person_singular)
Gar_CO.override_tense_join(Tense.present_subjective_tense, _gar_check)

#
# -ger, -gir verbs change g-> j
def _geir_check(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_G,STARTS_WITH_O,'j', operation=self.key)
    
Ger_CO = make_std_override(inf_match=re_compile('ger$'),
    key="ger"
    )
Gir_CO = make_std_override(inf_match=re_compile('gir$'),
    key="gir"
    )
for co in [ Ger_CO, Gir_CO]:
    co.override_tense_join(Tense.present_tense, _geir_check,
        persons=Person.first_person_singular,
        documentation='g->j before o (present:first person singular) (present subjective) - preserves "g" sound')

# just -egir verbs
E_Gir_CO = make_std_override(inf_match=re_compile('egir$'),
    parents="e:i",
    key="e_gir",
    examples=['elegir', 'corregir'],
    documentation="gir verbs that have a last stem vowel of e are stem changers ( so exigir is *not* a stem changer)"
)

# ========================================================================
def _car_check(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_C,STARTS_WITH_E,'qu', operation=self.key)
    
Car_CO = make_std_override(inf_match=re_compile('car$'), 
    key='car',
    documentation='verbs ending in -car have c -> qu before e',
    examples=['tocar'],
    irregular_nature=IrregularNature.sound_consistence
    )
Car_CO.override_tense_join(Tense.past_tense, _car_check, Person.first_person_singular)
Car_CO.override_tense_join(Tense.present_subjective_tense, _car_check)

# ========================================================================
# http://www.intro2spanish.com/verbs/listas/master-zco.htm

# TODO : NOTE: May need to do this check for e_and_o verbs?
def _v_ceir_check(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_C,STARTS_WITH_O,'zc', operation=self.key)

def _c2_z_check(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_C,STARTS_WITH_O,'z', operation=self.key)

Cer_After_Vowel_CO = make_std_override(inf_match=re_compile(Vowels.all_group+'cer$'),
    key='v_cer',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
    examples=['aparecer'],
    irregular_nature=IrregularNature.sound_consistence
    )
Cir_After_Vowel_CO = make_std_override(inf_match=re_compile(Vowels.all_group+'cir$'),
    key='v_cir',
    documentation='verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
    irregular_nature=IrregularNature.sound_consistence)
for co in [ Cer_After_Vowel_CO, Cir_After_Vowel_CO]:
    co.override_tense_join(Tense.present_tense, _v_ceir_check, Person.first_person_singular)
    # Exists to handle satisfacer/hacer: (e_and_o) verbs : May not to be so general?
    co.override_tense_join(Tense.past_tense, _c2_z_check, Person.third_person_singular)
  
Cer_After_Const_CO = make_std_override(inf_match=re_compile(Vowels.consonants+'cer$'),
    key='c_cer',
    documentation='verbs ending in -cer or -cir with a preceding consonant have c -> z before o',
    examples=['convencer'],
    irregular_nature=IrregularNature.sound_consistence
    )
Cir_After_Const_CO = make_std_override(inf_match=re_compile(Vowels.consonants+'cir$'),
    key='c_cir',
    documentation='verbs ending in -cer or -cir with a preceding consonant have c -> z before o',
    examples=['convencer'],
    irregular_nature=IrregularNature.sound_consistence
    )
for co in [ Cer_After_Const_CO, Cir_After_Const_CO ]:
    co.override_tense_join(Tense.present_tense, _c2_z_check, Person.first_person_singular)
# ========================================================================
# http://www.studyspanish.com/verbs/lessons/pretortho.htm

def __i2y_past_3rd_i_check(self, conjugation_notes, **kwargs):
    if not _check_and_change(conjugation_notes, ENDS_WITH_VOWEL,
        STARTS_WITH_I, ending_beginning_replacement='y', operation=self.key):
        # if no change remove the i in the ending (traer, decir)
        _check_and_change(conjugation_notes, ending_re=STARTS_WITH_I,ending_beginning_replacement='', operation=self.key)

I2Y_PastTense_CO = make_std_override(
    key='i2y',
    documentation="uir verbs, -aer, -eer, -oír, and -oer verbs: past tense (accented i, third person i->y) \
    IF the stem is still ending in a vowel \
    AND the ending hasn't already been changed (e_and_o) \
    IF the stem has been changed to a non-vowel ( traer ) then the i is dropped in third person\
    (triple vowels) http://www.studyspanish.com/verbs/lessons/pretortho.htm"
)
I2Y_PastTense_CO.override_tense_join(Tense.past_tense, __i2y_past_3rd_i_check, Person.third_person(), documentation="change i to y or remove i if stem doesn't end in vowel")

def _accent_i_check(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_VOWEL,
        STARTS_WITH_I, ending_beginning_replacement='í', operation=self.key)
    
Accent_All_But_3_PastTense_CO = make_std_override(key='accent_i_past', 
    documentation='-aer, -eer, -oír, and -oer verbs: past tense (accented i,for 1st,2nd persons) if stem still ends in a vowel'
    )
Accent_All_But_3_PastTense_CO.override_tense_join(Tense.past_tense, _accent_i_check, Person.all_except(Person.third_person()),
    documentation="change i to accented i")
Accent_I_PastParticipleAdjective_CO = make_std_override(key='accent_i_pp_adj', 
    documentation='-aer, -eer, -oír, and -oer verbs: past participle and adjective tense (accented i) if stem still ends in a vowel'
    )
Accent_I_PastParticipleAdjective_CO.override_tense_join(Tense.past_participle, _accent_i_check,
    documentation="change i to accented i")

I_I_CO = make_std_override(key="i_i_remove",
    documentation='remove duplicate i where the stem would end in an i and the ending would start with an i. past tense reír',
    examples= ['reír'])
def _i_i_remove(self,conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_I, STARTS_WITH_I, ending_beginning_replacement='', operation=self.key)
    
I_I_CO.override_tense_join(Tense.past_tense, _i_i_remove, Person.third_person())
I_I_CO.override_tense_join(Tense.gerund, _i_i_remove)
def _uir_present_check(self, conjugation_notes, **kwargs):
    """
    insert a 'y' between stem (if it still ends in a u) and any ending that starts in a vowel that is not 'i'
    """
    _check_and_change(conjugation_notes, ENDS_WITH_U, STARTS_WITH_NON_I_VOWEL, 'uy', operation=self.key)
    
Uir_CO = make_std_override(inf_match=re_compile('[^qg]uir$'),
    parents=[I2Y_PastTense_CO, Yendo_Gerund_CO], 
    key="uir",
    documentation='-uir but NOT quir nor guir verbs. Add a y before inflection except 1st/2nd plurals',
    examples=['incluir', 'construir', 'contribuir']
    )
#make sure the -u is still there and hasn't been removed by some other rule.
Uir_CO.override_tense_join(Tense.present_tense, _uir_present_check, Person.Present_Tense_Stem_Changing_Persons())

Guir_CO = make_std_override(inf_match=re_compile('guir$'),
    key='guir'
    )
# drop u in 1st person present
Guir_CO.override_tense_stem(Tense.present_tense, lambda self, conjugation_notes,
                            **kwargs:conjugation_notes.change(operation=self.key,
                                                              irregular_nature=IrregularNature.sound_consistence,
                                                               core_verb= _replace_last_letter_of_stem(conjugation_notes.core_verb,'u')), 
    Person.first_person_singular)

Quir_CO = make_std_override(inf_match=re_compile('quir$'),
    key='quir',
    examples= ['delinquir'],
    documentation='drop qu in first person and replace with c (sound preserving)'
    )
def _quir_(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_QU, STARTS_WITH_O,
        stem_ending_replacement='c',
        operation=self.key)
    
Quir_CO.override_tense_join(Tense.present_tense, _quir_, Person.first_person_singular)

Past_Yo_Ud_Irr_CO = make_std_override(key='e_and_o', 
    documentation="Some irregular verbs have past tense changes yo: 'e' and usted has 'o' (no accent) (this includes -ducir verbs)",
    examples=['estar', 'tener', 'traducir'])
Past_Yo_Ud_Irr_CO.override_tense_ending(Tense.past_tense, 'e', Person.first_person_singular)
Past_Yo_Ud_Irr_CO.override_tense_ending(Tense.past_tense, 'o', Person.third_person_singular)

## TODO : note this may also apply to decir verbs (bendecir)
Ducir_CO = make_std_override(inf_match=re_compile('d[úu]cir$'),
    key='ducir',
    parents='e_and_o',
    documentation='verbs ending in -ducir are also irregular in the past tense',
    examples=['producir', 'aducir']
    )
Ducir_CO.override_tense_stem(Tense.past_tense,
        lambda self, conjugation_notes, **kwargs: conjugation_notes.change(operation=self.key, 
           irregular_nature=IrregularNature.standard_irregular,
           core_verb=_replace_last_letter_of_stem(conjugation_notes.core_verb, 'c', 'j')),
        documentation='past tense is special case c-> j')
Ducir_CO.override_tense_ending(Tense.past_tense,
    lambda self, conjugation_notes, **kwargs: conjugation_notes.change(operation=self.key, 
        irregular_nature=IrregularNature.standard_irregular, ending='eron'),
        Person.third_person_plural, documentation='normally ieron')

Eir_CO = make_std_override(inf_match=re_compile('eír$'),
    #pattern does not include the unaccented i.
    key="eír",
    parents=["e:i", Accent_All_But_3_PastTense_CO, Accent_I_PastParticipleAdjective_CO, I_I_CO],
    documentation="eír verbs have accent on i in the infinitive",
    examples = ['reír', 'freír']
    )
def _eir_present_tense_first_plural(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_E, STARTS_WITH_I, ending_beginning_replacement='í',
                      irregular_nature=IrregularNature.standard_irregular,
                      operation=self.key)
    
def _eir_present_tense_most(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_I, STARTS_WITH_NON_I_VOWEL, stem_ending_replacement='í',
                      irregular_nature=IrregularNature.standard_irregular, operation=self.key)
    
def _eir_present_sub_tense_first_plural(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_ACCENTED_I, STARTS_WITH_NON_I_VOWEL, stem_ending_replacement='i',
                      irregular_nature=IrregularNature.standard_irregular, operation=self.key)
    
Eir_CO.override_tense_join(Tense.present_tense, _eir_present_tense_most, documentation="replace i (after stem change) with accented í", persons=Person.all_except(Person.first_person_plural))
Eir_CO.override_tense_join(Tense.present_tense, _eir_present_tense_first_plural, documentation="accent on the i", persons=Person.first_person_plural)
Eir_CO.override_tense_join(Tense.present_subjective_tense, _eir_present_sub_tense_first_plural, documentation="remove accent on the i", persons=Person.first_person_plural)

Ei_r_CO = make_std_override(inf_match=re_compile('eir$'),
    parents=Eir_CO,
    key='eir',
    documentation="eir ending usually has accent i but just in case, but separate than the 'correct' case")
# -aer, -eer, -oír, and -oer
for suffix in [ 'aer', 'eer', 'oír', 'oer'] :
    co = make_std_override(inf_match=re_compile(suffix+'$'),
        # the i2y pattern that can be automatically assigned to eer verbs
        key=suffix,
        parents=[Yendo_Gerund_CO, I2Y_PastTense_CO, Accent_All_But_3_PastTense_CO, Accent_I_PastParticipleAdjective_CO], 
        documentation=suffix+" verbs"
        )

#separate o and e with a 'y'
def _oir_present_tense(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_VOWEL, STARTS_WITH_E, ending_beginning_replacement='ye', operation=self.key)
    
Standard_Overrides['oír'].override_tense_join(Tense.present_tense,_oir_present_tense,
    [Person.second_person_singular, Person.third_person_singular, Person.third_person_plural])
def _oir_present_nos(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_VOWEL, STARTS_WITH_I, ending_beginning_replacement='í', operation=self.key)
    
Standard_Overrides['oír'].override_tense_join(Tense.present_tense,_oir_present_nos, Person.first_person_plural)

"""
http://www.spanish411.net/Spanish-Preterite-Tense.asp
"-ñir" or "-llir" use "-ó" and "-eron" endings instead of "-ió" and "-ieron" because they already have a "y" sound in their stems:
"""
def _ll_n_check(self, conjugation_notes, **kwargs):
    # remove the i if ends in ñ or ll (sound preservation)
    _check_and_change(conjugation_notes, ENDS_WITH_LL_N, STARTS_WITH_I, ending_beginning_replacement='', operation=self.key)
    
LL_N_CO = make_std_override(inf_match=re_compile('(ll|ñ)[eií]r$'),
    key="ll_ñ",
    examples=['tañer', 'reñir'],
    documentation="If the stem of -er or -ir verbs ends in ll or ñ, -iendo changes to -endo. (Since ll and ñ already have an i sound in them, it is not necessary to add it to the gerund ending.)")
LL_N_CO.override_tense_join(Tense.gerund, _ll_n_check)
LL_N_CO.override_tense_join(Tense.past_tense, _ll_n_check, Person.third_person())

Iar_CO = make_std_override(inf_match=re_compile('iar$'),
    auto_match=False,
    key='iar',
    parents=['i:í'],
    documentation='some iar verbs accent the i so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-iar-with-i-ii.htm\
     http://www.intro2spanish.com/verbs/listas/master-iar.htm',
    examples=['confiar','criar','desviar','enfriar','esquiar'])

No_Iar_CO = make_std_override(inf_match=re_compile('[d]iar$'),
    auto_match=True,
    key='no_iar',
    #parents=['-iar'],
    documentation='some iar verbs accent the i so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-iar-with-i-ii.htm\
     http://www.intro2spanish.com/verbs/listas/master-iar.htm \
     In listed examples -diar verbs were always "-iar"',
    examples=['envidiar','estudiar','fastidiar','odiar'])

Yes_Iar_CO = make_std_override(inf_match=re_compile('[lfr]iar$'),
    auto_match=True,
    key='yes_iar',
    parents=['iar'],
    documentation='some iar verbs accent the i so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-iar-with-i-ii.htm\
     http://www.intro2spanish.com/verbs/listas/master-iar.htm \
     In listed examples -fiar,-liar,riar verbs were always "iar"',
    examples=['amplifiar','confiar','desafiar','des-confiar','fiar','fotografiar', 'porfiar', 'telegrafiar', 'agriar','arriar','criar','enfriar'])

Uar_CO = make_std_override(inf_match=re_compile('[^g]uar$'),
    key='uar',
    parents=['u:ú'],
    documentation='some uar verbs accent the u so that it is not weak http://www.intro2spanish.com/verbs/conjugation/conj-uar-with-u-uu.htm only exceptions seem to be guar verbs',
    examples=['continuar'])

Guar_CO = make_std_override(inf_match=re_compile('guar$'),
    key='guar',
    examples=['averiguar'],
    documentation='guar verbs need a umlaut/dieresis ü to keep the u sound so we pronounce gu like gw which keeps it consistent with the infinitive sound http://www.spanish411.net/Spanish-Preterite-Tense.asp',
    irregular_nature=IrregularNature.sound_consistence)
def _umlaut_u_(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_U, STARTS_WITH_E, stem_ending_replacement='ü', operation=self.key)
    
Guar_CO.override_tense_join(Tense.past_tense, _umlaut_u_, Person.first_person_singular,
    documentation="preserves sound in infinitive")
Guar_CO.override_tense_join(Tense.present_subjective_tense, _umlaut_u_, documentation="preserves sound in infinitive")

def __go(self, conjugation_notes, **kwargs):
    if conjugation_notes.core_verb[-1:] in Vowels.all:
        conjugation_notes.change(operation='igo', irregular_nature=IrregularNature.standard_irregular, core_verb=conjugation_notes.core_verb +'ig')
    elif conjugation_notes.core_verb[-1:] == 'c':
        # hacer, saticificar is example
        # drop c before -go
        conjugation_notes.change(operation='c_go', irregular_nature=IrregularNature.standard_irregular, core_verb=conjugation_notes.core_verb[:-1]+'g')
    else:
        conjugation_notes.change(operation=self.key, irregular_nature=IrregularNature.standard_irregular, core_verb=conjugation_notes.core_verb +'g')
Go_CO = make_std_override(key='go', documentation="go verbs -ig if last stem letter is vowel", examples=['caer'])
Go_CO.override_tense_stem(Tense.present_tense, __go, Person.first_person_singular, documentation="go verb")

Oy_CO = make_std_override(key='oy', documentation="oy verbs")
Oy_CO.override_tense_ending(Tense.present_tense, lambda self, conjugation_notes, **kwargs: conjugation_notes.change(operation=self.key, irregular_nature=IrregularNature.standard_irregular, ending="oy"), Person.first_person_singular, documentation="oy verb")

Infinitive_Stems_E2D = make_std_override(key='e2d', documentation="Future Tense/Conditional Tense:Some verbs convert the -er ending infinitive stem to a 'd'",
        examples=['tener'])
Infinitive_Stems_E2D.override_tense_stem(Tense.future_cond(), lambda self, conjugation_notes, **kwargs: conjugation_notes.change(operation=self.key, irregular_nature=IrregularNature.rare, core_verb=conjugation_notes.core_verb[:-2] + 'dr'))

Infinitive_Stems_R_Only = make_std_override(key='r_only', documentation="Future Tense/Conditional Tense:Some verbs remove the vowel in the infinitive ending to a r",
        examples=['haber'])
Infinitive_Stems_R_Only.override_tense_stem(Tense.future_cond(), lambda self, conjugation_notes, **kwargs: conjugation_notes.change(operation=self.key, irregular_nature=IrregularNature.rare, core_verb=conjugation_notes.core_verb[:-2] + 'r'))

Imperative_Infinitive_Stem_Only = make_std_override(key="imp_inf_stem_only", 
    documentation='in second person positive some verbs only use the infinitive stem with no ending',
    examples=['poner','salir','tener'])
Imperative_Infinitive_Stem_Only.override_tense(Tense.imperative_positive,
                                               lambda self, conjugation_notes, **kwargs: 
                                               conjugation_notes.change(operation=self.key, irregular_nature=IrregularNature.rare, core_verb=conjugation_notes.phrase.stem, ending=''), Person.second_person_singular)

Past_Participle_To = make_std_override(key='pp_to',
                           documentation='past participle ends in -to',
                           examples=['abrir'])
Past_Participle_To.override_tense_ending(Tense.past_participle,
      lambda self, conjugation_notes, **kwargs: conjugation_notes.change(operation=self.key, irregular_nature=IrregularNature.rare, ending='to'))
Adjective_To = make_std_override(key='adj_to',
                documentation="adjective ends in -to but NOT the past participle")
Adjective_To.override_tense_ending(Tense.adjective,
   lambda self, conjugation_notes, **kwargs: conjugation_notes.change(operation=self.key, irregular_nature=IrregularNature.rare, ending='to'))

Past_Adj_To = make_std_override(key='pa_to', parents=[Past_Participle_To, Adjective_To])

def _olver_(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_OLV,
        stem_ending_replacement='uel', operation=self.key, irregular_nature=IrregularNature.standard_irregular)
    
Past_Participle_Olver = make_std_override(key="pp_olver",
    parents=Past_Adj_To,
    documentation="past participle that has a olver -to ending rather than the normal -ado, -ando",
    examples=['absolver', 'resolver', 'volver'])
Past_Participle_Olver.override_tense_join(Tense.past_participle, _olver_)
def _abrir_(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_R,
        stem_ending_replacement='ier', operation=self.key, irregular_nature=IrregularNature.standard_irregular)
    
Past_Participle_Rir = make_std_override(key="pp_rir",
    parents=Past_Adj_To,
    documentation="past participle that has a -rir -to ending rather than the normal -ado, -ando",
    examples=['abrir', 'cubrir'])
Past_Participle_Rir.override_tense_join(Tense.past_participle, _abrir_)
def _morir_(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_OR,
        stem_ending_replacement='uer', operation=self.key, irregular_nature=IrregularNature.standard_irregular)
    
Past_Participle_Orir = make_std_override(key="pp_orir",
    parents=Past_Adj_To,
    documentation="past participle that has a olver -to ending rather than the normal -ado, -ando",
    examples=['morir'])
Past_Participle_Orir.override_tense_join(Tense.past_participle, _morir_)
def _cribir_(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes, ENDS_WITH_B,
        stem_ending_replacement='', operation=self.key, irregular_nature=IrregularNature.standard_irregular)
    
Past_Participle_Cribir = make_std_override(key="pp_cribir",
    inf_match=re_compile('cribir$'),
    parents=Past_Adj_To,
    documentation="past participle that has a cribir -to ending rather than the normal -ado, -ando",
    examples=['escribir','transcribir','inscribir', 'describir' ])
Past_Participle_Cribir.override_tense_join(Tense.past_participle, _cribir_)

def _ver_(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes,
        stem_ending_replacement='is', operation=self.key, irregular_nature=IrregularNature.standard_irregular)
Past_Participle_Ver = make_std_override(key="pp_ver",
    parents=Past_Adj_To,
    documentation="past participle that has a ver -to ending rather than the normal -ado, -ando",
    examples=['ver'])
Past_Participle_Ver.override_tense_join(Tense.past_participle, _ver_)

def _acer_(self, conjugation_notes, **kwargs):
    _check_and_change(conjugation_notes,
        ENDS_WITH_AC, REMOVE_ENDING,
        stem_ending_replacement='',
        ending_beginning_replacement='echo',  operation=self.key, irregular_nature=IrregularNature.standard_irregular)
    
Past_Participle_Acer = make_std_override(key="pp_acer",
    documentation="past participle that has a acer -to ending rather than the normal -ado, -ando",
    examples=['hacer', 'satisfacer'])
Past_Participle_Acer.override_tense_join(Tense.past_participle, _acer_)

UnaccentPresent_Past_CO = make_std_override(key='unaccent_present_past', documentation='small verbs have no accent on past and present tense conjugations',
    examples= ['dar','ir'])
UnaccentPresent_Past_CO.override_tense_join([Tense.present_tense,Tense.past_tense],
     lambda self, conjugation_notes, **kwargs: conjugation_notes.change(operation=self.key, 
                irregular_nature=IrregularNature.standard_irregular, 
                core_verb=Vowels.remove_accent(conjugation_notes.core_verb), 
                ending=Vowels.remove_accent(conjugation_notes.ending)))

def __block_conjugation(self, conjugation_notes, options, **kwargs):
    force_conjugation = pick(options, ConjugationOverride.FORCE_CONJUGATION, False)
    if not force_conjugation:
        conjugation_notes.block()
        
Defective_CO = make_std_override(key='defective',
                                 documentation='special case verbs that have only a few tenses',
                                 examples=['soler'])
tenses = list(Tense.future_cond())
tenses.extend(Tense.imperative())
Defective_CO.override_tense(tenses, __block_conjugation)
# TODO: Need to check for reflexive verb
# Ir_Reflexive_Accent_I_CO = make_std_override(u'[ií]r$', key=u"imp_accent_i", 
#     documentation=u"Second person plural, reflexive positive, ir verbs accent the i: Vestíos! (get dressed!) ",
#     examples=[u'vestirse'])
# Ir_Reflexive_Accent_I_CO.override_tense_stem(Tense.imperative_positive, persons=Person.second_person_plural,
#     documentation=u"Second person plural, reflexive positive, ir verbs accent the i: Vestíos! (get dressed!) ",
#     overrides=lambda self, **kwargs: Vowels.remove_accent(self.stem) + u'ír'
#     )
# Third person only conjugations
    
Third_Person_Only_CO = make_std_override(key='3rd_only', examples=['gustar'])
Third_Person_Only_CO.override_tense(tenses=Tense.all_except(Tense.Person_Agnostic()), overrides=__block_conjugation, persons=Person.all_except(Person.third_person()), documentation="third person only verbs don't conjugate for any other person")

Third_Person_Singular_Only_CO = make_std_override(key='3rd_sing_only', examples=['helar'])
Third_Person_Singular_Only_CO.override_tense(tenses=Tense.all_except(Tense.Person_Agnostic()), overrides=__block_conjugation, persons=Person.all_except(Person.third_person_singular), documentation="third person singular only verbs don't conjugate for any other person (weather)")
