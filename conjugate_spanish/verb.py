# -*- coding: utf-8 -*-
'''

@author: patmoore
'''

import inspect
from .conjugation_override import *
from .constants import *
from .vowel import Vowels
import traceback
from .utils import cs_debug
import types
from .phrase import Phrase, Phrase_Association
from .standard_endings import *
from conjugate_spanish.conjugation_override import ConjugationOverride
from conjugate_spanish.conjugation_tracking import ConjugationTracking

_ending_vowel_check = re_compile(Vowels.all_group+'$')
# check for word with only a single vowel ( used in imperative conjugation )
_single_vowel_re = re_compile('^('+Vowels.consonants+'*)('+Vowels.all_group+')('+Vowels.consonants+'*)$')
    
class Verb(Phrase):
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
    REGULAR_VERB = 'regular'
    
    def __init__(self, phrase, definition='', conjugation_overrides=None, base_verb=None, manual_overrides=None, 
                 prefix_words='', prefix='', core_characters='', inf_ending=None, reflexive=Reflexive.not_reflexive,
                 suffix_words=None,
                 generated =False, process_conjugation_overrides=True,
                 **kwargs):
        '''
        Constructor
            phrase is assumed to be a correct construction of "prefix words"+" "+prefix+core_characters+"se"? +" " + suffix words
               there may be parsable separators.
                
            root_verb: used as root_verb for conjugation - for example: mantener would have a root_verb of tener
               tener has root_verb = tener
            base_verb: used to as the verb that this phrase or verb is most immediately derived from.
                for example "detenerse a [inf]","stop [inf]" -- base verb = detenerse , root = tener
                key point is that the base_verb can be semantically related to this verb, while the root verb may have *no* relation.
                tener and mantener are not semantically related.
            manual_overrides: explicit string that handles very unique cases that have no pattern.  
        '''
        
        super().__init__(phrase, definition, True, **kwargs)
           
        # Some verbs don't follow the default rules for their ending> for example, mercer
        self._doNotApply = []
        self._appliedOverrides = []
        self._generated = generated
 
        # determine if this verb has suffix words. for example: "aconsejar/con" which means to consult with"        
        phrase_match = Verb.is_verb(self.phrase_string)
        if phrase_match is None:
            self.__raise(self.phrase_string+": does not appear to be a verb or phrase with verb infinitive in it.")            

        self.prefix_words = prefix_words
        self.prefix = prefix
        self.core_characters = core_characters
        self.inf_ending = inf_ending
        self.reflexive = Reflexive.get(reflexive)        
        self.suffix_words = suffix_words
        self.conjugation_tracking = ConjugationTracking(self)
        self.correct_infinitive()
        
                        
        # note: determining the conjugation overrides in constructor because:
        #    1. some conjugation overrides happen automatically based on the verb endings ( i.e. -guir)
        #    2. some overrides for pronounciation preservation are only applied if a previous override has not removed the condition
        # ideally, the conjugation overrides would be a processing pipe - but i didn't know that the code would head that way when i started.
        # 
        # even for derived verbs we need to allow for the possibility that the derived verb has different overrides        
        
        # Note: self.overrides_string << top-level, human editable
        if isinstance(conjugation_overrides, str) and conjugation_overrides != '' and conjugation_overrides != Verb.REGULAR_VERB:
            self.overrides_string = conjugation_overrides
            self.conjugation_overrides = conjugation_overrides.split(",")    
        elif isinstance(conjugation_overrides, list):
            self.overrides_string = ''
            self.conjugation_overrides = conjugation_overrides
        elif isinstance(conjugation_overrides, ConjugationOverride):
            self.overrides_string = ''
            self.conjugation_overrides = [ conjugation_overrides ]
        else:
            self.overrides_string = ''
            self.conjugation_overrides = []
        self.manual_overrides_string = manual_overrides
        self.__processed_conjugation_overrides=False
        
        if process_conjugation_overrides or not self.is_derived:
            self.process_conjugation_overrides()
            
    def correct_infinitive(self):
        """
        TODO: correct ir verbs that need an accented ír
        """
        pass
        
    def process_conjugation_overrides(self):
        if self.__processed_conjugation_overrides:
            return                        
                    
        # TODO -- move all process_conjugation_override out of constructor so that we can properly handle derived verbs where the base verb has not been loaded
        for conjugation_override in get_iterable(self.conjugation_overrides):
            self.process_conjugation_override(conjugation_override)     
        # apply manual overrides after the standard overrides because this allows for the manual overrides to 'fix' the previous changes.
        # applied before the dependent conjugation overrides because many dependent overrides change based on a pattern. 
        # the manual override may change the verb in such a way that the dependent override no longer matches. Thus making it easier to get the correct result.
        self.process_conjugation_override(self._manual_override)
        
        # look for default overrides - apply to end so that user could explicitly turn off the default override
        for conjugation_override in Standard_Overrides.values():
            if conjugation_override.auto_match != False and conjugation_override.is_match(self):                
                applied = self.process_conjugation_override(conjugation_override)
                if applied:
                    if self.overrides_string == '':
                        self.overrides_string = conjugation_override.key
                    else:
                        self.overrides_string += ','+conjugation_override.key
        
        # dependent overrides are reused and are for programming convenience; as such we don't display in the string as it would
        # be confusing on the flash card.
        for conjugation_override in Dependent_Standard_Overrides.values():
            if conjugation_override.auto_match != False and conjugation_override.is_match(self):
                self.process_conjugation_override(conjugation_override)
            
        ## HACK -- should be supplied when generating a card    
        if self.overrides_string == '':
            self.overrides_string = Verb.REGULAR_VERB
            
        self.process_conjugation_override(UniversalAccentFix)
    
    @classmethod
    def importString(cls, phrase, definition='', conjugation_overrides=None, base_verb=None, **kwargs):
                # determine if this verb has suffix words. for example: "aconsejar/con" which means to consult with"        
        phrase_match = Verb.is_verb(phrase)
        if phrase_match is None:
            raise Exception(phrase+": does not appear to be a verb or phrase with verb infinitive in it.")            
            
        for key,value in [['prefix_words', lambda: PhraseGroup.PREFIX_WORDS.extract(phrase_match)], 
                    ['prefix', lambda: PhraseGroup.PREFIX_CHARS.extract(phrase_match)], 
                    ['core_characters', lambda: PhraseGroup.CORE_VERB.extract(phrase_match)], 
                    ['inf_ending', lambda: PhraseGroup.INF_ENDING.extract(phrase_match)], 
                    ['reflexive', lambda: Reflexive.getFromEnding(phrase_match)  ],
                    ['suffix_words', lambda: PhraseGroup.SUFFIX_WORDS.extract(phrase_match)] ]:
            if key not in kwargs:
                kwargs[key] = value()
        # determine base verb string
