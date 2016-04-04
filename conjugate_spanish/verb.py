# -*- coding: utf-8 -*-
'''

@author: patmoore
'''
from __future__ import print_function
import inspect
import sys
from conjugation_override import *
from constants import *
import traceback

# UTF8Writer = codecs.getwriter('utf8')
# sys.stdout = UTF8Writer(sys.stdout)
from standard_endings import Standard_Conjugation_Endings

_ending_vowel_check = re_compile(u'['+Vowels.all+u']$')
# check for word with only a single vowel ( used in imperative conjugation )
_single_vowel_re = re.compile(u'^([^'+Vowels.all+u']*)(['+Vowels.all+u'])([^'+Vowels.all+u']*)$', re.IGNORECASE+re.UNICODE)
#
# Parse up the infinitive string: 
# group 1 = prefix words (if present)
# group 2 = prefix characters (if present)
# group 3 = core verb (note: special case of 'ir' and 'irse'
# group 4 = infinitive ending ( -ir,-er,-ar )
# group 5 = reflexive se or -se if present
# group 6 = suffix words
# use '-' to separate out the prefix from the base verb
# use '/' to force the selection of the verb in complex cases or for cases where prefix words end in -ir,-ar,-er
_phrase_parsing = re.compile(u'^\s*([^/]*?)[\s/]*([^/\s-]*?)-?([^/\s-]*)([iíae]r)(-?se)?[/\s]*(.*?)\s*$', re.UNICODE)
PREFIX_WORDS = 1
PREFIX_CHARS = 2
CORE_VERB = 3
INF_ENDING = 4
REFLEXIVE_ENDING = 5
SUFFIX_WORDS = 6

