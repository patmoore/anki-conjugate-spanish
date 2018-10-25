from interface import Interface
from conjugate_spanish.constants import Person, Tense, IrregularNature
import copy

class PhrasePrinter(object):
    def __init__(self, phrase, irregular_nature = IrregularNature.regular, options=None):
        self._phrase = phrase
        self._irregular_nature = irregular_nature
        self._options = {} if options is None else copy.copy(options)

    @property
    def phrase(self):
        return self._phrase

    @property
    def detailed(self):
        return 'verbose' in self._options and self._options['verbose'] > 1

    @property
    def print_blocked(self):
        return 'blocked' in self._options and self._options['blocked']

    def _print_verb_header(self):
        pass

    def print(self, tenses=Tense.all(), persons=Person.all(), **kwargs):
        self._print_verb_header()
        irregular_nature = IrregularNature.regular
        for tense in tenses:
            returned_irregular_nature = self.print_tense(tense, persons)
            if returned_irregular_nature > irregular_nature:
                irregular_nature = returned_irregular_nature
        print(irregular_nature.human_readable)

    def print_tense(self, tense, persons=Person.all()):
        irregular_nature = IrregularNature.regular

        if tense in Tense.Person_Agnostic():
            conjugation_notes = self.phrase.conjugate(tense)
            if conjugation_notes.irregular_nature >= self._irregular_nature:
                self._print_tense_header(tense)
                self._print_conjugation_notes(conjugation_notes)
                print()
                irregular_nature = conjugation_notes.irregular_nature
        else:
            conj_list = []
            for person in persons:
                if person != Person.first_person_singular or tense not in Tense.imperative():
                    conjugation_notes = self.phrase.conjugate(tense, person)
                    if conjugation_notes is not None and conjugation_notes.irregular_nature >= self._irregular_nature and (self.print_blocked or not conjugation_notes.blocked):
                        conj_list.append(conjugation_notes)

            if len(conj_list) > 0:
                self._print_tense_header(tense)
                print('    ', end='')
                for conjugation_notes in conj_list:
                    print("{}({}):".format(str(conjugation_notes.person),
                        conjugation_notes.person), end=' ')

                    self._print_conjugation_notes(conjugation_notes)
                    if irregular_nature < conjugation_notes.irregular_nature:
                        irregular_nature = conjugation_notes.irregular_nature
                print()
        return irregular_nature

    def print_all_tenses(self):
        conjugations= self.conjugate_all_tenses()
        self._print_conjugations(conjugations)

    def print_irregular_tenses(self):
        conjugations = self.conjugate_irregular_tenses()
        self._print_conjugations(conjugations)

    def _print_tense_header(self, tense):
        pass

    def _print_verb_header(self):
        pass

    def _print_conjugation_notes(self, conjugation_notes):
        pass
