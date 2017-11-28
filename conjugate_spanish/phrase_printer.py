from interface import implements, Interface
from .constants import Persons, Tenses
from conjugate_spanish.constants import BaseConst, IrregularNature,\
    IrregularNatures
import copy
    
class PhrasePrinter(Interface):
    def print(self, *, tenses=Tenses.all, persons=Persons.all, options={}):
        pass
    
    @property
    def phrase(self):
        pass
    
class CsvPrinter(implements(PhrasePrinter)):
    def __init__(self, phrase, irregular_nature = IrregularNature.regular, options=None):
        self._phrase = phrase
        self._irregular_nature = irregular_nature
        self._options = {} if options is None else copy.copy(options) 
        
    @property
    def phrase(self):
        return self._phrase
        
    def print(self, *, tenses=Tenses.all, persons=Persons.all, options={}):
        result = ''
        irregular_nature = IrregularNatures.regular
        def __process(conjugation_notes):
            if conjugation_notes.irregular_nature > irregular_nature:
                irregular_nature = conjugation_notes.irregular_nature
            if conjugation_notes.conjugation is None:
                result += ','
            else:
                result += ',"'+conjugation_notes.conjugation+'"'
                
                
        for tense in Tenses.all:
            if tense in Tenses.Person_Agnostic:
                conjugation_notes = self.phrase.conjugate(tense)
                if conjugation_notes.irregular_nature > irregular_nature:
                    irregular_nature = conjugation_notes.irregular_nature
                if conjugation_notes.conjugation is None:
                    result += ','
                else:
                    result += ',"'+conjugation_notes.conjugation+'"'
            else:
                persons = Persons.all_except(Persons.first_person_singular) if tense in Tenses.imperative else Persons.all
                for person in persons:
                    conjugation_notes = self.phrase.conjugate(tense, person)
                    if conjugation_notes.irregular_nature > irregular_nature:
                        irregular_nature = conjugation_notes.irregular_nature
                    if conjugation_notes.conjugation is None:
                        result += ','
                    else:
                        result += ',"'+conjugation_notes.conjugation+'"'
        if irregular_nature == IrregularNatures.regular:            
            print('"'+self.phrase.full_phrase+'","'+irregular_nature.key+'"')
        else:
            print('"'+self.phrase.full_phrase+'","'+irregular_nature.key+'"' + result)
    
class ScreenPrinter(implements(PhrasePrinter)):
    def __init__(self, phrase, irregular_nature = IrregularNature.regular, options=None):
        self._phrase = phrase
        self._irregular_nature = irregular_nature
        self._options = {} if options is None else copy.copy(options) 
        
    @property
    def phrase(self):
        return self._phrase
    
    @property
    def detailed(self):
        return 'detailed' in self._options and self._options['detailed']
    
    @property
    def print_blocked(self):
        return 'blocked' in self._options and self._options['blocked']
    
    def print(self, tenses=Tenses.all, persons=Persons.all, **kwargs):
        print(self.phrase.full_phrase+ ' : ' + self.phrase.definition + ' (' + self.phrase.complete_overrides_string+ ')')
        irregular_nature = IrregularNature.regular
        for tense in tenses:
            returned_irregular_nature = self.print_tense(tense, persons)
            if returned_irregular_nature > irregular_nature:
                irregular_nature = returned_irregular_nature
        print(irregular_nature.human_readable)
                
    def print_tense(self, tense, persons=Persons.all):
        def _print_header_():
            print("  "+tense.human_readable+ "(" 
              + str(tense._value_) + "):")
        irregular_nature = IrregularNature.regular

        if tense in Tenses.Person_Agnostic:
            conjugation_notes = self.phrase.conjugate(tense)
            if conjugation_notes.irregular_nature >= self._irregular_nature:
                _print_header_()
                self._print_conjugation_notes(conjugation_notes) 
                print()
                irregular_nature = conjugation_notes.irregular_nature
        else:
            conj_list = []
            for person in persons:
                if person != Persons.first_person_singular or tense not in Tenses.imperative:
                    conjugation_notes = self.phrase.conjugate(tense, person)
                    if conjugation_notes is not None and conjugation_notes.irregular_nature >= self._irregular_nature and (self.print_blocked or not conjugation_notes.blocked):
                        conj_list.append(conjugation_notes)
            
            if len(conj_list) > 0:                
                _print_header_()
                print('    ', end='')
                for conjugation_notes in conj_list:                    
                    print(conjugation_notes.person.human_readable + "(" 
                          + str(conjugation_notes.person._value_) + "):", end=' ')
                
                    self._print_conjugation_notes(conjugation_notes) 
                    if irregular_nature < conjugation_notes.irregular_nature:
                        irregular_nature = conjugation_notes.irregular_nature
                print()
        return irregular_nature
    
    def _print_conjugation_notes(self, conjugation_notes):
        if conjugation_notes is None:
            print("---", end='; ')
        elif conjugation_notes.irregular_nature >= self._irregular_nature:
            print(conjugation_notes.full_conjugation+"("+conjugation_notes.operation_notes+")", end='')            
            if not conjugation_notes.is_regular and self.detailed:
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
                                print(conjugations[tense][person], end="; ")
                            else:
                                print(conjugations[tense][person])
                                 
                    print()