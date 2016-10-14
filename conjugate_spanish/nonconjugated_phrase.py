# -*- coding: utf-8 -*-
from .phrase import Phrase

class NonConjugatedPhrase(Phrase):
    """
    This is for phrases that have a verb used in them but are not conjugated into multiple tenses
    
    For example: 'cerca de' is related to 'acercar' but is not conjugated
    """
    def __init__(self, phrase, definition, associated_verbs=None, **kwargs):  
        super().__init__(phrase, definition, False, **kwargs)      
        if isinstance(associated_verbs, str):
            self.associated_verbs = associated_verbs.split(",")
        else:
            self.associated_verbs = associated_verbs
                    
    def sql_insert_values(self):
        return super().sql_insert_values()
    
    @classmethod
    def table_columns(cls):
        return super().table_columns()
    
    @property
    def is_derived(self):
        return self.associated_verbs is not None
    
    @property
    def derived_from(self):
        return self.associated_verbs
    
    ## HACK
    @property
    def base_verb_string(self):
        return self.associated_verbs[0]
    
    @property
    def tags(self):
        return None