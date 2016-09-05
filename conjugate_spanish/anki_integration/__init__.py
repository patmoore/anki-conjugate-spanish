# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal
from aqt.qt import QAction, QProgressDialog

from anki.hooks import addHook, wrap
from aqt import mw
from anki.lang import _
from anki.notes import Note
from aqt.editor import Editor
from aqt.utils import askUser, showInfo, shortcut
# import all of the Qt GUI library
from aqt.qt import *
from conjugate_spanish.verb import Verb
import six
from anki.notes import Note
from anki.utils import intTime
from conjugate_spanish.espanol_dictionary import Espanol_Dictionary
from conjugate_spanish.constants import *
import anki.stdmodels
import inspect
from string import Template
from functools import partial
from .model_template import *
from conjugate_spanish.nonconjugated_phrase import NonConjugatedPhrase
import conjugate_spanish
from conjugate_spanish.utils import cs_debug

__all__ = [ 'AnkiIntegration']
"""
Plan: non conjugated phrases -- just create cards for the non-conjugated phrases

Plan:
1. Define standard espanol card conjugation: stores fields that are represented in the Verb card. (string representations of co)
2. conjugation cards have parent card id stored.

NOTES: Anki Note objects have the information. Anki Card" are generated from Note
"""
class AnkiIntegration_(object):    
    
    def __init__(self, modelName=BASE_MODEL):        
        self.modelName = modelName
        self.modelTemplates = {}
        self.mw = mw
        addHook('editFocusGained', self.editFocusGained)
        addHook('setupEditorButtons', self.setupEditorButtons)
        addHook('editFocusLost', self.onFocusLost)
        
    def createNewDeck(self, deckName='Español Verbs'):
        """
        TODO figure out how to refresh the main window screen.
        """
        deckName += str(intTime())
        # will create deck if it doesn't exist (mw.col.decks is a DeckManager)
        did = mw.col.decks.id(deckName)
    
    def createDefaultConjugationOverride(self, note):        
        note['Conjugation Overrides'] = Verb(note['Text']).overrides_string
        
    def conjugateCurrentNote(self, *args, **kwargs):
        cs_debug(args)
        cs_debug(kwargs.items())
        pass
    
    def showQuestion(self):
        pass
    
    def showAnswer(self):
        pass
    
    def editFocusGained(self, note, currentFieldIndex):
        # TODO test for a spanish model        
        pass
    
    def onFocusLost(self, flag, note, currentFieldIndex):
        """
        returning true will cause the note to be saved and refreshed
        """
        if not ModelTemplate_.isSpanishModel(note):
            return flag
        modelTemplate = ModelTemplate_(note.model())
        inf_field = modelTemplate.getFieldIndex(ModelTemplate_.INFINITIVE_OR_PHRASE)
        conjugationoverrides_field = modelTemplate.getFieldIndex(ModelTemplate_.CONJUGATION_OVERRIDES)
        if currentFieldIndex == inf_field and note.fields[inf_field] != '' and note.fields[conjugationoverrides_field] == '':
            # don't generate unless leaving infinitive field
            verb = Verb(note.fields[inf_field])
            note.fields[conjugationoverrides_field] = verb.overrides_string
            return True
        return flag
         
    def isConjugationNote(self, note):
        return isinstance(note, Note) and note.model()['name'] == self.modelName
    
    def _createNote(self, note, derivedModelName, irregularOnly):        
        modelTemplate = self._getNoteModelTemplate(note)
        if modelTemplate is not None:
            if modelTemplate.isBaseModel:
                modelName = FULLY_CONJUGATED_MODEL
                currentModelTemplate = self._getModelTemplateByName(derivedModelName)
                word_phrase_str = note[ModelTemplate_.INFINITIVE_OR_PHRASE]
                word_phrase = Espanol_Dictionary.verbDictionary.get(word_phrase_str)
                newNote = currentModelTemplate.verbToNote(word_phrase, irregularOnly)
                mw.col.addNote(newNote)
                
    def onFullyConjugateVerb(self, editor, *args):
        note = editor.note
        editor.saveNow()
        self._createNote(note, FULLY_CONJUGATED_MODEL, False)
            
    def onIrregularConjugateVerb(self, editor, *args):
        note = editor.note
        editor.saveNow()
        self._createNote(note, FULLY_CONJUGATED_MODEL, True)
        
    def onConjugationOverrides(self, editor):      
        from conjugate_spanish.ui.forms.overrides import Ui_Dialog  
        editor.saveNow()
        verb_string = editor.note[ModelTemplate_.INFINITIVE_OR_PHRASE]
        verb = Espanol_Dictionary.verbDictionary.get(verb_string)
        Ui_Dialog(editor.mw, editor.note, verb, parent=editor.parentWindow)
        
    def _getNoteModelTemplate(self, note):
        if note is not None and ModelTemplate_.isSpanishModel(note):
            modelName = note.model()['name']
            return self._getModelTemplateByName(modelName)
        
    def _getModelTemplateByName(self, modelName):
        if modelName in self.modelTemplates:
            return self.modelTemplates[modelName]
        else:
            return None
    def setupEditorButtons(self, editor=None, *args):
        import pdb; pdb.set_trace()
        if not isinstance(editor, Editor):
            return
        b = editor._addButton
        print("setting up editor")
        ## TODO: Should only be visible for BASE_MODEL verbs        
        ## TODO : canDisable=True means that the button starts disabled ( need a way to turn off visibility? )
        b("fullyConjugate", partial(self.onFullyConjugateVerb, editor), "",
          shortcut(_("Fully Conjugate")), size=False, text=_("Fully Conjugate Verb..."),
          native=True, canDisable=False)
        b("irregularConjugation", partial(self.onIrregularConjugateVerb, editor), "",
          shortcut(_("Irregular Conjugate")), size=False, text=_("Irregular Conjugate Verb..."),
          native=True, canDisable=False)
        b("overrides", partial(self.onConjugationOverrides, editor), "",
          shortcut(_("Conjugation Overrides")), size=False, text=_("Conjugation Overrides"),
          native=True, canDisable=False)
         
    def convertInfinitiveCardToConjugatedCards(self):
        """
        Given an infinitive or phrase - maybe existing
        conjugate the infinitive and generate supporting cards.
        
        Goal 1: regular only
        TODO: 
        1. how to connect generated cards with the infinitive?
        
        Goal 2: regular conjugation overrides        
        1. how to store conjugation overrides
        2. show the specific co's affect the conjugation
        3. generate just the specific tense/person with the exceptional behavior.
        
        Goal 3:   
        1. how to allow manual overrides?
        """
        pass
        
    def setDeckNoteType(self, deck):
        model = self.getModel(self.modelName)
        deck_ = self._getDeck(deck)
        deck_['mid'] = model['id']
        self._saveDeck(deck_)
    
    def _getDeck(self, deck):
        from aqt import mw
        if isinstance(deck, six.string_types):
            deckId = mw.col.decks.id(deck)             
        elif isinstance(deck, six.integer_types):
            deckId = deckId
        else:            
            return deck
        deck_ = mw.col.decks.get(deckId)
        return deck_
    
    def _saveDeck(self, deck):
        from aqt import mw
        mw.col.decks.save(deck)
        
    def addMenuItem(self, menuString, func):
        # create a new menu item, "test"
        action = QAction(menuString, self.mw, triggered=lambda x: func(x))
        # set it to call testFunction when it's clicked
        self.menu_.addAction(action)     
        
    def loadDictionary(self,x):
        print("load_dic", x)
        Espanol_Dictionary.load()
        self.upsertPhrasesToDb(Espanol_Dictionary.phraseDictionary.values())
        self.upsertVerbsToDb(Espanol_Dictionary.verbDictionary.values())
