# -*- coding: utf-8 -*-
'''

@author: patmoore
'''
import copy
import inspect
import re
import codecs
import sys 
import six
from __init__ import *
# UTF8Writer = codecs.getwriter('utf8')
# sys.stdout = UTF8Writer(sys.stdout)

infinitive_endings = [
    u'ar',
    u'er',
    u'ir'
]

ar_verb = 0
er_verb = 1
ir_verb = 2

stem_changing_persons = [first_person_singular, second_person_singular, third_person_singular, third_person_plural]

Standard_Conjugation_Endings = [ [ [] for t in range(len(Tenses)) ] for v in range(len(infinitive_endings))]

"""
present tense
""" 
Standard_Conjugation_Endings[ar_verb][present_tense] = [
    lambda tense, person : u"o",
    lambda tense, person : u"as",
    lambda tense, person : u"a",
    lambda tense, person : u"amos",
    lambda tense, person : u"áis",
    lambda tense, person : u"an"
    ]  
Standard_Conjugation_Endings[er_verb][present_tense] = [
    Standard_Conjugation_Endings[ar_verb][present_tense][first_person_singular],
    lambda tense, person : u'es',
    lambda tense, person : u'e',
    lambda tense, person : u'emos',
    lambda tense, person : u'éis',
    lambda tense, person : u'en'
    ]  
Standard_Conjugation_Endings[ir_verb][present_tense] = list(Standard_Conjugation_Endings[er_verb][present_tense])
Standard_Conjugation_Endings[ir_verb][present_tense][first_person_plural] = lambda tense, person : u'imos'
Standard_Conjugation_Endings[ir_verb][present_tense][second_person_plural] = lambda tense, person : u'ís'

"""
imperfect tense
"""
Standard_Conjugation_Endings[ar_verb][incomplete_past_tense] = [
    lambda tense, person : u'aba',
    lambda tense, person : u'abas',
    lambda tense, person : u'aba',
    lambda tense, person : u'ábamos',
    lambda tense, person : u'abais',
    lambda tense, person : u'aban'
    ]
Standard_Conjugation_Endings[er_verb][incomplete_past_tense] = Standard_Conjugation_Endings[ir_verb][incomplete_past_tense] = [
    lambda tense, person : u'ía',
    lambda tense, person : u'ías',
    lambda tense, person : u'ía',
    lambda tense, person : u'íamos',
    lambda tense, person : u'íais',
    lambda tense, person : u'ían'
    ]
"""
past tense
"""
Standard_Conjugation_Endings[ar_verb][past_tense] = [
        lambda tense, person : u'é',
        lambda tense, person : u'aste',
        lambda tense, person : u'ó',
        Standard_Conjugation_Endings[ar_verb][present_tense][first_person_plural],
        lambda tense, person : u'asteis',
        lambda tense, person : u'aron' 
    ]
Standard_Conjugation_Endings[er_verb][past_tense] = Standard_Conjugation_Endings[ir_verb][past_tense] =  [
        lambda tense, person : u'í',
        lambda tense, person : u'iste',
        lambda tense, person : u'ió',
        Standard_Conjugation_Endings[ir_verb][present_tense][first_person_plural],
        lambda tense, person : u'isteis',
        lambda tense, person : u'ieron' 
    ]
"""
Future - present tense endings for haber
"""
Standard_Conjugation_Endings[ar_verb][future_tense] = \
    Standard_Conjugation_Endings[er_verb][future_tense] = Standard_Conjugation_Endings[ir_verb][future_tense] =  [
        lambda tense, person : u'é',
        lambda tense, person : u'ás',
        lambda tense, person : u'á',
        lambda tense, person : u'emos',
        lambda tense, person : u'éis',
        lambda tense, person : u'án' 
    ]
 
Standard_Conjugation_Endings[ar_verb][conditional_tense] = \
Standard_Conjugation_Endings[er_verb][conditional_tense] = Standard_Conjugation_Endings[ir_verb][conditional_tense] = \
    Standard_Conjugation_Endings[er_verb][incomplete_past_tense]
 
