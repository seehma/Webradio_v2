#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

from PyQt4.QtGui import QGridLayout, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget, QFont, \
    QSpacerItem
from PyQt4.QtCore import QSize, SIGNAL, QString, Qt, QTimer

font = QFont()          #font for LineEdit ...
font.setPointSize(24)

class InputState:
    LOWER = 0
    CAPITAL = 1


try:
    fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class KeyButton(QPushButton):

    def __init__(self, key):
        super(KeyButton, self).__init__()

        self._key = key
        self._activeSize = QSize(50,50)
        self.connect(self, SIGNAL("clicked()"), self.emitKey)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setFocusPolicy(Qt.NoFocus)
        self.setMinimumHeight(40)
#        self.setMinimumWeight(buttonMinSize)

    def emitKey(self):
        self.emit(SIGNAL("sigKeyButtonClicked"), self._key)

    def enterEvent(self, event):
        self.setFixedSize(self._activeSize)                 #this is the optical feedback when a touchscreen is in use
        QTimer.singleShot(500, lambda : self.setFixedSize(self.sizeHint()))

    def leaveEvent(self, event):
        self.setFixedSize(self.sizeHint())

    def sizeHint(self):
        return QSize(40, 40)

class SpaceKeyButton(QPushButton):

    def __init__(self, key):
        super(SpaceKeyButton, self).__init__()

        self._key = key
        self.connect(self, SIGNAL("clicked()"), self.emitKey)
#        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setFocusPolicy(Qt.NoFocus)
#        self.setMinimumHeight(buttonMinSize) 
#        self.setMinimumWeight(buttonMinSize)

    def emitKey(self):
        self.emit(SIGNAL("sigKeyButtonClicked"), self._key)

#    def sizeHint(self):
#        return QSize(800, 30)

class VirtualKeyboard(QWidget):

    def __init__(self, parent=None):
        super(VirtualKeyboard, self).__init__(parent)

        self.globalLayout = QVBoxLayout(self)
        self.keysLayout = QGridLayout()
        self.keysLayout.setObjectName("keysLayout")
        self.buttonLayout = QHBoxLayout()
        self.dictOfButtons = {}