#         modelTemplate = self._getModelTemplateByName(BASE_MODEL)
#         for key, verb in Verb_Dictionary.iteritems():
#             note = modelTemplate.verbToNote(verb)
#             mw.col.addNote(note)

    def initialize(self, *args):
        print("conjugate spanish :: initialize")
        self.menu_ = self.mw.form.menuPlugins.addMenu("CONJUGATE")
        for modelName, modelDefinition in ModelDefinitions.items():
            self.modelTemplates[modelName] = ModelTemplate_.getModel(modelName, collection=mw.col, create=True, **modelDefinition)
            
#     def enterNewVerbInit(key, definition):
#         global AnkiIntegration
#         def testFunction():
#             global mw
#             global showInfo
#             AnkiIntegration._createModel()
#             # get the number of cards in the current collection, which is stored in
#             # the main window
#             cardCount = mw.col.cardCount()
#             deckName = u'ImportDeck'
#             # will create deck if it doesn't exist (mw.col.decks is a DeckManager)
#             did = mw.col.decks.id(deckName)
#             # show a message box
#             showInfo("Card count: {0}, deck id={1}".format(cardCount,did))
#         
#         AnkiIntegration.addMenuItem(definition[u'menu'], testFunction)
        FEATURES = {
#         u'new_verb': {
#             u'menu': u'Enter new verb or phrase',
#             u'help': u'create a new verb',
#             u'init' : enterNewVerbInit,
#             u'disable': True
#         },
#             u'create_desk': {
#                 u'menu': u'Create a new deck',            
#                 u'init': self.createNewDeckMenu,
#                 u'disable': True
#             },
            'conjugate_note': {
                'menu': 'Conjugate a note',            
                'init': self.createConjugateMenu,
            },
            'load_dictionary': {
                'menu': 'Load a dictionary',            
                'init': self.createLoadMenu,
            },
        }
    
        self._addSchema()
        for key,value in FEATURES.items():
            if 'disable' not in value or value['disable'] == False:
                value['init'](key, value)
