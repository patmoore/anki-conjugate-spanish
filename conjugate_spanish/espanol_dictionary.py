# -*- coding: utf-8 -*-

# These are the standard words (special case)
import codecs
import csv
from .verb import Verb
from .constants import *

import os
from .nonconjugated_phrase import NonConjugatedPhrase
from .utils import cs_debug
from .storage import Storage

"""
load dictionaries/*-verbs.csv
load dictionaries/*-phrases.csv
----
in user directory
load cs_dictionaries/*-verbs.csv
load cs_dictionari
"""
class Dictionary_(dict):
    def __init__(self):
        self.by = {}

    def load(self, fileName, source):
        current = self.by[source] = []
        cs_debug("loading dictionary",fileName)
        with codecs.open(fileName, mode='r',encoding="utf-8" ) as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            count = 0
            for line in reader:
                try:
                    definition = {'definition':''}
                    for key,value in line.items():
                        _value = make_unicode(value)
                        if _value != '' and _value is not None:
                            definition[make_unicode(key)] = _value 
                    try:
                        phrase = self.add(force_add=True,**definition)
                        current.append(phrase.full_phrase)
                        count += 1
                    except Exception as e:
                        cs_debug("error reading ",fileName+": ", repr(definition),repr(e))
                        traceback.print_exc()            
                except Exception as e:
                    cs_debug("error reading ",fileName,": line=",repr(line), repr(e))
                    traceback.print_exc()
        cs_debug("loaded dictionary",fileName," (",str(count),"items)")

class Verb_Dictionary_(Dictionary_):
    VERBS_FILENAME = re_compile('(.*)-verbs.csv$')                            
    def add(self, phrase, definition='', generated=False, force_add=False, **kwargs):
        conjugation_overrides=kwargs.get('conjugation_overrides')
        if force_add or self._build_replacement_if_better(phrase, conjugation_overrides=conjugation_overrides, generated=generated):
            verb = Verb.importString(phrase, definition, generated=generated, **kwargs)
            self[verb.full_phrase] = verb
            if verb.is_derived:
                cs_debug(verb.full_phrase+" is derived from "+verb.root_verb_string+" base ="+verb.base_verb_string, " conjugation_overrides="+str(conjugation_overrides))
                verb.root_verb = self.add(verb.root_verb_string, conjugation_overrides=conjugation_overrides,generated=True)
                verb.base_verb = self.add(verb.base_verb_string, conjugation_overrides=conjugation_overrides, root_verb=verb.root_verb_string,generated=True)
            
        else:
            if not generated:
                cs_debug("Verb_Dictionary :", phrase,"already in dictionary")        
            verb = self[phrase]
        
        return verb
    
    def get(self, phrase, default_ = None):
        verb = super().get(phrase, default_)
        if verb is None:
            print("No verb with " + phrase)
            verb = Storage.get_phrase(phrase)
            if verb is not None:
                self[phrase] = verb
        return verb
    
    def processAllVerbs(self):
        for phrase, verb in self.items():
            if verb.is_derived:
                root_verb = self.get(verb.root_verb_string, None)
                
                if root_verb is None:
                    cs_debug(">>>> Missing root "+verb)
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
                cs_debug("found ",phrase)
                return False
            
            return True
        
        current_verb = self[phrase]
        if not current_verb.is_generated:
            if generated:
                return False
            else:
                cs_debug(phrase+":both claiming to not be generated")
                return False
        elif generated:
            if conjugation_overrides is None or len(conjugation_overrides) == 0:
                return False
            
            if current_verb.is_regular:
                return True
            else:
                # both generated -- which one has the best conjugation overrides
                cs_debug("both are irregular")
                return False
        else:
            return True
    def filename_match(self, fileName):
        return Verb_Dictionary_.VERBS_FILENAME.match(fileName) 

#     def load(self):
#         import special_cases
#         basedir = os.path.dirname(os.path.realpath(__file__))
#         dictionaryDirectory = basedir+u'/dictionaries/'
#     #     print(u"current directory=",basedir)
#         for fileNameBase in [u'501verbs',u'501extendedverbs']:
#             fileName = dictionaryDirectory+fileNameBase+u'.csv'
#             verbs = []
#             if fileNameBase == u'501verbs':
#                 verbs.extend([u'haber',u'ser',u'ir',u'irse',u'hacer',u'estar'])
#             self.by[fileNameBase] = verbs
#             self.load_verbs(fileName, verbs)
            
    def export(self, source, outputfile=None, testfn=lambda **kwargs:True):
        if outputfile is None:
            outputfile = source
        _outputfile = './conjugate_spanish/expanded/'+outputfile+'-verbs-only.csv'
        
        with codecs.open(_outputfile, "w", "utf-8") as f:
            f.write("full_phrase")
            for tense in Tenses.all:
                if tense in Tenses.Person_Agnostic:
                    f.write(','+Tenses[tense])
                else:
                    for person in Persons.all:
                        f.write(','+Tenses[tense]+"_"+Persons[person])
            f.write('\n')
            for phrase in self.by[source]:
                verb = self.get(phrase)
                call = {"verb":verb}
                if testfn(**call):   
                    cs_debug("conjugating>>"+verb.full_phrase)
                    f.write(verb.print_csv(False))
                    f.write("\n")

class Phrase_Dictionary_(Dictionary_):
    PHRASES_FILENAME = re_compile('(.*)-phrases.csv$')
    def add(self,phrase, definition,associated_verbs=None,**kwargs):
        phraseObj = NonConjugatedPhrase(phrase, definition,associated_verbs,**kwargs)
        if phrase in self:
            print("Phrase_Dictionary :" + phrase+" already in dictionary")
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
        for path in [basedir+'/dictionaries', '.']:
            filelist = os.listdir(path)
            for fileName in filelist:
                verbMatch = self.verbDictionary.filename_match(fileName)
                phraseMatch = self.phraseDictionary.filename_match(fileName)
                if verbMatch is not None:
                    self.verbDictionary.load(path+'/'+fileName, verbMatch.group(1))
                elif phraseMatch is not None:
                    self.phraseDictionary.load(path+'/'+fileName, phraseMatch.group(1))
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

Espanol_Dictionary = Espanol_Dictionary_()
Verb_Dictionary = Espanol_Dictionary.verbDictionary
Phrase_Dictionary = Espanol_Dictionary.phraseDictionary
import conjugate_spanish.special_cases