class Verb():
    '''
    verb conjugation
    instance properties:
    full_phrase - <prefix words> infinitive <suffix words>
    inf_verb_string - infinitive 
    # Now a bit of trickiness. Verbs that are based on the conjugation of another verb need to handle override conjugations or conjugation_stems
            # We don't have it as a 'visible' override because that would make it harder to highlight how a verb is irregular.
            # (has to handle acordarse -> acordar and descacordarse -> acordarse )
            # Note: that the prefix can be u'' - usually for reflexive verbs. 
    '''
    # constant used to tell human that the verb is explicitly known to be a regular verb 
    REGULAR_VERB = u'regular'
    def __init__(self, phrase_verb_string, definition=u'', conjugation_overrides=None, base_verb=None, manual_overrides=None, **kwargs):
        '''
        Constructor
        :param phrase_verb_string:
        :param base_verb: used as base verb for conjugation
        '''
        self.definition = make_unicode(definition)
        # Some verbs don't follow the default rules for their ending> for example, mercer
        self._doNotApply = []
        self._appliedOverrides = []
 
        # need to preserve with the / and - so that we can go from Note objects back to Verb objects
        self.key = _phrase_verb_string = make_unicode(phrase_verb_string)
                            
        # determine if this verb has suffix words. for example: "aconsejar/con" which means to consult with"        
        phrase_match = _phrase_parsing.match(_phrase_verb_string)
        if phrase_match is None:
            self.__raise(_phrase_verb_string+": does not appear to be a verb or phrase with verb infinitive in it.")            

        self.prefix_words = phrase_match.group(PREFIX_WORDS)
        self.prefix = phrase_match.group(PREFIX_CHARS)
        self.core_characters = phrase_match.group(CORE_VERB)
        self.inf_ending = phrase_match.group(INF_ENDING)
        self.reflexive = phrase_match.group(REFLEXIVE_ENDING) is not None and phrase_match.group(REFLEXIVE_ENDING) != u''        
        self.suffix_words = phrase_match.group(SUFFIX_WORDS)
        self.manualOverrides = None # TODO: be able to save manual overrides as a string for display/editting

        _base_verb = make_unicode(base_verb)
        if _base_verb == u'':
            _base_verb = None
        if _base_verb is not None:        
            if isinstance(_base_verb, Verb):
                self.base_verb = _base_verb
                self.base_verb_str = _base_verb.inf_verb_string
            elif isinstance(_base_verb, six.string_types) and _base_verb != u'':
                # TODO strip leading/trailing white space
                self.base_verb_str = _base_verb 
            else:
                self.__raise("base_verb must be Verb or string")
            # example abatir has base: batir
            _base_verb_parse = _phrase_parsing.match(self.base_verb_str)
            # "abat".find("bat")
            base_verb_index = self.core_characters.find(_base_verb_parse.group(CORE_VERB))
            if base_verb_index <0:
                self.__raise(repr(self.base_verb_str)+ " is not in core characters"+repr(self.core_characters))
            if self.prefix == u'' or self.prefix is None:
                self.prefix = self.core_characters[:base_verb_index]
                self.core_characters = self.core_characters[base_verb_index:]
            elif base_verb_index != 0 and self.prefix != self.core_characters[:base_verb_index]:
                self.__raise("prefix already="+self.prefix+" but should be "+self.core_characters[:base_verb_index])
            elif self.core_characters != _base_verb_parse.group(CORE_VERB):
                self.__raise("core_characters already="+self.core_characters+" but should be "+_base_verb_parse.group(CORE_VERB))
        elif self.is_phrase:
            # a phrase means the base verb is the actual verb being conjugated.
            self.base_verb_str = self.inf_verb_string
        elif self.prefix != u'' or phrase_match.group(REFLEXIVE_ENDING) == '-se':
            # explicit base verb formed by '-' embedded in the verb
            self.base_verb_str = self.core_characters + self.inf_ending
            if phrase_match.group(REFLEXIVE_ENDING) == 'se':
                self.base_verb_str += 'se'
        elif self.reflexive:
            # base verb is without the 'se' ( no prefix)
            self.base_verb_str = self.core_characters + self.inf_ending
        else:
            self.base_verb_str = None
                        
        self.manual_overrides_string = manual_overrides
        if isinstance(conjugation_overrides, six.string_types) and conjugation_overrides != u'' and conjugation_overrides != Verb.REGULAR_VERB:
            self.explicit_overrides_string = self.overrides_string = conjugation_overrides
            conjugation_overrides = conjugation_overrides.split(",")                
        else:
            self.explicit_overrides_string = self.overrides_string = u''
            
        if self.manual_overrides_string is not None and self.manual_overrides_string != u'': 
            self.manual_overrides_string = manual_overrides
            manual_conjugation_override = ConjugationOverride.create_from_json(self.manual_overrides_string, key=phrase_verb_string+"_irregular")
        
            if conjugation_overrides is None:
                conjugation_overrides = [manual_conjugation_override]
            else:
                conjugation_overrides.append(manual_conjugation_override) 
                 
        if conjugation_overrides is not None:            
            for conjugation_override in get_iterable(conjugation_overrides):
                self.process_conjugation_override(conjugation_override) 
                
        # look for default overrides - apply to end so that user could explicitly turn off the override
        for conjugation_override in Standard_Overrides.itervalues():
            if conjugation_override.auto_match != False and conjugation_override.is_match(self):                
                applied = self.process_conjugation_override(conjugation_override)
                if applied:
                    if self.overrides_string == u'':
                        self.overrides_string = conjugation_override.key
                    else:
                        self.overrides_string += u','+conjugation_override.key
                
        for conjugation_override in Dependent_Standard_Overrides.itervalues():
            if conjugation_override.auto_match != False and conjugation_override.is_match(self):
                self.process_conjugation_override(conjugation_override)
            
        ## HACK -- should be supplied when generating a card    
        if self.overrides_string == u'':
            self.overrides_string = Verb.REGULAR_VERB
            
        self.process_conjugation_override(UniversalAccentFix)
                
                
    def print_all_tenses(self):
        conjugations= self.conjugate_all_tenses()
        self._print_conjugations(conjugations)
    
    def print_irregular_tenses(self):
        conjugations = self.conjugate_irregular_tenses()
        self._print_conjugations(conjugations)
        
    def _print_conjugations(self, conjugations):
        if conjugations is not None:        
            for tense in range(len(Tenses)):
                if conjugations[tense] is None:
                    continue
                
                print("  "+ Tenses[tense], end=": ")
                if tense in Tenses.Person_Agnostic:
                    print(conjugations[tense])
                else:
                    for person in range(len(Persons)):
                        if conjugations[tense][person] is not None:
                            if not self.reflexive:
                                print( Persons[person]+" "+conjugations[tense][person], end="; ")
                            elif tense not in [ Tenses.imperative_negative, Tenses.imperative_positive ]:
                                print( conjugations[tense][person], end="; ")
                            else:
                                print(conjugations[tense][person])
                                 
                    print()

    def print_csv(self, full_info=True):
        result = u'"'+self.full_phrase+u'"'
        if full_info:
            if len(self.appliedOverrides) > 0:
                result+=u',"'+repr(self.appliedOverrides)+u'"'
            if len(self.doNotApply) > 0:
                result +=u',"'+repr(self.doNotApply)+u'"'
            if self.base_verb_str is not None:
                result += u',"'+self.base_verb_str+u'"'
        
        for tense in Tenses.all:
            if tense in Tenses.Person_Agnostic:
                conjugation = self.conjugate(tense)
                result += u',"'+conjugation+u'"'
            else:
                for person in Persons.all:
                    conjugation = self.conjugate(tense, person)
                    if conjugation is None:
                        result += u','
                    else:
                        result += u',"'+conjugation+u'"'
        return result
    
    def conjugate_irregular_tenses(self):        
        """
        Look for just the tenses and persons that are different than than completely regular conjugation rules
        """
        conjugations = [ None ] * len(Tenses)
        def __look_for_overrides(verb):            
            overrides = [ override_attribute for override_attribute in ['conjugations', 'conjugation_stems', 'conjugation_endings'] if hasattr(verb, override_attribute)]
            if len(overrides) == 0:
                return None
            
            for attr_name in overrides:
                for tense in range(len(Tenses)):
                    override = getattr(verb, attr_name)
                    if override[tense] is None:
                        continue
                    
                    if tense in Tenses.Person_Agnostic:
                        if conjugations[tense] is None:
                            conjugations[tense] = self.conjugate_tense(tense)
                    else:
                        for person in range(len(Persons)):
                            if override[tense][person] is not None:
                                if conjugations[tense] is None:
                                    conjugations[tense] = [ None ] * len(Persons)
                                if conjugations[tense][person] is None:
                                    conjugations[tense][person] = self.conjugate(tense, person)
        __look_for_overrides(self)
        if self.base_verb is not None:
            __look_for_overrides(self.base_verb)
        return conjugations
    
    def conjugate_all_tenses(self):
        # present to imperative
        return [ self.conjugate_tense(tense) for tense in Tenses.all ]
        
    def conjugate_tense(self, tense):
        """
        conjugate all persons for given tense
        """
        if tense in Tenses.Person_Agnostic:
            results = self.conjugate(tense=tense, person=None)
        else:
            results = [ self.conjugate(tense=tense, person=person) for person in Persons.all ]
        return results
            
    def conjugate(self, tense, person=None, options={}):
        """
        :param person: usually must be set but can be None if tense in Tenses.Person_Agnostic
        :return: The conjugated verb. Note: the verb must be <indirect pronoun> <verb> or just <verb>
        """                
        if tense in Tenses.imperative and person == Persons.first_person_singular:
            return None        
        if tense not in Tenses.Person_Agnostic and person not in Persons.all:
            self.__raise("Tense "+Tenses[tense]+" needs a person", tense, person)
        if self.base_verb is not None:            
            conjugation = self.__derived_conjugation(tense, person, options)
        else:            
            conjugation_overrides = self.__get_override(tense, person, 'conjugations')
            
            if conjugation_overrides is not None:
                for conjugation_override in conjugation_overrides:
                    if isinstance(conjugation_override, six.string_types):
                        conjugation = conjugation_override
                    elif conjugation_override is not None:
                        override_call = { 'tense': tense, 'person': person, "options":options }
                        try:
                            conjugation = conjugation_override(**override_call)
                        except Exception as e:
                            extype, ex, traceback_ = sys.exc_info()
                            formatted = traceback.format_exception_only(traceback_,extype, ex)[-1]
                            message = "Trying to conjugate irregular:%s %s" % ex.message, formatted
                            self.__raise(message, tense, person, traceback_)
                _reflexive = pick(options,'reflexive_override',self.reflexive)
                if _reflexive:
                    # needed in imperative to correctly add in the reflexive pronoun 
                    conjugation = self.__conjugation_imperative_reflexive(tense, person, conjugation)
            else:
                conjugation = self._conjugate_stem_and_endings(tense, person, options)
            
        self._check_for_multiple_accents(tense, person, conjugation)
        return conjugation
    
    def _conjugate_stem_and_endings(self,tense, person,options):
        """
        exists so that third person verbs can decide to conjugate normally for present subjective and past subjective
        """
        if tense not in Tenses.imperative:
            current_conjugation_ending = self.conjugate_ending(tense, person)            
            current_conjugation_stem = self.conjugate_stem(tense, person, current_conjugation_ending)
            conjugation = self.conjugation_joining(tense, person, current_conjugation_stem, current_conjugation_ending)
        else:
            conjugation = self.__conjugation_imperative(tense, person)
        return conjugation
        
    def __derived_conjugation(self, tense, person, options):
        """ This verb is based on another verb: example: abstenerse is based on tener
        these base verbs are not allowed to be reflexive verbs (I haven't found any examples yet where this is an issue)
        
        This is not "perfect" implementation because:
        1. in multiple level of ancestory: intermediate ancestor verbs are not allowed to apply their own overrides.
        2. child verbs cannot apply any conjugation overrides of their own ( maybe an issue with decir )
        
        However, the resulting code is similar. ( the issue is the accenting on the rare tener :2nd person singular imperative )
        
        I would like to eliminate this code and go to a pure conjugation override model 
        """
        # we never want the base verb to apply the reflexive pronoun - irregardless of reflexive_override
        _options = dict(options)
        _options['reflexive_override'] = False
        base_verb_conjugation = self.root_verb.conjugate(tense, person, _options)
        if base_verb_conjugation is None:
            # imperative, third-person only verbs
            return None
        
        # done because of multiple layers of derivation.
        _reflexive = pick(options,'reflexive_override', self.reflexive)
        explicit_accent_already_applied = False
        single_vowel_match = _single_vowel_re.match(base_verb_conjugation)        
        
        if tense == Tenses.imperative_positive and person == Persons.second_person_singular:
            #
            # Accent a single vowel base verb conjugation
            # 
            # TODO this may occur in other special cases but if so I have not found them.
            # parent ( self ) needs to be conjugated to determine special accent case.
            # example tener(self) and obtener ( child_verb) 
            # second person singular for tener is (ten), and obtener (obtén) - so accent is on the vowel that 
            # would be accented in the base verb case.
            # abstenerse does not need this special case because the reflexive pronoun will be added to the end ( so 'ten' syllable will be the second to last)
            # but not no always decir  ( di ) but maldecir ( maldice )
            # TODO accenting ( obtén - for example )
            # reflexive verbs are going to get 'te' at the end, so no need for an accent.
            if single_vowel_match is not None:
                explicit_accent_already_applied = True
                if not _reflexive:
                    _conjugation = self.full_prefix + accent_at(base_verb_conjugation, single_vowel_match.start(2))
                else:
                    _conjugation = self.full_prefix + base_verb_conjugation                
            else:
                _conjugation = self.full_prefix + base_verb_conjugation