#     def createNewDeckMenu(self, key, definition):
#         self.addMenuItem(definition[u'menu'], self.createNewDeck)
    
    def createConjugateMenu(self, key, definition):        
        self.addMenuItem(definition['menu'], self.conjugateCurrentNote)
        
    def createLoadMenu(self, key, definition):
        self.addMenuItem(definition['menu'], self.loadDictionary)

    def _addSchema(self):        
        # "phrase","definition", "prefix_words", "prefix", "core_characters", "inf_ending", "reflexive", "suffix_words"
        cs_debug(__file__, "addSchema")
        # "phrase","definition","conjugation_overrides","manual_overrides","synonyms","notes"
        dbFormatString = Template("""
            drop table if exists $conjugated_table_name;
            create table if not exists $conjugated_table_name (
                id                       integer primary key,
                phrase                   text not null unique,
                definition               text not null,
                prefix_words             text,
                prefix                   text,
                core_characters          text,
                inf_ending               text,
                reflexive                boolean,
                suffix_words             text,
                manual_overrides         text,
                synonyms                 text,
                notes                    text
            );
            drop table if exists ${table_prefix}conjugated_associations;
            create table if not exists ${table_prefix}conjugated_associations (
                ${conjugated_table_name}_root_id        integer null,
                ${conjugated_table_name}_root_phrase    text not null,
                ${conjugated_table_name}_derived_id     integer not null,
                FOREIGN KEY(${conjugated_table_name}_root_id) REFERENCES ${conjugated_table_name}(id),
                FOREIGN KEY(${conjugated_table_name}_derived_id) REFERENCES ${conjugated_table_name}(id)
            );
            drop table if exists ${table_prefix}conjugation_overrides;
            create table if not exists ${table_prefix}conjugation_overrides (
                id                           integer primary key,
                ${table_prefix}conjugation_overrides_key text not null,
                ${conjugated_table_name}_id                  integer,  
                FOREIGN KEY(${conjugated_table_name}_id) REFERENCES ${conjugated_table_name}(id)
            );
            drop table if exists ${nonconjugated_table_name};
            create table if not exists ${nonconjugated_table_name} (
                id                           integer primary key,
                phrase                       text not null unique,
                definition                   text not null
            );
            drop table if exists ${table_prefix}nonconjugated_associations;
            create table if not exists ${table_prefix}nonconjugated_associations(
                ${conjugated_table_name}_root_id        integer null,
                ${conjugated_table_name}_root_phrase    text not null,
                ${nonconjugated_table_name}_derived_id     integer not null,
                FOREIGN KEY(${conjugated_table_name}_root_id) REFERENCES ${conjugated_table_name}(id),
                FOREIGN KEY(${nonconjugated_table_name}_derived_id) REFERENCES ${nonconjugated_table_name}(id)
            );
        """)
        table_prefix="cs_"
        dbString = dbFormatString.substitute(conjugated_table_name=Verb.table_name(), nonconjugated_table_name=NonConjugatedPhrase.table_name(), table_prefix=table_prefix)
        cs_debug("dbString=",dbString)
        self.mw.col.db.executescript(dbString)
        mw.reset()
        
    def generate_insert_sql(self, cls):
        table_columns = cls.table_columns()
        table_columns_names = ",".join(table_columns)
        questions = ",".join(["?"] * len(cls.table_columns()))
        insert_sql = "insert or replace into "+cls.table_name()+"("+table_columns_names+") values ("+questions+")"
        return insert_sql
    
    def batch_insert(self, insert_sql, dbobjects):
        data = map(lambda dbobject: dbobject.sql_insert_values(), dbobjects)
        print(" insert_sql=",insert_sql)
        mw.col.db.executemany(insert_sql, data)
    
    def upsertPhrasesToDb(self, nonConjugatedPhrases):
        insert_sql = self.generate_insert_sql(NonConjugatedPhrase)
        self.batch_insert(insert_sql, nonConjugatedPhrases)
        for nc in nonConjugatedPhrases:
            "insert or replace into select id from nc where"
        for count in mw.col.db.execute("select count(*) from "+NonConjugatedPhrase.table_name()):
            cs_debug("Count = ",count)
 
    def upsertVerbsToDb(self, verbs):
        insert_sql = self.generate_insert_sql(Verb)
        self.batch_insert(insert_sql, verbs)
        for count in mw.col.db.execute("select count(*) from "+Verb.table_name()):
            cs_debug("Count = ",count)
    
AnkiIntegration = AnkiIntegration_()
addHook('profileLoaded', AnkiIntegration.initialize)


## TODO: I saw code like this in the japanese addon : but the models are not created 
## maybe only on installation?
# for modelName, modelDefinition in ModelDefinitions.iteritems():
#     def __makecall(modelName, modelDefinition):
#         return lambda col: ModelTemplate_(modelName, collection=col, **modelDefinition)
#     anki.stdmodels.models.append((_(modelName), __makecall(modelName, modelDefinition)))