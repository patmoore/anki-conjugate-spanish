from interface import implements, Interface
from .constants import Persons, Tenses

class PhrasePrinter(Interface):
    def print(self):
        pass
    
    @property
    def phrase(self):
        pass
    
class CsvPrinter(implements(PhrasePrinter)):
    def __init__(self, phrase):
        self._phrase = phrase
        
    def print(self, full_info=True):
        result = '"'+self.full_phrase+'"'
        if full_info:
            if len(self.appliedOverrides) > 0:
                result+=',"'+repr(self.appliedOverrides)+'"'
            if len(self.doNotApply) > 0:
                result +=',"'+repr(self.doNotApply)+'"'
            if self.base_verb_string is not None:
                result += ',"'+self.base_verb_string+'"'
        
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