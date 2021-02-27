# -*- coding: utf-8 -*-

# These are the standard words (special case)
import codecs
import csv
from .verb import Verb
from .constants import *

import os
from .nonconjugated_phrase import NonConjugatedPhrase
from .utils import cs_debug, cs_error
from .storage import Storage


class DerivationNode():
    def __init__(self, phrase_str):
        """
        phrase_str - because actual entry may change if a generated entry is replaced with a real entry
        """
        self._phrase_str = phrase_str
        self._derived = []
        self._parent_str = None

    def add_derived(self, derived):
        if derived not in self._derived:
            self._derived.append(derived)

    def add_parent(self, parent_str):
        """
        todo check to see if parent already set.
        """
        if self._parent_str is None:
            self._parent_str = parent_str
        else:
            cs_error("parent already set")

    @property
    def derived(self):
        return self._derived

    def __repr__(self):
        return "{'phrase_str': '" + self._phrase_str + "', 'derived' :" + str(self._derived) + '}'


class DerivationTree_():
    def __init__(self):
        self._map = {}
        self._irregular = {}
        self._regular = []
        self._custom = []
        # used to help find possible base verb
        self._reversed_verb_map = {}
        self._reversed_no_base_verb = {}

    def _look_for_base_verb(self, phrase):
        #
        # look for possible base verbs
        # TODO need to look at existing verbs already processed.
        # TODO when looking for possible base_verbs, we really want to find the base_verb that is the longest
        # ie. if choice between 'rebullir' and 'bullir' we want to pick 'rebullir'
        #
        def _handle_match(phrase, possible_base_verb):
            if phrase.full_phrase == possible_base_verb.full_phrase:
                if possible_base_verb.is_generated:
                    print("possible_base_verb {} generated".format(possible_base_verb.full_phrase))
                return False

            if phrase.is_generated:
                print("phrase {} generated".format(phrase.full_phrase))
            if possible_base_verb.is_generated:
                print("possible_base_verb {} generated".format(possible_base_verb.full_phrase))

            # phrase.base_verb = possible_base_verb
            print("{} derived from {} ?".format(phrase.full_phrase, possible_base_verb.full_phrase))
            return False

        if not phrase.is_phrase and not phrase.is_derived and len(
                phrase.full_phrase) > 4 and not phrase.is_explicit_regular:
            # does not have any '-'
            # ( reversed because in future this will be stored in sql db and doing a like 'xxxx%' search )
            reversed_verb_string = phrase.full_phrase[-1::-1]
            # drop the infinitive endings and 'se'
            base_reversed = reversed_verb_string[2:] if phrase.is_reflexive else reversed_verb_string
            # exclude short verbs (dar, ser, etc.) that tend to be irregular but are not good indications of
            # other verbs being irregular.
            # only invoke if no base verb is explicitly supplied
            # TODO - a way to exclude a verb from this check.
            for c in range(1, len(base_reversed)):
                possible_base_verb = self._reversed_verb_map.get(base_reversed[:-c])
                if possible_base_verb is not None:
                    _handle_match(phrase, possible_base_verb)
                    break
            # only add a verb to the reverse lookup table if it is irregular.
            # regular verbs do not have any impact on conjugation,
            # however adding regular verbs allows for the discovery of possible derived verbs
            if not phrase.is_regular:
                # now look for possible previous verbs
                # TODO (sql query)
                for key in self._reversed_no_base_verb.keys():
                    if key.startswith(base_reversed):
                        if _handle_match(self._reversed_no_base_verb[key], phrase):
                            del self._reversed_no_base_verb[key]
                # so does not match self
                self._reversed_verb_map[base_reversed] = phrase
            elif not phrase.is_derived:
                self._reversed_no_base_verb[base_reversed] = phrase

    def add_phrase(self, phrase):
        if False:
            self._look_for_base_verb(phrase)
        else:
            # TODO: Need option to turn off this check / explicitly indicate that the verb is not derived.
            cs_debug("Not looking for derivitive possibilities")

        if phrase.is_derived:
            self._add_derived(phrase, phrase.root_verb_string)
            if phrase.root_verb_string != phrase.base_verb_string:
                self._add_derived(phrase, phrase.base_verb_string)
        if phrase.is_regular:
            self._regular.append(phrase.full_phrase)
        else:
            for override in phrase.appliedOverrides:
                if override.endswith('_irregular'):
                    self._custom.append(phrase.full_phrase)
                else:
                    if override not in self._irregular:
                        self._irregular[override] = DerivationNode(override)
                    self._irregular[override].add_derived(phrase.full_phrase)

    def _add_derived(self, phrase, parent_str):
        if parent_str not in self._map:
            self._map[parent_str] = DerivationNode(parent_str)
        self._map[parent_str].add_derived(phrase.full_phrase)

    def get_derived(self, parent_str):
        return self._map[parent_str] if parent_str in self._map else None

    def print_tree(self):
        print('{')
        for key in sorted(self._map.keys()):
            print("'" + key + "': '" + str(self._map[key]))
        print('}')
        print("custom=" + str(self._custom))
        print("regular=" + str(self._regular))
        print('{')
        for key in sorted(self._irregular.keys()):
            print("'" + key + "': '" + str(self._irregular[key]))
        print('}')

    def custom(self):
        return self._custom

    def irregularity(self, conjugation_override_key):
        # the dictionary(s) loaded may not have an example of the irregularity in question.
        if conjugation_override_key in self._irregular:
            return self._irregular[conjugation_override_key].derived
        else:
            return []

    def regular(self):
        return self._regular


