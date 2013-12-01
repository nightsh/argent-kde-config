# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../_ui/settings.ui'
#
# Created: Thu Nov  1 19:58:14 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(454, 220)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.kbuttongroup_layout = KButtonGroup(Form)
        self.kbuttongroup_layout.setObjectName(_fromUtf8("kbuttongroup_layout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.kbuttongroup_layout)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.button_horizontal = QtGui.QRadioButton(self.kbuttongroup_layout)
        self.button_horizontal.setObjectName(_fromUtf8("button_horizontal"))
        self.verticalLayout_2.addWidget(self.button_horizontal)
        self.button_vertical = QtGui.QRadioButton(self.kbuttongroup_layout)
        self.button_vertical.setObjectName(_fromUtf8("button_vertical"))
        self.verticalLayout_2.addWidget(self.button_vertical)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.kbuttongroup_layout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.kbuttongroup_layout.setTitle(QtGui.QApplication.translate("Form", "Layout", None, QtGui.QApplication.UnicodeUTF8))
        self.button_horizontal.setText(QtGui.QApplication.translate("Form", "horizontal", None, QtGui.QApplication.UnicodeUTF8))
        self.button_vertical.setText(QtGui.QApplication.translate("Form", "vertical", None, QtGui.QApplication.UnicodeUTF8))

from PyKDE4.kdeui import KButtonGroup
