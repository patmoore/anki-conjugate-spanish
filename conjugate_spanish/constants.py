# -*- coding: utf-8 -*-
import collections
import six

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
    
Tenses = Tenses_([
    u'present',
    ur'incomplete past',
    ur'past',
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
    @staticmethod
    def all_except(except_persons):
        _except_persons = except_persons if isinstance(except_persons, list) else [ except_persons ]
        return [person for person in range(len(Persons)) if person not in _except_persons]
     
    Present_Tense_Stem_Changing_Persons = [first_person_singular, second_person_singular, third_person_singular, third_person_plural]
    Past_Tense_Stem_Changing_Persons = [third_person_singular, third_person_plural]

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