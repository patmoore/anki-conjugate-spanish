# -*- coding: utf-8 -*-
from constants import make_unicode

class NonConjugatedPhrase(object):
    """
    This is for phrases that have a verb used in them but are not conjugated into multiple tenses
    
    For example: 'cerca de' is related to 'acercar' but is not conjugated
    """
    def __init__(self, phrase_string, definition, associated_verbs=[]):
        self.phrase_string = make_unicode(phrase_string)
        self.definition = make_unicode(definition)
        
    @property
    def full_phrase(self):
        return self.phrase_string
    

