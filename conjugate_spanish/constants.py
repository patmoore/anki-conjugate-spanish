# -*- coding: utf-8 -*-
import collections
import six
import re

class Infinitive_Endings_(list):
    ar_verb = 0
    er_verb = 1
    ir_verb = 2
     
Infinitive_Endings = Infinitive_Endings_( [
    u'ar',
    u'er',
    u'ir'
])

class Tenses_(list):
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
    Person_Agnostic = [ gerund, past_participle ]
    imperative = [ imperative_negative, imperative_positive ]

    @property
    def all(self):
        return range(len(self))
    def all_except(self, _except):
        if not isinstance(_except, list):
            _except = [ _except ]
        return [index for index in self.all if index not in _except]
    
# names also used in manually defined override files
Tenses = Tenses_([
    u'present',
    u'incomplete past',
    u'past',
    u'future',
    u'conditional',
    u'present subjective',
    u'past subjective',
    u'imperative positive',
    u'imperative negative',
    u'gerund',
    u'past participle'
])

class Persons_(list):
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
    @property
    def all(self):
        return range(len(self))
    def all_except(self, _except):
        if not isinstance(_except, list):
            _except = [ _except ]
        return [index for index in self.all if index not in _except]

Persons = Persons_([
    u'yo',
    u'tú',
    u'usted',
    u'nosotros',
    u'vosotros',
    u'ustedes'
])

Persons_Indirect = [
    u'me',
    u'te',
    u'se',
    u'nos',
    u'os',
    u'se'
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
    if inputStr is None:
        return None
    elif type(inputStr) != unicode:
        inputStr = inputStr.decode('utf-8')
        return inputStr
    else:
        return inputStr
    
## for convenience with creating strings
Vowels = u'aeiou'
AccentedVowels = u'áéíóú'
AllVowels = Vowels+AccentedVowels
CombiningAccent = u'\u0301'
def accent_at(string_, index_=None):
    if index_ is None:
        index_ = len(string_)-1
    
    vowel = string_[index_]
    vindex = Vowels.find(vowel)
    if vindex < 0:
        accented = AccentedVowels.find(vowel)
        if accented < 0:
            raise Exception(string_+" at index="+index_+" there is no vowel.")
        else:
            return string_
    
    accented = AccentedVowels[vindex]
    result = string_[:index_] + accented + string_[index_+1:]
    return result

_replace_accents = [
    [ re.compile(u'á'), u'a' ],
    [ re.compile(u'é'), u'e' ],
    [ re.compile(u'í'), u'i' ],
    [ re.compile(u'ó'), u'o' ],
    [ re.compile(u'ú'), u'u' ]
]    
def remove_accent(string_):       
    result = string_ 
    for regex, replace in _replace_accents:
        result = regex.sub(replace, result)
    return result