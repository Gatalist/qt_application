# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(813, 622)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(9, 9, 9, 9)
        self.gridLayout.setHorizontalSpacing(9)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.widget_2 = QtWidgets.QWidget(Form)
        self.widget_2.setMinimumSize(QtCore.QSize(400, 50))
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 50))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(50, 27, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(self.widget_2)
        self.label_2.setMinimumSize(QtCore.QSize(70, 30))
        self.label_2.setMaximumSize(QtCore.QSize(70, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.lineEdit_from = QtWidgets.QLineEdit(self.widget_2)
        self.lineEdit_from.setMinimumSize(QtCore.QSize(60, 30))
        self.lineEdit_from.setMaximumSize(QtCore.QSize(60, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_from.setFont(font)
        self.lineEdit_from.setMaxLength(6)
        self.lineEdit_from.setObjectName("lineEdit_from")
        self.horizontalLayout.addWidget(self.lineEdit_from)
        spacerItem1 = QtWidgets.QSpacerItem(50, 27, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.label = QtWidgets.QLabel(self.widget_2)
        self.label.setMinimumSize(QtCore.QSize(70, 30))
        self.label.setMaximumSize(QtCore.QSize(70, 30))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_to = QtWidgets.QLineEdit(self.widget_2)
        self.lineEdit_to.setMinimumSize(QtCore.QSize(60, 30))
        self.lineEdit_to.setMaximumSize(QtCore.QSize(60, 30))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit_to.setFont(font)
        self.lineEdit_to.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lineEdit_to.setText("")
        self.lineEdit_to.setMaxLength(6)
        self.lineEdit_to.setObjectName("lineEdit_to")
        self.horizontalLayout.addWidget(self.lineEdit_to)
        spacerItem2 = QtWidgets.QSpacerItem(105, 27, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.btn_start = QtWidgets.QPushButton(self.widget_2)
        self.btn_start.setMinimumSize(QtCore.QSize(100, 25))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.btn_start.setFont(font)
        self.btn_start.setStyleSheet("#btn_start {\n"
"    background-color:#198754;\n"
"    color: #fff;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"#btn_start:hover {\n"
"    color: #fff;\n"
"    background-color:#157347;\n"
"}\n"
"\n"
"#btn_start:pressed {\n"
"    border: 4px solid #9dccb6;\n"
"}\n"
"")
        self.btn_start.setObjectName("btn_start")
        self.horizontalLayout.addWidget(self.btn_start)
        spacerItem3 = QtWidgets.QSpacerItem(100, 27, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.gridLayout.addWidget(self.widget_2, 0, 0, 1, 1)
        self.textEdit = QtWidgets.QTextEdit(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_2.setText(_translate("Form", "С колонки"))
        self.lineEdit_from.setPlaceholderText(_translate("Form", "AC"))
        self.label.setText(_translate("Form", "В колонку"))
        self.lineEdit_to.setPlaceholderText(_translate("Form", "AD"))
        self.btn_start.setText(_translate("Form", "Начать"))