#         elif single_vowel_match is not None:
            # leave comment in so that i know this has been checked.
            # traer and atraer -- this is fine : no accenting
#             self.__raise("Single vowel case in tense", tense, person)
        else:
            _conjugation = self.full_prefix + base_verb_conjugation
            
        if tense in Tenses.imperative:
            returned_conjugation = self.__apply_imperative_reflexive_pronoun(tense, person, _conjugation, explicit_accent_already_applied)                        
        elif _reflexive and tense not in Tenses.Person_Agnostic:
            returned_conjugation = Persons_Indirect[person] +" "+ _conjugation
        elif _reflexive and tense == Tenses.gerund:
            returned_conjugation = self.__explicit_accent(_conjugation)+u'se'
        else:
            returned_conjugation = _conjugation
        return returned_conjugation
        
        
    def conjugate_stem(self, tense, person, current_conjugation_ending):
        def __check_override(override, current_conjugation_stem):
            if isinstance(override, six.string_types):
                current_conjugation_stem = override
            elif override is not None:
                override_call = { 'tense': tense, 'person': person, 'stem': current_conjugation_stem, 'ending' : current_conjugation_ending }
                try:
                    current_conjugation_stem = override(**override_call)
                except Exception as e:
                    extype, ex, tb = sys.exc_info()
                    traceback.print_tb(tb)
                    formatted = traceback.format_exception(extype, ex, tb)[-1]
                    message = "Trying to conjugate " + formatted
                    self.__raise(message, tense, person, tb)
            return current_conjugation_stem
        if tense in [ Tenses.present_tense, Tenses.incomplete_past_tense, Tenses.past_tense, Tenses.gerund, Tenses.past_participle]:
            current_conjugation_stem = self.stem
        elif tense == Tenses.adjective:
            current_conjugation_stem = self.conjugate_stem(Tenses.past_participle, person, current_conjugation_ending)
        elif tense in [ Tenses.future_tense, Tenses.conditional_tense]:
            current_conjugation_stem = remove_accent(self.inf_verb_string)
        elif tense == Tenses.present_subjective_tense:
            current_conjugation_stem = self.__conjugation_present_subjective_stem(tense, person)
        elif tense == Tenses.past_subjective_tense:
            current_conjugation_stem = self.__conjugation_past_subjective_stem(tense, person)
        else:
            self.__raise(": Can't be handled", tense, person)
            
        overrides = self.__get_override(tense, person, 'conjugation_stems')
        if overrides is not None:
            for override in get_iterable(overrides):
                current_conjugation_stem = __check_override(override, current_conjugation_stem)
        
        if current_conjugation_stem is None:
            self.__raise("no stem created", tense, person)
        
        return current_conjugation_stem
        
    def conjugate_ending(self, tense, person):
        def __check_override(override, current_conjugation_ending):
            if isinstance(override, six.string_types):
                current_conjugation_ending = override
            elif override:
                override_call = { 'tense': tense, 'person': person, 'stem': self.stem, 'ending' : current_conjugation_ending }
                try:
                    current_conjugation_ending = override(**override_call)
                except Exception as e:
                    extype, ex, traceback_ = sys.exc_info()
