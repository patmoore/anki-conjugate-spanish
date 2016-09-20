# -*- coding: utf-8 -*-
from aqt.qt import QAction, QProgressDialog

from anki.hooks import addHook, wrap
from aqt import mw
from anki.lang import _
from anki.notes import Note
from aqt.editor import Editor
from aqt.utils import askUser, showInfo, shortcut
# import all of the Qt GUI library
from aqt.qt import *
import six
from anki.utils import intTime
from conjugate_spanish.espanol_dictionary import Verb_Dictionary
from conjugate_spanish.verb import Verb
from conjugate_spanish.constants import *
import anki.stdmodels
import inspect
from functools import partial

__all__ = [ 'ModelTemplate_', "CardTemplate_", 'BASE_MODEL','FULLY_CONJUGATED_MODEL', 'ModelDefinitions']
MODEL_FIELDS = {
    'font': 'Arial',
    'media': [],
    'name': 'phraseField',
    'ord': 0,
    'rtl': False,
    'size': 20,
    'sticky': False
}


def addToList(list_, item):
    item['ord'] = len(list_)
    list_.append(item)
    
def td(string_):
    return '<td>' + string_ + '</td>'

def iftest(variable, string_ = None):
    if string_ is None:
        string_ = '{{' + variable +'}}'
    return '{{#'+variable+'}}'+string_+'{{/'+variable+'}}'

class ModelTemplate_(object):
    INFINITIVE_OR_PHRASE = 'Infinitive or Phrase'
    ENGLISH_DEFINITION = 'English definition'
    CONJUGATION_OVERRIDES = 'Conjugation Overrides'
    MANUAL_CONJUGATION_OVERRIDES = 'Manual Conjugation Overrides'
    KEY = 'Key'
    ROOT_VERB = 'Root Verb'
    splitTensePerson = re_compile('(.*)/(.*)')
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
                fieldName = fieldDefinition['name']
                if not self.hasField(fieldName):
                    self._changed = True
                    field = self.createField(fieldName)
                    self.addField(field)
        
        self.model['sortf'] = self.getFieldIndex(ModelTemplate_.KEY)
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
            return Tenses[tense]+'/-'
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
        elif isinstance(model, str):
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
        # TODO:         
        note = Note(self.collection, model=self.model )
        for field in self.model['flds']:
            fieldName = field['name']
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
                value = verb.manual_overrides_string
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
                value = ''
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
        if 'id' in self.model and self.model['id'] is not None:
            self.modelManager.update(self.model)
        else:
            self.modelManager.add(self.model)
            
    def getCard(self, cardName, create=False):
        for template in self.model['tmpls']:
            if template['name'] == cardName:
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
        return note.model()['name'].find(SPANISH_PREFIX) >=0
    
    @property
    def name(self):
        return self.model['name']
    
    @property
    def isBaseModel(self):
        return self.name == BASE_MODEL
    
    def _createTemplates(self):
        card = self.createConjugationOverrideCard()
        for tense in Tenses.all:
            card = self.createTenseCard(tense)
    
    def createConjugationOverrideCard(self):
        cardName='Conjugation Overrides'
        def _create(cardTemplate):                
            cardTemplate.questionFormat = '{{'+ModelTemplate_.INFINITIVE_OR_PHRASE+'}}'
            answer = '{{' + ModelTemplate_.ENGLISH_DEFINITION+'}}' +\
                '<br/>' + \
                iftest(ModelTemplate_.CONJUGATION_OVERRIDES) +\
                '<br/>' +\
                iftest(ModelTemplate_.MANUAL_CONJUGATION_OVERRIDES) +\
                '<br/>' +\
                iftest(ModelTemplate_.ROOT_VERB)  
            cardTemplate.answerFormat = answer
            self.addCard(cardTemplate)
            self._changed = True
            
        cardTemplate = self.getCard(cardName, create=_create)
        return cardTemplate

    def createTenseCard(self, tense):   
        def addCell(person):
            return iftest(Tenses[tense]+' '+Persons[person],td(Persons[person])+ td('{{'+Tenses[tense]+' '+Persons[person]+'}}'))
        cardName = Tenses[tense]
        def _create(cardTemplate):
            cardTemplate.questionFormat = '{{'+ModelTemplate_.INFINITIVE_OR_PHRASE+'}}'+'<br>'+Tenses[tense]
            answer = '<table>\n'
            answer += '<tr>'
            if tense in Tenses.Person_Agnostic:            
                answer += iftest(Tenses[tense], td('{{'+Tenses[tense]+'}}'))            
            else:
                if tense in Tenses.imperative:
                    answer+=td('')+addCell(Persons.first_person_plural)
                else:
                    for person in Persons.first_person:
                        answer += addCell(person)
                answer += '</tr>\n'
                answer += '<tr>'
                for person in Persons.second_person:
                    answer += addCell(person)
                answer += '</tr>\n'
                answer += '<tr>'
                for person in Persons.third_person:
                    answer += addCell(person)
            answer += '</tr>\n'
            answer += '</table>'
            cardTemplate.answerFormat = answer
            self.addCard(cardTemplate)
            self._changed = True
        cardTemplate = self.getCard(cardName,create=True)
        return cardTemplate
    
