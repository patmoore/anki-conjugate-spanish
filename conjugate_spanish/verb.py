# -*- coding: utf-8 -*-
'''

@author: patmoore
'''
import inspect
import re
import six
import sys
from conjugation_override import *
from constants import *
# UTF8Writer = codecs.getwriter('utf8')
# sys.stdout = UTF8Writer(sys.stdout)
from standard_endings import Standard_Conjugation_Endings

def make_unicode(inputStr):
    if type(inputStr) != unicode:
        inputStr = inputStr.decode('utf-8')
        return inputStr
    else:
        return inputStr
    
_vowel_check = re.compile(six.u('[aeiou]$'), re.UNICODE)
class Verb():
    '''
    classdocs
    '''
    
    def __init__(self, verb_string, definition, conjugation_overrides=None, prefix=None, base_verb=None):
        '''
        Constructor
        prefix - remove to find related word for conjugation.
        '''
        # when reading from a file or some other place - it may be a ascii string.
        # must be unicode for us reliably do things like [:-1] to peel off last character 
        verb_string = make_unicode(verb_string)
        self.inf_verb_string = verb_string
        if verb_string[-2:] == 'se':
            self.reflexive = True
            verb_string = verb_string[:-2]                    
            
        self.verb_string = verb_string
        self.inf_ending = verb_string[-2:]
        # special casing for eír verbs which have accented i
        if verb_string == u'ir': 
            # ir special case
            self.stem = verb_string
            self.verb_ending_index = Infinitive_Endings.ir_verb
        elif self.inf_ending == u'ír':
            self.inf_ending = u'ir'
            self.stem = verb_string[:-2]
            self.verb_ending_index = Infinitive_Endings.ir_verb
        else:
            self.stem = verb_string[:-2]
            self.verb_ending_index = Infinitive_Endings.index(self.inf_ending)
            
        self.prefix = prefix
        self.definition = definition
        # Some verbs don't follow the default rules for their ending> for example, mercer
        self.doNotApply = []
        self.appliedOverrides = []
        self.overridesMap = []
                        
        if conjugation_overrides is not None:
            if isinstance(conjugation_overrides, list):
                for conjugation_override in conjugation_overrides:
                    self.__process_conjugation_override(conjugation_override)  
            else:
                self.__process_conjugation_override(conjugation_overrides)
                 
        # look for default overrides - apply to end so that user could explicitly turn off the override
        for conjugation_override in Standard_Overrides.itervalues():
            if conjugation_override.auto_match != False and conjugation_override.is_match(self.inf_verb_string):
                self.__process_conjugation_override(conjugation_override)
                 
    def conjugate_irregular_tenses(self):
        pass
    
    def conjugate_all_tenses(self):
        # present to imperative
        return [ self.conjugate_tense(tense) for tense in range(len(Tenses)) ]
        
    def conjugate_tense(self, tense):
        return [ self.conjugate(tense=tense, person=person) for person in range(len(Persons)) ]    
            
    def conjugate(self, tense, person):
        conjugation_overrides = self.__get_override(tense, person, 'conjugations')
        if conjugation_overrides is None:
            current_conjugation_ending = self.conjugate_ending(tense, person)
            conjugation = self.conjugate_stem(tense, person, current_conjugation_ending) + current_conjugation_ending
        else:
            for conjugation_override in conjugation_overrides:
                if isinstance(conjugation_override, six.string_types):
                    conjugation = conjugation_override
                else:
                    try:
                        conjugation = conjugation_override(tense, person)
                    except Exception as e:
                        extype, ex, traceback = sys.exc_info()
#                         formatted = traceback.format_exception_only(extype, ex)[-1]
                        message = "%s: Trying to conjugate irregular=%d person=%d; %s" % self.inf_verb_string, tense, person, ex.message
                        raise RuntimeError, message, traceback

        return conjugation
    
    def conjugate_stem(self, tense, person, current_conjugation_ending):
        """
        :current_conjugation_ending - important because some rule only apply if the conjugation ending starts with an o or e
        """         
        if tense == Tenses.present_tense or tense == Tenses.incomplete_past_tense or tense == Tenses.past_tense:
            current_conjugation_stem = self.stem
        elif tense == Tenses.future_tense or tense == Tenses.conditional_tense:
            current_conjugation_stem = self.verb_string
        elif tense == Tenses.present_subjective_tense:
            current_conjugation_stem = self.__conjugation_present_subjective_stem(tense, person)
        elif tense == Tenses.past_subjective_tense:
            current_conjugation_stem = self.__conjugation_past_subjective_stem(tense, person)
        
        stem_overrides = self.__get_override(tense, person, 'conjugation_stems')
        if stem_overrides is not None:
            for stem_override in stem_overrides:
                if isinstance(stem_override, six.string_types):
                    current_conjugation_stem = stem_override
                else:
                    override_call = { 'tense': tense, 'person': person, 'stem': current_conjugation_stem, 'ending' : current_conjugation_ending }
                    try:
                        current_conjugation_stem = stem_override(**override_call)
                    except Exception as e:
                        extype, ex, traceback = sys.exc_info()
                        print ex.message