#                         formatted = traceback_.format_exception_only(extype, ex)[-1]
                    message = "Trying to conjugate ending; %s" % ex.message
                    self.__raise(message, tense, person, traceback_)
            return current_conjugation_ending
        
        if tense in Tenses.Person_Agnostic:
            current_conjugation_ending = Standard_Conjugation_Endings[self.verb_ending_index][tense]
        else:
            current_conjugation_ending = Standard_Conjugation_Endings[self.verb_ending_index][tense][person]
            
        overrides = self.__get_override(tense, person, 'conjugation_endings')
        if overrides is not None:
            for override in get_iterable(overrides):
                current_conjugation_ending = __check_override(override, current_conjugation_ending)
        return current_conjugation_ending
    
    def conjugation_joining(self, tense, person, current_conjugation_stem, current_conjugation_ending):
        def __check_override(override, current_conjugation_stem, current_conjugation_ending):
            if override is not None:
                override_call = { 'tense': tense, 'person': person, 'stem': current_conjugation_stem, 'ending' : current_conjugation_ending }
                try:
                    results = override(**override_call)
                except Exception as e:
                    extype, ex, tb = sys.exc_info()
                    traceback.print_tb(tb)
                    formatted = traceback.format_exception(extype, ex, tb)[-1]
                    message = "Trying to conjugate " + formatted
                    self.__raise(message, tense, person, tb)
            else:
                results = [current_conjugation_stem, current_conjugation_ending]
            return results
        overrides = self.__get_override(tense, person, 'conjugation_joins')
        if overrides is not None:
            for override in get_iterable(overrides):
                [current_conjugation_stem, current_conjugation_ending]  = __check_override(override, current_conjugation_stem, current_conjugation_ending)
                if not isinstance(current_conjugation_stem, six.string_types):
                    self.__raise("stem is not string", tense, person)
                if not isinstance(current_conjugation_ending, six.string_types):
                    self.__raise("ending is not string", tense, person) 
 
        return current_conjugation_stem+current_conjugation_ending
    
    def __explicit_accent(self, conjugation_string):
        """
        Accent a vowel explicitly UNLESS there is an accent already
        The rules on accenting in spanish is the last vowel if the word ends in a consonent other than n or s
        Otherwise the second to last vowel.
        If the vowel to be accented is a strong-weak (au,ai,ei,... ) or a weak-strong pair (ua,ia, ... ) the strong vowel of the pair gets the accent
        TODO: NOTE: an h between 2 vowels does not break the diphthong
        https://en.wikipedia.org/wiki/Spanish_irregular_verbs
        Remember that the presence of a silent h does not break a diphthong, so a written accent is needed anyway in rehúso.
        """
        _strong_vowel = [u'a', u'e', u'o']
        _weak_vowel = [u'i', u'u']
        if accented_vowel_check.search(conjugation_string):
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
                        else:
                            result = accent_at(conjugation_string,index)
                            break
                    elif conjugation_string[index] in _weak_vowel:
                        #weak vowel                                                           
                        if vowel_skip > 0:
                            vowel_skip -=1
                        elif index >= 1 and conjugation_string[index-1] in _strong_vowel:
                            # accent should be on strong vowel immediately before the weak vowel (so skip the current weak vowel)                           
                            continue
                        elif index >= 1 and conjugation_string[index-1:index+1] in [u'qu',u'gu' ]:
                            # qu is a dipthong ( see accent rules on acercarse : 1st person plural and 3rd person plural imperative  ) 
                            continue
                        else:
                            # for two weak vowels the accent is on the second one (i.e. this one) 
                            # or if there is any other letter or this is the beginning of the word
                            result = accent_at(conjugation_string,index)
                            break
                            
            return result
    
    def __conjugation_imperative(self, tense, person, conjugation=None):
        """
        :conjugation: - the overridden conjugation
        
        non-reflexive:
        positive
        2nd person -- third person present tense
        2nd person plural - infinitive drop last r replace with d
        all others present subjective
        
        negative
        present subjective
        
        reflexive:
        
        Imperative is a bit tricky.
        1. If there is a conjugation
        TODO: placement of lo. examples:
            no me lo dé - don't give it to me
            Démelo - give it to me
            
        2. TODO: (reflexive) apply accent to vowel that was originally accented
        when appending reflexive pronoun 
        3. TODO: handle verbs that have base verbs
        4. imperatives rarely? ever override a stem for entire imperative
        5. positive v negative conjugation
        """
        """
        Handle the very odd cases first
        """        
        if person == Persons.first_person_singular:
            # no such conjugation
            return None
        
        # Step #1 - for verbs with no override conjugation - get the conjugation        
        if conjugation is None:
            # For most persons the conjugation is the present_subjective ( because imperative is a "mood" - enhancement to the present_subjective )
            if tense == Tenses.imperative_negative or person not in Persons.second_person:
                # all negative imperatives use the present_subjective AND all positives EXCEPT second person
                _conjugation = self.conjugate(Tenses.present_subjective_tense, person)
