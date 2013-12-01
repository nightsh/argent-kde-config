from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *

class Task():
    def __init__(self, app):
        self.app = app
        self.isActive = False
        self.totalTime = 0
        self.startTime = QDateTime.currentDateTime()
        self.title = "Task Name"

        self.button = Plasma.PushButton(self.app.applet)
        self.setButtonColor()
        self.button.clicked.connect(self.toggleTiming)

        self.updateButtonText()


    def toggleTiming(self):
      if(self.isActive):
         self.stopTiming()
      else:
        self.app.callback()
        self.isActive = True
        self.setButtonColor()

    def stopTiming(self):
        self.isActive = False
        self.setButtonColor()
        
    def setButtonColor(self):
        colors = self.app.colors
        if self.isActive:
            self.button.setStyleSheet("background-color:%s;color:%s;padding:5px 10px;" % (
                colors['activeTaskBackground'],
                colors['activeTaskText'])
                )
        else:
            self.button.setStyleSheet("background-color:%s;color:%s;padding:5px 10px;" % (
                colors['inactiveTaskBackground'],
                colors['inactiveTaskText'])
                )
            #self.button.setStyleSheet("background-color:#FFBBBB")
        
    def updateButtonText(self):
        seconds = self.totalTime % 60
        minutes = (self.totalTime/60) % 60
        hours = (self.totalTime/3600)
        
        timeText = '(%02d:%02d:%02d)' % (hours, minutes, seconds)

        buttonText = self.title + ' ' + timeText 

        self.button.setText(buttonText)

    def loadConfig(self, config):
        self.title = config.readEntry("title", "Task Name").toString()
        self.totalTime = config.readEntry("totalTime", 0).toInt()[0]
        self.updateButtonText()
    
    def save(self, config):
        config.writeEntry("title", self.title)
        config.writeEntry("totalTime", self.totalTime)
    
    def tick(self):
        if self.isActive:
            self.totalTime += 1
            self.updateButtonText()

    def showContextMenu(self, screenPos):
        m = KMenu()

        # we need to use signal mappers so that we can pass the taskID argument
        self.resetTimerAction = m.addAction(KIcon('edit-undo'), 'Reset Timer')
        self.resetTimerSignalMapper = QSignalMapper()
        self.resetTimerSignalMapper.setMapping(self.resetTimerAction, self.getID())
        QObject.connect(self.resetTimerAction, SIGNAL("triggered()"),
            self.resetTimerSignalMapper, SLOT("map()"))
        self.resetTimerSignalMapper.mapped[int].connect(self.app.resetTimer)

        self.setTimerAction = m.addAction(KIcon('document-edit'), 'Set Timer Value')
        self.setTimerSignalMapper = QSignalMapper();
        self.setTimerSignalMapper.setMapping(self.setTimerAction, self.getID())
        QObject.connect(self.setTimerAction, SIGNAL("triggered()"),
            self.setTimerSignalMapper, SLOT("map()"))
        self.setTimerSignalMapper.mapped[int].connect(self.app.setTimer)

        self.renameTaskAction = m.addAction(KIcon('edit-rename'), 'Rename Task')
        self.renameTaskSignalMapper = QSignalMapper()
        self.renameTaskSignalMapper.setMapping(self.renameTaskAction, self.getID())
        QObject.connect(self.renameTaskAction, SIGNAL("triggered()"),
            self.renameTaskSignalMapper, SLOT("map()"))
        self.renameTaskSignalMapper.mapped[int].connect(self.app.renameTask)

        self.removeTaskAction = m.addAction(KIcon('edit-delete'), 'Remove Task')
        self.removeTaskSignalMapper = QSignalMapper()
        self.removeTaskSignalMapper.setMapping(self.removeTaskAction, self.getID())
        QObject.connect(self.removeTaskAction, SIGNAL("triggered()"),
            self.removeTaskSignalMapper, SLOT("map()"))
        self.removeTaskSignalMapper.mapped[int].connect(self.app.removeTask)


        m.exec_(screenPos)

    def resetTimer(self):
        self.totalTime = 0
        self.updateButtonText()


    def setTimerValue(self,timerValue):
        self.totalTime = timerValue
        self.updateButtonText()

    def getTitle(self):
        return self.title

    def getLayoutItem(self):
        return self.button

    def setTitle(self, title):
        self.title = title
        self.updateButtonText()
    
    def setID(self, id):
        self.id = id
        self.button.setData(0, self.id)

    def getID(self):
        return self.id

