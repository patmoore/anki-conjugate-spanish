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
    def __new__(cls, code:int, key: list, human_readable: str, *subclass_args):
        """
        :param **kwargs:
        :param key: unique string - used to store this in the database
        and for look up by value

        Nothing complicated should happen here. Use __init__ for more extensive setup
        """
        # for a string enum:
        # inst = str.__new__(cls, key)
        # inst._value_ = key

        # for the old IntEnum
        inst = int.__new__(cls, code)
        inst._value_ = code
        return inst

    def __init__(self, code, keys: list, human_readable: str):
        """
        :param key: unique string - used to store this in the database
        :param human_readable: for display
        """
        super().__init__()
        self.key = keys[0]
        self.keys = keys
        self.human_readable = human_readable

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, right):
        if isinstance(right, str):
            return self.key == right
        else:
            return self.cmp(right) == 0

    def __ne__(self, right):
        return not (self.__eq__(right))

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

    # new str enum value
    # def cmp(self, right):
    #     if isinstance(right, self.__class__):
    #         return self.__class__._member_names_.index(self) - self.__class__._member_names_.index(right)
    #     else:
    #         return NotImplemented

    def cmp(self, right):
        if isinstance(right, self.__class__):
            return self._value_ - right._value_
        elif isinstance(right, int) and not isinstance(right, Enum):
            # make sure we cannot compare to different Enum class accidently
            return self._value_ - right
        else:
            return NotImplemented

    @classmethod
    def all(cls):
        return list(cls)

    @classmethod
    def all_except(cls, _except):
        if not isinstance(_except, list):
            _except = [_except]
        return [e for e in cls.all() if e not in _except]

    @classmethod
    def keys(cls) -> list:
        """
        Used to get all the keys for example to construct a Enum
        :return: list(str)
        """
        return [v.key for v in cls.all()]

    @classmethod
    def index(cls, stringName):
        for name, item in cls.__members__.items():
            if stringName in item.keys:
                return item
        else:
            return None

    def __str__(self):
        return self.human_readable

    def __repr__(self):
        return self.key

    @property
    def short_key(self):
        return self.keys[1] if len(self.keys) > 1 else self.keys[0]

@unique
class Tense(BaseConst):
    present_tense = (0, ['present', 'pres'], 'Present')
    incomplete_past_tense = (1, ['incomplete_past', 'ipres'],  'Incomplete Past')
    past_tense=(2, ['past'], 'Past')
    future_tense=(3, ['future'], 'Future')
    conditional_tense=(4, ['conditional', 'cond'], 'Conditional')
    present_subjective_tense = (5, ['present_subjective', 'spres'], 'Present Subjective')
    past_subjective_tense = (6, ['past_subjective', 'spast'], 'Past Subjective')
    imperative_positive = (7, ['imperative_positive', 'ipos'], 'Imperative Positive')
    imperative_negative = (8, ['imperative_negative', 'ineg'], 'Imperative Negative')
    gerund = (9, ['gerund', 'ed'], 'Gerund (-ed)')
    past_participle = (10, ['past_participle', 'pp', 'ing'], 'Past Participle (-ing)')
    #usually it is same as past participle: However,
    #The boy is cursed. --> el niño está maldito. (adjective)
    #The boy has been cursed --> el niño ha sido maldecido ( one of the perfect tenses)
    adjective = (11, ['adjective', 'adj'], 'Adjective (usually Past Participle)' )

    @classmethod
    def Person_Agnostic(cls):
        return [ Tense.gerund, Tense.past_participle, Tense.adjective ]
    # these tenses conjugate for all persons ( note: imperative and Person_agnostic is missing)
    @classmethod
    def All_Persons(cls):
        return [ Tense.present_tense, Tense.incomplete_past_tense, Tense.past_tense, Tense.future_tense, \
                 Tense.conditional_tense, Tense.present_subjective_tense, Tense.past_subjective_tense]

    @classmethod
    def imperative(cls):
        return [ Tense.imperative_negative, Tense.imperative_positive ]

    @classmethod
    def future_cond(cls):
        return [ Tense.future_tense, Tense.conditional_tense]
    # Most of the time these 2 have same conjugation
#     past_part_adj = [ past_participle, adjective]
    # these tenses are the ones that are most commonly needed used in normal conversation
    # note that future tense can be "cheated" with "ir a"    
    @classmethod
    def core(cls):
        return [ Tense.present_tense, Tense.past_tense ]

