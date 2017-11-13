# -*- coding: utf-8 -*-
import collections
import re
import sys
import traceback
from enum import IntEnum, Enum, unique

# Used as prefix to actions, models, etc.
ADDON_PREFIX = 'EspañolConjugator'
def re_compile(string_):
    """
    unicode, ignore case
    """
    return re.compile(string_, re.IGNORECASE)

def re_group(args, not_=False):
    multiple = any([len(arg) > 1 for arg in args]) 
    if multiple:
        if not_:
            return "(?!:"+"|".join(args)+")"
        else:
            return "(?:"+"|".join(args)+")"
    else:
        if not_:
            return "[^"+"".join(args)+"]"
        else:
            return "["+"".join(args)+"]"
    
class BaseConst(IntEnum):
    def __new__(cls, code, key, human_readable):
        inst = int.__new__(cls, code)
        inst._value_ = code
        return inst
    
    def __init__(self, code, key, human_readable):
        self.code = code
        self.key = key
        self.human_readable = human_readable
        
    def __eq__(self, right):
        if isinstance(right, str):
            return self.key == right
        else:
            return self.cmp(right) == 0
    
    def __ne__(self, right):
        return not(self.__eq__(right))
        
    def __lt__(self, right):
        if isinstance(right, str):
            return self.key < right
        else:
            return self.cmp(right) < 0
        
    def __le__(self, right):
        if isinstance(right, str):
            return self.key <= right
        else:
            return self.cmp(right) <= 0
        
    def __gt__(self, right):
        if isinstance(right, str):
            return self.key > right
        else:
            return self.cmp(right) > 0
        
    def __ge__(self, right):
        if isinstance(right, str):
            return self.key >= right
        else:
            return self.cmp(right) >= 0
        
    def cmp(self, right):
        if isinstance(right, self.__class__):
            return self._value_ - right._value_
        elif isinstance(right, int) and not isinstance(right, Enum):
            # make sure we cannot compare to different Enum class accidently
            return self._value_ - right
        else:
            return NotImplemented
        
@unique
class Tense(BaseConst):
    present_tense = (0, 'present', 'Present')
    incomplete_past_tense = (1, 'incomplete_past',  'Incomplete Past')
    past_tense=(2, 'past', 'Past')
    future_tense=(3, 'future', 'Future')
    conditional_tense=(4, 'conditional', 'Conditional')
    present_subjective_tense = (5, 'present_subjective', 'Present Subjective')
    past_subjective_tense = (6, 'past_subjective', 'Past Subjective')
    imperative_positive = (7, 'imperative_positive', 'Imperative Positive')
    imperative_negative = (8, 'imperative_negative', 'Imperative Negative')
    gerund = (9, 'gerund', 'Gerund (-ed)')
    past_participle = (10, 'past_participle', 'Past Participle (-ing)')
    #usually it is same as past participle: However,
    #The boy is cursed. --> el niño está maldito. (adjective)
    #The boy has been cursed --> el niño ha sido maldecido ( one of the perfect tenses)
    adjective = (11, 'adjective', 'Adjective (usually Past Participle)' )
    
class BaseConsts_(list):
    def __init__(self, constants):
        super().__init__(constants)
#         self._human_readable = human_readable
        
    @property
    def all(self):
        return self
    
    def all_except(self, _except):
        if not isinstance(_except, list):
            _except = [ _except ]
        return [index for index in self.all if index not in _except]
    
    def human_readable(self, index):
        return self[index].human_readable
    
    def index(self, index_):
        for v in self:
            if v == index_: 
                return v
        return None

class Tenses_(BaseConsts_):
    present_tense = Tense.present_tense
    incomplete_past_tense = Tense.incomplete_past_tense
    past_tense = Tense.past_tense
    future_tense = Tense.future_tense
    conditional_tense = Tense.conditional_tense
    present_subjective_tense = Tense.present_subjective_tense
    past_subjective_tense = Tense.past_subjective_tense
    imperative_positive = Tense.imperative_positive
    imperative_negative = Tense.imperative_negative
    gerund = Tense.gerund
    past_participle = Tense.past_participle
    adjective = Tense.adjective
    Person_Agnostic = [ gerund, past_participle, adjective ]
    # these tenses conjugate for all persons ( note: imperative and Person_agnostic is missing)
    All_Persons = [ present_tense, incomplete_past_tense, past_tense, future_tense,
        conditional_tense, present_subjective_tense, past_subjective_tense]
    imperative = [ imperative_negative, imperative_positive ]
    future_cond = [ future_tense, conditional_tense]
    # Most of the time these 2 have same conjugation
    past_part_adj = [ past_participle, adjective]
    # these tenses are the ones that are most commonly needed used in normal conversation
    # note that future tense can be "cheated" with "ir a"    
    core = [ present_tense, past_tense ]
    
# names also used in manually defined override files
Tenses = Tenses_(list(Tense))

@unique
class Person(BaseConst):
    first_person_singular = (0, 'yo', 'yo')
    second_person_singular = (1, 'tú', 'tú')
    third_person_singular = (2, 'usted', 'usted')
    first_person_plural = (3, 'nosotros', 'nosotros')
    second_person_plural = (4, 'vosotros', 'vosotros')
    third_person_plural = (5, 'ustedes', 'ustedes')
    
