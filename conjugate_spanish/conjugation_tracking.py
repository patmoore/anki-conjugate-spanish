# -*- coding: utf-8 -*-
from .constants import *
import json
from functools import reduce
from .utils import cs_debug, cs_error
from .vowel import Vowels
"""
This code holds the history of how the verb is conjugated
1. Shows the rules used (in order)
2. Is responsible for the final joining together of the verb 
"""
from conjugate_spanish.standard_endings import Infinitive_Ending

class ConjugationNote:
    """
    Intended to be immutable
    """
    def __init__(self, operation, tense, person):
        """
        conjugation - the new conjugation string
        """
        self._operation = operation
        self._tense = tense
        self._person = person
        self._core_verb = None
        self._ending = None
        self.irregular_nature = IrregularNature.regular
    
    @property
    def not_applied(self):
        """
        Used to indicate that the operation was *not* applied
        """
        return self._not_applied
    
    @not_applied.setter
    def not_applied(self, not_applied_reason):
        self._not_applied = True
        self._not_applied_reason = not_applied_reason
    
    @property
    def not_applied_reason(self):
        return self._not_applied_reason if self._not_applied else None
    
    @property
    def conjugation(self):
        if hasattr(self, "_conjugation"):
            return self._conjugation 
        else:
            return None
        
    @conjugation.setter
    def conjugation(self, conjugation):        
        self._conjugation = conjugation
    
    @property      
    def core_verb(self):
        return self._core_verb
    
    @core_verb.setter
    def core_verb(self, core_verb):
        self._core_verb = core_verb
    
    @property
    def ending(self):
        return self._ending
    
    @ending.setter
    def ending(self, ending):
        self._ending = ending
        
    @property
    def operation(self):
        return self._operation
            
    @operation.setter
    def operation(self, operation):        
        self._operation = operation

    def change(self, conjugation):
        self.conjugation = conjugation
        
    @property
    def irregular_nature(self):
        return self._irregular_nature
    
    @irregular_nature.setter
    def irregular_nature(self, irregular_nature):
        self._irregular_nature = irregular_nature
        
    @property
    def is_irregular(self):
        return self.irregular_nature != None and self.irregular_nature != IrregularNature.regular 
                  
    def __repr__(self):
        return {
                'operation' : self.operation,
                'conjugation' : self.conjugation,
                'core_verb' : self.core_verb,
                'ending' : self.ending,
                'irregular_nature' : self.irregular_nature
                }
    def __str__(self):
        return self.conjugation if self.conjugation else self.core_verb+self.ending
            
