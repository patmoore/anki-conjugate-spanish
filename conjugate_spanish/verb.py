# -*- coding: utf-8 -*-
'''

@author: patmoore
'''
from __future__ import print_function
import inspect
import re
import six
import sys
from conjugation_override import *
from conjugation_override import _replace_last_letter_of_stem
from constants import *


# UTF8Writer = codecs.getwriter('utf8')
# sys.stdout = UTF8Writer(sys.stdout)
from standard_endings import Standard_Conjugation_Endings

def make_unicode(inputStr):
    if inputStr is None:
        return None
    elif type(inputStr) != unicode:
        inputStr = inputStr.decode('utf-8')
        return inputStr
    else:
        return inputStr
    
_vowel_check = re.compile(six.u('[aeiou]$'), re.UNICODE)
_accented_vowels = re.compile(u'[áéíóú]')
def _check_for_multiple_accents(conjugation):
    if conjugation is not None:
        accented = _accented_vowels.findall(conjugation)
        if len(accented) > 1:
            raise Exception("Too many accents in "+conjugation)

            
def _remove_accent(string_):       
    result = string_ 
    for regex, replace in _replace_accents:
        result = regex.sub(replace, result)
    return result

_replace_accents = [
    [ re.compile(u'á'), u'a' ],
    [ re.compile(u'é'), u'e' ],
    [ re.compile(u'í'), u'i' ],
    [ re.compile(u'ó'), u'o' ],
    [ re.compile(u'ú'), u'u' ]
]    