#                 if person == Persons.first_person_plural and verb.reflexive:
#                     # properly prepare the verb by removing the trailing 's'
#                     # TODO: notice we don't handle a case of irregular nosotros - that does not have a trailing 's'
#                     # this seems to not be a problem for anything - but we will raise an exception if it is
#                     # this seems to only be a problem for irse
#                     _conjugation = _replace_last_letter_of_stem(_conjugation, u's', u'')
            elif person == Persons.second_person_singular and tense == Tenses.imperative_positive:
                # positive tu form uses present tense usted                
                _conjugation = self.conjugate(Tenses.present_tense, Persons.third_person_singular)
            elif person == Persons.second_person_plural and tense == Tenses.imperative_positive:                
                # remove 'r' from infinitive - and replace it with 'd'
                _conjugation = _replace_last_letter_of_stem(self.inf_verb_string, u'r', u'd')
            else:
                self.__raise("Missed case"+tense+" "+person)  
        else:
            _conjugation = conjugation                      
        
        returned_conjugation = self.__apply_imperative_reflexive_pronoun(tense, person, _conjugation)
        return returned_conjugation
    
    def __apply_imperative_reflexive_pronoun(self, tense, person, conjugation, explicit_accent_already_applied=False):
        # Step 3 - handle the placement of the indirect pronoun for reflexive verbs.  
        # The important issue here is the effect on the accent.      
        def handle_explicit_accent_():
            if explicit_accent_already_applied:
                return conjugation
            else:
                return self.__explicit_accent(conjugation)
        if self.reflexive:
            #Now apply the reflexive pronoun rules.
            if person in Persons.third_person:
                # simple!
                returned_conjugation = handle_explicit_accent_() + Persons_Indirect[person]
            elif person == Persons.first_person_plural:
                # mostly simple (same as third person except trailing 's' is dropped before adding the indirect pronoun
                returned_conjugation = _replace_last_letter_of_stem(handle_explicit_accent_(), u's', Persons_Indirect[person])
            elif tense == Tenses.imperative_negative:
                # second person negative : simple as well!
                # reflexive pronoun is a separate word in front of the verb. (i.e. 'no te abstengas')
                # notice that the second person cases negative do not have any accent issues.
                returned_conjugation = Persons_Indirect[person]+ " " + conjugation
            elif person == Persons.second_person_singular: # (imperative positive) 
                # Need to put explicit accent in SOME cases for example: quitarse ( quítate ) but not in all: abstener ( abstente )
                # ( could it be that 'ten' is a single vowel word and retains the accent on the ten - even with the prefix? )
                # ensure that there is an accent somewhere (note that in abstenerse case the accent should already be on the abs-tén 
                returned_conjugation = handle_explicit_accent_() + Persons_Indirect[person]
            elif person == Persons.second_person_plural:  # (imperative positive) 
                # TODO look for single vowel in conjugation for model verb.
                # TODO : Would like to make this a conjugation override - but conjugation overrides are not applied on derived verbs
                if self.verb_ending_index == Infinitive_Endings.ir_verb:
                    if conjugation[-2:] == u'id':
                        # ir verbs need the i (in ir) accented rule k and l
                        # this makes sense because otherwise the os would be accented.
                        # example ¡Vestíos! - Get Dressed!
                        # we don't need to worry about accenting the -ir verbs that already have the i accented ( example reírse )
                        # what about verbs that already have explicit accent?
                        returned_conjugation = remove_accent(conjugation[:-2]) + u'í' + Persons_Indirect[Persons.second_person_plural]
                    elif conjugation[-2:] == u'íd':
                        returned_conjugation = _replace_last_letter_of_stem(conjugation, u'd', Persons_Indirect[Persons.second_person_plural])
                    else:
                        self.__raise(u"don't know how to handle:"+conjugation, tense, person)
                else:
                    # ex: ¡Sentaos! - Sit down! ( the spoken accent will be on the ending a )
                    returned_conjugation = _replace_last_letter_of_stem(remove_accent(conjugation), u'd', Persons_Indirect[Persons.second_person_plural])
        else:
            returned_conjugation = conjugation
        return returned_conjugation
             
    def __conjugation_present_subjective_stem(self, tense, person):
        options = { 'force_conjugation': True }
        first_person_conjugation = self.conjugate(Tenses.present_tense, Persons.first_person_singular, options)
        if first_person_conjugation[-1:] ==u'o':
            conjugation_stem = first_person_conjugation[:-1]            
        elif first_person_conjugation[-2:] == u'oy':
            # estoy, doy, voy, etc.
            conjugation_stem = first_person_conjugation[:-2]
        else:
            # haber (he) is just such an example - but there better be an override available.
            return None
