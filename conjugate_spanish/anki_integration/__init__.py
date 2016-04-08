# -*- coding: utf-8 -*-
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QAction, QProgressDialog

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
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
from conjugate_spanish.constants import *
import anki.stdmodels
import inspect
from functools import partial
from model_template import *

__all__ = [ 'AnkiIntegration']
"""
Plan:
1. Define standard espanol card conjugation: stores fields that are represented in the Verb card. (string representations of co)
2. conjugation cards have parent card id stored.

NOTES: Anki Note objects have the information. Anki Card" are generated from Note
"""
class AnkiIntegration_(object):
    
    def __init__(self, modelName=BASE_MODEL):
        self.modelName = modelName
        self.modelTemplates = {}
        addHook('editFocusGained', self.editFocusGained)
        addHook('setupEditorButtons', self.setupEditorButtons)
        addHook('editFocusLost', self.onFocusLost)
        
    def createNewDeck(self, deckName=u'Español Verbs'):
        """
        TODO figure out how to refresh the main window screen.
        """
        deckName += unicode(intTime())
        # will create deck if it doesn't exist (mw.col.decks is a DeckManager)
        did = mw.col.decks.id(deckName)
    
    def createDefaultConjugationOverride(self, note):        
        note[u'Conjugation Overrides'] = Verb(note[u'Text']).overrides_string
        
    def conjugateCurrentNote(self):
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
        if currentFieldIndex == inf_field and note.fields[inf_field] != u'' and note.fields[conjugationoverrides_field] == u'':
            # don't generate unless leaving infinitive field
            verb = Verb(note.fields[inf_field])
            note.fields[conjugationoverrides_field] = verb.overrides_string
            return True
        return flag
         
    def isConjugationNote(self, note):
        return isinstance(note, Note) and note.model()[u'name'] == self.modelName
    
    def _createNote(self, note, derivedModelName, irregularOnly):        
        modelTemplate = self._getNoteModelTemplate(note)
        if modelTemplate is not None:
            if modelTemplate.isBaseModel:
                modelName = FULLY_CONJUGATED_MODEL
                currentModelTemplate = self._getModelTemplateByName(derivedModelName)
                word_phrase_str = note[ModelTemplate_.INFINITIVE_OR_PHRASE]
                word_phrase = Verb_Dictionary.get(word_phrase_str)
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
        from ui.overrides import OverridesDialog
        editor.saveNow()
        verb_string = editor.note[ModelTemplate_.INFINITIVE_OR_PHRASE]
        verb = Verb_Dictionary.get(verb_string)
        OverridesDialog(editor.mw, editor.note, verb, parent=editor.parentWindow)
        
    def _getNoteModelTemplate(self, note):
        if note is not None and ModelTemplate_.isSpanishModel(note):
            modelName = note.model()[u'name']
            return self._getModelTemplateByName(modelName)
        
    def _getModelTemplateByName(self, modelName):
        if modelName in self.modelTemplates:
            return self.modelTemplates[modelName]
        else:
            return None
    def setupEditorButtons(self, editor=None, *args):
        if not isinstance(editor, Editor):
            return
        b = editor._addButton
        ## TODO: Should only be visible for BASE_MODEL verbs        
        ## TODO : canDisable=True means that the button starts disabled ( need a way to turn off visibility? )
        b(u"fullyConjugate", partial(self.onFullyConjugateVerb, editor), "",
          shortcut(_(u"Fully Conjugate")), size=False, text=_(u"Fully Conjugate Verb..."),
          native=True, canDisable=False)
        b(u"irregularConjugation", partial(self.onIrregularConjugateVerb, editor), "",
          shortcut(_(u"Irregular Conjugate")), size=False, text=_(u"Irregular Conjugate Verb..."),
          native=True, canDisable=False)
        b(u"overrides", partial(self.onConjugationOverrides, editor), "",
          shortcut(_(u"Conjugation Overrides")), size=False, text=_(u"Conjugation Overrides"),
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
        deck_[u'mid'] = model[u'id']
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
        from aqt import mw
        # create a new menu item, "test"
        action = QAction(menuString, mw)
        # set it to call testFunction when it's clicked
        mw.connect(action, SIGNAL("triggered()"), func)
        # and add it to the tools menu
        mw.form.menuTools.addAction(action)        
        
    def loadDictionary(self):
        Verb_Dictionary.load()
#         modelTemplate = self._getModelTemplateByName(BASE_MODEL)
#         for key, verb in Verb_Dictionary.iteritems():
#             note = modelTemplate.verbToNote(verb)
#             mw.col.addNote(note)

    def initialize(self, *args):
        for modelName, modelDefinition in ModelDefinitions.iteritems():
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
            u'conjugate_note': {
                u'menu': u'Conjugate a note',            
                u'init': self.createConjugateMenu,
            },
            u'load_dictionary': {
                u'menu': u'Load a dictionary',            
                u'init': self.createLoadMenu,
            },
        }
    
        for key,value in FEATURES.iteritems():
            if u'disable' not in value or value[u'disable'] == False:
                value[u'init'](key, value)
#     def createNewDeckMenu(self, key, definition):
#         self.addMenuItem(definition[u'menu'], self.createNewDeck)
    
    def createConjugateMenu(self, key, definition):
        self.addMenuItem(definition[u'menu'], self.conjugateCurrentNote)
        
    def createLoadMenu(self, key, definition):
        self.addMenuItem(definition[u'menu'], self.loadDictionary)

AnkiIntegration = AnkiIntegration_()
addHook(u'profileLoaded', AnkiIntegration.initialize)

## TODO: I saw code like this in the japanese addon : but the models are not created 
## maybe only on installation?
for modelName, modelDefinition in ModelDefinitions.iteritems():
    def __makecall(modelName, modelDefinition):
        return lambda col: ModelTemplate_(modelName, collection=col, **modelDefinition)
    anki.stdmodels.models.append((_(modelName), __makecall(modelName, modelDefinition)))
