# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../_ui/config.ui'
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
        Form.resize(384, 148)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.formLayout_3 = QtGui.QFormLayout()
        self.formLayout_3.setFormAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.label_13 = QtGui.QLabel(self.groupBox)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_13)
        self.activeTaskBackgroundColor = KColorButton(self.groupBox)
        self.activeTaskBackgroundColor.setObjectName(_fromUtf8("activeTaskBackgroundColor"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.activeTaskBackgroundColor)
        self.label_14 = QtGui.QLabel(self.groupBox)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_14)
        self.activeTaskTextColor = KColorButton(self.groupBox)
        self.activeTaskTextColor.setObjectName(_fromUtf8("activeTaskTextColor"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.activeTaskTextColor)
        self.verticalLayout.addLayout(self.formLayout_3)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_3.addWidget(self.label_4)
        self.formLayout_4 = QtGui.QFormLayout()
        self.formLayout_4.setFormAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.formLayout_4.setObjectName(_fromUtf8("formLayout_4"))
        self.label_15 = QtGui.QLabel(self.groupBox)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.formLayout_4.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_15)
        self.inactiveTaskBackgroundColor = KColorButton(self.groupBox)
        self.inactiveTaskBackgroundColor.setObjectName(_fromUtf8("inactiveTaskBackgroundColor"))
        self.formLayout_4.setWidget(0, QtGui.QFormLayout.FieldRole, self.inactiveTaskBackgroundColor)
        self.label_16 = QtGui.QLabel(self.groupBox)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.formLayout_4.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_16)
        self.inactiveTaskTextColor = KColorButton(self.groupBox)
        self.inactiveTaskTextColor.setObjectName(_fromUtf8("inactiveTaskTextColor"))
        self.formLayout_4.setWidget(1, QtGui.QFormLayout.FieldRole, self.inactiveTaskTextColor)
        self.verticalLayout_3.addLayout(self.formLayout_4)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addWidget(self.groupBox)
        spacerItem1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Colors", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Active Task", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("Form", "Background", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("Form", "Text", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Inactive Task", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("Form", "Background", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setText(QtGui.QApplication.translate("Form", "Text", None, QtGui.QApplication.UnicodeUTF8))

from PyKDE4.kdeui import KColorButton
