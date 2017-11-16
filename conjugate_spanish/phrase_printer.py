from interface import implements, Interface
from .constants import Persons, Tenses
from conjugate_spanish.constants import BaseConst, IrregularNature
    
class PhrasePrinter(Interface):
    def print(self, *, tenses=Tenses.all, persons=Persons.all, options={}):
        pass
    
    @property
    def phrase(self):
        pass
    
class CsvPrinter(implements(PhrasePrinter)):
    def __init__(self, phrase):
        self._phrase = phrase
        
    @property
    def phrase(self):
        return self._phrase
        
    def print(self, *, tenses=Tenses.all, persons=Persons.all, options={}):
        result = '"'+self.full_phrase+'"'
#         if full_info:
#             if len(self.appliedOverrides) > 0:
#                 result+=',"'+repr(self.appliedOverrides)+'"'
#             if len(self.doNotApply) > 0:
#                 result +=',"'+repr(self.doNotApply)+'"'
#             if self.base_verb_string is not None:
#                 result += ',"'+self.base_verb_string+'"'
        
        for tense in Tenses.all:
            if tense in Tenses.Person_Agnostic:
                conjugation = self.conjugate(tense)
                result += ',"'+conjugation+'"'
            else:
                for person in Persons.all:
                    conjugation = self.conjugate(tense, person)
                    if conjugation is None:
                        result += ','
                    else:
                        result += ',"'+conjugation+'"'
        return result
    
class ScreenPrinter(implements(PhrasePrinter)):
    def __init__(self, phrase, irregular_nature = IrregularNature.regular):
        self._phrase = phrase
        self._irregular_nature = irregular_nature
        
    @property
    def phrase(self):
        return self._phrase
    
    def print(self, tenses=Tenses.all, persons=Persons.all, **kwargs):
        print(self.phrase.full_phrase+ ' : ' + self.phrase.definition)
        for tense in tenses:
            self.print_tense(tense, persons)
                
    def print_tense(self, tense, persons=Persons.all):
        def _print_header_():
            print(tense.human_readable+ "(" 
              + str(tense._value_) + "):")
            print('\t', end='')
        _print_header_()
        if tense in Tenses.Person_Agnostic:
            conjugation_notes = self.phrase.conjugate(tense)
            if conjugation_notes.irregular_nature >= self._irregular_nature:
                _print_header_()
                self._print_conjugation_notes(conjugation_notes) 
                print()
        else:
            conj_list = []
            for person in persons:
                conjugation_notes = self.phrase.conjugate(tense, person)
                if conjugation_notes is not None and conjugation_notes.irregular_nature >= self._irregular_nature:
                    conj_list.append(conjugation_notes)
            
            if len(conj_list) > 0:
                _print_header_()
                for conjugation_notes in conj_list:
                    print(conjugation_notes.person.human_readable + "(" 
                          + str(conjugation_notes.person._value_) + "):", end=' ')
                
                    self._print_conjugation_notes(conjugation_notes)    
                print()
    
    def _print_conjugation_notes(self, conjugation_notes):
        if conjugation_notes is None:
            print("---", end='; ')
        elif conjugation_notes.irregular_nature >= self._irregular_nature:
            print(conjugation_notes.full_conjugation, end='')            
            if not conjugation_notes.is_regular:
                print('', end=' <= ')
                core_verb = None
                ending = None
                conjugation = None
                output = []
                for conjugation_note in reversed(conjugation_notes.conjugation_note_list):
                    if conjugation_note.core_verb is not None:
                        core_verb = conjugation_note.core_verb
                    if conjugation_note.ending is not None:
                        ending = conjugation_note.ending
                    if conjugation_note.conjugation is not None:
                        conjugation = conjugation_note.conjugation
                                        
                    if conjugation is None:
                        output.insert(0, core_verb+ending)
                    else:
                        output.insert(0, conjugation)
                print(*output[1:], sep=' <= ', end='; ')
            else:
                print('', end='; ')
                
    def print_all_tenses(self):
        conjugations= self.conjugate_all_tenses()
        self._print_conjugations(conjugations)
    
    def print_irregular_tenses(self):
        conjugations = self.conjugate_irregular_tenses()
        self._print_conjugations(conjugations)
        
    def _print_conjugations(self, conjugations):
        if conjugations is not None:        
            for tense in range(len(Tenses)):
                if conjugations[tense] is None:
                    continue
                
                print("  "+ Tenses[tense], end=": ")
                if tense in Tenses.Person_Agnostic:
                    print(conjugations[tense])
                else:
                    for person in range(len(Persons)):
                        if conjugations[tense][person] is not None:
                            if not self.is_reflexive:
                                print( Persons[person]+" "+conjugations[tense][person], end="; ")
                            elif tense not in Tenses.imperative:
                                print( conjugations[tense][person], end="; ")
                            else:
                                print(conjugations[tense][person])
                                 
                    print()