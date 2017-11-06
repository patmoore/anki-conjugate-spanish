# -*- coding: utf-8 -*-
from .constants import *
import json
from .utils import cs_debug
"""
This code holds the history of how the verb is conjugated
1. Shows the rules used (in order)
2. Is responsible for the final joining together of the verb 
"""
from conjugate_spanish.standard_endings import Infinitive_Endings

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
        self._conjugation = None
    
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
        if self._conjugation is not None:
            return self._conjugation 
        elif self._core_verb is None and self._ending is None:
            return ""
        elif self._core_verb is None:
            return "-" + self._ending
        else:
            return ""
        
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
                  
    def __repr__(self):
        return {
                'operation' : self.operation,
                'conjugation' : self.conjugation,
                'core_verb' : self.core_verb,
                'ending' : self.ending
                }
            
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
        infinitive_ending = Infinitive_Endings.index(phrase.verb_ending_index)
        inf_conjugation_note = self._new_conjugation_note("infinitive")
        inf_conjugation_note.core_verb = phrase.stem
        # TODO replace with infinitive_ending.code?
        inf_conjugation_note.ending = phrase.inf_ending
        std_ending = infinitive_ending.get_standard_conjugation_ending(self, phrase.verb_ending_index)
        if std_ending is not None:
            std_conjugation_note = self._new_conjugation_note("std_ending")
            std_conjugation_note.ending = std_ending 
        
    def _new_conjugation_note(self, operation):
        if self.completed:
            self.__raise("Already completed")
        conjugation_note = ConjugationNote(operation, self._tense, self._person)
        self._conjugation_note_list.insert(0, conjugation_note)
        return conjugation_note
        
    @property
    def operation(self):
        return self._operation;
    
    @operation.setter
    def operation(self, operation):
        self._operation = operation
        
    @property
    def core_verb(self):
        if not self.blocked:
            for conjugation_note in self._conjugation_note_list:
                if conjugation_note.core_verb is not None:
                    return conjugation_note.core_verb
        return None
    
    @core_verb.setter
    def core_verb(self, core_verb):
        if self.blocked:
            self.__raise("blocked")
        elif not isinstance(core_verb, str):
            self.__raise("stem is not string")
        elif self.core_verb != core_verb:
            self._new_conjugation_note(self.operation).core_verb = core_verb
        
    @property
    def ending(self):
        if not self.blocked:
            for conjugation_note in self._conjugation_note_list:
                if conjugation_note.ending is not None:
                    return conjugation_note.ending
        return None
    
    @ending.setter
    def ending(self, ending):
        if self.blocked:
            self.__raise("blocked")
        elif not isinstance(ending, str):
            self.__raise("stem is not string", self.tense, self.person)
        elif self.ending != ending:
            self._new_conjugation_note(self.operation).ending = ending
    
    def change(self, operation, *, conjugation=None, core_verb=None, ending=None):
        """
        Some tenses depend on other tenses / person
        """
        if self.blocked:
            self.__raise("blocked")
        elif conjugation is None and core_verb is None and ending is None:
            self.__raise(operation + " supplied only None arguments - probable error")
        else:
            conjugation_note = self._new_conjugation_note(operation)
            conjugation_note.operation = operation
            if conjugation is not None:
                conjugation_note.conjugation = conjugation
            else:
                if core_verb is not None:
                    conjugation_note.core_verb = core_verb
                if ending is not None:
                    conjugation_note.ending = ending
    
    @property
    def conjugation(self):
        if not self.blocked:
            for conjugation_note in self._conjugation_note_list:
                if conjugation_note.conjugation is not None:
                    return conjugation_note.conjugation
        return None
      
    @conjugation.setter
    def conjugation(self, conjugation):
        self._new_conjugation_note(self._operation).conjugation = conjugation
        
    @property
    def tense(self):
        return self._tense
    
    @property
    def person(self):
        return self._person  
    
    @property
    def phrase(self):
        return self._phrase
    
    def block(self):
        """
        Used to indicate a conjugation does not exist.
        For example, first person singular imperative
        or 3rd person only verbs
        """
        self._blocked = True
        self._new_conjugation_note("blocked")
        
    @property
    def blocked(self):
        return self._blocked
    
    @property
    def completed(self):
        return self._completed
    
    def complete(self):
        self._completed = True
        
    def __raise(self, msg, traceback_=None):
        msg_ = "{0}: (tense={1},person={2}): {3}".format(self.phrase.full_phrase, 
             Tenses[self.tense] if self.tense is not None else "-", 
             Persons[self.person] if self.person is not None else "-", msg)
        cs_debug(">>>>>>",msg_)
        
    def __repr__(self):
        return { 
            'tense' : self.tense,
            'person' : self.person,
            'changes' : [ conjugation_note.__repr__() for conjugation_note in self._conjugation_note_list ]
        }.__str__()
    
class ConjugationTracking():
    """
    Tracks every change to a verb /phrase as it is being conjugated
    Owned by a phrase / verb
    """
    def __init__(self, phrase):
        self.conjugation_notes = [ None for tense in Tenses.all ]
        self._phrase = phrase
                
    def get_conjugation_notes(self, tense, person = None):
        if self.conjugation_notes[tense] is None:
            if tense in Tenses.Person_Agnostic:
                self.conjugation_notes[tense] = ConjugationNotes(tense, None, self._phrase)
            else:
                self.conjugation_notes[tense] =\
                    [ None for person in Persons.all ]
        
        if tense in Tenses.Person_Agnostic:
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