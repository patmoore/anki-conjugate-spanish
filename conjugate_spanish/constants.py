# -*- coding: utf-8 -*-
import collections
from . import six
import re
import sys
import traceback

# Used as prefix to actions, models, etc.
ADDON_PREFIX = 'Español:'
def re_compile(string_):
    """
    unicode, ignore case
    """
    return re.compile(string_, re.UNICODE+re.IGNORECASE)

class BaseConsts_(list):
    @property
    def all(self):
        return list(range(len(self)))
    def all_except(self, _except):
        if not isinstance(_except, list):
            _except = [ _except ]
        return [index for index in self.all if index not in _except]
    
class Infinitive_Endings_(BaseConsts_):
    ar_verb = 0
    er_verb = 1
    ir_verb = 2
     
Infinitive_Endings = Infinitive_Endings_( [
    'ar',
    'er',
    'ir'
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

Persons = Persons_([
    'yo',
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
    if not isinstance(x, six.string_types) and isinstance(x, collections.Iterable):
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
    if isinstance(inputStr, six.string_types) and type(inputStr) != str:
        result = inputStr.decode('utf-8')
        return result
    else:
        return inputStr
    
def pick(dictionary, key, default_value):
    if dictionary is not None and key in dictionary and dictionary[key] is not None:
        return dictionary[key]
    else:
        return default_value

## for convenience with creating strings
class Vowels_(list):
    a = 'a'
    e = 'e'
    i = 'i'
    o = 'o'
    u = 'u'
    a_a = 'á'
    e_a = 'é'
    i_a = 'í'
    o_a = 'ó'
    u_a = 'ú'
    u_u = 'ü'
    a_any = a + a_a
    e_any = e + e_a
    i_any = i + i_a
    o_any = o + o_a
    u_any = u + u_a + u_u
    
    unaccented = a+e+i+o+u
    accented = a_a + e_a + i_a + o_a + u_a
    all = a_any + e_any + i_any +o_any +u_any
    any_ = [ a_any, e_any, i_any, o_any, u_any ]
    
    strong = [ a, a_a, e, e_a, o, o_a ]
    weak = [ i, i_a, u, u_a, u_u ]
    @classmethod
    def any(cls, vowel):
        for an_any in Vowels_.any_:
            if an_any.find(vowel) >= 0:
                return an_any
        return vowel
    @classmethod
    def re_any_string(cls, string_):
        regex_str = ''
        for char in string_:
            reg_chars = Vowels_.any(char)
            if len(reg_chars) == 1:
                regex_str += reg_chars
            else:
                regex_str += '['+reg_chars+']'
        return regex_str    
    dipthong_regex_pattern = '(?:(?:[iu]?h?[aeo])|(?:[aeo]h?[iu]?))'
    
    accent_rules = [
        # word ends in strong vowel, dipthong or n,s
        re_compile('^(.*?)('+dipthong_regex_pattern+')([^'+all+']*)('+dipthong_regex_pattern+'[ns]{0,2})$'),
        # word ends in weak vowel or n,s
        re_compile('^(.*?)('+dipthong_regex_pattern+')([^'+all+']*)([iu]?[ns]{0,2})$'),
        re_compile('^(.*?)('+'[iu]'+')([^'+all+']*)([ns]{0,2})$'),
    ]
    #TODO needs more work
    # need to pick out the exact vowel to accent.
    @classmethod
    def find_accented(cls, word):
        for accent_rule in Vowels_.accent_rules:
            match = accent_rule.match(word)
            if match is not None:
                break
        return match
        
    
Vowels = Vowels_([
    'a',
    'e',
    'i',
    'o',
    'u'
])
accented_vowel_check = re_compile('['+Vowels.accented+']')
def accent_at(string_, index_=None):
    """
    allow the vowel to already be accented
    """
    if index_ is None:
        index_ = len(string_)-1
    
    vowel = string_[index_]
    vindex = Vowels.unaccented.find(vowel)
    if vindex < 0:
        accented = Vowels.accented.find(vowel)
        if accented < 0:
            raise Exception(string_+" at index="+index_+" there is no vowel.")
        else:
            return string_
    
    accented = Vowels.accented[vindex]
    result = string_[:index_] + accented + string_[index_+1:]
    return result

_replace_accents = [
    [ re.compile('á'), 'a' ],
    [ re.compile('é'), 'e' ],
    [ re.compile('í'), 'i' ],
    [ re.compile('ó'), 'o' ],
    [ re.compile('ú'), 'u' ]
]    
def remove_accent(string_):       
    result = string_ 
    for regex, replace in _replace_accents:
        result = regex.sub(replace, result)
    return result

def dump_trace(e, message):
    extype, ex, tb = sys.exc_info()
    traceback.print_tb(tb)
    formatted = traceback.format_exception(extype, ex, tb)[-1]

