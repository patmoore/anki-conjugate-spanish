import copy

from conjugate_spanish import Tense, Person
from conjugate_spanish.constants import IrregularNature
from .phrase_printer import PhrasePrinter


class ScreenPrinter(PhrasePrinter): # implements(PhrasePrinter)

    def _print_verb_header(self, options={}):
        print("{} : {} ( {} ) {}".format(self.phrase.full_phrase, self.phrase.definition,
                                    self.phrase.complete_overrides_string,
                                    "derived from "+", ".join([ base_verb.full_phrase for base_verb in self.phrase.derived_list ]) if self.phrase.is_derived else "")
              )

    def _print_tense_header(self, tense):
        print("  {} ({}):".format(tense.human_readable, str(tense._value_)))

    def _print_conjugation_notes(self, conjugation_notes):
        if conjugation_notes is None:
            print("---", end='; ')
        elif conjugation_notes.irregular_nature >= self._irregular_nature:
            if self._options["verbose"] == 1:
                print("{}({})".format(conjugation_notes.full_conjugation,
                      [operation_note for operation_note in conjugation_notes.operation_notes if operation_note.irregular_nature !=  IrregularNature.base]
                ), end='')
            else:
                print(conjugation_notes.full_conjugation, end='')
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

    def _print_conjugations(self, conjugations):
        if conjugations is not None:
            for tense in range(len(Tense)):
                if conjugations[tense] is None:
                    continue

                print("  "+ tense, end=": ")
                if tense in Tense.Person_Agnostic():
                    print(conjugations[tense])
                else:
                    for person in range(len(Person)):
                        if conjugations[tense][person] is not None:
                            if not self.is_reflexive:
                                print( person+" "+conjugations[tense][person], end="; ")
                            elif tense not in Tense.imperative():
                                print(conjugations[tense][person], end="; ")
                            else:
                                print(conjugations[tense][person])

                    print()