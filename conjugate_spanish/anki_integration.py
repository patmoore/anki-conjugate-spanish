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
from verb_dictionary import Verb_Dictionary
from constants import *
import anki.stdmodels
import inspect
from functools import partial

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


def addToList(list_, item):
    item[u'ord'] = len(list_)
    list_.append(item)
    
def td(string_):
    return u'<td>' + string_ + u'</td>'

def iftest(variable, string_ = None):
    if string_ is None:
        string_ = u'{{' + variable +u'}}'
    return u'{{#'+variable+u'}}'+string_+u'{{/'+variable+u'}}'

class ModelTemplate_(object):
    INFINITIVE_OR_PHRASE = u'Infinitive or Phrase'
    ENGLISH_DEFINITION = u'English definition'
    CONJUGATION_OVERRIDES = u'Conjugation Overrides'
    MANUAL_CONJUGATION_OVERRIDES = u'Manual Conjugation Overrides'
    KEY = u'Key'
    ROOT_VERB = u'Root Verb'
    splitTensePerson = re_compile(u'(.*)/(.*)')
    """
    Used to create custom models for verbs
    """
    def __init__(self, model, fields=None, collection=None, **kwargs):
        global mw
        self.model = model
        if collection is None:
            collection = mw.col
        self.collection = collection
        self.modelManager = collection.models 
        self._changed = False       
        if fields is not None:
            for fieldDefinition in fields:
                fieldName = fieldDefinition[u'name']
                if not self.hasField(fieldName):
                    self._changed = True
                    field = self.createField(fieldName)
                    self.addField(field)
        
        self.model[u'sortf'] = self.getFieldIndex(ModelTemplate_.KEY)
        self._createTemplates()
        if self._changed: 
            self.save()
            self._changed = False           
        
    def createConjugationFields(self, tenses=Tenses.all, persons=Persons.all):
        for tense in tenses:
            if tense in Tenses.Person_Agnostic:
                self.createField(name=ModelTemplate_.fieldName(tense))
            else:
                for person in persons:
                    name = ModelTemplate_.fieldName(tense, person)
                    if name is not None:
                        self.createField(name=name)
        
    @classmethod        
    def fieldName(cls, tense, person=None):
        if tense in Tenses.Person_Agnostic:
            return Tenses[tense]+u'/-'
        elif tense not in Tenses.imperative or person != Persons.first_person_singular:
            return Tenses[tense]+'/'+Persons[person]
        else:
            return None
        
    def hasField(self, fieldName):
        fieldNames = self.modelManager.fieldNames(self.model)
        return fieldName in fieldNames
    
    def getFieldIndex(self, fieldName):
        fieldNames = self.modelManager.fieldNames(self.model)
        try:
            index = fieldNames.index(fieldName)
            return index
        except ValueError:
            return -1
                    
    def getFieldByIndex(self, index):
        return self.modelManager.fieldNames(self.model)[index]
    
    def createField(self, fieldName):
        field = self.modelManager.newField(fieldName)
        return field
        
    def addField(self, field):
        self.modelManager.addField(self.model,field)
        
    def addCard(self, cardTemplate):
        self.modelManager.addTemplate(self.model, cardTemplate.card)
        
    @classmethod
    def getModel(cls, model, create=False, **kwargs):
        global mw
        
        if isinstance(model, ModelTemplate_):
            return model
        elif isinstance(model, six.string_types):
            modelName = model
            model_ = mw.col.models.byName(modelName)
            if model_ is None:
                if not create:
                    return None
        else:
            modelName = BASE_MODEL
            
        if model_ is None:
            model_ = mw.col.models.new(name=modelName)
            
        if modelName in ModelDefinitions:            
            kwargs.update(ModelDefinitions[modelName])
            
        modelTemplate = ModelTemplate_(model=model_, **kwargs)
        return modelTemplate
    
    def verbToNote(self, verb, irregularOnly=True):
        conjugations = verb.conjugate_irregular_tenses() if irregularOnly else verb.conjugate_all_tenses()        
        note = Note(self.collection, model=self.model )
        for field in self.model[u'flds']:
            fieldName = field[u'name']
            if fieldName == ModelTemplate_.KEY:
                # TODO Some key
                value = verb.key
            elif fieldName == ModelTemplate_.INFINITIVE_OR_PHRASE:
                value = verb.full_phrase
            elif fieldName == ModelTemplate_.ENGLISH_DEFINITION:
                value = verb.definition
            elif fieldName == ModelTemplate_.CONJUGATION_OVERRIDES:
                value = verb.overrides_string
            elif fieldName == ModelTemplate_.MANUAL_CONJUGATION_OVERRIDES:
                value = verb.manualOverrides
            elif fieldName == ModelTemplate_.ROOT_VERB:
                value = verb.base_verb_str
            else:
                conjugation_match = ModelTemplate_.splitTensePerson.match(fieldName)
                if conjugation_match is not None:
                    tense = Tenses.index(conjugation_match.group(1))
                    if tense in Tenses.Person_Agnostic:
                        value = conjugations[tense] #verb.conjugate(tense)
                    else:
                        person = Persons.index(conjugation_match.group(2))
                        value = conjugations[tense][person] if conjugations[tense] is not None else None
                    
            if value is None:
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
                value = u''
            note[fieldName] = value
        return note
    
    def noteToVerb(self,note):
        phrase = note[ModelTemplate_.INFINITIVE_OR_PHRASE]
        key = note[ModelTemplate_.KEY] if ModelTemplate_.key in note else phrase
        definition = note[ModelTemplate_.ENGLISH_DEFINITION]
        conjugation_overrides = note[ModelTemplate_.CONJUGATION_OVERRIDES]
        # TODO 
        manual_overrides = note[ModelTemplate_.MANUAL_CONJUGATION_OVERRIDES]
        verb = Verb_Dictionary.get(key)
        if verb is None:
            verb = Verb_Dictionary.add(key, definition, conjugation_overrides, manual_overrides=manual_overrides)

    def save(self):
        if u'id' in self.model and self.model[u'id'] is not None:
            self.modelManager.update(self.model)
        else:
            self.modelManager.add(self.model)
            
    def getCard(self, cardName, create=False):
        for template in self.model[u'tmpls']:
            if template[u'name'] == cardName:
                return CardTemplate_(template)
        if create:
            card = self.modelManager.newTemplate(name=cardName)
            cardTemplate = CardTemplate_(card)
            if inspect.isfunction(create) or inspect.ismethod(create):
                create(cardTemplate)
            return cardTemplate
        return None
    
    @classmethod
    def isSpanishModel(cls, note):
        return note.model()[u'name'].find(SPANISH_PREFIX) >=0
    
    @property
    def name(self):
        return self.model[u'name']
    
    @property
    def isBaseModel(self):
        return self.name == BASE_MODEL
    
    def _createTemplates(self):
        card = self.createConjugationOverrideCard()
        for tense in Tenses.all:
            card = self.createTenseCard(tense)
    
    def createConjugationOverrideCard(self):
        cardName=u'Conjugation Overrides'
        def _create(cardTemplate):                
            cardTemplate.questionFormat = u'{{'+ModelTemplate_.INFINITIVE_OR_PHRASE+u'}}'
            answer = u'{{' + ModelTemplate_.ENGLISH_DEFINITION+u'}}' +\
                u'<br/>' + \
                iftest(ModelTemplate_.CONJUGATION_OVERRIDES) +\
                u'<br/>' +\
                iftest(ModelTemplate_.MANUAL_CONJUGATION_OVERRIDES) +\
                u'<br/>' +\
                iftest(ModelTemplate_.ROOT_VERB)  
            cardTemplate.answerFormat = answer
            self.addCard(cardTemplate)
            self._changed = True
            
        cardTemplate = self.getCard(cardName, create=_create)
        return cardTemplate

    def createTenseCard(self, tense):   
        def addCell(person):
            return iftest(Tenses[tense]+u' '+Persons[person],td(Persons[person])+ td(u'{{'+Tenses[tense]+u' '+Persons[person]+u'}}'))
        cardName = Tenses[tense]
        def _create(cardTemplate):
            cardTemplate.questionFormat = u'{{'+ModelTemplate_.INFINITIVE_OR_PHRASE+u'}}'+u'<br>'+Tenses[tense]
            answer = u'<table>\n'
            answer += u'<tr>'
            if tense in Tenses.Person_Agnostic:            
                answer += iftest(Tenses[tense], td(u'{{'+Tenses[tense]+u'}}'))            
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
            cardTemplate.answerFormat = answer
            self.addCard(cardTemplate)
            self._changed = True
        cardTemplate = self.getCard(cardName,create=True)
        return cardTemplate
    