@unique
class Person(BaseConst):
    first_person_singular = (0, ['yo', '1s'], 'yo', 'me' )
    second_person_singular = (1, ['tú', '2s', 'tu'], 'tú', 'te')
    third_person_singular = (2, ['usted', '3s'], 'usted', 'se')
    first_person_plural = (3, ['nosotros', '1p'], 'nosotros', 'nos')
    second_person_plural = (4, ['vosotros', '2p'], 'vosotros', 'os')
    third_person_plural = (5, ['ustedes', '3p'], 'ustedes', 'se')

    def __init__(self, code:int, keys: list, human_readable: str, indirect_pronoun: str):
        super().__init__(code, keys, human_readable)
        self.indirect_pronoun = indirect_pronoun

    @classmethod
    def Present_Tense_Stem_Changing_Persons(cls):
        return [Person.first_person_singular, Person.second_person_singular, Person.third_person_singular, Person.third_person_plural]

    @classmethod
    def Past_Tense_Stem_Changing_Persons(cls):
        return [Person.third_person_singular, Person.third_person_plural]

    @classmethod
    def first_person(cls):
        return [ Person.first_person_singular, Person.first_person_plural ]

    @classmethod
    def second_person(cls):
        return [ Person.second_person_singular, Person.second_person_plural ]

    @classmethod
    def third_person(cls):
        return [ Person.third_person_singular, Person.third_person_plural]
    # arguably second person singular is not core...
    @classmethod
    def core(cls):
        return [ Person.first_person_singular, Person.first_person_plural, Person.second_person_singular, Person.third_person_singular, Person.third_person_plural ]

class IrregularNature(BaseConst):
    """
    Note: we don't track if from base or not because we want to know reason
    """
    regular = (0, ['regular'], 'regular')
    """ 
    preserve the sound when spoken
    """
    sound_consistence = (1, ['sound', 's'], 'preserves sound (c->qu)')
    radical_stem_change =(2, ['radical','r'], "Radical Stem Change (e.g: i:ie, o:ue, e:i)")
    standard_irregular = (3, ['std_irregular', 'std'], 'irregularity comes from a standard irregular pattern')
    rare= (4, ['rare'], 'irregularity is not unique but only occurs in a few verbs')
    custom = (5, ['custom'], 'irregularity is unique to this verb')
    blocked = (6, ['blocked'], 'no conjugation')

#
# Parse up the infinitive string: 
__trim_ws='\s*'
# verb forms: 
#  1. verb ( has proper spanish infinitive ending )
#  2. reflexive verb ( has proper spanish infinitive ending -se)
#  3. derived verb ( prefix'-'base_verb) 
#  4. (prefix words)* (prefix_characters*)-()-se (suffix words)
#  4. (prefix words)* (verb_form_1) (suffix words)*
#  5. (prefix words)* (verb_form_2) (suffix words)* 
# group 1 = prefix words (if present)
__prefix_words='([^-/]*?)'
# group 2 = prefix characters (if present)
# group 3 = core verb (note: special case of 'ir' and 'irse'
# group 4 = infinitive ending ( -ir,-er,-ar )
# group 5 = reflexive se or -se if present
# group 6 = suffix words
# use '-' to separate out the prefix from the base verb
# use '/' to force the selection of the verb in complex cases or for cases where prefix words end in -ir,-ar,-er

_phrase_parsing = re_compile('^'+__trim_ws+__prefix_words+__trim_ws+'/?([^/\s-]*?)-?([^/\s-]*)([iíae]r)(-?se)?/?'+__trim_ws+'([^-/]*?)'+__trim_ws+'$')
class PhraseMatch:
    def __init__(self, phrase_match):
        self._phrase_match = phrase_match
        self._reflexive = Reflexive.getFromEnding(phrase_match)
        
    @property
    def reflexive(self):
        return self._reflexive
    
# NOTE: the index are used into a regex match so MUST start at 1
class PhraseGroup(BaseConst):
    PREFIX_WORDS = (1, ['prefix_words'], None)
    PREFIX_CHARS = (2, ['prefix'], None)
    CORE_VERB = (3, ['core_characters'], None)
    INF_ENDING = (4, ['inf_ending'], None)
    REFLEXIVE_ENDING = (5, ['reflexive'], None)
    SUFFIX_WORDS = (6, ['suffix_words'], None)
    
    def extract(self, phrase_match):
        return phrase_match.group(self._value_)

    @classmethod
    def is_verb(cls, phrase_string):
        matched = _phrase_parsing.match(phrase_string)
        return matched
    
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
