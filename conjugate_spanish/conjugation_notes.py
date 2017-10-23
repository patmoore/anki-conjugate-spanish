# -*- coding: utf-8 -*-

class ConjugationNote:
    def __init__(self, operation):
        self._operation = operation
    
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
            
class ConjugationNotes(list):
    """
    collects the overrides and alterations applied.
    Some alterations also will note if they cannot be applied
    but normally would.
    """ 
    def __init__(self):
        pass
    
    def checking(self, operation, tense, person=None):
        conjugation_note = ConjugationNote(operation, tense, person)
        self.append(conjugation_note)
        return conjugation_note
        