class CardTemplate_(object):
    STD_ANSWER_FORMAT = u'{{FrontSide}}\n\n<hr id=answer>\n\n'
    """
    This class is mostly here to document the way that anki works.
    """
    def __init__(self, card, **kwargs):
        self.card =card
        
    @property
    def name(self):
        return self.card[u'name']
    @name.setter
    def name(self, name):
        self.card[u'name'] = name
    @property
    def questionFormat(self):
        return self.card[u'qfmt']
    @questionFormat.setter
    def questionFormat(self, qfmt):
        self.card[u'qfmt'] = qfmt
    @property
    def answerFormat(self):
        return self.card[u'afmt']
    @answerFormat.setter
    def answerFormat(self, afmt):
        self.card[u'afmt'] = CardTemplate_.STD_ANSWER_FORMAT + afmt
    @property
    def backQuestionFormat(self):
        return self.card[u'bqfmt']
    @backQuestionFormat.setter
    def backQuestionFormat(self, bqfmt):
        self.card[u'bqfmt'] = bqfmt
    @property
    def backAnswerFormat(self):
        return self.card[u'bafmt']
    @backAnswerFormat.setter
    def backAnswerFormat(self, bafmt):
        self.card[u'bafmt'] = bafmt
        
SPANISH_PREFIX = ADDON_PREFIX
BASE_MODEL = SPANISH_PREFIX+u'Verb'
FULLY_CONJUGATED_MODEL = SPANISH_PREFIX+u'Fully Conjugated Verb'
THIRD_PERSON_ONLY_MODEL = SPANISH_PREFIX+u'Third Person Only'

