import unittest
from conjugate_spanish.constants import Tenses, Persons
from conjugate_spanish.vowel import Vowels
from conjugate_spanish.verb import Verb
from conjugate_spanish.espanol_dictionary import Espanol_Dictionary


class TestVerifyBaseVerb(unittest.TestCase):
    """
    Test to see how derived verbs behave
    """
    def test_derived_irregular(self):
        Espanol_Dictionary.load()
        verb = Espanol_Dictionary.get("mantener")
        conjugations = verb.conjugate_irregular_tenses()
        print(conjugations)
        verb = Espanol_Dictionary.get("tener")
        conjugations = verb.conjugate_irregular_tenses()
        print(conjugations)
        