# -*- coding: utf-8 -*-
import collections
import re
import sys
import traceback

# Used as prefix to actions, models, etc.
ADDON_PREFIX = 'EspañolConjugator'
def re_compile(string_):
    """
    unicode, ignore case
    """
    return re.compile(string_, re.UNICODE+re.IGNORECASE)

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


class BaseConsts_(list):
    def __init__(self, constants, human_readable):
        super().__init__(constants)
        self._human_readable = human_readable
        
    @property
    def all(self):
        return list(range(len(self)))
    def all_except(self, _except):
        if not isinstance(_except, list):
            _except = [ _except ]
        return [index for index in self.all if index not in _except]
    
    def human_readable(self, index):
        return self._human_readable[index]
    
class Infinitive_Endings_(BaseConsts_):
    ar_verb = 0
    er_verb = 1
    ir_verb = 2
     
Infinitive_Endings = Infinitive_Endings_( [
    'ar',
    'er',
    'ir'
],[
    '-ar',
    '-er',
    '-ir'
])

class Tenses_(BaseConsts_):
    present_tense = 0
    incomplete_past_tense = 1
    past_tense = 2
    future_tense = 3
    conditional_tense = 4
    present_subjective_tense = 5
    past_subjective_tense = 6
    imperative_positive = 7
    imperative_negative = 8
    gerund = 9
    past_participle = 10
    adjective = 11
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
Tenses = Tenses_([
    'present',
    'incomplete_past',
    'past',
    'future',
    'conditional',
    'present_subjective',
    'past_subjective',
    'imperative_positive',
    'imperative_negative',
    'gerund',
    'past_participle',
    #usually it is same as past participle: However,
    #The boy is cursed. --> el niño está maldito. (adjective)
    #The boy has been cursed --> el niño ha sido maldecido ( one of the perfect tenses)
    'adjective'
],[
    'Present',
    'Incomplete Past',
    'Past',
    'Future',
    'Conditional',
    'Present Subjective',
    'Past Subjective',
    'Imperative Positive',
    'Imperative Negative',
    'Gerund (-ed)',
    'Past Participle (-ing)',
    'Adjective (usually Past Participle)'
])

class Persons_(BaseConsts_):
    first_person_singular = 0
    second_person_singular = 1
    third_person_singular = 2
    first_person_plural = 3
    second_person_plural = 4
    third_person_plural = 5
        
    Present_Tense_Stem_Changing_Persons = [first_person_singular, second_person_singular, third_person_singular, third_person_plural]
    Past_Tense_Stem_Changing_Persons = [third_person_singular, third_person_plural]
    first_person = [ first_person_singular, first_person_plural ]
    second_person = [ second_person_singular, second_person_plural ]
    third_person = [ third_person_singular, third_person_plural]    
    # arguably second person singular is not core...
    core = [ first_person_singular, first_person_plural, second_person_singular, third_person_singular, third_person_plural ]

Persons = Persons_([
    'yo',
    'tú',
    'usted',
    'nosotros',
    'vosotros',
    'ustedes'
],['yo',
    'tú',
    'usted',
    'nosotros',
    'vosotros',
    'ustedes'
])

Persons_Indirect = [
    'me',
    'te',
    'se',
    'nos',
    'os',
    'se'
    ]


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
#####
# some standard methods to help document the cryptic keys used by anki
# Not elegant or 'good' practice but this isolates the anki constants. 
#####
def deck_id(dict_, value=None):    
    if value == None:
        return dict_.get('did', None)
    else:
        dict_['did'] = value
        
def model_id(dict_, value=None):
    if value == None:
        return dict_.get('mid', None)
    else:
        dict_['mid'] = value
        
def model_fields(dict_, value=None):
    if value == None:
        return dict_.get('flds',None)
    else:
        dict_['flds'] = value