class CardTemplate_(object):
    STD_ANSWER_FORMAT = '{{FrontSide}}\n\n<hr id=answer>\n\n'
    """
    This class is mostly here to document the way that anki works.
    """
    def __init__(self, card, **kwargs):
        self.card =card
        
    @property
    def name(self):
        return self.card['name']
    @name.setter
    def name(self, name):
        self.card['name'] = name
    @property
    def questionFormat(self):
        return self.card['qfmt']
    @questionFormat.setter
    def questionFormat(self, qfmt):
        self.card['qfmt'] = qfmt
    @property
    def answerFormat(self):
        return self.card['afmt']
    @answerFormat.setter
    def answerFormat(self, afmt):
        self.card['afmt'] = CardTemplate_.STD_ANSWER_FORMAT + afmt
    @property
    def backQuestionFormat(self):
        return self.card['bqfmt']
    @backQuestionFormat.setter
    def backQuestionFormat(self, bqfmt):
        self.card['bqfmt'] = bqfmt
    @property
    def backAnswerFormat(self):
        return self.card['bafmt']
    @backAnswerFormat.setter
    def backAnswerFormat(self, bafmt):
        self.card['bafmt'] = bafmt
        
SPANISH_PREFIX = ADDON_PREFIX
BASE_MODEL = SPANISH_PREFIX+'Verb'
FULLY_CONJUGATED_MODEL = SPANISH_PREFIX+'Fully Conjugated Verb'
THIRD_PERSON_ONLY_MODEL = SPANISH_PREFIX+'Third Person Only'

ModelDefinitions = { }

for modelName in [ BASE_MODEL, FULLY_CONJUGATED_MODEL, THIRD_PERSON_ONLY_MODEL]:
    ModelDefinitions[modelName] = {
        'modelName': modelName,
        'fields': [
            {'name': ModelTemplate_.INFINITIVE_OR_PHRASE},
            {'name': ModelTemplate_.ENGLISH_DEFINITION},
            {'name': ModelTemplate_.CONJUGATION_OVERRIDES},
            {'name': ModelTemplate_.MANUAL_CONJUGATION_OVERRIDES},
            {'name': ModelTemplate_.ROOT_VERB},
            {'name': ModelTemplate_.KEY},
        ]
    }

ModelDefinitions[BASE_MODEL]['menuName'] = 'Conjugate Spanish:Basic'
ModelDefinitions[FULLY_CONJUGATED_MODEL]['menuName'] = 'Conjugate Spanish:Full Conjugation'
ModelDefinitions[THIRD_PERSON_ONLY_MODEL]['menuName'] = 'Conjugate Spanish:Third party only verbs'
for tense in Tenses.All_Persons:
    for person in Persons.all:
        ModelDefinitions[FULLY_CONJUGATED_MODEL]['fields'].append({'name':ModelTemplate_.fieldName(tense,person)})
for tense in Tenses.imperative:
    for person in Persons.all_except(Persons.first_person_singular):
        ModelDefinitions[FULLY_CONJUGATED_MODEL]['fields'].append({'name':ModelTemplate_.fieldName(tense,person)})
for tense in Tenses.Person_Agnostic:
    ModelDefinitions[FULLY_CONJUGATED_MODEL]['fields'].append({'name':ModelTemplate_.fieldName(tense)})

for tense in Tenses.All_Persons:
    for person in Persons.third_person:
        ModelDefinitions[THIRD_PERSON_ONLY_MODEL]['fields'].append({'name':ModelTemplate_.fieldName(tense,person)})
for tense in Tenses.imperative:
    for person in Persons.third_person:
        ModelDefinitions[THIRD_PERSON_ONLY_MODEL]['fields'].append({'name':ModelTemplate_.fieldName(tense,person)})
for tense in Tenses.Person_Agnostic:
    ModelDefinitions[THIRD_PERSON_ONLY_MODEL]['fields'].append({'name':ModelTemplate_.fieldName(tense)})