Standard_Conjugation_Endings[ar_verb][present_subjective_tense] = list(Standard_Conjugation_Endings[er_verb][present_tense])
Standard_Conjugation_Endings[ar_verb][present_subjective_tense][first_person_singular] = lambda tense, person : u'e'     
Standard_Conjugation_Endings[er_verb][present_subjective_tense] = Standard_Conjugation_Endings[ir_verb][present_subjective_tense] =\
    list(Standard_Conjugation_Endings[ar_verb][present_tense])
Standard_Conjugation_Endings[er_verb][present_subjective_tense][first_person_singular] = lambda tense, person : u'a'       
 
Standard_Conjugation_Endings[ar_verb][past_subjective_tense] =\
Standard_Conjugation_Endings[er_verb][past_subjective_tense] = Standard_Conjugation_Endings[ir_verb][past_subjective_tense] = [
    lambda tense, person : u'ra',
    lambda tense, person : u'ras',
    lambda tense, person : u'ra',
    lambda tense, person : u'ramos',
    lambda tense, person : u'ráis',
    lambda tense, person : u'ran'
    ]

"""
Special casing
key: need to allow verbs to opt out of special casing. For example, relucir does not have a c-> j substitution in past tense.
"""
Special_Changes = [
    {
        'key': 'v_cr',        
        '__doc__': 'verbs ending in -cer or -cir with a preceding vowel have c -> zc before o',
        '__examples__': 'http://www.intro2spanish.com/verbs/listas/master-zco.htm',                
        'inf_ending': re.compile(u'[aeiouáéíóú]c[ie]r$'),
        # tocar - example
        'conjugation_ending' : re.compile(u'^[oó]'),
        'conjugation': lambda stem, ending: stem[:-1] + u'zc' + ending
    },
    {
        '__doc__': 'verbs ending in -cer or -cir with preceding constant have c -> z before o',
        '__examples__': r'convencer',                
        'inf_ending': re.compile(u'[^aeiouáéíóú]c[ie]r$'),
        'conjugation_ending' : re.compile(u'^[oó]'),
        'conjugation': lambda stem, ending: stem[:-1] + u'z'+ ending,
    },
    {
        '__doc__': 'verbs ending in -car have c -> qu before e',
        '__examples__': 'tocar',                
        'inf_ending': re.compile(u'car$'),
        'conjugation_ending' : re.compile(u'^[eé]'),
        'conjugation': lambda stem, ending: stem[:-1] + u'qu'+ ending,
    },
    {
        '__doc__': 'verbs ending in -gar have g -> gu before e',
        '__examples__': 'pagar',                
        'inf_ending': re.compile(u'gar$'),
        'conjugation_ending' : re.compile(u'^[eé]'),
        'conjugation': lambda stem, ending: stem[:-1] + u'gu'+ ending,
    },
    {
        '__doc__': 'verbs ending in -zar have z -> c before e',
        '__examples__': 'comenzar',                
        'inf_ending': re.compile(u'zar$'),
        # tocar - example
        'conjugation_ending' : re.compile(u'^[eé]'),
        'conjugation': lambda stem, ending: stem[:-1] + u'c'+ ending,
    },
    {
        'key' : u'ucir_present',
        'inf_ending': re.compile(u'ucir'),
        
    },
    {
        '__doc__':'verbs ending in -ducir are also irregular in the past tense',
        '__examples__': 'introducir, traducir',
        'inf_ending': re.compile(u'ducir'),
        'override': {
            'tense': past_tense,
            'conjugation': [
                
                ]
        }
    }
]

Ducir = re.compile(six.u('d[úu]cir$'))
# (includes -ducir rules ) 
Ucir = re.compile(six.u('[úu]cir$'))
#
Guir = re.compile(six.u('guir'))
Uir = re.compile(six.u('[^q]uir$'))

#TODO: does this include ucir words?
Cer_Cir_With_Vowel = re.compile(u'[aeiouáéíóú]c[ie]r$')

Cer_Cir_Without_Vowel = re.compile(u'[^aeiouáéíóú]c[ie]r$')

Ger_Gir = re.compile(six.u('g[ei]r$'))

Gar = re.compile(six.u('gar$'))
Car = re.compile(six.u('car$'))
Car = re.compile(six.u('car$'))
Zar = re.compile(six.u('zar$'))