#        self.setStyleSheet("QWidget {"
#                           "background-color: rgb(118, 118, 118);"
#                           "color: rgb(240, 240, 240);"
#                           "}"
#                           ""
#                           "QLabel{"
#                           "color: rgb(240, 240, 240);"
#                           "}"
#                           "QPushButton{"
#                           "background-color: rgb(42, 42, 42);"
#                           "color: rgb(255, 255, 255);"
#                           "border-style: solid;"
#                           "border-color: black;"
#                           "border-width: 5px;"
#                           "border-radius: 10px;"
#                           "font: 63 20pt 'Ubuntu';"
#                           "}")
        self.keyListByLines = [
                    ['1','2','3','4','5','6','7','8','9','0',u'ß','?'],    # comment this line if you dont want numbers
                    ['q', 'w', 'e', 'r', 't', 'z', 'u', 'i', 'o', 'p', u'ü','+'],
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', u'ö', u'ä','#' ],
                    ['y', 'x', 'c', 'v', 'b', 'n', 'm', '_', '-', '/', '.',':'],
                ]
        self.inputString = ""
        self.state = InputState.LOWER

        self.stateButton = QPushButton()
        self.stateButton.setText(self.tr('Shift'))
        self.stateButton.setObjectName("Shift")
        self.stateButton.setFocusPolicy(Qt.NoFocus)
        self.backButton = QPushButton()
        self.backButton.setText(self.tr('Delete'))
        self.backButton.setFocusPolicy(Qt.NoFocus)
        self.backButton.setObjectName("Back")
        self.okButton = QPushButton()
        self.okButton.setText('Ok')
        self.okButton.setFocusPolicy(Qt.NoFocus)
        self.okButton.setObjectName("Ok")
        self.cancelButton = QPushButton()
        self.cancelButton.setText(self.tr("Abort"))
        self.cancelButton.setFocusPolicy(Qt.NoFocus)
        self.cancelButton.setObjectName("Cancel")
        self.spaceButton = SpaceKeyButton(" ")
        self.spaceButton.setText(self.tr("Space"))
        self.spaceButton.setObjectName("Space")
        self.spaceButton.setFocusPolicy(Qt.NoFocus)
        self.dictOfButtons.update({"keyButton " : self.spaceButton})
        self.connect(self.spaceButton, SIGNAL("sigKeyButtonClicked"), self.addInputByKey)

        self.inputLine = QLineEdit()
        self.inputLine.setObjectName("SearchText")
        self.inputLine.setFont(font)


        for lineIndex, line in enumerate(self.keyListByLines):
            for keyIndex, key in enumerate(line):
                buttonName = "keyButton" + key.capitalize()
                self.dictOfButtons.update({buttonName : KeyButton(key)})
                self.keysLayout.addWidget(self.getButtonByKey(key), self.keyListByLines.index(line), line.index(key))
                self.getButtonByKey(key).setText(key)
                self.connect(self.getButtonByKey(key), SIGNAL("sigKeyButtonClicked"), self.addInputByKey)
                self.keysLayout.setColumnMinimumWidth(keyIndex, 50)  # needed space for optical feedback
            self.keysLayout.setRowMinimumHeight(lineIndex, 50)

        self.connect(self.stateButton, SIGNAL("clicked()"), self.switchState)
        self.connect(self.backButton, SIGNAL("clicked()"), self.backspace)
        self.connect(self.okButton, SIGNAL("clicked()"), self.emitInputString)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self.emitCancel)

        self.buttonLayout.addWidget(self.cancelButton, 1)
        self.buttonLayout.addWidget(self.backButton, 1)
        self.buttonLayout.addWidget(self.spaceButton, 3)   # replaced with layout (tmpLayout)
        self.buttonLayout.addWidget(self.stateButton, 1)
        self.buttonLayout.addWidget(self.okButton, 1)

        self.globalLayout.addWidget(self.inputLine)
        self.globalLayout.addLayout(self.keysLayout, 1)
#        # construct a small horizontal layout, to assure that space-bare is in the middle of the keyboard...
#        tmpLayout = QHBoxLayout()
#        space = QSpacerItem(0,0)
#        tmpLayout.addSpacerItem(space)
#        tmpLayout.addWidget(self.spaceButton)
#        tmpLayout.addSpacerItem(space)
#        self.globalLayout.addLayout(tmpLayout)

        self.globalLayout.addLayout(self.buttonLayout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.inputLine.setFocus()


    def getButtonByKey(self, key):
        dictKey = "keyButton" + key.capitalize()
        return self.dictOfButtons[dictKey]

    def getLineForButtonByKey(self, key):
        return [key in keyList for keyList in self.keyListByLines].index(True)

    def switchState(self):
        self.state = not self.state
        #print("State", self.state)
        if self.state == InputState.LOWER:
            for line in self.keyListByLines:
                for key in line:
                    self.getButtonByKey(key).setText(key.lower())
                    self.stateButton.clearFocus()
        if self.state == InputState.CAPITAL:
            for line in self.keyListByLines:
                for key in line:
                    self.getButtonByKey(key).setText(key.capitalize())

    def addInputByKey(self, key):
        self.inputString += (key.lower(), key.capitalize())[self.state]
        self.inputLine.setText(self.inputString)
        self.inputLine.setFocus()

    def backspace(self):
        self.inputLine.backspace()
        self.inputString = self.inputString[:-1]
        self.inputLine.setFocus()

    def emitInputString(self):
        self.emit(SIGNAL("sigInputString"), self.inputLine.text())

    def emitCancel(self):
        self.emit(SIGNAL("sigInputString"), "")

    def clearContent(self):
        self.inputLine.setText("")
        self.inputString = ""

    def sizeHint(self):
        return QSize(480,272)



if __name__ == '__main__':
    def printText(text):
        print text
    import sys
    from PyQt4.QtGui import QApplication
    app = QApplication(sys.argv)
    win = VirtualKeyboard()
    app.connect(win, SIGNAL("sigInputString"), printText)
    win.show()
    app.exec_()
