from .constants import make_unicode

class Phrase(object):
    def __init__(self, phrase_string, definition, conjugatable=True):
        self.phrase_string = make_unicode(phrase_string)
        self.definition = make_unicode(definition)
        self.conjugatable=conjugatable
        
    @property
    def full_phrase(self):
        return self.phrase_string
    
    @classmethod
    def table_columns(cls):
        return ["phrase","definition", "conjugatable"]
    
    def sql_insert_values(self):
        return [self.full_phrase, self.definition, self.conjugatable]