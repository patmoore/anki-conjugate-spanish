import copy

from conjugate_spanish import Tense, Person
from conjugate_spanish.constants import IrregularNature


class CsvPrinter(object):
    def __init__(self, phrase, irregular_nature = IrregularNature.regular, options=None):
        self._phrase = phrase
        self._irregular_nature = irregular_nature
        self._options = {} if options is None else copy.copy(options)

    @property
    def phrase(self):
        return self._phrase

    def print(self, *, tenses=Tense.all(), persons=Person.all(), options={}):
        result = ''
        irregular_nature = IrregularNature.regular
        def __process(conjugation_notes):
            if conjugation_notes.irregular_nature >= irregular_nature:
                irregular_nature = conjugation_notes.irregular_nature
            if conjugation_notes.conjugation is None:
                result += ','
            else:
                result += ',"'+conjugation_notes.conjugation+'"'

        for tense in Tense.all():
            if tense in Tense.Person_Agnostic():
                conjugation_notes = self.phrase.conjugate(tense)
                if conjugation_notes.irregular_nature > irregular_nature:
                    irregular_nature = conjugation_notes.irregular_nature
                if conjugation_notes.conjugation is None:
                    result += ','
                elif conjugation_notes.irregular_nature == IrregularNature.regular:
                    result += ',"-"'
                else:
                    result += ',"'+conjugation_notes.conjugation+'"'
            else:
                persons = Person.all_except(Person.first_person_singular) if tense in Tense.imperative() else Person.all()
                for person in persons:
                    conjugation_notes = self.phrase.conjugate(tense, person)
                    if conjugation_notes.irregular_nature > irregular_nature:
                        irregular_nature = conjugation_notes.irregular_nature
                    if conjugation_notes.conjugation is None:
                        result += ','
                    elif conjugation_notes.irregular_nature == IrregularNature.regular:
                        result += ',"-"'
                    else:
                        result += ',"'+conjugation_notes.conjugation+'"'
        if irregular_nature < self._irregular_nature:
            print('"'+self.phrase.full_phrase+'","'+self.phrase.definition+'","'+irregular_nature.key+'"')
        else:
            print('"'+self.phrase.full_phrase+'","'+self.phrase.definition+'","'+irregular_nature.key+'"' + result)