ModelDefinitions = { }
for modelName in [ BASE_MODEL, FULLY_CONJUGATED_MODEL, THIRD_PERSON_ONLY_MODEL]:
    ModelDefinitions[modelName] = {
        u'fields': [
            {u'name': ModelTemplate_.INFINITIVE_OR_PHRASE},
            {u'name': ModelTemplate_.ENGLISH_DEFINITION},
            {u'name': ModelTemplate_.CONJUGATION_OVERRIDES},
            {u'name': ModelTemplate_.MANUAL_CONJUGATION_OVERRIDES},
            {u'name': ModelTemplate_.ROOT_VERB},
            {u'name': ModelTemplate_.KEY},
        ]
    }

ModelDefinitions[BASE_MODEL][u'menuName'] = u'Conjugate Spanish:Basic'
ModelDefinitions[FULLY_CONJUGATED_MODEL][u'menuName'] = u'Conjugate Spanish:Full Conjugation'
ModelDefinitions[THIRD_PERSON_ONLY_MODEL][u'menuName'] = u'Conjugate Spanish:Third party only verbs'
for tense in Tenses.All_Persons:
    for person in Persons.all:
        ModelDefinitions[FULLY_CONJUGATED_MODEL][u'fields'].append({u'name':ModelTemplate_.fieldName(tense,person)})
for tense in Tenses.imperative:
    for person in Persons.all_except(Persons.first_person_singular):
        ModelDefinitions[FULLY_CONJUGATED_MODEL][u'fields'].append({u'name':ModelTemplate_.fieldName(tense,person)})
for tense in Tenses.Person_Agnostic:
    ModelDefinitions[FULLY_CONJUGATED_MODEL][u'fields'].append({u'name':ModelTemplate_.fieldName(tense)})

for tense in Tenses.All_Persons:
    for person in Persons.third_person:
        ModelDefinitions[THIRD_PERSON_ONLY_MODEL][u'fields'].append({u'name':ModelTemplate_.fieldName(tense,person)})
for tense in Tenses.imperative:
    for person in Persons.third_person:
        ModelDefinitions[THIRD_PERSON_ONLY_MODEL][u'fields'].append({u'name':ModelTemplate_.fieldName(tense,person)})
for tense in Tenses.Person_Agnostic:
    ModelDefinitions[THIRD_PERSON_ONLY_MODEL][u'fields'].append({u'name':ModelTemplate_.fieldName(tense)})

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
        OverridesDialog(editor.mw, editor.note, parent=editor.parentWindow)
        
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
        modelTemplate = self._getModelTemplateByName(BASE_MODEL)
        for key, verb in Verb_Dictionary.iteritems():
            note = modelTemplate.verbToNote(verb)
            mw.col.addNote(note)

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
