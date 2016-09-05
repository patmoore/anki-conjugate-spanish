# -*- coding: utf-8 -*-
from .constants import make_unicode

class NonConjugatedPhrase(object):
    """
    This is for phrases that have a verb used in them but are not conjugated into multiple tenses
    
    For example: 'cerca de' is related to 'acercar' but is not conjugated
    """
    def __init__(self, phrase_string, definition, associated_verbs=None):        
        self.phrase_string = make_unicode(phrase_string)
        self.definition = make_unicode(definition)
        if isinstance(associated_verbs, str):
            self.associated_verbs = associated_verbs.split(",")
        else:
            self.associated_verbs = associated_verbs
                
    @property
    def full_phrase(self):
        return self.phrase_string
    
    def sql_insert_values(self):
        return [self.full_phrase, self.definition]
    
    @classmethod
    def table_columns(cls):
        return ["phrase","definition"]
    
    @classmethod
    def table_name(cls):
        return "cs_nonconjugated_phrase"
    
    def make_note(self):
        from aqt import mw
#         from anki.notes import Note 
#         from aqt.qt import debug; 
#         debug()
#         note = Note(mw.col)
#         note.flush()