class ConjugationNotes():
    """
    collects the overrides and alterations applied.
    Some alterations also will note if they cannot be applied
    but normally would.
    """ 
    def __init__(self, tense, person, phrase):
        self._tense = tense
        self._person = person
        self._conjugation_note_list = [ ]
        self._operation = None
        self._blocked = False
        self._completed = False
        self._phrase = phrase
        infinitive_ending = Infinitive_Ending.index(phrase.verb_ending_index)
        inf_conjugation_note = self._new_conjugation_note("infinitive")
        inf_conjugation_note.core_verb = phrase.stem
        # TODO replace with infinitive_ending.code?
        inf_conjugation_note.ending = phrase.inf_ending
        inf_conjugation_note.irregular_nature = IrregularNature.base
        std_ending = infinitive_ending.get_standard_conjugation_ending(self, phrase.verb_ending_index)
        if std_ending is not None:
            std_conjugation_note = self._new_conjugation_note("std_ending")
            std_conjugation_note.ending = std_ending 
            std_conjugation_note.irregular_nature = IrregularNature.regular
        
    def _new_conjugation_note(self, operation):
        if self.completed:
            self.__raise("Already completed")
        conjugation_note = ConjugationNote(operation, self._tense, self._person)
        self._conjugation_note_list.insert(0, conjugation_note)
        return conjugation_note
        
    def _check_for_multiple_accents(self):
        """
        Error checking to make sure code did not accent multiple vowels. (or to make sure that we didn't forget to remove an accent)
        """
        if not is_empty_str(self.conjugation):
            accented = Vowels.accented_vowel_check.findall(self.conjugation)
            if len(accented) > 1:
                self.__raise("{} {} Too many accents in {}".format(self.tense, self.person,self.conjugation))
                
    @property
    def conjugation_note_list(self):
        return self._conjugation_note_list
    
    @property
    def operation(self):
        return self._operation;
    
    @property
    def irregular_nature(self):
        if len(self._conjugation_note_list) > 0:
            return reduce(lambda x,y: x if x > y else y, [conjugation_note.irregular_nature for conjugation_note in self._conjugation_note_list ])
        else:
            return IrregularNature.blocked
    
    def batch(self, operation, irregular_nature):
        self._operation = operation
        self._irregular_nature_in_progress = irregular_nature
        return self
        
    def end_batch(self):
        self._operation = None
        return self
        
    @property
    def core_verb(self):
        if not self.blocked:
            for conjugation_note in self._conjugation_note_list:
                if conjugation_note.core_verb is not None:
                    return conjugation_note.core_verb
        return None
        
    @property
    def ending(self):
        if not self.blocked:
            for conjugation_note in self._conjugation_note_list:
                if conjugation_note.ending is not None:
                    return conjugation_note.ending
        return None
    
    def change(self, operation=None, irregular_nature=None, **kwargs):
        """
        Some tenses depend on other tenses / person
        """
        if self.blocked:
            self.__raise("blocked")
        if operation is None:
            operation = self.operation
        else:
            self._operation = None
            
        if irregular_nature is None:
            irregular_nature = self._irregular_nature_in_progress
        else:
            self._irregular_nature_in_progress = None
            
        change_keys = []
        if 'conjugation' in kwargs and isinstance(kwargs['conjugation'], ConjugationNotes):
            conjugation = kwargs['conjugation']
            if conjugation.conjugation is not None:
                self._conjugation_note_list = [ ]
                kwargs['conjugation'] = conjugation.conjugation
                kwargs['core_verb'] = conjugation.core_verb
                kwargs['ending'] = conjugation.ending
                
        for change_key in ['conjugation', 'core_verb', 'ending']:
            if change_key in kwargs and getattr(self, change_key) != kwargs[change_key]:
                change_keys.append(change_key)
        if len(change_keys) > 0:
            conjugation_note = self._new_conjugation_note(operation)
            for change_key in change_keys:
                setattr(conjugation_note, change_key, kwargs[change_key])
            conjugation_note.irregular_nature = irregular_nature
    
    @property
    def conjugation(self):        
        if self.blocked:
            return None
        explicit_conjugation_ = self.explicit_conjugation
        if explicit_conjugation_ is not None:
            return explicit_conjugation_
        else:
            return (self.core_verb if self.core_verb is not None else '') + (self.ending if self.ending is not None else '')
        
    @property
    def explicit_conjugation(self):
        if not self.blocked:
            for conjugation_note in self._conjugation_note_list:
                if conjugation_note.conjugation is not None:
                    return conjugation_note.conjugation
        return None
    
    @property
    def tense(self):
        return self._tense
    
    @property
    def person(self):
        return self._person  
    
    @property
    def phrase(self):
        return self._phrase
    
    @property
    def full_conjugation(self):
        if self.phrase.has_prefix_words:
            full = self.phrase.prefix_words + ' ' + self.conjugation
        else:
            full = self.conjugation
        if self.phrase.has_suffix_words:
            full += ' ' + self.phrase.suffix_words
        return full
    
    def block(self):
        """
        Used to indicate a conjugation does not exist.
        For example, first person singular imperative
        or 3rd person only verbs
        """
        if not self.blocked: 
            self._blocked = True
            conjugation_note =self._new_conjugation_note("blocked")
            conjugation_note.irregular_nature = IrregularNature.blocked
            self.complete()
        return self
        
    @property
    def blocked(self):
        return self._blocked
    
    @property
    def completed(self):
        return self._completed
    
    def complete(self):
        self._completed = True
        self._check_for_multiple_accents()
        return self
    
    @property
    def operation_notes(self):
        return str([ note.operation for note in self._conjugation_note_list ])
    
    @property
    def is_regular(self):
        return self.irregular_nature in [ IrregularNature.regular, IrregularNature.base]
        
    def __raise(self, msg, traceback_=None):
        msg_ = "{0}: (tense={1},person={2}): {3}".format(self.phrase.full_phrase, 
             Tense[self.tense].human_readable if self.tense is not None else "-",
             Person[self.person].human_readable if self.person is not None else "-", msg)
        cs_error(">>>>>>",msg_)
        
    def __repr__(self):
        return { 
            'tense' : self.tense,
            'person' : self.person,
            'changes' : [ conjugation_note.__repr__() for conjugation_note in self._conjugation_note_list if conjugation_note.is_irregular]
        }.__str__()

    def __str__(self):
        return self.full_conjugation
    
class ConjugationTracking():
    """
    Tracks every change to a verb /phrase as it is being conjugated
    Owned by a phrase / verb
    """
    def __init__(self, phrase):
        self.conjugation_notes = [ None for tense in Tense.all() ]
        self._phrase = phrase
                
    def get_conjugation_notes(self, tense, person = None):
        if self.conjugation_notes[tense] is None:
            if tense in Tense.Person_Agnostic():
                self.conjugation_notes[tense] = ConjugationNotes(tense, None, self._phrase)
            else:
                self.conjugation_notes[tense] =\
                    [ None for person in Person.all() ]
        
        if tense in Tense.Person_Agnostic():
            conjugation_notes = self.conjugation_notes[tense] 
        elif self.conjugation_notes[tense][person] is None:
            conjugation_notes = self.conjugation_notes[tense][person] =\
                    ConjugationNotes(tense, person, self._phrase)
        else:
            conjugation_notes = self.conjugation_notes[tense][person]
        
        return conjugation_notes
    
    def __repr__(self):
        return json.dumps({'phrase' : self._phrase.full_phrase, 
                           'conjugation_notes' : self.conjugation_notes.__repr__()})