# -*- coding: utf-8 -*-
from .phrase import Phrase

class NonConjugatedPhrase(Phrase):
    """
    This is for phrases that have a verb used in them but are not conjugated into multiple tenses
    
    For example: 'cerca de' is related to 'acercar' but is not conjugated
    """
    def __init__(self, phrase_string, definition, associated_verbs=None):  
        super().__init__(phrase_string, definition, False)      
        if isinstance(associated_verbs, str):
            self.associated_verbs = associated_verbs.split(",")
        else:
            self.associated_verbs = associated_verbs
                
    
    def sql_insert_values(self):
        return super().sql_insert_values()
    
    @classmethod
    def table_columns(cls):
        return super().table_columns()
    
    def make_note(self):
        from aqt import mw
#         from anki.notes import Note 
#         from aqt.qt import debug; 
#         debug()
#         note = Note(mw.col)
#         note.flush()