class Persons_(BaseConsts_):
    first_person_singular = Person.first_person_singular
    second_person_singular =Person.second_person_singular
    third_person_singular = Person.third_person_singular
    first_person_plural = Person.first_person_plural
    second_person_plural = Person.second_person_plural
    third_person_plural = Person.third_person_plural
        
    Present_Tense_Stem_Changing_Persons = [first_person_singular, second_person_singular, third_person_singular, third_person_plural]
    Past_Tense_Stem_Changing_Persons = [third_person_singular, third_person_plural]
    first_person = [ first_person_singular, first_person_plural ]
    second_person = [ second_person_singular, second_person_plural ]
    third_person = [ third_person_singular, third_person_plural]    
    # arguably second person singular is not core...
    core = [ first_person_singular, first_person_plural, second_person_singular, third_person_singular, third_person_plural ]

Persons = Persons_(list(Person))

Persons_Indirect = [
    'me',
    'te',
    'se',
    'nos',
    'os',
    'se'
    ]

class IrregularNature(BaseConst):
    """
    Note: we don't track if from base or not because we want to know reason
    """
    regular = (0, 'regular', 'regular')
    """ 
    preserve the sound when spoken
    """
    sound_consistence = (1, 'sound', 'preserves sound')
    standard_irregular = (2, 'std_irregular', 'irregularity comes from a standard irregular pattern')
    custom = (3, 'custom', 'irregularity is unique to this verb')
    
    
class IrregularNatures_(BaseConsts_):
    regular = IrregularNature.regular
    sound_consistence = IrregularNature.sound_consistence
    standard_irregular = IrregularNature.standard_irregular
    custom = IrregularNature.custom

IrregularNatures = IrregularNatures_(list(IrregularNature))
#
# Parse up the infinitive string: 
# verb forms: 
#  1. verb ( has proper spanish infinitive ending )
#  2. reflexive verb ( has proper spanish infinitive ending -se)
#  3. derived verb ( prefix'-'base_verb) 
#  4. (prefix words)* (prefix_characters*)-()-se (suffix words)
#  4. (prefix words)* (verb_form_1) (suffix words)*
#  5. (prefix words)* (verb_form_2) (suffix words)* 
# group 1 = prefix words (if present)
# group 2 = prefix characters (if present)
# group 3 = core verb (note: special case of 'ir' and 'irse'
# group 4 = infinitive ending ( -ir,-er,-ar )
# group 5 = reflexive se or -se if present
# group 6 = suffix words
# use '-' to separate out the prefix from the base verb
# use '/' to force the selection of the verb in complex cases or for cases where prefix words end in -ir,-ar,-er
_phrase_parsing = re_compile('^\s*([^/]*?)[\s/]*([^/\s-]*?)-?([^/\s-]*)([iíae]r)(-?se)?[/\s]*(.*?)\s*$')
class PhraseGroup(BaseConst):
    PREFIX_WORDS = (1, 'prefix_words', None)
    PREFIX_CHARS = (2, 'prefix', None)
    CORE_VERB = (3, 'core_characters', None)
    INF_ENDING = (4, 'inf_ending', None)
    REFLEXIVE_ENDING = (5, 'reflexive', None)
    SUFFIX_WORDS = (6, 'suffix_words', None)
    
    def extract(self, phrase_match):
        return phrase_match.group(self.code)

    @classmethod
    def is_verb(cls, phrase_string):
        return _phrase_parsing.match(phrase_string)
    
@unique
class Reflexive(Enum):
    not_reflexive = 0
    reflexive = 1
    base_reflexive = 2
    @classmethod
    def get(cls, value):
        if value is None:
            return cls.non_reflexive
        else:
            return Reflexive(value)

    @classmethod
    def getFromEnding(cls, phrase_match):
        reflexive_ending = phrase_match.group(PhraseGroup.REFLEXIVE_ENDING)
        if is_empty_str(reflexive_ending):
            return cls.not_reflexive
        elif reflexive_ending == '-se':
            return cls.base_reflexive
        else:
            return cls.reflexive

def get_iterable(x):
    """
    except ... a string is iterable :-(
    http://stackoverflow.com/a/6711233/20161
    """
    if not isinstance(x, str) and isinstance(x, collections.Iterable):
        return x
    else:
        return (x,)

def make_list(list_or):
    if list_or is None:
        return []
    elif isinstance(list_or, list):
        return list_or
    else:
        return [ list_or ]
    
def make_unicode(inputStr):
    """
    :returns: original inputStr if inputStr is not a string or inputStr is already a unicode. This means None and random
    objects can be passed
    """
    if isinstance(inputStr, str) and type(inputStr) != str:
        result = inputStr.decode('utf-8')
        return result
    else:
        return inputStr
    
def pick(dictionary, key, default_value):
    if dictionary is not None and key in dictionary and dictionary[key] is not None:
        return dictionary[key]
    else:
        return default_value

def dump_trace(e, message):
    extype, ex, tb = sys.exc_info()
    traceback.print_tb(tb)
    formatted = traceback.format_exception(extype, ex, tb)[-1]

def is_empty_str(string):
    if string is None or string == "":
        return True
    elif isinstance(string, str):
        return False
    else:
        raise Exception("value is not a string")
