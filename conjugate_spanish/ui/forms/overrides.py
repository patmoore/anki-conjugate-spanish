# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer/overrides.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(395, 761)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.pastTenseBox = QtGui.QGroupBox(Dialog)
        self.pastTenseBox.setGeometry(QtCore.QRect(30, 270, 221, 71))
        self.pastTenseBox.setObjectName(_fromUtf8("pastTenseBox"))
        self.checkBox = QtGui.QCheckBox(self.pastTenseBox)
        self.checkBox.setGeometry(QtCore.QRect(20, 30, 85, 18))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.futureAndConditionalBox = QtGui.QGroupBox(Dialog)
        self.futureAndConditionalBox.setGeometry(QtCore.QRect(30, 350, 221, 80))
        self.futureAndConditionalBox.setObjectName(_fromUtf8("futureAndConditionalBox"))
        self.futureAndCondEnding = QtGui.QComboBox(self.futureAndConditionalBox)
        self.futureAndCondEnding.setGeometry(QtCore.QRect(100, 20, 104, 26))
        self.futureAndCondEnding.setObjectName(_fromUtf8("futureAndCondEnding"))
        self.futureAndCondEnding.addItem(_fromUtf8(""))
        self.futureAndCondEnding.addItem(_fromUtf8(""))
        self.futureAndCondEnding.addItem(_fromUtf8(""))
        self.label_2 = QtGui.QLabel(self.futureAndConditionalBox)
        self.label_2.setGeometry(QtCore.QRect(30, 30, 56, 13))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.presentTenseBox = QtGui.QGroupBox(Dialog)
        self.presentTenseBox.setGeometry(QtCore.QRect(30, 130, 219, 131))
        self.presentTenseBox.setObjectName(_fromUtf8("presentTenseBox"))
        self.go_verb = QtGui.QCheckBox(self.presentTenseBox)
        self.go_verb.setGeometry(QtCore.QRect(20, 30, 85, 18))
        self.go_verb.setObjectName(_fromUtf8("go_verb"))
        self.oy_verb = QtGui.QCheckBox(self.presentTenseBox)
        self.oy_verb.setGeometry(QtCore.QRect(90, 30, 85, 18))
        self.oy_verb.setObjectName(_fromUtf8("oy_verb"))
        self.label = QtGui.QLabel(self.presentTenseBox)
        self.label.setGeometry(QtCore.QRect(10, 60, 141, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.radicalStemChanging = QtGui.QComboBox(self.presentTenseBox)
        self.radicalStemChanging.setGeometry(QtCore.QRect(100, 80, 104, 26))
        self.radicalStemChanging.setObjectName(_fromUtf8("radicalStemChanging"))
        self.radicalStemChanging.addItem(_fromUtf8(""))
        self.radicalStemChanging.addItem(_fromUtf8(""))
        self.radicalStemChanging.addItem(_fromUtf8(""))
        self.radicalStemChanging.addItem(_fromUtf8(""))
        self.radicalStemChanging.addItem(_fromUtf8(""))
        self.gerundBox = QtGui.QGroupBox(Dialog)
        self.gerundBox.setGeometry(QtCore.QRect(30, 430, 221, 80))
        self.gerundBox.setObjectName(_fromUtf8("gerundBox"))
        self.pastParticiple = QtGui.QGroupBox(Dialog)
        self.pastParticiple.setGeometry(QtCore.QRect(30, 520, 221, 80))
        self.pastParticiple.setObjectName(_fromUtf8("pastParticiple"))
        self.adjectiveBox = QtGui.QGroupBox(Dialog)
        self.adjectiveBox.setGeometry(QtCore.QRect(30, 610, 221, 80))
        self.adjectiveBox.setObjectName(_fromUtf8("adjectiveBox"))
        self.adjUsePastParticiple = QtGui.QCheckBox(self.adjectiveBox)
        self.adjUsePastParticiple.setGeometry(QtCore.QRect(10, 30, 171, 18))
        self.adjUsePastParticiple.setChecked(True)
        self.adjUsePastParticiple.setObjectName(_fromUtf8("adjUsePastParticiple"))
        self.endingBasedBox = QtGui.QGroupBox(Dialog)
        self.endingBasedBox.setGeometry(QtCore.QRect(30, 10, 221, 101))
        self.endingBasedBox.setObjectName(_fromUtf8("endingBasedBox"))
        self.standardEndingOverride = QtGui.QCheckBox(self.endingBasedBox)
        self.standardEndingOverride.setGeometry(QtCore.QRect(30, 30, 151, 18))
        self.standardEndingOverride.setObjectName(_fromUtf8("standardEndingOverride"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Overrides for ____"))
        Dialog.setAccessibleName(_("Overrides"))
        self.pastTenseBox.setTitle(_("Past Tense"))
        self.checkBox.setText(_("E and O"))
        self.futureAndConditionalBox.setTitle(_("Future and Conditional"))
        self.futureAndCondEnding.setItemText(0, _("Infinitive"))
        self.futureAndCondEnding.setItemText(1, _("er -> dr"))
        self.futureAndCondEnding.setItemText(2, _("_r -> r"))
        self.label_2.setText(_("Ending"))
        self.presentTenseBox.setTitle(_("Present Tense"))
        self.go_verb.setToolTip(_("Go Verbs ( tengo, caigo )"))
        self.go_verb.setText(_("-g verb"))
        self.oy_verb.setToolTip(_("voy, soy"))
        self.oy_verb.setText(_("-oy verb"))
        self.label.setText(_("Radical Stem Changers"))
        self.radicalStemChanging.setItemText(0, _("None"))
        self.radicalStemChanging.setItemText(1, _("e:ie"))
        self.radicalStemChanging.setItemText(2, _("e:i"))
        self.radicalStemChanging.setItemText(3, _("o:ue"))
        self.radicalStemChanging.setItemText(4, _("u:ue"))
        self.gerundBox.setTitle(_("Gerund (-ing)"))
        self.pastParticiple.setTitle(_("Past Participle"))
        self.adjectiveBox.setTitle(_("Adjective"))
        self.adjUsePastParticiple.setText(_("Use Past Participle Form"))
        self.endingBasedBox.setTitle(_("Ending based"))
        self.standardEndingOverride.setText(_("replace with ending"))