class ConjugationOverrides():
    
    def __init__(self, inf_match=None, parent=None, documentation=None, examples=None):
        self.parent = parent
        self.inf_match = inf_match
#         self.conjugation = ConjugationOverrides.SparseList()
#         self.conjugation_endings = ConjugationOverrides.SparseList()
#         self.conjugation_stems = ConjugationOverrides.SparseList()
        
    def __overrides(self, tense, overrides, attr_name, persons):
        if not hasattr(self, attr_name):
            self_overrides = [ None for t in range(len(tenses)) ]
            setattr(self, attr_name, self_overrides) 
        else:
            self_overrides = getattr(self, attr_name)
            
        if isinstance(overrides, six.string_types):
            if persons is not None:
                if self_overrides[tense] is None:
                    self_overrides[tense] = [None] * len(Persons)
                    
                if isinstance(persons, six.integer_types):
                    # a single person has an override
                    self_overrides[tense][persons] = overrides
                else:
                    for person in persons:
                        self_overrides[tense][person] = overrides
            else:
                # a single stem for all persons of this tense
                self_overrides[tense] = [overrides] * len(Persons)
        else:
            # overrides better be a list
            if self_overrides[tense] is None:
                self_overrides[tense] = [None] * len(Persons)
                
            for person, override in enumerate(overrides):
                if override is not None:
                    self_overrides[tense][person] = override
                    
    def override_tense_stem(self, tense, overrides,persons=None):
        self.__overrides(tense, overrides, 'conjugation_stems', persons)
                    
    def override_tense_ending(self, tense, overrides,persons=None):
        self.__overrides(tense, overrides, 'conjugation_endings',persons)
    
    def override_tense(self, tense, overrides,persons=None):
        """
        Used for case when the entire tense is very irregular
        """
        self.__overrides(tense, overrides, 'conjugations',persons)
        
    def __get_override(self, tense, person, attr_name):
        if hasattr(self, attr_name):
            self_overrides = getattr(self, attr_name)
            if self_overrides[tense] is not None:
            # some overrides exist for this tense        
                if isinstance(self_overrides[tense], six.string_types):
                    # a single different stem for the entire tense
                    return self_overrides[tense]
                elif isinstance(self_overrides[tense][person], six.string_types):
                    # a specific override for the tense/person
                    return self_overrides[tense][person]

        if self.parent is not None:
            override = self.parent.__get_override(tense, person, attr_name)
            return override
            
        return None

class Verb():
    '''
    classdocs
    '''
    
    def __init__(self, verb_string, conjugation_overrides=None, prefix=None):
        '''
        Constructor
        prefix - remove to find related word for conjugation.
        '''
        self.inf_verb_string = verb_string
        if verb_string[-2:] == 'se':
            self.reflexive = True
            verb_string = verb_string[:-2]
            
        self.verb_string = verb_string
        self.inf_ending = verb_string[-2:]            
        self.verb_ending_index = infinitive_endings.index(self.inf_ending)      
           
        if verb_string == six.u('ir'):
            # ir special case
            self.stem = verb_string
        else:
            self.stem = verb_string[:-2]
            
        self.prefix = prefix
        
        if conjugation_overrides is not None:
            conjugation_overrides.apply(self)
                
            
        # look for known special cases
