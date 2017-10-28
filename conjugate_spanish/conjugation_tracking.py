# -*- coding: utf-8 -*-
from .constants import *

class ConjugationNote:
    def __init__(self, operation, tense, person=None):
        """
        conjugation - the new conjugation string
        """
        self._operation = operation
        self._tense = tense
        self._person = person
    
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
    
    def change(self, conjugation):
        self.conjugation = conjugation
        
    @property
    def conjugation(self):
        return self._conjugation
    
    @conjugation.setter
    def conjugation(self, conjugation):        
        self._conjugation = conjugation
            
class ConjugationNotes(list):
    """
    collects the overrides and alterations applied.
    Some alterations also will note if they cannot be applied
    but normally would.
    """ 
    def __init__(self, tense, person=None):
        self._tense = tense
        self._person = person
    
    def checking(self, operation):
        conjugation_note = ConjugationNote(operation, self._tense, self._person)
        self.insert(0, conjugation_note)
        return conjugation_note

    def change(self, conjugation):
        self[0].conjugation(conjugation)
        
    def not_applied(self, not_applied_reason):
        self[0].not_applied(not_applied_reason)
        
    def current_conjugation(self):
        return self[0].conjugate()
    
class ConjugationTracking():
    """
    Tracks every change to a verb as it is being conjugated
    """
    def __init__(self):
        self.conjugation_notes = [ None for tense in Tenses.all ]
                
    def conjugation_note(self, tense, person = None, *, operation=None):
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
        
        return conjugation_notes.checking(operation)
        
    def current_conjugation(self, tense, person):
        return self.conjugation_notes.current_conjugation()