# -*- coding: utf-8 -*-

# #####################################################################
# main.py
#
# Przemyslaw Kaminski <cgenie@gmail.com>
# Time-stamp: <>
######################################################################
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import KDialog, KDateTimeWidget
from datetime import datetime

class CountdownTimerConfig(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.layout = QVBoxLayout()
        self.inner_layout = QGridLayout()

        self.kdatetime = KDateTimeWidget(self)
        self.event_label = QLabel(self)
        self.event_label.setText("Message: ")
        self.event_txt = QLineEdit(self)

        self.layout.addWidget(self.kdatetime)
        self.layout.addLayout(self.inner_layout)

        self.inner_layout.addWidget(self.event_label, 0, 0)
        self.inner_layout.addWidget(self.event_txt, 0, 1)

        self.setLayout(self.layout)

class CountdownTimer(plasmascript.Applet):
    def __init__(self, parent, args=None):
        plasmascript.Applet.__init__(self, parent)

    def init(self):
        self.setHasConfigurationInterface(True)
        self.setAspectRatioMode(Plasma.Square)

        self.end = datetime.now()

        cg = self.config()
        print(cg.name())
        rent = str(cg.readEntry("endTime", QVariant("")).toString())
        msg = str(cg.readEntry("message", QVariant("")).toString())
        if rent:
            self.end = datetime(*[int(x) for x in rent.split(" ")])
        self.message = "Needs configuration"
        if msg:
            self.message = msg
        
        self.resize(300, 125)
        self.dialog = None
        self.connectToEngine()

    # plasma DataEngines
    # for more info, run plasmaengineexplorer
    def connectToEngine(self):
        # the timer
        self.timeEngine = self.dataEngine("time")
        self.timeEngine.connectSource("Europe/Warsaw", self, 500)
        
    @pyqtSignature("dataUpdated(const QString &, const Plasma::DataEngine::Data &)")
    def dataUpdated(self, sourceName, data):
        self.update()

    def showConfigurationInterface(self):
        windowTitle = str(self.applet.name() + " Settings")
        
        if self.dialog is None:
            self.dialog = KDialog(None)
            self.dialog.setWindowTitle(windowTitle)
            
            self.ui = CountdownTimerConfig(self.dialog)
            self.dialog.setMainWidget(self.ui)
            
            self.dialog.setButtons(KDialog.ButtonCodes(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel | KDialog.Apply)))
            self.dialog.showButton(KDialog.Apply, False)

            # set up the values so they correspond to config
            dateTime = QDateTime()
            dateTime.setDate(QDate(self.end.year, self.end.month, self.end.day))
            dateTime.setTime(QTime(self.end.hour, self.end.minute, self.end.second))
            self.ui.kdatetime.setDateTime(dateTime)
            self.ui.event_txt.setText(self.message)

            self.connect(self.dialog, SIGNAL("applyClicked()"), self, SLOT("configAccepted()"))
            self.connect(self.dialog, SIGNAL("okClicked()"), self, SLOT("configAccepted()"))

        now = datetime.now()
        
        self.dialog.show()

    @pyqtSignature("configAccepted()")
    def configAccepted(self):
        cg = self.config()

        self.end = datetime(*[int(x) for x in self.ui.kdatetime.dateTime().toString("yyyy MM dd hh mm ss").split(" ")])
        self.message = self.ui.event_txt.displayText()
        
        cg.writeEntry("endTime", QString('{:%Y %m %d %H %M %S}'.format(self.end)))
        cg.writeEntry("message", QString(self.message))

        self.emit(SIGNAL("configNeedsSaving()"))

    def paintInterface(self, painter, option, rect):
        painter.save()
        painter.setPen(Qt.white)
        align = Qt.AlignVCenter | Qt.AlignHCenter
        painter.drawText(rect, Qt.AlignHCenter | Qt.AlignTop, self.message)
        n = datetime.now()
        timeDiff = self.end - n
        if self.end >= n:
            painter.drawText(rect, Qt.AlignHCenter | Qt.AlignVCenter, str(timeDiff).split(".")[0])
        else:
            painter.drawText(rect, Qt.AlignHCenter | Qt.AlignVCenter, str("Timer ended!"))
        painter.restore()

def CreateApplet(parent):
    return CountdownTimer(parent)
