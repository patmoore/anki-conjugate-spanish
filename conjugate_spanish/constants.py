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

## for convenience with creating strings
class Vowels_():
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
    y = 'y'
    # umplauted u
    qu = 'qu'
    # umplauted u
    gu = 'gu'
    h = 'h'
    
    unaccented = a+e+i+o+u
    accented = a_a + e_a + i_a + o_a + u_a
    all = a_any + e_any + i_any +o_any +u_any
    any_ = [ a_any, e_any, i_any, o_any, u_any ]
    
    strong = [ a, a_a, e, e_a, o, o_a ]
    weak = [ i, i_a, u, u_a, u_u ]
    # http://www.123teachme.com/learn_spanish/diphthongs_and_triphthongs
    # TODO - need to verify accent rules!
    accent_mapping = {
        e+h+u: e_a+h+u,
        u+a+y : u+a_a+y,
        u+e+y : u+e_a+y,
        u+a+u : u+a_a+u,
        u+a+i: u+a_a+i,
        i+a+i: i+a_a+i,
        i+e+i: i+e_a+i,
        a+i : a_a + i,
        a+y : a_a + y, 
        e+i : e_a + i,
        e+y : e_a + y,
        o+i : o_a + i,
        o+y : o_a + y,
        u+i : u_a + i,
        u+y : u_a + y,
        a+u : a_a + u,
        e+u : e_a + u,
        i+a : i + a_a,
        i+e : i + e_a,
        i+o : i + o_a,
        i+a : i_a + u,
        u+a : u + a_a,
        u+e : u + a_a,
        u+o : u + a_a,    
        a: a_a,
        e: e_a,
        i: i_a,
        o: o_a,
        u: u_a,            
    }
    # used to preserve order.
    # non-accented because we check first for accented
    vowel_combinations = [
            e+h+u,
            u+a+y,
            u+e+y,
            u+a+u,
            # uái
            u+a+i,
            # guiáis
            i+a+i,
            # estudiéis
            i+e+i,
            a+i,
            a+y, 
            e+i,
            e+y,
            o+i,
            o+y,
            u+i,
            u+y,
            a+u,
            e+u,
            i+a,
            i+e,
            i+o,
            i+a,
            u+a,
            u+e,
            u+o
        ]    
    
    def __init__(self):
        # note: order is important here
        self.accent_rules = []
        weak_beginning = '^(.*?)'
        consonants = '([^'+self.all+']*)'
        vowel_groups = "(?:"+"|".join(self.vowel_combinations)+")"
        unaccented_group = "(["+self.unaccented+"])"
        # possible combinations are broken up to avoid having to be super exact on the regex rules ( also makes much more readable)
        # in onle case we want to match on the dipthongs / triphongs first before single vowels.
        """
        Accent a vowel explicitly UNLESS there is an accent already
        The rules on accenting in spanish is the last vowel if the word ends in a consonent other than n or s
        Otherwise the second to last vowel.
        If the vowel to be accented is a strong-weak (au,ai,ei,... ) or a weak-strong pair (ua,ia, ... ) the strong vowel of the pair gets the accent
        TODO: NOTE: an h between 2 vowels does not break the diphthong
        https://en.wikipedia.org/wiki/Spanish_irregular_verbs
        Remember that the presence of a silent h does not break a diphthong, so a written accent is needed anyway in rehúso.
        http://www.123teachme.com/learn_spanish/diphthongs_and_triphthongs
        I don't feel i understand the rules correctly.
        """
        self.accent_rules = [
            re_compile(weak_beginning+"("+vowel_groups+")"+consonants+"("+vowel_groups+'[ns]{0,2})$'),
            re_compile(weak_beginning+unaccented_group+consonants+"("+vowel_groups+'[ns]{0,2})$'),
            
            re_compile(weak_beginning+"("+vowel_groups+")"+consonants+"(["+self.unaccented+'][ns]{0,2})$'),
            re_compile(weak_beginning+unaccented_group+consonants+"(["+self.unaccented+'][ns]{0,2})$'),
            
            re_compile(weak_beginning+"("+vowel_groups+")"+consonants+"()$"),
            re_compile(weak_beginning+unaccented_group+consonants+"()$"),
            
            re_compile(weak_beginning+"("+vowel_groups+")"+"()()$"),
            re_compile(weak_beginning+unaccented_group+consonants+"()$")
        ]
        
    def any(self, vowel):
        for an_any in self.any_:
            if an_any.find(vowel) >= 0:
                return an_any
        return vowel
    
    def re_any_string(self, string_):
        regex_str = ''
        for char in string_:
            reg_chars = self.any(char)
            if len(reg_chars) == 1:
                regex_str += reg_chars
            else:
                regex_str += '['+reg_chars+']'
        return regex_str    
#     dipthong_regex_pattern = '(?:(?:[iu]?h?[aeo])|(?:[aeo]h?[iu]?))'
    
#     accent_rules = [
#         # word ends in strong vowel, dipthong or n,s
#         re_compile('^(.*?)('+dipthong_regex_pattern+')([^'+all+']*)('+dipthong_regex_pattern+'[ns]{0,2})$'),
#         # word ends in weak vowel or n,s
#         re_compile('^(.*?)('+dipthong_regex_pattern+')([^'+all+']*)([iu]?[ns]{0,2})$'),
#         re_compile('^(.*?)('+'[iu]'+')([^'+all+']*)([ns]{0,2})$'),
#     ]
    #TODO needs more work
    # need to pick out the exact vowel to accent.
    def find_accented(self, word):
        for accent_rule in self.accent_rules:
            match = accent_rule.match(word)
            if match is not None:
                break
        return match
        
    def accent(self, word):
        match = self.find_accented(word)
        if match:
            print(match.groups())
            accented = self.accent_mapping[match.group(2)]
            result = match.group(1)+accented+match.group(3)+match.group(4)
            print("word="+word+";accent-->"+result)
            return result
        else:
            return word
    
Vowels = Vowels_()
if True:
    for word in ['repite', 'se', 'cambia', 'irgue']:
        answer = Vowels.accent(word)
    
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