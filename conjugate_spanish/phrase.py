from .constants import make_unicode
import abc

class Phrase(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, phrase_string, definition, conjugatable=True, **kwargs):
        self.phrase_string = make_unicode(phrase_string)
        self.definition = make_unicode(definition)
        self.conjugatable=conjugatable
        self.id = kwargs.get('id')
        
    @property
    def id(self):
        return self.id_
    
    @id.setter
    def id(self, id):
        self.id_ = id
         
    @property
    def full_phrase(self):
        return self.phrase_string
    
    @abc.abstractproperty
    def derived_from(self):
        pass
    
    @abc.abstractproperty
    def is_derived(self):
        pass
    
    @classmethod
    def table_columns(cls):
        return ["phrase","definition", "conjugatable"]
    
    def sql_insert_values(self):
        return [self.full_phrase, self.definition, self.conjugatable]
    
    
    #
    # HACK really shouldn't have the super class know about the subclasses 
    # But this is a convenient place to put this factory method until a better location makes sense.
    @classmethod
    def from_dict(cls, phrase_dict):
        from .verb import Verb
        from .nonconjugated_phrase import NonConjugatedPhrase
        if phrase_dict['conjugatable']:
            return Verb(**phrase_dict)
        else:
            return NonConjugatedPhrase(**phrase_dict)