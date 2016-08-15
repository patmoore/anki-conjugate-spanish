# -*- coding: utf-8 -*-

# These are the standard words (special case)
import codecs
import traceback
import csv
from .verb import Verb
from .constants import *

from .conjugation_override import ConjugationOverride
import os
from test.test_decimal import directory
from .nonconjugated_phrase import NonConjugatedPhrase

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
        print("conjugate_spanish::loading dictionary "+fileName)
        with codecs.open(fileName, mode='r' ) as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            try:
                count = 0
                for line in reader:
                    definition = {'definition':''}
                    for key,value in line.items():
                        _value = make_unicode(value)
                        if _value != '' and _value is not None:
                            definition[make_unicode(key)] = _value 
                    try:
                        phrase = self.add(**definition)
                        current.append(phrase.full_phrase)
                        count = count +1
                    except Exception as e:
                        print("error reading "+fileName+": "+ repr(definition)+ repr(e))
                        traceback.print_exc()            
            except Exception as e:
                print("error reading "+fileName+": "+e.message+" line="+repr(line), repr(e))
                traceback.print_exc()
        print("conjugate_spanish::loaded dictionary "+fileName+ " ("+str(count)+" items)")

class Verb_Dictionary_(Dictionary_):
                            
    def add(self, phrase, definition, conjugation_overrides=None,base_verb=None, manual_overrides=None, **kwargs):
        verb = Verb(phrase, definition,conjugation_overrides=conjugation_overrides, base_verb=base_verb, manual_overrides=manual_overrides)  
        if phrase in self:
            print("Verb_Dictionary :"+ phrase+" already in dictionary")
        else:      
            self[verb.full_phrase] = verb
        return verb

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
                    print("conjugating>>"+verb.full_phrase)
                    f.write(verb.print_csv(False))
                    f.write("\n")

class Phrase_Dictionary_(Dictionary_):
    def add(self,phrase, definition,associated_verbs=None,**kwargs):
        phraseObj = NonConjugatedPhrase(phrase, definition,associated_verbs,**kwargs)
        if phrase in self:
            print("Phrase_Dictionary :" + phrase+" already in dictionary")
        else:      
            self[phraseObj.full_phrase] = phraseObj
        return phraseObj

        
class Espanol_Dictionary_():
    VERBS_FILENAME = re_compile('(.*)-verbs.csv$')
    PHRASES_FILENAME = re_compile('(.*)-phrases.csv$')
    def __init__(self):
        self.verbDictionary = Verb_Dictionary_()
        self.phraseDictionary = Phrase_Dictionary_()
        
    def load(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        for path in [basedir+'/dictionaries', '.']:
            filelist = os.listdir(path)
            for fileName in filelist:
                verbMatch = Espanol_Dictionary_.VERBS_FILENAME.match(fileName)
                phraseMatch = Espanol_Dictionary_.PHRASES_FILENAME.match(fileName)
                if verbMatch is not None:
                    self.verbDictionary.load(path+'/'+fileName, verbMatch.group(1))
                elif phraseMatch is not None:
                    self.phraseDictionary.load(path+'/'+fileName, phraseMatch.group(1))

    def add_verb(self, phrase, definition, **kwargs):
        self.verbDictionary.add(phrase, definition, **kwargs)
    def add_phrase(self, phrase, definition, **kwargs):
        self.phraseDictionary.add(phrase, definition, **kwargs)

Espanol_Dictionary = Espanol_Dictionary_()
Verb_Dictionary = Espanol_Dictionary.verbDictionary
Phrase_Dictionary = Espanol_Dictionary.phraseDictionary