class Verb():
    '''
    verb conjugation
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
        else:
            self.reflexive = False                   
            
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
        self.conjugation_overrides =conjugation_overrides
                        
        if conjugation_overrides is not None:
            if isinstance(conjugation_overrides, list):
                for conjugation_override in conjugation_overrides:
                    self.__process_conjugation_override(conjugation_override)  
            else:
                self.__process_conjugation_override(conjugation_overrides)
                 
        # look for default overrides - apply to end so that user could explicitly turn off the override
        for conjugation_override in Standard_Overrides.itervalues():
            if conjugation_override.auto_match != False and conjugation_override.is_match(self):
                self.__process_conjugation_override(conjugation_override)
                
    def print_all_tenses(self):
        c= self.conjugate_all_tenses()
        for tense in range(len(Tenses)):
            print( Tenses[tense])
            if tense in Tenses.Person_Agnostic:
                print(c[tense])
            else:
                for person in range(len(Persons)):
                    if c[tense][person] is not None:
                        print( Persons[person]+" "+c[tense][person], end="; ") 
            print()

    
    def conjugate_all_tenses(self):
        # present to imperative
        return [ self.conjugate_tense(tense) for tense in range(len(Tenses)) ]
        
    def conjugate_tense(self, tense):
        if tense in Tenses.Person_Agnostic:
            results = self.conjugate(tense=tense, person=None)
        else:
            results = [ self.conjugate(tense=tense, person=person) for person in range(len(Persons)) ]
        return results
            
    def conjugate(self, tense, person):
        conjugation_overrides = self.__get_override(tense, person, 'conjugations')
        if conjugation_overrides is not None:
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
        elif tense in [Tenses.imperative_positive, Tenses.imperative_negative]:
            conjugation = self.__conjugation_imperative(tense, person)
        else:
            current_conjugation_ending = self.conjugate_ending(tense, person)
            conjugation = self.conjugate_stem(tense, person, current_conjugation_ending) + current_conjugation_ending
        
        _check_for_multiple_accents(conjugation)
        return conjugation
    
    def conjugate_stem(self, tense, person, current_conjugation_ending):
        """
        :current_conjugation_ending - important because some rule only apply if the conjugation ending starts with an o or e
        """         
        if tense in [ Tenses.present_tense, Tenses.incomplete_past_tense, Tenses.past_tense]:
            current_conjugation_stem = self.stem
        elif tense in Tenses.Person_Agnostic:
            current_conjugation_stem = self.stem
        elif tense in [ Tenses.future_tense, Tenses.conditional_tense]:
            current_conjugation_stem = _remove_accent(self.verb_string)
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
                        print( ex.message)
#                         formatted = traceback.format_exception_only(extype, ex)[-1]
#                         message = "%s: Trying to conjugate stem tense=%d person=%d" % self.inf_verb_string, tense, person, ex.message
#                         raise RuntimeError, message, traceback
        if current_conjugation_stem is None:
            raise Exception(self.inf_verb_string+": no stem created tense="+tense+" person="+person)
        
        # if the ending has an accent then we remove the accent on the stem
        if _accented_vowels.search(current_conjugation_stem) and _accented_vowels.search(current_conjugation_ending):
            current_conjugation_stem = _remove_accent(current_conjugation_stem)
            
        return current_conjugation_stem
        
    def conjugate_ending(self, tense, person):
        if tense in Tenses.Person_Agnostic:
            current_conjugation_ending = Standard_Conjugation_Endings[self.verb_ending_index][tense]
        else:
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
    
    def __explicit_accent(self, conjugation_string):
        """
        look for vowel to accent.
        """
        _strong_vowel = [u'a', u'e', u'o']
        _weak_vowel = [u'i', u'u']
        if _accented_vowels.search(conjugation_string):
            return conjugation_string
        else:            
            if conjugation_string[-1] in [u'n', u's'] or conjugation_string[-1] in _strong_vowel or conjugation_string[-1] in _weak_vowel:
                # skip the first vowel for words ending in s or n or a vowel
                vowel_skip = 1
            else:
                vowel_skip = 0
            
            result = None
            while result is None:
                #May need to go through twice if there is only 1 vowel in the word and it would be normally skipped
                for index in range(len(conjugation_string)-1,0,-1):                    
                    if conjugation_string[index] in _strong_vowel:
                        #strong vowel                        
                        if vowel_skip > 0:
                            vowel_skip -=1
                            continue
                        else:
                            result = conjugation_string[:index+1] + u'\u0301' + conjugation_string[index+1:]
                    elif conjugation_string[index] in _weak_vowel:
                        #weak vowel                                   
                        if vowel_skip > 0:
                            vowel_skip -=1
                            continue
                        elif index-1 >= 0 and conjugation_string[index-1] in _strong_vowel:
                            # accent should be on strong vowel immediately before the weak vowel                            
                            continue
                        else:
                            # for two weak vowels the accent is on the second one (i.e. this one) 
                            # or if there is any other letter or this is the beginning of the word
                            result = conjugation_string[:index+1] + u'\u0301' + conjugation_string[index+1:]
                            
            return result
    
    def __conjugation_imperative(self, tense, person):
        """
        TODO: placement of lo. examples:
            no me lo dé - don't give it to me
            Démelo - give it to me
            
        TODO: (reflexive) apply accent to vowel that was originally accented
        when appending reflexive pronoun 
        """        
        if person == Persons.first_person_singular:
            # no such conjugation
            return None
        elif person == Persons.first_person_plural:
            conjugation = self.conjugate(Tenses.present_subjective_tense, person)
            if self.reflexive:
                conjugation = _replace_last_letter_of_stem(self.__explicit_accent(conjugation), u's', Persons_Indirect[Persons.first_person_plural])
                
        elif person == Persons.second_person_singular and tense == Tenses.imperative_positive:
            conjugation = self.conjugate(Tenses.present_tense, Persons.third_person_singular)
            if self.reflexive:
                conjugation = self.__explicit_accent(conjugation) + Persons_Indirect[person]
        elif person == Persons.second_person_plural and tense == Tenses.imperative_positive:
            if not self.reflexive:
                # xxxv rule j: drop 'r' in infinitive and replace with 'd' in non-reflexive cases 
                conjugation = _replace_last_letter_of_stem(self.inf_verb_string, u'r', u'd')
            elif self.verb_ending_index == Infinitive_Endings.ir_verb:
                # ir verbs need the i accented rule k and l
                # example ¡Vestíos! - Get Dressed!
                # what about verbs that already have explicit accent?
                conjugation = _remove_accent(self.stem) + u'í' + Persons_Indirect[Persons.second_person_plural]
            else:
                # ex: ¡Sentaos! - Sit down!
                conjugation = _replace_last_letter_of_stem(self.__explicit_accent(self.inf_verb_string), u'r', Persons_Indirect[Persons.second_person_plural])                
        elif person in [Persons.second_person_singular, Persons.second_person_plural] and tense == Tenses.imperative_negative:
            conjugation = u"no "
            if self.reflexive:
                conjugation += Persons_Indirect[person] + " "
            conjugation += self.conjugate(Tenses.present_subjective_tense, person)                   
        elif person in [Persons.third_person_singular, Persons.third_person_plural]:
            conjugation = self.conjugate(Tenses.present_subjective_tense, person)
        else:
            raise Exception("Person value is out of range person="+str(person))                                                
        return conjugation
            
    def __conjugation_present_subjective_stem(self, tense, person):
        first_person_conjugation = self.conjugate(Tenses.present_tense, Persons.first_person_singular)
        if first_person_conjugation[-1:] ==u'o':
            conjugation_stem = first_person_conjugation[:-1]            
        elif first_person_conjugation[-2:] == u'oy':
            # estoy, doy, voy, etc.
            conjugation_stem = first_person_conjugation[:-2]
        else:
            # haber (he) is just such an example - but there better be an override available.
            return None
#             raise Exception("First person conjugation does not end in 'o' = "+first_person_conjugation)
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
            
        if tense in Tenses.Person_Agnostic:
            if isinstance(overrides, six.string_types) or inspect.isfunction(overrides) or inspect.ismethod(overrides):
                self_overrides[tense] = overrides
            elif len(overrides) == 1:
                self_overrides[tense] = overrides[0]
            elif len(overrides) ==0:
                pass
            else:
                raise Exception(self.inf_verb_string+":Tense is person agnostic so only 1 override is allowed")
            return
        
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
                if tense in Tenses.Person_Agnostic:
                    return self_overrides[tense]
                else:
                    return self_overrides[tense][person]
        return None
    
    def __process_conjugation_override(self, conjugation_override):
        """
        Before applying the override first check to see if this verb says that it is a special case
        and the override should not be applied.
        """        
        if isinstance(conjugation_override, ConjugationOverride):
            override = conjugation_override            
        elif len(conjugation_override) > 1:
            lookup_key = conjugation_override if conjugation_override[0] != '-' else conjugation_override[1:]
            override = Standard_Overrides[lookup_key]
            if override is None:
                raise Exception("no override with key ", lookup_key)
            if conjugation_override[0] == '-':
                self.doNotApply.append(override.key)
                return
        else:
            #No override or blank
            return
        if override.key not in self.doNotApply and override.key not in self.appliedOverrides:
            override.apply(self)
            self.appliedOverrides.append(override.key)            