#         _base_verb = make_unicode(base_verb)
#         if _base_verb == '':
#             _base_verb = None
#         if _base_verb is not None:        
#             if isinstance(_base_verb, Verb):                
#                 _base_verb_str = _base_verb.inf_verb_string
#             elif isinstance(_base_verb, str) and _base_verb != '':
#                 # TODO strip leading/trailing white space
#                 _base_verb_str = _base_verb 
#             else:
#                 raise Exception(phrase+":base_verb must be Verb or string base_verb="+_base_verb).with_traceback()
#             # example abatir has base: batir
#             _base_verb_parse = Verb.is_verb(_base_verb_str)
#             # "abat".find("bat")
#             core_characters_ = kwargs['core_characters']
#             base_verb_index = core_characters_.find(_base_verb_parse.group(CORE_VERB))
#             if base_verb_index <0:
#                 raise Exception(phrase+":"+repr(_base_verb_str)+ " is not in core characters"+repr(core_characters_))
#             if kwargs['prefix'] == '':
#                 kwargs['prefix'] = core_characters_[:base_verb_index]
#                 kwargs['core_characters'] = core_characters_[base_verb_index:]
#             elif base_verb_index != 0 and kwargs['prefix'] != core_characters_[:base_verb_index]:
#                 raise Exception("prefix already="+kwargs['prefix']+" but should be "+core_characters_[:base_verb_index])
#             elif core_characters_ != _base_verb_parse.group(CORE_VERB):
#                 raise Exception("core_characters already="+core_characters_+" but should be "+_base_verb_parse.group(CORE_VERB))
#         
#             
#         kwargs['base_verb'] = _base_verb_str
        verb = Verb(phrase, definition, conjugation_overrides, process_conjugation_overrides=False, **kwargs)
        if not verb.is_derived:
            # process root verbs so that they are available for derived verbs.
            verb.process_conjugation_overrides()
        return verb
    @classmethod        
    def is_verb(cls, phrase_string):
        return PhraseGroup.is_verb(phrase_string)
                
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
                            if not self.is_reflexive:
                                print( Persons[person]+" "+conjugations[tense][person], end="; ")
                            elif tense not in Tenses.imperative:
                                print( conjugations[tense][person], end="; ")
                            else:
                                print(conjugations[tense][person])
                                 
                    print()

    def print_csv(self, full_info=True):
        result = '"'+self.full_phrase+'"'
        if full_info:
            if len(self.appliedOverrides) > 0:
                result+=',"'+repr(self.appliedOverrides)+'"'
            if len(self.doNotApply) > 0:
                result +=',"'+repr(self.doNotApply)+'"'
            if self.base_verb_string is not None:
                result += ',"'+self.base_verb_string+'"'
        
        for tense in Tenses.all:
            if tense in Tenses.Person_Agnostic:
                conjugation = self.conjugate(tense)
                result += ',"'+conjugation+'"'
            else:
                for person in Persons.all:
                    conjugation = self.conjugate(tense, person)
                    if conjugation is None:
                        result += ','
                    else:
                        result += ',"'+conjugation+'"'
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
        options -
            reflexive_override - set to False to force the verb to be conjugated without the reflexive pronoun 
               (needed in cases of a base verb being a reflexive verb.)
            
        :return: The conjugated verb. Note: the verb must be <indirect pronoun> <verb> or just <verb>
        """           
        conjugation_notes = self.conjugation_tracking.get_conjugation_notes(tense, person)     
        if tense in Tenses.imperative and person == Persons.first_person_singular:
            conjugation_notes.change(core_verb = None, ending = None)
            return None        
        if tense not in Tenses.Person_Agnostic and person not in Persons.all:
            self.__raise("Tense "+Tenses[tense]+" needs a person", tense, person)
        if self.base_verb is not None:            
            conjugation = self.__derived_conjugation(conjugation_notes, options)
            conjugation_notes.change(conjugation=conjugation)
        else:            
            conjugation_overrides = self.__get_override(conjugation_notes, 'conjugations')
            
            if conjugation_overrides is not None:
                for conjugation_override in conjugation_overrides:
                    if isinstance(conjugation_override, str):
                        conjugation = conjugation_override
                        conjugation_notes.change(conjugation = conjugation)
                    elif conjugation_override is not None:
                        override_call = { 'tense': tense, 'person': person, "options":options }
                        try:
                            conjugation = conjugation_override(**override_call)
                        except Exception as e:
                            extype, ex, traceback_ = sys.exc_info()
                            formatted = traceback.format_exception_only(traceback_,extype, ex)[-1]
                            message = "Trying to conjugate irregular:%s %s" % ex.message, formatted
                            self.__raise(message, tense, person, traceback_)
                if pick(options,ConjugationOverride.REFLEXIVE_OVERRIDE,self.reflexive) and not is_empty_str(conjugation):
                    # needed in imperative to correctly add in the reflexive pronoun 
                    # TODO: may not to check for explicit accent.
                    conjugation = self.__apply_reflexive_pronoun(conjugation_notes, conjugation, False)
            else:
                conjugation = self._conjugate_stem_and_endings(conjugation_notes, options)
            
        self._check_for_multiple_accents(tense, person, conjugation)
        return conjugation
    
    def _conjugate_stem_and_endings(self, conjugation_notes, options):
        """
        exists so that third person verbs can decide to conjugate normally for present subjective and past subjective
        """
        if conjugation_notes.tense not in Tenses.imperative:
            self.conjugate_ending(conjugation_notes)            
            current_conjugation_stem = self.conjugate_stem(conjugation_notes.tense, conjugation_notes.person, conjugation_notes.ending)
            conjugation = self.conjugation_joining(conjugation_notes.tense, conjugation_notes.person, current_conjugation_stem, conjugation_notes.ending)
        else:
            conjugation = self.__conjugation_imperative(conjugation_notes)
        return conjugation
        
    def __derived_conjugation(self, conjugation_notes, options):
        """ This verb is based on another verb: example: abstenerse is based on tener
        these base verbs are not allowed to be reflexive verbs (I haven't found any examples yet where this is an issue)
        
        This is not "perfect" implementation because:
        1. in multiple level of ancestory: intermediate ancestor verbs are not allowed to apply their own overrides.
        2. child verbs cannot apply any conjugation overrides of their own ( maybe an issue with decir )
        
        However, the resulting code is similar. ( the issue is the accenting on the rare tener :2nd person singular imperative )
        
        I would like to eliminate this code and go to a pure conjugation override model 
        """
        # we never want the base verb to apply the reflexive pronoun - irregardless of reflexive_override
        _options = { **options, **{ConjugationOverride.REFLEXIVE_OVERRIDE : False} }
        base_verb_conjugation = self.base_verb.conjugate(conjugation_notes.tense, conjugation_notes.person, _options)
        if base_verb_conjugation is None:
            # imperative, third-person only verbs
            return None
        
        # done because of multiple layers of derivation.
        _reflexive = pick(options,ConjugationOverride.REFLEXIVE_OVERRIDE, self.is_reflexive)
        explicit_accent_already_applied = False
        # TODO: look for 2/3 vowel dipthongs as well
        single_vowel_match = _single_vowel_re.match(base_verb_conjugation)        
        
        if conjugation_notes.tense == Tenses.imperative_positive and conjugation_notes.person == Persons.second_person_singular:
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
                    _conjugation = self.full_prefix + Vowels.accent_at(base_verb_conjugation, single_vowel_match.start(2))
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
            
        if _reflexive:
            _conjugation = self.__apply_reflexive_pronoun(conjugation_notes,_conjugation, explicit_accent_already_applied)
        
        if not is_empty_str(self.prefix_words):
            returned_conjugation = self.prefix_words
        else:
            returned_conjugation = ''
        returned_conjugation += _conjugation
        if not is_empty_str(self.suffix_words):
            returned_conjugation += ' '+self.suffix_words
        return returned_conjugation
    def __apply_reflexive_pronoun(self, conjugation_notes, _conjugation, explicit_accent_already_applied):
        """
        assume that self.is_reflexive has been checked 
        """
        if conjugation_notes.tense in Tenses.imperative:
            returned_conjugation = self.__apply_imperative_reflexive_pronoun(conjugation_notes, _conjugation, explicit_accent_already_applied)                        
        elif conjugation_notes.tense not in Tenses.Person_Agnostic:
            returned_conjugation = Persons_Indirect[conjugation_notes.person] +" "+ _conjugation
        elif conjugation_notes.tense == Tenses.gerund:
            returned_conjugation = Vowels.accent(_conjugation)+'se'
        else:
            returned_conjugation = _conjugation
        conjugation_notes.conjugation = returned_conjugation
        return returned_conjugation
            
    def conjugate_stem(self, tense, person, current_conjugation_ending):
        conjugation_notes = self.conjugation_tracking.get_conjugation_notes(tense, person)
        def __check_override(override, current_conjugation_stem):
            if isinstance(override, str):
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
            current_conjugation_stem = Vowels.remove_accent(self.inf_verb_string)
        elif tense == Tenses.present_subjective_tense:
            current_conjugation_stem = self.__conjugation_present_subjective_stem(conjugation_notes)
        elif tense == Tenses.past_subjective_tense:
            current_conjugation_stem = self.__conjugation_past_subjective_stem(conjugation_notes)
        else:
            self.__raise(": Can't be handled", tense, person)
        conjugation_notes.core_verb = current_conjugation_stem
            
        overrides = self.__get_override(conjugation_notes, 'conjugation_stems')
        if overrides is not None:
            for override in get_iterable(overrides):
                current_conjugation_stem = __check_override(override, current_conjugation_stem)
                conjugation_notes.core_verb = current_conjugation_stem
        
        if current_conjugation_stem is None:
            self.__raise("no stem created", tense, person)
        
        return current_conjugation_stem
        
    def conjugate_ending(self, conjugation_notes):
        def __check_override(override):
            if isinstance(override, str):
                conjugation_notes.ending = override
            elif override:
                override_call = { 'tense': conjugation_notes.tense, 'person': conjugation_notes.person, 'stem': self.stem, 'ending' : conjugation_notes.ending }
                try:
                    conjugation_notes.ending = override(**override_call)
                except Exception as e:
                    extype, ex, traceback_ = sys.exc_info()
#                         formatted = traceback_.format_exception_only(extype, ex)[-1]
                    message = "Trying to conjugate ending; %s" % ex.message
                    self.__raise(message, conjugation_notes.tense, conjugation_notes.person, traceback_)
        
        overrides = self.__get_override(conjugation_notes, 'conjugation_endings')
        if overrides is not None:
            for override in get_iterable(overrides):
                __check_override(override)
    
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
        conjugation_notes = self.conjugation_tracking.get_conjugation_notes(tense, person)
        overrides = self.__get_override(conjugation_notes, 'conjugation_joins')
        if overrides is not None:
            for override in get_iterable(overrides):
                [current_conjugation_stem, current_conjugation_ending]  = __check_override(override, current_conjugation_stem, current_conjugation_ending)
                if not isinstance(current_conjugation_stem, str):
                    self.__raise("stem is not string", tense, person)
                if not isinstance(current_conjugation_ending, str):
                    self.__raise("ending is not string", tense, person) 
                conjugation_notes.change(core_verb=current_conjugation_stem, ending = current_conjugation_ending)
 
        return current_conjugation_stem+current_conjugation_ending
    
    def __conjugation_imperative(self, conjugation_notes, conjugation=None):
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
        if conjugation_notes.person == Persons.first_person_singular:
            # no such conjugation
            return None
        
        # Step #1 - for verbs with no override conjugation - get the conjugation        
        if conjugation is None:
            # For most persons the conjugation is the present_subjective ( because imperative is a "mood" - enhancement to the present_subjective )
            if conjugation_notes.tense == Tenses.imperative_negative or conjugation_notes.person not in Persons.second_person:
                # all negative imperatives use the present_subjective AND all positives EXCEPT second person
                _conjugation = self.conjugate(Tenses.present_subjective_tense, conjugation_notes.person)
#                 if person == Persons.first_person_plural and verb.reflexive:
#                     # properly prepare the verb by removing the trailing 's'
#                     # TODO: notice we don't handle a case of irregular nosotros - that does not have a trailing 's'
#                     # this seems to not be a problem for anything - but we will raise an exception if it is
#                     # this seems to only be a problem for irse
#                     _conjugation = _replace_last_letter_of_stem(_conjugation, u's', u'')
            elif conjugation_notes.person == Persons.second_person_singular and conjugation_notes.tense == Tenses.imperative_positive:
                # positive tu form uses present tense usted                
                _conjugation = self.conjugate(Tenses.present_tense, Persons.third_person_singular)
            elif conjugation_notes.person == Persons.second_person_plural and conjugation_notes.tense == Tenses.imperative_positive:                
                # remove 'r' from infinitive - and replace it with 'd'
                _conjugation = _replace_last_letter_of_stem(self.inf_verb_string, 'r', 'd')
            else:
                self.__raise("Missed case"+conjugation_notes.tense+" "+conjugation_notes.person)  
        else:
            _conjugation = conjugation                      
        
        returned_conjugation = self.__apply_imperative_reflexive_pronoun(conjugation_notes, _conjugation)
        return returned_conjugation
    
    def __apply_imperative_reflexive_pronoun(self, conjugation_notes, conjugation, explicit_accent_already_applied=False):
        # Step 3 - handle the placement of the indirect pronoun for reflexive verbs.  
        # The important issue here is the effect on the accent.      
        if is_empty_str(conjugation):
            # degenerate verbs such as solerse
            return conjugation
        def handle_explicit_accent_():
            if explicit_accent_already_applied:
                return conjugation
            else:
                return Vowels.accent(conjugation)
        if self.is_reflexive:
            #Now apply the reflexive pronoun rules.
            if conjugation_notes.person in Persons.third_person:
                # simple!
                returned_conjugation = handle_explicit_accent_() + Persons_Indirect[conjugation_notes.person]
            elif conjugation_notes.person == Persons.first_person_plural:
                # mostly simple (same as third person except trailing 's' is dropped before adding the indirect pronoun
                returned_conjugation = _replace_last_letter_of_stem(handle_explicit_accent_(), 's', Persons_Indirect[conjugation_notes.person])
            elif conjugation_notes.tense == Tenses.imperative_negative:
                # second person negative : simple as well!
                # reflexive pronoun is a separate word in front of the verb. (i.e. 'no te abstengas')
                # notice that the second person cases negative do not have any accent issues.
                returned_conjugation = Persons_Indirect[conjugation_notes.person]+ " " + conjugation
            elif conjugation_notes.person == Persons.second_person_singular: # (imperative positive) 
                # Need to put explicit accent in SOME cases for example: quitarse ( quítate ) but not in all: abstener ( abstente )
                # ( could it be that 'ten' is a single vowel word and retains the accent on the ten - even with the prefix? )
                # ensure that there is an accent somewhere (note that in abstenerse case the accent should already be on the abs-tén 
                returned_conjugation = handle_explicit_accent_() + Persons_Indirect[conjugation_notes.person]
            elif conjugation_notes.person == Persons.second_person_plural:  # (imperative positive) 
                # TODO look for single vowel in conjugation for model verb.
                # TODO : Would like to make this a conjugation override - but conjugation overrides are not applied on derived verbs
                if self.verb_ending_index == Infinitive_Endings.ir_verb:
                    if conjugation[-2:] == 'id':
                        # ir verbs need the i (in ir) accented rule k and l
                        # this makes sense because otherwise the os would be accented.
                        # example ¡Vestíos! - Get Dressed!
                        # we don't need to worry about accenting the -ir verbs that already have the i accented ( example reírse )
                        # what about verbs that already have explicit accent?
                        returned_conjugation = Vowels.remove_accent(conjugation[:-2]) + 'í' + Persons_Indirect[Persons.second_person_plural]
                    elif conjugation[-2:] == 'íd':
                        returned_conjugation = _replace_last_letter_of_stem(conjugation, 'd', Persons_Indirect[Persons.second_person_plural])
                    else:
                        self.__raise("don't know how to handle:"+conjugation, conjugation_notes.tense, conjugation_notes.person)
                else:
                    # ex: ¡Sentaos! - Sit down! ( the spoken accent will be on the ending a )
                    returned_conjugation = _replace_last_letter_of_stem(Vowels.remove_accent(conjugation), 'd', Persons_Indirect[Persons.second_person_plural])
            else:
                self.__raise("applying reflexive pronoun", conjugation_notes.tense, conjugation_notes.person)
        else:
            returned_conjugation = conjugation
        return returned_conjugation
             
    def __conjugation_present_subjective_stem(self, conjugation_notes):
        # need to force for verbs that are normally third person only
        options = { ConjugationOverride.FORCE_CONJUGATION: True, ConjugationOverride.REFLEXIVE_OVERRIDE: False }
        first_person_conjugation = self.conjugate(Tenses.present_tense, Persons.first_person_singular, options)
        if first_person_conjugation[-1:] =='o':
            conjugation_stem = first_person_conjugation[:-1]            
        elif first_person_conjugation[-2:] == 'oy':
            # estoy, doy, voy, etc.
            conjugation_stem = first_person_conjugation[:-2]
        else:
            # haber (he) is just such an example - but there better be an override available.
            return None
#             self.__raise("First person conjugation does not end in 'o' = "+first_person_conjugation)
        # HACK: Not certain if this is correct - but i checked enviar and reunierse - shich both have an accented 1st sing present stem.
        if conjugation_notes.person in [ Persons.first_person_plural, Persons.second_person_plural ]:
            conjugation_stem = Vowels.remove_accent(conjugation_stem)
        return conjugation_stem

    def __conjugation_past_subjective_stem(self, conjugation_notes):
        """
        in First person plural, accent if third person plural ends in a vowel after dropping -ron        
        """
        # need to force for verbs that are normally third person only
        options = { ConjugationOverride.FORCE_CONJUGATION: True, ConjugationOverride.REFLEXIVE_OVERRIDE: False }
        third_person_plural_conjugation = self.conjugate(Tenses.past_tense, Persons.third_person_plural, options)
        if third_person_plural_conjugation[-3:] == 'ron':
            conjugation_stem = third_person_plural_conjugation[:-3]
            if conjugation_notes.person == Persons.first_person_plural:
                # accent on last vowel                                
                if _ending_vowel_check.search(conjugation_stem):
                    conjugation_stem = Vowels.accent_at(conjugation_stem)
                else:
                    # assuming last stem character is a vowel
                    # and assuming already accented for some reason
                    self.__raise("No ending vowel", conjugation_notes.tense, conjugation_notes.person)
            return conjugation_stem
        else:
            self.__raise("Third person conjugation does not end in 'ron' = "+third_person_plural_conjugation, conjugation_notes.tense, conjugation_notes.person)
            
    def _overrides(self, tense, overrides, attr_name,persons=None):
        """
        Called by Conjugation_Override as an override is applied
        """        
        def __convert_to_self_function(override):            
            if inspect.isfunction(override) or inspect.ismethod(override):
                boundfunc = types.MethodType(override, self)
                return boundfunc                
            elif isinstance(override, str):
                return override                        
            else:
                self.__raise("Override must be function or string not"+type(override),tense)           
            
        if not hasattr(self, attr_name):
            self_overrides = [ None ] * len(Tenses)
            setattr(self, attr_name, self_overrides) 
        else:
            self_overrides = getattr(self, attr_name)
            
        if tense in Tenses.Person_Agnostic:
            override_ = __convert_to_self_function(overrides)
            if isinstance(override_, str) or self_overrides[tense] is None:
                self_overrides[tense] = [ override_ ]
            else:
                self_overrides[tense].append(override_)
            return
        
        if persons is None:
            _persons = Persons
        elif isinstance(persons, int):
            _persons = [ persons ]
        elif isinstance(persons, list):
            _persons = persons
        else:
            self.__raise("persons must be None, integer or list of integers", tense)
            
        if self_overrides[tense] is None:
            self_overrides[tense] = [None] * len(Persons)
            
        if isinstance(overrides, str) or inspect.isfunction(overrides) or inspect.ismethod(overrides):            
            fn = __convert_to_self_function(overrides)
            for person in _persons:
                if isinstance(fn, str) or self_overrides[tense][person] is None:
                    # if a hard replacement (string), previous overrides are discarded because they will be replaced.
                    # or this is the first override
                    self_overrides[tense][person] = [fn]
                else:
                    self_overrides[tense][person].append(fn)                    
        
        elif isinstance(overrides, list):
            for person, override in enumerate(overrides):
                if override is not None:
                    fn = __convert_to_self_function(override)
                    if isinstance(fn, str) or self_overrides[tense][person] is None:
                        # if a hard replacement (string), previous overrides are discarded because they will be replaced.
                        # or this is the first override
                        self_overrides[tense][person] = [fn]
                    else:
                        self_overrides[tense][person].append(fn)                    
                    
    def overrides_applied(self):
        result = {}
        if self.appliedOverrides is not None and self.appliedOverrides != []:
            result['applied']= self.appliedOverrides
        if self.doNotApply is not None and self.doNotApply != []:
            result['excluded'] = self.doNotApply
        if self._base_verb_str is not None:
            result['base_verb'] = self._base_verb_str
        return result
    
    @property
    def complete_overrides_string(self):    
        """
        so users can edit a note         
        """            
        if self.doNotApply is not None and self.doNotApply != []:
            result = '-' + ',-'.join(self.doNotApply)
        else:
            result = None
        if self.appliedOverrides is not None and self.appliedOverrides != []:
            if result is not None:
                result += ',' + ','.join(self.appliedOverrides)
            else:
                result = ','.join(self.appliedOverrides)
        if result is None:
            return Verb.REGULAR_VERB
        else:
            return result
        
    def __get_override(self, conjugation_notes, attr_name):
        """
        :return a list of the overrides for this tense/person ( list because a series of overrides can be applied) 
        """
        if hasattr(self, attr_name):
            self_overrides = getattr(self, attr_name)
            if self_overrides[conjugation_notes.tense] is not None:
                if conjugation_notes.tense in Tenses.Person_Agnostic:
                    return self_overrides[conjugation_notes.tense]
                else:
                    return self_overrides[conjugation_notes.tense][conjugation_notes.person]
        return None
    
    @property
    def _manual_override(self):
        if self.manual_overrides_string is not None and self.manual_overrides_string != '':             
            manual_conjugation_override = ConjugationOverride.create_from_json(self.manual_overrides_string, key=self.key+"_irregular")
            return manual_conjugation_override
        else:
            return None

    def process_conjugation_override(self, conjugation_override):
        """
        Before applying the override first check to see if this verb says that it is a special case
        and the override should not be applied.
        """        
        if conjugation_override is None:
            return
        elif isinstance(conjugation_override, ConjugationOverride):
            override = conjugation_override            
        elif len(conjugation_override) > 1:
            lookup_key = conjugation_override if conjugation_override[0] != '-' else conjugation_override[1:]
            if lookup_key in Standard_Overrides:
                override = Standard_Overrides[lookup_key]
            elif lookup_key in Dependent_Standard_Overrides:
                override = Dependent_Standard_Overrides[lookup_key]
            else:
                self.__raise(lookup_key+": override is not one of "+repr(list(Standard_Overrides.keys()))+" or "+repr(list(Dependent_Standard_Overrides.keys())))
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
        key = override_or_key if isinstance(override_or_key, str) else override_or_key.key
        return key not in self.doNotApply and key not in self.appliedOverrides        
    
    @property
    def prefix(self):
        return self._prefix
    
    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix
    
    @property
    def has_prefix(self):
        return self.prefix is not None and self.prefix != ''
    
    @property
    def is_reflexive(self):
        return self.reflexive != Reflexive.not_reflexive
    
    @property
    def is_generated(self):
        return self._generated
    
    @property
    def base_verb(self):
        if not self.is_derived:
            return None
        elif not hasattr(self, '_base_verb'):
            # some verbs are based off of others (tener)
            # TODO: maldecir has different tu affirmative than decir  
            #HACK : would prefer to not trigger sql calls... but this works o.k. 
            # and allows for out of ordering loading.      
            from .espanol_dictionary import Verb_Dictionary
            _base_verb = Verb_Dictionary.get(self.base_verb_string)
            if _base_verb is None:
                # TODO - may not be in dictionary yet?
                return None 
            else:
                self._base_verb = _base_verb
                
        return self._base_verb
    
    @base_verb.setter
    def base_verb(self, base_verb):
        """ should only be called by the storage
        """
        self._base_verb = base_verb    
    
    @property
    def base_verb_string(self):
        if self.is_derived:                
            _base_verb_str= getattr(self, '_base_verb_string', None)
            if is_empty_str(_base_verb_str):
                if self.is_phrase:
                    # a phrase means the base verb is the actual verb being conjugated.
                    self._base_verb_string = self.inf_verb_string
                elif self.reflexive == Reflexive.base_reflexive:
                    self._base_verb_string = self.core_characters + self.inf_ending +'se'
                else:                    
                    self._base_verb_string = self.core_characters + self.inf_ending
            return self._base_verb_string
        else:
            return None
    @base_verb_string.setter
    def base_verb_string(self, base_verb_string_):
        self._base_verb_string = base_verb_string_
        
    @property
    def root_verb(self):
        """
        Root verb is the verb that provides the conjugation rules.
        """
        if hasattr(self, '_root_verb'):
            return self._root_verb
                    # some verbs are based off of others (tener)
            # TODO: maldecir has different tu affirmative than decir  
            #HACK : would prefer to not trigger sql calls... but this works o.k. 
            # and allows for out of ordering loading.
        if self.root_verb_string:      
            from .espanol_dictionary import Verb_Dictionary
    
            self._root_verb = Verb_Dictionary.get(self.root_verb_string)
                # TODO - may not be in dictionary yet?
            return self._root_verb

        elif self.base_verb is not None:
            return self.base_verb.root_verb
        else:
            return None
        
    @root_verb.setter
    def root_verb(self, root_verb_):
        self._root_verb = root_verb_
            
    @property
    def root_verb_string(self):
        if self.is_derived:
            return self.core_characters+self.inf_ending
        else:
            return None
    
    @property
    def is_derived(self):
        return self.is_phrase or self.has_prefix or self.is_reflexive    
    
    @property
    def derived_from(self):
        """
        return derived from
        TODO: maybe a chain of derivations
        """
        if self.is_derived:
            if self.is_reflexive:
                return [ self.base_verb_string, self.inf_verb_string ]
            else:
                return [ self.base_verb_string ]
        else:
            return None
        
    @property
    def full_prefix(self):
        if self.base_verb is None:
            return ''
        elif self.has_prefix:
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
        if not is_empty_str(self.prefix_words):
            result = self.prefix_words + ' '
        else:
            result = ''
        result += self.inf_verb_string
        if self.is_reflexive:
            result += 'se'
        if not is_empty_str(self.suffix_words):
            result += ' ' + self.suffix_words
        return result
        
    @property
    def verb_ending_index(self):
        if self.inf_ending == 'ír':
            # special casing for eír verbs which have accented i
            return Infinitive_Endings.ir_verb
        else:
            return Infinitive_Endings.index(self.inf_ending)
           
    @property
    def is_phrase(self):
        return not is_empty_str(self.prefix_words) or not is_empty_str(self.suffix_words)
    
    @property
    def is_regular(self):
        return self.appliedOverrides is None or len(self.appliedOverrides) == 0  
    
    def has_conjugation_overrides(self, conjugation_overrides):
        result = True
        for conjugation_override in get_iterable(conjugation_overrides):
            result = result & (conjugation_override in self.appliedOverrides )
        return result 
    
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
    
    @property    
    def conjugation_overrides(self):
        return self._conjugation_overrides
    
    @conjugation_overrides.setter
    def conjugation_overrides(self, explicit_overrides_string):
        self._conjugation_overrides = explicit_overrides_string
                 
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
    
    @property
    def tags(self):
        _tags = list( self.conjugation_overrides)
        if self.is_phrase:
            _tags.append(self.PHRASE_TAG)
        if self.manual_overrides_string is not None:
            _tags.append(self.MANUAL_TAG)
        if self.base_verb_string:
            _tags.append(self.base_verb_string)
        if self.root_verb_string and self.root_verb_string != self.base_verb_string:
            _tags.append(self.root_verb_string)
        return _tags
    
    def _check_for_multiple_accents(self, tense, person, conjugation):
        """
        Error checking to make sure code did not accent multiple vowels. (or to make sure that we didn't forget to remove an accent)
        """
        if not is_empty_str(conjugation):
            accented = Vowels.accented_vowel_check.findall(conjugation)
            if len(accented) > 1:
                self.__raise("Too many accents in "+conjugation, tense, person)
                
    def __raise(self, msg, tense=None, person=None, traceback_=None):
        msg_ = "{0}: (tense={1},person={2}): {3}".format(self.full_phrase, Tenses[tense] if tense is not None else "-", Persons[person] if person is not None else "-", msg)
        cs_debug(">>>>>>",msg_)
#         raise Exception(msg_).with_traceback(traceback_)
        
    def __str__(self):
        s= ''
        for k,v in zip(Verb.table_columns(),self.sql_insert_values()):
            if v is not None and v != '':
                s = s + str(k)+'='+str(v)+';'
        return s
    
    def __repr__(self):
        return self.__str__()

    @classmethod
    def table_columns(cls):
        table_columns_ = super().table_columns()
        table_columns_.extend( ["prefix_words", "prefix", "core_characters", "inf_ending", "inf_ending_index","reflexive", "suffix_words", "conjugation_overrides","applied_overrides","manual_overrides", 'base_verb','root_verb','generated'])
        return table_columns_
                       
    def sql_insert_values(self):
        insert_values_ = super().sql_insert_values()
        insert_values_.extend( [self.prefix_words, self.prefix, self.core_characters, self.inf_ending, self.verb_ending_index, self.reflexive.value, self.suffix_words, ",".join(self.conjugation_overrides), ",".join(self.appliedOverrides), self.manual_overrides_string, self.base_verb_string, self.root_verb_string, self.is_generated])    
        return insert_values_
    
    