#             self.__raise("First person conjugation does not end in 'o' = "+first_person_conjugation)
        return conjugation_stem

    def __conjugation_past_subjective_stem(self, tense, person):
        """
        in First person plural, accent if third person plural ends in a vowel after dropping -ron        
        """
        options = { 'force_conjugation': True }
        third_person_plural_conjugation = self.conjugate(Tenses.past_tense, Persons.third_person_plural, options)
        if third_person_plural_conjugation[-3:] == u'ron':
            conjugation_stem = third_person_plural_conjugation[:-3]
            if person == Persons.first_person_plural:
                # accent on last vowel                                
                if _ending_vowel_check.search(conjugation_stem):
                    conjugation_stem = accent_at(conjugation_stem)
                else:
                    # assuming last stem character is a vowel
                    # and assuming already accented for some reason
                    self.__raise("No ending vowel", tense, person)
            return conjugation_stem
        else:
            self.__raise("Third person conjugation does not end in 'ron' = "+third_person_plural_conjugation, tense, person)
            
    def _overrides(self, tense, overrides, attr_name,persons=None):
        """
        Called by Conjugation_Override as an override is applied
        """        
        def __convert_to_self_function(override):            
            if inspect.isfunction(override) or inspect.ismethod(override):
                boundfunc = six.create_bound_method(override, self)
                return boundfunc                
            elif isinstance(override, six.string_types):
                return override                        
            else:
                self.__raise(u"Override must be function or string not"+type(override),tense)           
            
        if not hasattr(self, attr_name):
            self_overrides = [ None ] * len(Tenses)
            setattr(self, attr_name, self_overrides) 
        else:
            self_overrides = getattr(self, attr_name)
            
        if tense in Tenses.Person_Agnostic:
            override_ = __convert_to_self_function(overrides)
            if isinstance(override_, six.string_types) or self_overrides[tense] is None:
                self_overrides[tense] = [ override_ ]
            else:
                self_overrides[tense].append(override_)
            return
        
        if persons is None:
            _persons = Persons
        elif isinstance(persons, six.integer_types):
            _persons = [ persons ]
        elif isinstance(persons, list):
            _persons = persons
        else:
            self.__raise("persons must be None, integer or list of integers", tense)
            
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
        result = {}
        if self.appliedOverrides is not None and self.appliedOverrides != []:
            result[u'applied']= self.appliedOverrides
        if self.doNotApply is not None and self.doNotApply != []:
            result[u'excluded'] = self.doNotApply
        if self.base_verb_str is not None:
            result[u'base_verb'] = self.base_verb_str
        return result
    
    @property
    def complete_overrides_string(self):    
        """
        so users can edit a note         
        """            
        if self.doNotApply is not None and self.doNotApply != []:
            result = u'-' + u',-'.join(self.doNotApply)
        else:
            result = None
        if self.appliedOverrides is not None and self.appliedOverrides != []:
            if result is not None:
                result += u',' + u','.join(self.appliedOverrides)
            else:
                result = u','.join(self.appliedOverrides)
        if result is None:
            return Verb.REGULAR_VERB
        else:
            return result
        
    def __get_override(self, tense, person, attr_name):
        """
        :return a list of the overrides for this tense/person ( list because a series of overrides can be applied) 
        """
        if hasattr(self, attr_name):
            self_overrides = getattr(self, attr_name)
            if self_overrides[tense] is not None:
                if tense in Tenses.Person_Agnostic:
                    return self_overrides[tense]
                else:
                    return self_overrides[tense][person]
        return None
    
    def process_conjugation_override(self, conjugation_override):
        """
        Before applying the override first check to see if this verb says that it is a special case
        and the override should not be applied.
        """        
        if isinstance(conjugation_override, ConjugationOverride):
            override = conjugation_override            
        elif len(conjugation_override) > 1:
            lookup_key = conjugation_override if conjugation_override[0] != '-' else conjugation_override[1:]
            if lookup_key in Standard_Overrides:
                override = Standard_Overrides[lookup_key]
            elif lookup_key in Dependent_Standard_Overrides:
                override = Dependent_Standard_Overrides[lookup_key]
            else:
                self.__raise(lookup_key+": override is not one of "+repr(Standard_Overrides.keys())+" or "+repr(Dependent_Standard_Overrides.keys()))
            if override is None:
                self.__raise("no override with key ", lookup_key)
            if conjugation_override[0] == '-':
                self.add_doNotApply(override.key)
                return False
        else:
            #No override or blank
            return False
        if self.canApply(override):
            if override.key:
                # Custom overrides do not always have keys
                self.add_applied_override(override.key)
            override.apply(self)      
            return True
        else:
            return False  

    def canApply(self,override_or_key):
        key = override_or_key if isinstance(override_or_key, six.string_types) else override_or_key.key
        return key not in self.doNotApply and key not in self.appliedOverrides
        
    @property
    def root_verb(self):
        if self.base_verb is None:
            return self
        else:
            return self.base_verb.root_verb
            
    @property
    def base_verb(self):
        if self.base_verb_str is None:
            return None
        elif not hasattr(self, '_base_verb'):
            # some verbs are based off of others (tener)
            # TODO: maldecir has different tu affirmative than decir        
            from espanol_dictionary import Verb_Dictionary
            _base_verb = Verb_Dictionary.get(self.base_verb_str)
            if _base_verb is None:
                # TODO - may not be in dictionary yet?
                return None 
            else:
                self._base_verb = _base_verb
                
        return self._base_verb
    
    @property
    def full_prefix(self):
        if self.base_verb is None:
            return u''
        elif self.prefix is not None:
            return self.prefix + self.base_verb.full_prefix
        else:
            # basically self is a reflexive verb with a base verb that adds a prefix
            return self.base_verb.full_prefix
    
    def is_child(self, ancestor_verb):
        if self.base_verb == None or ancestor_verb is None:
            return False
        elif self.base_verb.inf_verb_string == ancestor_verb.inf_verb_string:
            return True
        else:
            # multiple derived verb levels
            return self.base_verb.is_child(ancestor_verb)
        
    @property
    def stem(self):
        return self.prefix + self.core_characters
    
    @property
    def inf_verb_string(self):
        return self.stem + self.inf_ending
        
    @property
    def full_phrase(self):
        if self.prefix_words != u'':
            result = self.prefix_words + u' '
        else:
            result = u''
        result += self.inf_verb_string
        if self.reflexive:
            result += u'se'
        if self.suffix_words != u'':
            result += u' ' + self.suffix_words
        return result
        
    @property
    def verb_ending_index(self):
        if self.inf_ending == u'ír':
            # special casing for eír verbs which have accented i
            return Infinitive_Endings.ir_verb
        else:
            return Infinitive_Endings.index(self.inf_ending)
           
    @property
    def is_phrase(self):
        return self.prefix_words != u'' or self.suffix_words != u''
    
    @property
    def is_regular(self):
        return self.appliedOverrides is None or len(self.appliedOverrides) == 0  
    
    @property
    def appliedOverrides(self):
        appliedOverrides_ = list(self._appliedOverrides)
        if self.base_verb is not None:
            appliedOverrides_.extend(self.base_verb.appliedOverrides)
        return appliedOverrides_
    
    def add_applied_override(self, applied):
        self._appliedOverrides.append(applied)
        
    @property
    def doNotApply(self):
        doNotApply_ = list(self._doNotApply)
        if self.base_verb is not None:
            doNotApply_.extend(self.base_verb.doNotApply)
        return doNotApply_
    
    def add_doNotApply(self, applied):
        self._doNotApply.append(applied)
                 
    def has_override_applied(self, override_key):
        for conjugation_override in get_iterable(self.appliedOverrides):            
            if isinstance(conjugation_override, ConjugationOverride):
                _key = conjugation_override.key
            else:
                _key =conjugation_override
            if _key is not None: # _key is None is always fail.
                if _key == override_key:
                    return True
        return False
    
    def _check_for_multiple_accents(self, tense, person, conjugation):
        """
        Error checking to make sure code did not accent multiple vowels. (or to make sure that we didn't forget to remove an accent)
        """
        if conjugation is not None:
            accented = accented_vowel_check.findall(conjugation)
            if len(accented) > 1:
                self.__raise("Too many accents in "+conjugation, tense, person)
                
    def __raise(self, msg, tense=None, person=None, traceback_=None):
        msg_ = u"{0}: (tense={1},person={2}): {3}".format(self.full_phrase, Tenses[tense] if tense is not None else "-", Persons[person] if person is not None else "-", msg)
        raise Exception, msg_, traceback_
