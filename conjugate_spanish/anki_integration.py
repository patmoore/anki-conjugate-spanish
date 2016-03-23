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
from anki.utils import intTime
from verb_dictionary import Verb_Dictionary_get
from constants import *

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
def addToList(list_, item):
    item[u'ord'] = len(list_)
    list_.append(item)
    
class ModelTemplate_(dict):
    """
    Used to combine a model with a verb
    """
    def __init__(self, model, **kwargs):
        super(ModelTemplate_, self).__init__(model)
    
    def createConjugationFields(self, tenses=Tenses.all, persons=Persons.all):
        for tense in tenses:
            if tense in Tenses.Person_Agnostic:
                self.createField(name=Tenses[tense])
            else:
                for person in persons:
                    self.createField(name=Tenses[tense]+' '+Persons[person])
                
    def createField(self, name):
        field = dict(MODEL_FIELDS)
        field[u'name'] = name
        self.addField(field)
        
    def addField(self, field):
        addToList(self[u'flds'],field)
        
    def addCard(self, card):
        addToList(self[u'tmpls'], card)
        
def td(string_):
    return u'<td>' + string_ + u'</td>'

class CardTemplate_(dict):
    STD_ANSWER_FORMAT = u'{{FrontSide}}\n\n<hr id=answer>\n\n'
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
    def name(self, name):
        self[u'name'] = name
    @property
    def questionFormat(self):
        return self[u'qfmt']
    @questionFormat.setter
    def questionFormat(self, qfmt):
        self[u'qfmt'] = qfmt
    @property
    def answerFormat(self):
        return self[u'afmt']
    @answerFormat.setter
    def answerFormat(self, afmt):
        self[u'afmt'] = afmt
    @property
    def backQuestionFormat(self):
        return self[u'bqfmt']
    @backQuestionFormat.setter
    def backQuestionFormat(self, bqfmt):
        self[u'bqfmt'] = bqfmt
    @property
    def backAnswerFormat(self):
        return self[u'bafmt']
    @backAnswerFormat.setter
    def backAnswerFormat(self, bafmt):
        self[u'bafmt'] = bafmt
    
    def add(self, model=None):
        model_ = model if model is not None else self.model
        model_.addCard(self)
        
    @classmethod
    def createConjugationOverrideCard(cls, model=None):
        card = CardTemplate_(model)
        card.name = u'Conjugation Overrides'
        card.questionFormat = u'{{'+INFINITIVE_OR_PHRASE+u'}}'
        card.answerFormat = CardTemplate_.STD_ANSWER_FORMAT + u'{{'+CONJUGATION_OVERRIDES+u'}}'
        return card

    @classmethod
    def createTenseCard(cls, tense, model=None):   
        def addCell(person):
            return td(Persons[person])+ td(u'{{'+Tenses[tense]+u' '+Persons[person]+u'}}')     
        card = CardTemplate_(model)        
        card.name = Tenses[tense]
        card.questionFormat = u'{{'+INFINITIVE_OR_PHRASE+u'}}'+u'<br>'+Tenses[tense]
        answer = CardTemplate_.STD_ANSWER_FORMAT+u'<table>\n'
        answer += u'<tr>'
        if tense in Tenses.Person_Agnostic:
            answer += td(u'{{'+Tenses[tense]+u'}}')            
        else:
            if tense in Tenses.imperative:
                answer+=td(u'')+addCell(Persons.first_person_plural)
            else:
                for person in Persons.first_person:
                    answer += addCell(person)
            answer += u'</tr>\n'
            answer += u'<tr>'
            for person in Persons.second_person:
                answer += addCell(person)
            answer += u'</tr>\n'
            answer += u'<tr>'
            for person in Persons.third_person:
                answer += addCell(person)
        answer += u'</tr>\n'
        answer += u'</table>'
        card.answerFormat = answer
        return card
        
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
            model[u'flds']=[]    
            modelT = ModelTemplate_(model)   
            modelT.createField(name=INFINITIVE_OR_PHRASE)
            
            modelT.createField(name=ENGLISH_DEFINITION)
            #How to provide help text? 
            modelT.createField(name=CONJUGATION_OVERRIDES)
            modelT.createConjugationFields()
            
            self._createTemplates(modelT)
            mw.col.models.add(modelT)
            mw.col.models.flush()
            
    def _createTemplates(self, model):
        card = CardTemplate_.createConjugationOverrideCard(model)
        card.add()
        for tense in Tenses.all:
            card = CardTemplate_.createTenseCard(tense, model)
            card.add()
        
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
        
    def setDeckNoteType(self, deck):
        model = self._getModel(self.modelName)
        deck_ = self._getDeck(deck)
        deck_[u'mid'] = model[u'id']
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
        
        
    def verbToNote(self, verb):
        note = Note(mw.col, model=self._getModel(self.modelName) )
        note[INFINITIVE_OR_PHRASE] = verb.full_phrase
        note[ENGLISH_DEFINITION] = verb.definition
        note[CONJUGATION_OVERRIDES] = verb.overrides_string
        for tense in Tenses.all:
            if tense in Tenses.Person_Agnostic:
                note[Tenses[tense]] = verb.conjugate(tense)
            else:
                for person in Persons.all:
                    conjugation = verb.conjugate(tense,person)
                    if conjugation is None:
                        """
                         HACK because anki can't handle None as a field value
                        "/Users/patmoore/Documents/Anki/addons/conjugate_spanish/anki_integration.py", line 324, in loadDictionary
                            mw.col.addNote(note)
                          File "/Users/patmoore/side-projects/anki/anki/collection.py", line 250, in addNote
                            cms = self.findTemplates(note)
                          File "/Users/patmoore/side-projects/anki/anki/collection.py", line 284, in findTemplates
                            avail = self.models.availOrds(model, joinFields(note.fields))
                          File "/Users/patmoore/side-projects/anki/anki/utils.py", line 265, in joinFields
                            return "\x1f".join(list)
                        TypeError: sequence item 3: expected string or Unicode, NoneType found
                        """
                        conjugation = u''
                    note[Tenses[tense]+' '+Persons[person]] = conjugation
        return note
        
    def loadDictionary(self):
        from verb_dictionary import Verb_Dictionary, Verb_Dictionary_load
        Verb_Dictionary_load()
        for key, verb in Verb_Dictionary.iteritems():
            note = self.verbToNote(verb)
            mw.col.addNote(note)

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
    
    def createNewDeckMenu(key, definition):
        AnkiIntegration.addMenuItem(definition[u'menu'], AnkiIntegration.createNewDeck)
    
    def createConjugateMenu(key, definition):
        AnkiIntegration.addMenuItem(definition[u'menu'], AnkiIntegration.conjugateCurrentNote)
        
    def createLoadMenu(key, definition):
        AnkiIntegration.addMenuItem(definition[u'menu'], AnkiIntegration.loadDictionary)
    FEATURES = {
        u'new_verb': {
            u'menu': u'Enter new verb or phrase',
            u'help': u'create a new verb',
            u'init' : enterNewVerbInit,
            u'disable': True
        },
        u'create_desk': {
            u'menu': u'Create a new deck',            
            u'init': createNewDeckMenu,
            u'disable': True
        },
        u'conjugate_note': {
            u'menu': u'Conjugate a note',            
            u'init': createConjugateMenu,
        },
        u'load_dictionary': {
            u'menu': u'Load a dictionary',            
            u'init': createLoadMenu,
        },
    }
    
    for key,value in FEATURES.iteritems():
        if u'disable' not in value or value[u'disable'] == False:
            value[u'init'](key, value)
    
addHook(u'profileLoaded', AnkiIntegration_initialize)
