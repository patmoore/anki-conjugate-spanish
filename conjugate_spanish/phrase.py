from .constants import make_unicode
import abc

class Phrase(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self, phrase_string, definition, conjugatable, **kwargs):
        # key = because full_phrase is used to generate readable string
        self.phrase_string = make_unicode(phrase_string)
        # need to preserve with the / and - so that we can go from Note objects back to Verb objects
        self.key = self.phrase_string.lower()
        self.definition = make_unicode(definition)
        self._conjugatable=conjugatable
        self._id = kwargs.get('id')
        
    @property
    def id(self):
        return self._id
#     
#     @id.setter
#     def id(self, id):
#         self._id = id
         
    @property
    def full_phrase(self):
        return self.phrase_string
    
    @abc.abstractproperty
    def derived_from(self):
        pass
    
    @abc.abstractproperty
    def is_derived(self):
        pass
    
    @property
    def is_conjugatable(self):
        return self._conjugatable
    
    @property
    def has_tags(self):
        return self.tags is not None
    
    @classmethod
    def table_columns(cls):
        return ["phrase","definition", "conjugatable"]
    
    def sql_insert_values(self):
        return [self.full_phrase, self.definition, self.is_conjugatable]
    
    
    #
    # HACK really shouldn't have the super class know about the subclasses 
    # But this is a convenient place to put this factory method until a better location makes sense.
    @classmethod
    def from_dict(cls, phrase_dict):
        from .verb import Verb
        from .nonconjugated_phrase import NonConjugatedPhrase
        conjugatable = phrase_dict.pop('conjugatable')
        if conjugatable:
            return Verb(**phrase_dict)
        else:
            return NonConjugatedPhrase(**phrase_dict)