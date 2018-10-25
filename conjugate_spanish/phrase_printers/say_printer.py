
import os
from conjugate_spanish import Tense, Person
from conjugate_spanish.constants import IrregularNature
from .phrase_printer import PhrasePrinter


class SayPrinter(PhrasePrinter):
    def _print_conjugation_notes(self, conjugation_notes):
        print(conjugation_notes.full_conjugation)
        os.system("say -v Monica {}".format(conjugation_notes.full_conjugation))