#                         formatted = traceback.format_exception_only(extype, ex)[-1]
#                         message = "%s: Trying to conjugate stem tense=%d person=%d" % self.inf_verb_string, tense, person, ex.message
#                         raise RuntimeError, message, traceback

        return current_conjugation_stem
        
    def conjugate_ending(self, tense, person):
        current_conjugation_ending = Standard_Conjugation_Endings[self.verb_ending_index][tense][person]
        ending_overrides = self.__get_override(tense, person, 'conjugation_endings')
        if ending_overrides is not None:
            for ending_override in ending_overrides:
                if isinstance(ending_override, six.string_types):
                    current_conjugation_ending = ending_override
                else:
                    override_call = { 'tense': tense, 'person': person, 'ending' : current_conjugation_ending }
                    try:
                        current_conjugation_ending = ending_override(**override_call)
                    except Exception as e:
                        extype, ex, traceback = sys.exc_info()
#                         formatted = traceback.format_exception_only(extype, ex)[-1]
                        message = "%s: Trying to conjugate ending=%d person=%d; %s" % self.inf_verb_string, tense, person, ex.message
                        raise RuntimeError, message, traceback
                    
        return current_conjugation_ending
    
    def __conjugation_present_subjective_stem(self, tense, person):
        first_person_conjugation = self.conjugate(Tenses.present_tense, Persons.first_person_singular)
        if first_person_conjugation[-1:] =='o':
            conjugation_stem = first_person_conjugation[:-1]            
        elif first_person_conjugation[-2:] == u'oy':
            # estoy, doy, voy, etc.
            conjugation_stem = first_person_conjugation[:-2]
        else:
            raise Exception("First person conjugation does not end in 'o' = "+first_person_conjugation)
        return conjugation_stem

    def __conjugation_past_subjective_stem(self, tense, person):
        third_person_plural_conjugation = self.conjugate(Tenses.past_tense, Persons.third_person_plural)
        if third_person_plural_conjugation[-3:] == u'ron':
            conjugation_stem = third_person_plural_conjugation[:-3]
            if person == Persons.first_person_plural:
                # accent on last vowel                                
                if _vowel_check.search(conjugation_stem):
                    conjugation_stem += u'\u0301'
                else:
                    # assuming last stem character is a vowel
                    # and assuming already accented for some reason
                    raise Exception("No ending vowel")
            return conjugation_stem
        else:
            raise "Third person conjugation does not end in 'ron' = "+third_person_plural_conjugation            
            
    def _overrides(self, tense, overrides, attr_name,persons=None):
        """
        Called by Conjugation_Override as an override is applied
        """        
        def __convert_to_self_function(override):            
            if inspect.isfunction(override) or inspect.ismethod(override):
                boundfunc = six.create_bound_method(override, self)
                return boundfunc                
            else:
                return override                        
           
        if persons is None:
            _persons = Persons
        elif isinstance(persons, six.integer_types):
            _persons = [ persons ]
        elif isinstance(persons, list):
            _persons = persons
        else:
            raise Exception("persons must be None, integer or list of integers")
            
        if not hasattr(self, attr_name):
            self_overrides = [ None ] * len(Tenses)
            setattr(self, attr_name, self_overrides) 
        else:
            self_overrides = getattr(self, attr_name)
            
        if self_overrides[tense] is None:
            self_overrides[tense] = [None] * len(Persons)
            
        if isinstance(overrides, six.string_types) or inspect.isfunction(overrides) or inspect.ismethod(overrides):            
            fn = __convert_to_self_function(overrides)
            for person in _persons:
                if isinstance(fn, six.string_types) or self_overrides[tense][person] is None:
                    # if a hard replacement (string), previous overrides are discarded because they will be replaced.
                    # or this is the first override
                    self_overrides[tense][person] = [fn]
                else:
                    self_overrides[tense][person].append(fn)                    
        
        elif isinstance(overrides, list):
            for person, override in enumerate(overrides):
                if override is not None:
                    fn = __convert_to_self_function(override)
                    if isinstance(fn, six.string_types) or self_overrides[tense][person] is None:
                        # if a hard replacement (string), previous overrides are discarded because they will be replaced.
                        # or this is the first override
                        self_overrides[tense][person] = [fn]
                    else:
                        self_overrides[tense][person].append(fn)                    
                    
    def overrides_applied(self):
        return {u'applied' : self.appliedOverrides,
            u'excluded': self.doNotApply
        }
        
    def __get_override(self, tense, person, attr_name):
        """
        TODO return just the function to allow the stem as it currently is in progress, 
        this will allow multiple stem changing to be handled
        return string corresponding override.
        """
        if hasattr(self, attr_name):
            self_overrides = getattr(self, attr_name)
            if self_overrides[tense] is not None:
                return self_overrides[tense][person]
        return None
    
    def __process_conjugation_override(self, conjugation_override):
        """
        Before applying the override first check to see if this verb says that it is a special case
        and the override should not be applied.
        """        
        if isinstance(conjugation_override, ConjugationOverride):
            override = conjugation_override            
        else:
            lookup_key = conjugation_override if conjugation_override[0] != '-' else conjugation_override[1:]
            override = Standard_Overrides[lookup_key]
            if override is None:
                raise Exception("no override with key ", lookup_key)
            if conjugation_override[0] == '-':
                self.doNotApply.append(override.key)
                return
            
        if override.key not in self.doNotApply and override.key not in self.appliedOverrides:
            override.apply(self)
            self.appliedOverrides.append(override.key)            
