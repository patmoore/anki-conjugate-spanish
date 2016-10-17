# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal
from aqt.qt import QAction, QProgressDialog

from anki.hooks import addHook, wrap, remHook
from aqt import mw
from anki.lang import _
from anki.notes import Note
from aqt.editor import Editor
from aqt.utils import askUser, showInfo, shortcut
# import all of the Qt GUI library
from aqt.qt import *
from conjugate_spanish.verb import Verb
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
from conjugate_spanish.storage import Storage
from conjugate_spanish.anki_integration.model_template import PHRASE_MODEL, VERB_SHORT_MODEL

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
        self.addon_menu_name = "Español Conjugation"        
        self.modelName = modelName
        # HACK should really be ModelDefinitions
        self.modelTemplates = {}
        self.mw = mw
        addHook('editFocusGained', self.editFocusGained)
        addHook('setupEditorButtons', self.setupEditorButtons)
        addHook('editFocusLost', self.onFocusLost)
        addHook('profileLoaded', self.initialize)
        
    def createNewDeck(self, deckName):
        """
        TODO figure out how to refresh the main window screen.
        """
#         deckName += str(intTime())
        # will create deck if it doesn't exist (mw.col.decks is a DeckManager)
        deck_id = mw.col.decks.id(deckName)
        return deck_id
    
    def createDefaultConjugationOverride(self, note):        
        note['Conjugation Overrides'] = Verb.importString(note['Text']).overrides_string
            
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
        modelTemplate = ModelDefinitions.getModelTemplate(note.model(), False)
        #look for required - doesn't anki have code for this?
        inf_field = modelTemplate.getFieldIndex(ModelTemplate_.INFINITIVE_OR_PHRASE)
        conjugationoverrides_field = modelTemplate.getFieldIndex(ModelTemplate_.CONJUGATION_OVERRIDES)
        if currentFieldIndex == inf_field and note.fields[inf_field] != '' and note.fields[conjugationoverrides_field] == '':
            # don't generate unless leaving infinitive field
            phrase = Storage.get_phrase_from_note(note)
            if phrase is None:
                cs_debug("No phrase for note "+note.id)
            # TODO: allow changes?                
            ##TODO: save() <<<,
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
        """
        HACK- should be part of ModelDefinitions
        """
        _model_name = ModelDefinitions.model_name(modelName)
        return self.modelTemplates.get(_model_name, None)
    
    def setupEditorButtons(self, editor=None, *args):
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
        
#     def setDeckNoteType(self, deck):
#         model = self.getModelTemplate(self.modelName)
#         deck_ = self._getDeck(deck)
#         deck_['mid'] = model['id']
#         self._saveDeck(deck_)
    
    def _getDeck(self, deck):
        from aqt import mw
        if isinstance(deck, str):
            deckId = mw.col.decks.id(deck)             
        elif isinstance(deck, int):
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
        
    def initialize(self, *args):
        cs_debug("initialize")
        self.menu_ = self.mw.form.menuPlugins.addMenu(self.addon_menu_name)        

## TODO: I saw code like this in the japanese addon : but the models are not created 
## maybe only on installation?
# for modelName, modelDefinition in ModelDefinitions.iteritems():
#     def __makecall(modelName, modelDefinition):
#         return lambda col: ModelTemplate_(modelName, collection=col, **modelDefinition)
#     anki.stdmodels.models.append((_(modelName), __makecall(modelName, modelDefinition)))
        # Make sure our standard models are defined.
        for modelName, modelDefinition in ModelDefinitions.items():
            cs_debug("model ",modelName)
            self.modelTemplates[modelName] = ModelDefinitions.getModelTemplate(modelName, collection=mw.col, create=True, **modelDefinition)
            
        FEATURES = [
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
            {
                'key': 'conjugate_note',
                'menu': 'Conjugate a note',  
                'disable': True,          
                'init': self.createConjugateMenu,
            },
            {
                'key': 'load_dictionary',
                'menu': 'Load a dictionary',            
                'init': self.createLoadMenu,
            },
            {
                'key': 'create_phrase_notes',
                'menu': 'create phrase notes',            
                'init': self.createAllNotesMenu,
            },
            {
                'key': 'create_verb_notes',
                'menu': 'create verb notes',            
                'init': self.createAllVerbNotesMenu,
            },
            {
                'key':'resetdb',
                'menu': 'reset database',            
                'init': self.resetDbMenu,
            }
        ]
    
        for value in FEATURES:
            if value.get('disable') != True:
                value['init'](value)
#         remHook('profileLoaded', AnkiIntegration.initialize)

#     def createNewDeckMenu(self, key, definition):
#         self.addMenuItem(definition[u'menu'], self.createNewDeck)
        
    def menu_remove_all_notes(self, *args, **kwargs):
        Storage.remove_notes()

    def createConjugateMenu(self, definition):        
        self.addMenuItem(definition['menu'], self.menu_conjugateCurrentNote)
        
    def menu_loadDictionary(self,x):
        cs_debug("load_dic", x)
        Espanol_Dictionary.load()
        Storage.upsertPhrasesToDb(*Espanol_Dictionary.phraseDictionary.values())
        Storage.upsertPhrasesToDb(*Espanol_Dictionary.verbDictionary.values())

    def createLoadMenu(self, definition):
        self.addMenuItem(definition['menu'], self.menu_loadDictionary)

    def menu_createNotes(self, *args, **kwargs):
        model_name = PHRASE_MODEL
        modelTemplate = self._getModelTemplateByName(model_name)
        self.createNewDeck(model_name)
        for phrase in Espanol_Dictionary.get_phrases():
            note = modelTemplate.verbToNote(phrase)
            mw.col.addNote(note)
            Storage.connect_phrase_to_note(phrase, note)
                
    def _create_Notes_Menu(self, modelName, irregular_only=True, *args):
        modelTemplate = self._getModelTemplateByName(modelName)
        for phrase in Espanol_Dictionary.get_verbs():
            note = modelTemplate.verbToNote(phrase, irregular_only)
            mw.col.addNote(note)
            Storage.connect_phrase_to_note(phrase, note)                
    
    def createAllNotesMenu(self, definition):
        self.addMenuItem(definition['menu'], self.menu_createNotes)
    
    def createAllVerbNotesMenu(self, definition):
#         for person in Persons.all:
#             self.addMenuItem(Persons.human_readable(person), lambda *args: self._create_Notes_Menu(Persons[person], False, *args))
#         for tense in Tenses.all:
#             self.addMenuItem(Tenses.human_readable(tense), lambda *args: self._create_Notes_Menu(Tenses[tense], False, *args))
        
        self.addMenuItem(definition['menu'], lambda *args: self._create_Notes_Menu(FULLY_CONJUGATED_MODEL, False, *args))
         
    def resetDb_(self, *args, **kwargs):
        Storage.resetDb()

    def resetDbMenu(self, definition):
        self.addMenuItem(definition['menu'], self.resetDb_)
    
AnkiIntegration = AnkiIntegration_()
