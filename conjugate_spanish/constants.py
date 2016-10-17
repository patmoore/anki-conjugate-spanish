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

class Vowels_():
    """
    Long form creation allows developers to easily see if all needed vowel combinations are handled.
    Fancy programatic creation could result in a bug of missing some vowel combination.
    """
     
    
    """
    Long form creation allows developers to easily see if all needed vowel combinations are handled.
    Fancy programatic creation could result in a bug of missing some vowel combination.
    """
    
    # TODO - need to verify accent rules!
    
    # used to preserve order.
    # non-accented because we check first for accented
    
    def __init__(self):        
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
        a_any = [a, a_a]
        e_any = [e, e_a]
        i_any = [i, i_a]
        o_any = [o, o_a]
        u_any = [u, u_a, u_u]
        y = 'y'
        qu_gu = "(?:[gq]["+u+u_u+"])"
        h = 'h'
        self.unaccented = unaccented = [a,e,i,o,u]
        self.accented = accented = [a_a, e_a, i_a, o_a, u_a]
        self.accented_vowel_check = re_compile(re_group(accented))
        self._replace_accents = [ [re_compile(accented[i]), unaccented[i] ] for i in range(4)]
        self.all = all = [ *a_any, *e_any, *i_any, *o_any, *u_any ]
        self._any =  [ "".join(a_any), "".join(e_any), "".join(i_any), "".join(o_any), "".join(u_any) ]
        self.all_group = all_group = re_group(self.all)
        self.consonants = consonants = re_group(self.all, True)
        
        strong = [ a, a_a, e, e_a, o, o_a ]
        weak = [ i, i_a, u, u_a ]
        self.to_accent_mapping = to_accent_mapping = { a: a_a,
                              e: e_a,
                              i: i_a,
                              o: o_a,
                              u: u_a }
        # combinations with 'h' in the middle - his silent does not break up dipthongs
        # # http://www.123teachme.com/learn_spanish/diphthongs_and_triphthongs
        # note: ou is not a valid dipthong
        for strong_vowel in [ a, e, o ]:
            strong_accent = to_accent_mapping[strong_vowel]
            for weak_vowel in [i, u]:
                for h_ in [h,'']:
                    to_accent_mapping[weak_vowel+h_+strong_vowel] = weak_vowel+h_+strong_accent
                    if not(strong_vowel == o and weak_vowel == u):
                        # note: ou is not a valid dipthong but uho /uo is...
                        to_accent_mapping[strong_vowel+h_+weak_vowel] = strong_accent+h_+weak_vowel
                
            # y does not have a reversed case.
            # ay, ey, oy
            to_accent_mapping[strong_vowel+y] = strong_accent+y
            
        # >>>>> Note: qu and gu are treated special!
        to_accent_mapping[u+i] = u+i_a
        to_accent_mapping[u+y] = u+i_a
        self.from_accent_mapping = { value: key for key, value in to_accent_mapping.items()}
        
        strong_group=re_group(strong)
        weak_group = re_group([i,u])    #  a trip-/dip- thong is accented only on the strong vowels 
        three_letter_combinations = []
        two_letter_combinations = []
        three_letter_combinations.append(re_group([*a_any,*e_any])+h+weak_group)
        three_letter_combinations.append(re_group(o_any)+h+i)
        two_letter_combinations.append(re_group([*a_any,*e_any])+weak_group)
        two_letter_combinations.append(re_group(o_any)+i)
        
        three_letter_combinations.append(weak_group+h+strong_group)
        two_letter_combinations.append(weak_group+strong_group)
        
        for unaccented_, accented_ in [[u+a+y, u+a_a+y],
                                     [u+e+y, u+e_a+y],
                                     [u+a+u, u+a_a+u],
                                     [u+a+i, u+a_a+i],
                                     [i+a+i, i+a_a+i],
                                     [i+e+i, i+e_a+i]]:
            to_accent_mapping[unaccented_] = accented_
    
        
        three_letter_combinations.extend([u+re_group([*a_any,*e_any])+y,
                                          # situáis 
                                          u+re_group(a_any)+re_group([u,i]),
                                          # guiáis, estudiéis
                                          i+re_group([*a_any,*e_any])+i])
        
        two_letter_combinations.extend([
                                        # ui, uy
                                        u+re_group([*i_any,y])])
                                        

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
        # looking for the biggest valid combination of vowels - remember:
        #    1. 2 strong vowels cannot be together
        #    2. special h usecase
        #    3. special handling of y
        #    4. special handling of qu, gu
        # note: order is important here
        # first rule is to look for accent already present. - if present then immediately done.
        self.accent_rules = [re_compile('^(.*?)'+"("+re_group(accented)+")(.*)()$")]
        three_letter_groups = "(?:"+"|".join(three_letter_combinations)+")"
        two_letter_groups = "(?:"+"|".join(two_letter_combinations)+")"
        combinations = [ three_letter_groups, two_letter_groups, all_group]
        for vowels_to_accent in combinations:
            for weak_beginning in ['^(.*?'+qu_gu+')','^(.*?)']:
                for last in combinations:
                    self.accent_rules.extend([
                                              # could have double vowel ending. 
                                              re_compile(weak_beginning+"("+vowels_to_accent+")("+consonants+"*)("+qu_gu+last+'[ns]{0,2})$'),
                                              re_compile(weak_beginning+"("+vowels_to_accent+")("+consonants+"*)("+last+'[ns]{0,2})$')
                                              ])
                self.accent_rules.extend([
                                              # ends in required consonants 
                                              re_compile(weak_beginning+"("+vowels_to_accent+")("+consonants+'+)()$'),
                                              re_compile("^("+consonants+"*)("+vowels_to_accent+')()()$')
                                              ])
        print(self.accent_rules)
        # used to find the vowel groups for displaying vowels in words.
        self.vowel_groups = []
        for vowel_group in combinations:
            self.vowel_groups.extend([
                                      re_compile("("+vowel_group+")"),
                                      ])
        
    def any(self, vowel):
        for an_any in self._any:
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
            accented = match.group(2) if match.group(2) in self.from_accent_mapping else self.to_accent_mapping[match.group(2)]
            
            result = match.group(1)+accented+match.group(3)+match.group(4)
            print(match.groups())
            print("word="+word+";accent-->"+result)
            return result
        else:
            cs_debug("no vowels in "+word)
            return word
    def accent_at(self, string_, index_=None):
        """
        allow the vowel to already be accented
        """
        if index_ is None:
            index_ = len(string_)-1
        
        vowel = string_[index_]
        if vowel in self.from_accent_mapping:
            # already accented
            return string_
        elif vowel in self.to_accent_mapping:
            result = string_[:index_] + self.to_accent_mapping[vowel] + string_[index_+1:]
            return result
        else:
            raise Exception(string_+" at index="+index_+" there is no vowel.")
            
    def remove_accent(self, string_):
        """
        intentionally removes all accents
        """       
        result = string_ 
        for regex, replace in self._replace_accents:
            result = regex.sub(replace, result)
        return result
    
Vowels = Vowels_()
if True:
    for word in ['irgue', 'repite', 'se', 'cambia']:
        answer = Vowels.find_accented(word)
    

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