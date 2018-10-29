
import os
from conjugate_spanish import Tense, Person
from conjugate_spanish.constants import IrregularNature
from .phrase_printer import PhrasePrinter


class SayPrinter(PhrasePrinter):

    def _print_tense_header(self, tense):
        print("  {} ({}):".format(tense.human_readable, str(tense._value_)))

    def _print_conjugation_notes(self, conjugation_notes):
        print(conjugation_notes.full_conjugation)
        os.system("say -i -v Monica {}".format(conjugation_notes.full_conjugation))