#         last_three = verb_string[-3:]
#         last_four = verb_string[-4:]        
#         if verb_string[-5:] == u'ducir':
#             # past tense is special case c-> j
#             self.__conjugation_stems[past_tense] = [lambda tense, person: self.stem[:-1] + u'j' for person in Persons]
#             # first person past is e instead of i
#             self.__conjugation_endings[past_tense][first_person_singular] = lambda tense, person: u'e'
#             # normally ió
#             self.__conjugation_endings[past_tense][third_person_singular] = lambda tense, person: u'o'
#             # normally ieron
#             self.__conjugation_endings[past_tense][third_person_singular] = lambda tense, person: u'eron'
#             
#         if last_four == u'ucir':
#             # including ducir verbs
#             pass # for now
#         elif last_four == u'quir':
#             #not special - does not follow uir exceptions
#             pass
#         if Cer_Cir_With_Vowel.search(self.verb_string):
#             self.override_tense_stem(present_tense, self.stem[:-1] +u'zc', first_person_singular)
#         elif last_three == u'ger' or last_three == u'gir':
#             # g-> j in yo form
#             self.__conjugation_stems[present_tense][first_person_singular] = lambda tense, person: self.stem[:-1] +u'j'
#         elif last_four == u'guir':
#             # drop the 'u' in yo form
#             self.override_tense_stem(present_tense, self.stem[:-1], first_person_singular) 
#         elif last_three == u'uir':
#             for person in stem_changing_persons :
#                 self.__conjugation_stems[present_tense][person] = lambda tense, person: self.stem + u'y'
#             
#             self.__conjugation_ending[past_tense][third_person_singular] = lambda tense, person: u'yó'
#             self.__conjugation_ending[past_tense][third_person_singular] = lambda tense, person: u'yeron'
#             
#         elif last_three == u'car':
#             # c -> qu in past tense first person ( before e ) 
#             self.__conjugation_stems[past_tense][first_person_singular] = lambda tense, person: self.stem[:-1] +u'qu'
#             self.__conjugation_stems[present_subjective_tense][first_person_singular] = lambda tense, person: self.stem[:-1] +u'qu'
#         elif last_three == u'gar':
#             # g -> gu in past tense first person ( before e ) 
#             self.__conjugation_stems[past_tense][first_person_singular] = lambda tense, person: self.stem[:-1] +u'gu'
#         elif last_three == u'zar':
#             # z -> c in past tense first person ( before e ) 
#             self.__conjugation_stems[past_tense][first_person_singular] = lambda tense, person: self.stem[:-1] +u'c'
#             
#         if modifiers is not None:
#             if "stem_modifiers" in modifiers:
#                 self.__stem_changing(modifiers['stem_modifiers'])             
        
    def conjugate_all_tenses(self):
        # present to imperative
        return [ self.conjugate_tense(tense) for tense in range(len(Tenses)) ]
        
    def conjugate_tense(self, tense):
        return [ self.conjugate(tense=tense, person=person) for person in range(len(Persons)) ]    
            
    def conjugate(self, tense, person):
        conjugation = self.__get_override(tense, person, 'conjugations')
        if conjugation is None:
            conjugation = self.conjugate_stem(tense, person) + self.conjugate_ending(tense, person)
        return conjugation
    
    def conjugate_stem(self, tense, person):
        stem = self.__get_override(tense, person, 'conjugation_stems')
        if stem is not None:
            return stem
        
        if tense == present_tense or tense == incomplete_past_tense or tense == past_tense:
            return self.stem
        elif tense == future_tense or tense == conditional_tense:
            return self.verb_string
        elif tense == present_subjective_tense:
            return self.__conjugation_present_subjective_stem(tense, person)
        elif tense == past_subjective_tense:
            return self.__conjugation_past_subjective_stem(tense, person)
        raise "tense="+str(tense)
        
    def conjugate_ending(self, tense, person):
        ending = self.__get_override(tense, person, 'conjugation_endings')
        if ending is None:
            ending = Standard_Conjugation_Endings[self.verb_ending_index][tense][person](tense, person)
        return ending
    
    def __conjugation_present_subjective_stem(self, tense, person):
        first_person_conjugation = self.conjugate(present_tense, first_person_singular)
        if first_person_conjugation[-1:] =='o':
            conjugation_stem = first_person_conjugation[:-1]
            return conjugation_stem
        else:
            raise "First person conjugation does not end in 'o' = "+first_person_conjugation

    def __conjugation_past_subjective_stem(self, tense, person):
        third_person_plural_conjugation = self.conjugate(past_tense, third_person_plural)
        if third_person_plural_conjugation[-3:] == u'ron':
            conjugation_stem = third_person_plural_conjugation[:-3]
            return conjugation_stem
        else:
            raise "Third person conjugation does not end in 'ron' = "+third_person_plural_conjugation            
        
    def _overrides(self, tense, overrides, attr_name,persons=None):
        def __convert_to_function(override):            
            if inspect.isfunction(override) or inspect.ismethod(override):
                func = override                
            else:
                func = lambda self, tense, person: override
            boundfunc = six.create_bound_method(func, self)
            return boundfunc
            
        if not hasattr(self, attr_name):
            self_overrides = [ None ] * len(Tenses)
            setattr(self, attr_name, self_overrides) 
        else:
            self_overrides = getattr(self, attr_name)
            
        if isinstance(overrides, six.string_types) or inspect.isfunction(overrides):
            fn = __convert_to_function(overrides)
            if persons is not None:
                if self_overrides[tense] is None:
                    self_overrides[tense] = [None] * len(Persons)
                    
                if isinstance(persons, six.integer_types):
                    # a single person has an override
                    self_overrides[tense][persons] = fn
                else:
                    for person in persons:
                        self_overrides[tense][person] = fn
            else:
                # a single stem for all persons of this tense
                self_overrides[tense] = [fn] * len(Persons)
        else:
            # overrides better be a list
            if self_overrides[tense] is None:
                self_overrides[tense] = [None] * len(Persons)
                
            for person, override in enumerate(overrides):
                if override is not None:
                    self_overrides[tense][person] = __convert_to_function(override)
                    
    def override_tense_stem(self, tense, overrides,persons=None):
        """
        :param overrides - array of all persons, or a unicode string that applies to all persons
        :param persons - person or array of persons that get the overrides ( which must be a string )
        """
        self._overrides(tense, overrides, 'conjugation_stems', persons)
                    
    def override_tense_ending(self, tense, overrides,persons=None):
        self._overrides(tense, overrides, 'conjugation_endings',persons)
    
    def override_tense(self, tense, overrides,persons=None):
        """
        Used for case when the entire tense is very irregular
        """
        self._overrides(tense, overrides, 'conjugations',persons)
        
    def __get_override(self, tense, person, attr_name):
        if hasattr(self, attr_name):
            self_overrides = getattr(self, attr_name)
            if self_overrides[tense] is not None:
            # some overrides exist for this tense        
                if isinstance(self_overrides[tense], six.string_types):
                    # a single different stem for the entire tense
                    return self_overrides[tense]
                elif inspect.ismethod(self_overrides[tense]) or inspect.isfunction(self_overrides[tense]):
                    return self_overrides[tense](tense, person)
                elif self_overrides[tense][person] is None:
                    return None
                elif isinstance(self_overrides[tense][person], six.string_types):
                    # a specific override for the tense/person
                    return self_overrides[tense][person]
                elif inspect.ismethod(self_overrides[tense][person]) or inspect.isfunction(self_overrides[tense][person]):
                    # a specific override for the tense/person
                    return self_overrides[tense][person](tense, person)
                else:
                    raise "Unknown type in override"
        return None
    
            
            
