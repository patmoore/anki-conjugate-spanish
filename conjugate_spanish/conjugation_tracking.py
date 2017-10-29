# -*- coding: utf-8 -*-
from .constants import *
"""
This code holds the history of how the verb is conjugated
1. Shows the rules used (in order)
2. Is responsible for the final joining together of the verb 
"""

class ConjugationNote:
    """
    Intended to be immutable
    """
    def __init__(self, operation, tense, person=None):
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
            return self._core_verb + self._ending
        
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
        return self.conjugation if self.conjugation else "---"
            
class ConjugationNotes():
    """
    collects the overrides and alterations applied.
    Some alterations also will note if they cannot be applied
    but normally would.
    """ 
    def __init__(self, tense, person=None):
        self._tense = tense
        self._person = person
        self._conjugation_note_list = [ ConjugationNote(self, self._tense, self._person) ]
        
    def _new_conjugation_note(self):
        conjugation_note = ConjugationNote(self._tense, self._person)
        self._conjugation_note_list.insert(0, conjugation_note)
        return conjugation_note
    
    @property
    def core_verb(self):
        for conjugation_note in self._conjugation_note_list:
            if conjugation_note.core_verb is not None:
                return conjugation_note.core_verb
        return None
    
    @core_verb.setter
    def core_verb(self, core_verb):
        self._new_conjugation_note().core_verb = core_verb
        
    @property
    def ending(self):
        for conjugation_note in self._conjugation_note_list:
            if conjugation_note.ending is not None:
                return conjugation_note.ending
        return None
    
    @ending.setter
    def ending(self, ending):
        self._new_conjugation_note().ending = ending
    
    def change(self, *, conjugation=None, core_verb=None, ending=None):
        """
        Some tenses depend on other tenses / person
        """
        conjugation_note = self._new_conjugation_note()
        if conjugation is not None:
            conjugation_note.conjugation = conjugation
        else:
            conjugation_note.core_verb = core_verb
            conjugation_note.ending = ending
        
    def clear(self):
        """
        Way to make this tense person and not having a value 
        TODO ?
        """
        pass
    
    @property
    def conjugation(self):
        for conjugation_note in self._conjugation_note_list:
            if conjugation_note.conjugation is not None:
                return conjugation_note.conjugation
        return None
      
    @conjugation.setter
    def conjugation(self, conjugation):
        self._new_conjugation_note().conjugation = conjugation
        
    @property
    def tense(self):
        return self._tense
    
    @property
    def person(self):
        return self._person  
    
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
                self.conjugation_notes[tense] = ConjugationNotes(tense)
            else:
                self.conjugation_notes[tense] =\
                    [ None for person in Persons.all ]
        
        if tense in Tenses.Person_Agnostic:
            conjugation_notes = self.conjugation_notes[tense] 
        elif self.conjugation_notes[tense][person] is None:
            conjugation_notes = self.conjugation_notes[tense][person] =\
                    ConjugationNotes(tense, person)
        else:
            conjugation_notes = self.conjugation_notes[tense][person]
        
        return conjugation_notes