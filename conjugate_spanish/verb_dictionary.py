# -*- coding: utf-8 -*-

# These are the standard words (special case)
import codecs
import csv
import re
from verb import Verb

Verb_Dictionary = {}
def Verb_Dictionary_add(inf_ending, definition):
    verb = Verb(inf_ending, definition)
    Verb_Dictionary[inf_ending] = verb


import special_cases

csvfile = codecs.open('./conjugate_spanish/dictionary.csv', 'r', 'utf8' )
reader = csv.reader(csvfile, delimiter=',')
try:
    # discard header
    csvfile.readline()
    for line in reader:
        Verb_Dictionary_add(line[0], line[1])
except:
    print "error reading dictionary.csv"