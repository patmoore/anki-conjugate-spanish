# -*- coding: utf-8 -*-
from .constants import make_unicode
from . import six

class NonConjugatedPhrase(object):
    """
    This is for phrases that have a verb used in them but are not conjugated into multiple tenses
    
    For example: 'cerca de' is related to 'acercar' but is not conjugated
    """
    def __init__(self, phrase_string, definition, associated_verbs=None):
        self.phrase_string = make_unicode(phrase_string)
        self.definition = make_unicode(definition)
        if isinstance(associated_verbs, six.string_types):
            self.associated_verbs = associated_verbs.split(",")
        else:
            self.associated_verbs = associated_verbs
                
    @property
    def full_phrase(self):
        return self.phrase_string
    
    