v = Verb("lanzar", conjugation_overrides=Zar_CO)
# c = v.conjugate_all_tenses()
c = v.conjugate_tense(past_tense)
print repr(c).decode("unicode-escape")
c = v.conjugate_tense(present_subjective_tense)
print repr(c).decode("unicode-escape")

# v = Verb(u"hablar")
# c = v.conjugate_all_tenses()
# print repr(c).decode("unicode-escape")
# 
# v = Verb(u"ofrecer")
# c = v.conjugate_all_tenses()
# print repr(c).decode("unicode-escape")
# 
# v = Verb(u"distinguir")
# c = v.conjugate_all_tenses()
# print repr(c).decode("unicode-escape")

ir_conjugation_overrides = ConjugationOverrides()
ir_conjugation_overrides.override_tense(present_tense, six.u('voy'), first_person_singular) 
ir_conjugation_overrides.override_tense(present_tense, six.u('vais'), second_person_plural)
ir_conjugation_overrides.override_tense_stem(present_tense, six('v'))
ir_conjugation_overrides.override_tense(incomplete_past_tense, [six.u('iba'), six.u('ibas'), six.u('iba'), six.u('ibamos'),six.u('ibais'), six.u('iban')])
ir_conjugation_overrides.override_tense_stem(past_tense, six('fu'))
ir_conjugation_overrides.override_tense_ending(past_tense, six('e'), third_person_singular)
ir_conjugation_overrides.override_tense_ending(past_tense, six('eron'), third_person_plural)
ir_conjugation_overrides.override_tense_stem(present_subjective_tense, six.u('vay'))
v = Verb(six.u('ir'), ir_conjugation_overrides)
