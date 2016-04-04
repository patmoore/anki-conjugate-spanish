# -*- coding: utf-8 -*-
from __future__ import print_function
# These are the standard words (special case)
import codecs
import traceback
import csv
from verb import Verb
from constants import *

from conjugation_override import ConjugationOverride
import os
from test.test_decimal import directory

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
        with codecs.open(fileName, mode='r' ) as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            try:
                for line in reader:
                    definition = {u'definition':u''}
                    for key,value in line.iteritems():
                        _value = make_unicode(value)
                        if _value != u'' and _value is not None:
                            definition[make_unicode(key)] = _value 
                    try:
                        phrase = self.add(**definition)
                        current.append(phrase.full_phrase)
                        print (phrase.full_phrase)
                    except Exception as e:
                        print("error reading "+fileName+": "+ repr(definition)+ repr(e))
                        traceback.print_exc()            
            except Exception as e:
                print("error reading "+fileName+": "+e.message+" line="+repr(line), repr(e))
                traceback.print_exc()

class Verb_Dictionary_(Dictionary_):
                            
    def add(self, phrase, definition, conjugation_overrides=None,base_verb=None, manual_overrides=None, **kwargs):
        verb = Verb(phrase, definition,conjugation_overrides=conjugation_overrides, base_verb=base_verb, manual_overrides=manual_overrides)  
        if phrase in self:
            print(phrase+" already in dictionary")
        else:      
            self[verb.full_phrase] = verb
        return verb

    def load(self):
        import special_cases
        basedir = os.path.dirname(os.path.realpath(__file__))
        dictionaryDirectory = basedir+u'/dictionaries/'
    #     print(u"current directory=",basedir)
        for fileNameBase in [u'501verbs',u'501extendedverbs']:
            fileName = dictionaryDirectory+fileNameBase+u'.csv'
            verbs = []
            if fileNameBase == u'501verbs':
                verbs.extend([u'hacer',u'ser',u'ir',u'irse',u'hacer',u'estar'])
            self.by[fileNameBase] = verbs
            self.load_verbs(fileName, verbs)
            
    def export(self, source, outputfile=None, testfn=lambda **kwargs:True):
        if outputfile is None:
            outputfile = source
        _outputfile = u'./conjugate_spanish/expanded/'+outputfile+u'-verbs-only.csv'
        
        with codecs.open(_outputfile, u"w", u"utf-8") as f:
            f.write(u"full_phrase")
            for tense in Tenses.all:
                if tense in Tenses.Person_Agnostic:
                    f.write(u','+Tenses[tense])
                else:
                    for person in Persons.all:
                        f.write(u','+Tenses[tense]+"_"+Persons[person])
            f.write(u'\n')
            for phrase in self.by[source]:
                verb = self.get(phrase)
                call = {u"verb":verb}
                if testfn(**call):   
                    print(u"conjugating>>"+verb.full_phrase)
                    f.write(verb.print_csv(False))
                    f.write(u"\n")

class Phrase_Dictionary_(Dictionary_):
    def add(self):
        pass
        
class Espanol_Dictionary_():
    VERBS_FILENAME = re_compile(u'(.*)-verbs.csv')
    PHRASES_FILENAME = re_compile(u'(.*)-phrases.csv')
    def __init__(self):
        self.verbDictionary = Verb_Dictionary_()
        self.phraseDictionary = Phrase_Dictionary_()
        
    def load(self):
        basedir = os.path.dirname(os.path.realpath(__file__))
        for path in [basedir, '.']:
            filelist = os.listdir(path)
            for fileName in filelist:
                verbMatch = Espanol_Dictionary_.VERBS_FILENAME.match(fileName)
                phraseMatch = Espanol_Dictionary_.PHRASES_FILENAME.match(fileName)
                if verbMatch is not None:
                    self.verbDictionary.load(fileName, verbMatch.group(1))
                elif phraseMatch is not None:
                    self.phraseDictionary.load(fileName, phraseMatch.group(1))


Espanol_Dictionary = Espanol_Dictionary_()
Verb_Dictionary = Espanol_Dictionary.verbDictionary
Phrase_Dictionary = Espanol_Dictionary.phraseDictionary