DerivationTree = DerivationTree_()
"""
load dictionaries/*-verbs.csv
load dictionaries/*-phrases.csv
----
in user directory
load cs_dictionaries/*-verbs.csv
load cs_dictionaries/*.csv
"""


class LanguageDictionary_(dict):
    def __init__(self):
        super().__init__()
        self.by = {}

    def load(self, fileName, source):
        current = self.by[source] = []
        cs_debug("loading dictionary", fileName)
        with codecs.open(fileName, mode='r', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            count = 0
            for line in reader:
                try:
                    definition = {'definition': ''}
                    for key, value in line.items():
                        _value = make_unicode(value)
                        if _value != '' and _value is not None:
                            definition[make_unicode(key)] = _value
                    try:
                        phrase = self.add(force_add=True, **definition)
                        current.append(phrase.full_phrase)
                        count += 1
                    except Exception as e:
                        cs_debug("error reading ", fileName + ": ", repr(definition), repr(e))
                        traceback.print_exc()
                except Exception as e:
                    cs_debug("error reading ", fileName, ": line=", repr(line), repr(e))
                    traceback.print_exc()
        cs_debug("loaded dictionary", fileName, " (", str(count), "items)")


# declare up here so Verb_Dictionary_() can access
Verb_Dictionary = None


class Verb_Dictionary_(LanguageDictionary_):
    VERBS_FILENAME = re_compile('(.*)-verbs.csv$')

    def add(self, phrase, definition='', generated=False, force_add=False, **kwargs):
        conjugation_overrides = kwargs.get('conjugation_overrides')
        if force_add or self._build_replacement_if_better(phrase, conjugation_overrides=conjugation_overrides,
                                                          generated=generated):
            verb = Verb.importString(phrase, definition, generated=generated, **kwargs)
            verb.verb_finder = self
            self[verb.full_phrase] = verb
            DerivationTree.add_phrase(verb)
            if verb.is_derived:
                cs_debug(
                    verb.full_phrase + " is derived from " + verb.root_verb_string + " base =" + verb.base_verb_string,
                    " conjugation_overrides=" + str(conjugation_overrides))
                verb.root_verb = self.add(verb.root_verb_string, conjugation_overrides=conjugation_overrides,
                                          generated=True)
                verb.base_verb = self.add(verb.base_verb_string, conjugation_overrides=conjugation_overrides,
                                          root_verb=verb.root_verb_string, generated=True)

        else:
            if not generated:
                cs_debug("Verb_Dictionary :", phrase, "already in dictionary")
            verb = self[phrase]

        return verb

    def get(self, phrase, default_=None):
        verb = super().get(phrase, default_)
        if verb is None:
            cs_debug("No verb with " + phrase)
            verb = Storage.get_phrase(phrase)
            if verb is not None:
                self[phrase] = verb
        return verb

    def processAllVerbs(self):
        for phrase, verb in self.items():
            if verb.is_derived:
                root_verb = self.get(verb.root_verb_string, None)

                if root_verb is None:
                    cs_debug(">>>> Missing root " + str(verb))
                else:
                    root_verb.process_conjugation_overrides()
                    verb.root_verb = root_verb
                base_verb = self.get(verb.base_verb_string, None)

                if base_verb is None:
                    cs_debug(">>>>>> Base verb missing")
                else:
                    verb.base_verb = base_verb
                    base_verb.process_conjugation_overrides()
            verb.process_conjugation_overrides()

    def _build_replacement_if_better(self, phrase, conjugation_overrides, generated):
        if phrase not in self:
            verb = Storage.get_phrase(phrase=phrase)
            if verb is not None:
                self[phrase] = verb
                cs_debug("found ", phrase)
                return False

            return True

        current_verb = self[phrase]
        if not current_verb.is_generated:
            if generated:
                return False
            else:
                cs_debug(phrase + ":both claiming to not be generated")
                return False
        elif generated:
            if conjugation_overrides is None or len(conjugation_overrides) == 0:
                return False

            if current_verb.is_regular:
                return True
            else:
                # both generated -- which one has the best conjugation overrides
                cs_debug(current_verb.full_phrase + ": both are irregular")
                return False
        else:
            return True

    def filename_match(self, fileName):
        return Verb_Dictionary_.VERBS_FILENAME.match(fileName)

    def list_generated(self):
        for verb in self.values():
            if verb.is_generated:
                print(verb.full_phrase)

    #     def load(self):
    #         basedir = os.path.dirname(os.path.realpath(__file__))
    #         dictionaryDirectory = basedir+u'/dictionaries/'
    #         print(u"current directory=",basedir)
    #         for fileNameBase in [u'501verbs',u'501extendedverbs']:
    #             fileName = dictionaryDirectory+fileNameBase+u'.csv'
    #             verbs = []
    #             if fileNameBase == u'501verbs':
    #                 verbs.extend([u'haber',u'ser',u'ir',u'irse',u'hacer',u'estar'])
    #             self.by[fileNameBase] = verbs
    #             self.load_verbs(fileName, verbs)

    def export(self, source, outputfile=None, testfn=lambda **kwargs: True):
        if outputfile is None:
            outputfile = source
        _outputfile = './conjugate_spanish/expanded/' + outputfile + '-verbs-only.csv'

        with codecs.open(_outputfile, "w", "utf-8") as f:
            f.write("full_phrase")
            for tense in Tense.all():
                if tense in Tense.Person_Agnostic():
                    f.write(',' + tense)
                else:
                    for person in Person.all():
                        f.write(',' + tense + "_" + person)
            f.write('\n')
            for phrase in self.by[source]:
                verb = self.get(phrase)
                call = {"verb": verb}
                if testfn(**call):
                    cs_debug("conjugating>>" + verb.full_phrase)
                    f.write(verb.print_csv(False))
                    f.write("\n")


class Phrase_Dictionary_(LanguageDictionary_):
    PHRASES_FILENAME = re_compile('(.*)-phrases.csv$')

    def add(self, phrase, definition, associated_verbs=None, **kwargs):
        # TODO: Should be able to handle conjugated phrases as well.
        phraseObj = NonConjugatedPhrase(phrase, definition, associated_verbs, **kwargs)
        if phrase in self:
            print("Phrase_Dictionary :" + phrase + " already in dictionary")
        else:
            self[phraseObj.full_phrase] = phraseObj
        return phraseObj

    def filename_match(self, fileName):
        return Phrase_Dictionary_.PHRASES_FILENAME.match(fileName)


class Espanol_Dictionary_():
    def __init__(self):
        self.verbDictionary = Verb_Dictionary_()
        self.phraseDictionary = Phrase_Dictionary_()

    def load(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        for path in [basedir + '/dictionaries', '.']:
            filelist = os.listdir(path)
            for fileName in filelist:
                verbMatch = self.verbDictionary.filename_match(fileName)
                phraseMatch = self.phraseDictionary.filename_match(fileName)
                if verbMatch is not None:
                    self.verbDictionary.load(path + '/' + fileName, verbMatch.group(1))
                elif phraseMatch is not None:
                    self.phraseDictionary.load(path + '/' + fileName, phraseMatch.group(1))
        self.verbDictionary.processAllVerbs()

    def add_verb(self, phrase, definition, **kwargs):
        self.verbDictionary.add(phrase, definition, **kwargs)

    def add_phrase(self, phrase, definition, **kwargs):
        self.phraseDictionary.add(phrase, definition, **kwargs)

    def get_phrases(self):
        return self.phraseDictionary.keys();

    def get_verbs(self):
        return self.verbDictionary.keys();

    def get_phrase(self, phrase):
        return Storage.get_phrase(phrase)

    def get(self, phrase):
        verb = self.verbDictionary.get(phrase)
        if verb is None:
            return self.phraseDictionary.get(phrase)
        else:
            return verb

    def get_derived_definitions(self, phrase_str):
        if isinstance(phrase_str, str):
            return DerivationTree.get_derived(phrase_str)

    def get_derived(self, phrase_str):
        derivation_node = self.get_derived_definitions(phrase_str)
        derived = list(derivation_node.derived) if derivation_node is not None else []
        derived.append(phrase_str)
        return derived

    def get_by_irregularity(self, *, irregular_nature=IrregularNature.custom, conjugation_override_key=None):
        if irregular_nature == IrregularNature.custom:
            return DerivationTree.custom()
        else:
            return DerivationTree.irregularity(conjugation_override_key)

    def list_generated(self):
        return self.verbDictionary.list_generated()


Espanol_Dictionary = Espanol_Dictionary_()
Verb_Dictionary = Espanol_Dictionary.verbDictionary
Phrase_Dictionary = Espanol_Dictionary.phraseDictionary
