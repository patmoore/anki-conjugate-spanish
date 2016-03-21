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
from verb import Verb
import six
from anki.notes import Note

__all__ = [ 'AnkiIntegration']
MODEL_FIELDS = {
    u'font': u'Arial',
    u'media': [],
    u'name': u'phraseField',
    u'ord': 0,
    u'rtl': False,
    u'size': 20,
    u'sticky': False
}

INFINITIVE_OR_PHRASE = u'Infinitive or Phrase'
ENGLISH_DEFINITION = u'English definition'
CONJUGATION_OVERRIDES = u'Conjugation Overrides'

class CardTemplate_(dict):
    """
    This class is mostly here to document the way that anki works.
    """
    def __init__(self, model=None, **kwargs):
        super(CardTemplate_, self).__init__({
            u'name': u'',
            u'qfmt': u'', 
            u'afmt': u'', 
            u'did': None, 
            u'bafmt': u'', 
            u'bqfmt': u'',
            u'ord': 0
        })
        self.update(kwargs)
        self.model = model
    @property
    def name(self):
        return self[u'name']
    @name.setter
    def setName(self, name):
        self[u'name'] = name
    @property
    def questionFormat(self):
        return self[u'qfmt']
    @questionFormat.setter
    def setQuestionFormat(self, qfmt):
        self[u'qfmt'] = qfmt
    @property
    def answerFormat(self):
        return self[u'afmt']
    @answerFormat.setter
    def setAnswerFormat(self, afmt):
        self[u'afmt'] = afmt
    @property
    def backQuestionFormat(self):
        return self[u'bqfmt']
    @backQuestionFormat.setter
    def setBackQuestionFormat(self, bqfmt):
        self[u'bqfmt'] = bqfmt
    @property
    def backAnswerFormat(self):
        return self[u'bafmt']
    @backAnswerFormat.setter
    def setBackAnswerFormat(self, bafmt):
        self[u'bafmt'] = bafmt
    
    def add(self, model=None):
        model_ = model if model is not None else self.model
        templates = model_[u'tmpls']
        self[u'ord'] = len(templates)
        templates.append(self)
        
TEMPLATE_FIELDS = {
    u'name': u'Card 1',
    u'qfmt': u'{{Front}}', 
    u'did': None, 
    u'bafmt': u'', 
    u'afmt': u'{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}', 
    u'ord': 0, 
    u'bqfmt': u''
}
"""
Plan:
1. Define standard espanol card conjugation: stores fields that are represented in the Verb card. (string representations of co)
2. conjugation cards have parent card id stored.

NOTES: Anki Note objects have the information. Anki Card" are generated from Note
"""
class AnkiIntegration_(object):
    
    def __init__(self, modelName=u'Español Verbs-1'):
        self.modelName = modelName
        addHook('editFocusGained', self.editFocusGained)
        addHook('setupEditorButtons', self.setupEditorButtons)
        
    def _createModel(self):
        """
        see if we can generate card templates automatically
        """
        model = self._getModel(self.modelName) 
        if model is None:
            model = self._getModel(self.modelName, True)       
            fields = model[u'flds'] = []
            phraseField = dict(MODEL_FIELDS)
            phraseField[u'name'] = INFINITIVE_OR_PHRASE
            self.addToList(fields,phraseField)
            
            definition = dict(MODEL_FIELDS)
            definition[u'name'] = ENGLISH_DEFINITION
            self.addToList(fields,definition)
            #How to provide help text? 
            conjugationOverrides = dict(MODEL_FIELDS)
            conjugationOverrides[u'name'] = CONJUGATION_OVERRIDES
            self.addToList(fields, conjugationOverrides)
            mw.col.models.add(model)
            mw.col.models.flush()
    def _createTemplates(self, model):
        card = CardTemplate_(model)
        card.name = u'Conjugation Overrides'
        card.questionFormat = u'{{'
        self.addToList(templates, card)
    
    def createDefaultConjugationOverride(self, note):        
        note[u'Conjugation Overrides'] = Verb(note[u'Text']).overrides_string
        
    def editFocusGained(self, *args):
        if len(args) == 0 or not self.isConjugationNote(args[0]):
            return
        note = args[0]
        pass
        # TODO test for a spanish model
        
    def isConjugationNote(self, note):
        return isinstance(note, Note) and note.model()[u'name'] == self.modelName
    
    def onFoo(self, *args):
        pass
    
    def setupEditorButtons(self, *args):
        if len(args) == 0 or not isinstance(args[0], Editor):
            return
        editor = args[0]
        b = editor._addButton
        b("foo", self.onFoo, "",
          shortcut(_("Customize onFoo")), size=False, text=_("onFoo..."),
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
    
        
    def setDeckNoteType(self, deck, noteTypeName):
        model = self._getModel(noteTypeName)
        deck_ = self._getDeck(deck)
        deck_['mid'] = model['id']
        self._saveDeck(deck_)
    
    def _getDeck(self, deck):
        global mw
        if isinstance(deck, six.string_types):
            deckId = mw.col.decks.id(deck)             
        elif isinstance(deck, six.integer_types):
            deckId = deckId
        else:            
            return deck
        deck_ = mw.col.decks.get(deckId)
        return deck_
        
    def _getModel(self, model, create=False):
        global mw
        if isinstance(model, six.string_types):
            model_ = mw.col.models.byName(model)
            if model_ is None and create:
                model_ = mw.col.models.new(model)
        else:
            return model
        return model_
    
    def _saveDeck(self, deck):
        mw.col.decks.save(deck)
        
    def addMenuItem(self, menuString, func):
        global mw
        # create a new menu item, "test"
        action = QAction(menuString, mw)
        # set it to call testFunction when it's clicked
        mw.connect(action, SIGNAL("triggered()"), func)
        # and add it to the tools menu
        mw.form.menuTools.addAction(action)
        
    def addToList(self, list, item):
        item[u'ord'] = len(list)
        list.append(item)

AnkiIntegration = AnkiIntegration_()   
def AnkiIntegration_initialize(*args):
    global AnkiIntegration
    AnkiIntegration._createModel()
       
    def enterNewVerbInit(key, definition):
        global AnkiIntegration
        def testFunction():
            global mw
            global showInfo
            AnkiIntegration._createModel()
            # get the number of cards in the current collection, which is stored in
            # the main window
            cardCount = mw.col.cardCount()
            deckName = u'ImportDeck'
            # will create deck if it doesn't exist (mw.col.decks is a DeckManager)
            did = mw.col.decks.id(deckName)
            # show a message box
            showInfo("Card count: {0}, deck id={1}".format(cardCount,did))
        
        AnkiIntegration.addMenuItem(definition[u'menu'], testFunction)
    
    FEATURES = {
        u'new_verb': {
            u'menu': u'Enter new verb or phrase',
            u'help': u'create a new verb',
            u'init' : enterNewVerbInit
        },
        u'create_default_model': {
            u'menu': u'Create a new model',            
            u'disable': True
        },
    }
    
    for key,value in FEATURES.iteritems():
        if u'disable' not in value or value[u'disable'] == False:
            value[u'init'](key, value)
    
addHook(u'profileLoaded', AnkiIntegration_initialize)
