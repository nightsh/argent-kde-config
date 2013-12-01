# -*- coding: utf-8 -*-
#
# Author: Shafqat Bhuiyan <priomsrb@gmail.com>
# Date: Sat Jun 5 2010, 21:06:19
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation; either version 2, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
#
# You should have received a copy of the GNU Library General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

# Import essential modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *

from Task import Task
from TaskConfig import TaskConfig
from SettingsConfig import SettingsConfig


class TaskTimer(plasmascript.Applet):

    #   Constructor, forward initialization to its superclass
    #   Note: try to NOT modify this constructor; all the setup code
    #   should be placed in the init method.
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)

    #   init method
    #   Put here all the code needed to initialize our plasmoid
    def init(self):
        self.setHasConfigurationInterface(True)
        #self.resize(250, 200)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        self.setBackgroundHints(self.TranslucentBackground)

        self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)

        self.addNewTaskButton = Plasma.PushButton(self.applet)
        self.addNewTaskButton.setText('Add new task')

        self.addNewTaskButton.clicked.connect(self.showAddNewTaskLineEdit)
        self.layout.addItem(self.addNewTaskButton)
        #self.layout.addStretch()
        
        self.tasks = []
        self.isRenamingTask = False
        self.isAddingTask = False

        self.colors = {}
        self.horizontal_layout = False

        self.loadConfig()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.updateTasks)
        self.timer.start()

        self.saveTimer = QTimer()
        self.saveTimer.setInterval(30 * 1000) # save every 30 seconds
        self.saveTimer.timeout.connect(self.saveState)
        self.saveTimer.start()

    def eventFilter(self, watched, event):
        if isinstance(watched, Plasma.PushButton):
            if event.type() == QEvent.GraphicsSceneContextMenu:
                taskID = watched.data(0).toInt()[0]
                task = self.tasks[taskID]
                task.showContextMenu(event.screenPos())

                #self.showContextMenuForTask(task, event.screenPos())
                return True

        if isinstance(watched, Plasma.LineEdit):
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Escape:
                    # delete the text and press enter
                    # The line edits are made so that if they are blank when
                    # subimitted, the keep their previous value
                    watched.setText("")
                    watched.returnPressed.emit()
                    return True

        return False

    def loadConfig(self):
        colorsConfig = self.config().group("colors")

        self.colors['activeTaskBackground'] = colorsConfig.readEntry('activeTaskBackground', "#88FF88").toString()
        self.colors['activeTaskText'] = colorsConfig.readEntry('activeTaskText', "#000000").toString()
        self.colors['inactiveTaskBackground'] = colorsConfig.readEntry('inactiveTaskBackground', "#FFBBBB").toString()
        self.colors['inactiveTaskText'] = colorsConfig.readEntry('inactiveTaskText', "#000000").toString()

        config = self.config()
        self.horizontal_layout = config.readEntry('horizontal_layout')
        if(self.horizontal_layout):
            self.horizontal_layout = True
        else:
            self.horizontal_layout = False
            
        tasksConfig = self.config().group("tasks")
        numberOfTasks = tasksConfig.readEntry("numberOfTasks", 0).toInt()[0]
        for i in range(numberOfTasks):
            taskConfig = tasksConfig.group(str(i))
            newTask = Task(self)
            newTask.loadConfig(taskConfig)
            self.addTask(newTask)

        self.updateLayout()

    def saveState(self, config=None):
        colorsConfig = self.config().group("colors")
        colorsConfig.writeEntry('activeTaskBackground', self.colors['activeTaskBackground'])
        colorsConfig.writeEntry('activeTaskText', self.colors['activeTaskText'])
        colorsConfig.writeEntry('inactiveTaskBackground', self.colors['inactiveTaskBackground'])
        colorsConfig.writeEntry('inactiveTaskText', self.colors['inactiveTaskText'])
        
        config = self.config()
        config.writeEntry('horizontal_layout', self.horizontal_layout)
        
        tasksConfig = self.config().group("tasks")
        tasksConfig.deleteGroup()
        numberOfTasks = len(self.tasks)
        tasksConfig.writeEntry("numberOfTasks", numberOfTasks)
        for i in range(numberOfTasks):
            taskConfig = tasksConfig.group(str(i))
            task = self.tasks[i]
            task.save(taskConfig)

    def showAddNewTaskLineEdit(self):
        if self.isEditing() == False:
            self.addNewTaskLineEdit = Plasma.LineEdit(self.applet)
            self.addNewTaskLineEdit.installEventFilter(self)
            self.addNewTaskLineEdit.returnPressed.connect(self.addNewTaskFromLineEdit)
            self.addNewTaskLineEdit.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
            self.addNewTaskLineEdit.setClearButtonShown(True)

            itemCount = self.layout.count()
            self.layout.insertItem(itemCount - 1, self.addNewTaskLineEdit)

            self.addNewTaskLineEdit.setFocus()

            self.isAddingTask = True
        else:
            if self.isAddingTask:
                self.addNewTaskFromLineEdit()

    def addNewTaskFromLineEdit(self):
        title = self.addNewTaskLineEdit.text()
        self.addNewTaskLineEdit.deleteLater()

        if not title.isEmpty():
            task = Task(self)
            task.setTitle(title)
            self.addTask(task)
            self.saveState()

        self.isAddingTask = False

    def addTask(self, task):
        taskCount = len(self.tasks)

        task.setID(taskCount)
        task.getLayoutItem().installEventFilter(self)
        self.tasks.append(task)

        self.layout.insertItem(taskCount, task.getLayoutItem())

    def isEditing(self):
        return (self.isRenamingTask or self.isAddingTask)

    @pyqtSlot(int)
    def resetTimer(self, taskID):
        # This condition is not necessary but it keeps behaviour consistent
        if self.isEditing() == False:
            task = self.tasks[taskID]
            task.resetTimer()
            self.saveState()

    @pyqtSlot(int)
    def setTimer(self, taskID):
        if self.isEditing() == False:
            newValue, ok = KInputDialog.getText("New Value",
                                 "Insert timer value",
                                 "00:00:00",
                                 None,
                                 None,
                                 "00:00:00")
        if ok:
            task = self.tasks[taskID]
            values = newValue.split(":")
            task.setTimerValue(values[0].toInt()[0] * 3600 + values[1].toInt()[0] * 60 + values[2].toInt()[0])
            self.saveState()


    @pyqtSlot(int)
    def removeTask(self, taskID):
        if self.isEditing() == False:
            task = self.tasks[taskID]
            task.getLayoutItem().deleteLater()

            self.tasks[taskID] = None
            self.updateTaskIDs()
            self.saveState()

    @pyqtSlot(int)
    def renameTask(self, taskID):
        if self.isEditing() == False:
            task = self.tasks[taskID]
            self.renameTaskID = taskID
            self.renameTaskLineEdit = Plasma.LineEdit(self.applet)
            self.renameTaskLineEdit.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
            self.renameTaskLineEdit.installEventFilter(self)
            self.renameTaskLineEdit.setText(task.getTitle())
            self.renameTaskLineEdit.setClearButtonShown(True)
            self.renameTaskLineEdit.setFocus()
            self.renameTaskLineEdit.returnPressed.connect(self.renameTaskDone)

            self.tasks[taskID].getLayoutItem().hide()
            self.layout.removeAt(taskID)
            self.layout.insertItem(taskID, self.renameTaskLineEdit)

            self.isRenamingTask = True

    def renameTaskDone(self):
        taskID = self.renameTaskID

        newTitle = self.renameTaskLineEdit.text()
        self.renameTaskLineEdit.deleteLater()

        if not newTitle.isEmpty():
            self.tasks[taskID].setTitle(newTitle)

        self.layout.insertItem(taskID, self.tasks[taskID].getLayoutItem())
        self.tasks[taskID].getLayoutItem().show()

        self.isRenamingTask = False
        self.saveState()

    def updateTasks(self):
        for task in self.tasks:
            task.tick()

    def updateTaskIDs(self):
        """
        This function removes all tasks that are now None. Then it assings
        new task IDs to the tasks. Task IDs are the same as the task's
        index in self.tasks.
        """
        i = 0
        while i < len(self.tasks):
            if self.tasks[i] == None:
                self.tasks.pop(i)
            else:
                self.tasks[i].setID(i)
                i += 1
        
    def createConfigurationInterface(self, parent):
        self.taskConfig = TaskConfig(parent)
        self.taskConfig.activeTaskBackgroundColor.setColor(QColor(self.colors['activeTaskBackground']))
        self.taskConfig.activeTaskTextColor.setColor(QColor(self.colors['activeTaskText']))
        self.taskConfig.inactiveTaskBackgroundColor.setColor(QColor(self.colors['inactiveTaskBackground']))
        self.taskConfig.inactiveTaskTextColor.setColor(QColor(self.colors['inactiveTaskText']))

        page = parent.addPage(self.taskConfig,"Colors")
        page.setIcon(KIcon("preferences-desktop-color"))

        self.settingsConfig = SettingsConfig(parent)
        self.settingsConfig.button_horizontal.setChecked(self.horizontal_layout)
        self.settingsConfig.button_vertical.setChecked(not self.horizontal_layout)
            
        page2 = parent.addPage(self.settingsConfig,"Layout")
        page2.setIcon(KIcon("configure"))
        
        self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
        self.connect(parent, SIGNAL("cancelClicked()"), self.configCanceled)

    def showConfigurationInterface(self):
        dialog = KPageDialog()
        dialog.setFaceType(KPageDialog.List)
        dialog.setButtons( KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel) )
        self.createConfigurationInterface(dialog)
        #dialog.resize(500,400)
        dialog.exec_()

    def configAccepted(self):
        self.colors['activeTaskBackground'] = self.taskConfig.activeTaskBackgroundColor.color().name()
        self.colors['activeTaskText'] = self.taskConfig.activeTaskTextColor.color().name()
        self.colors['inactiveTaskBackground'] = self.taskConfig.inactiveTaskBackgroundColor.color().name()
        self.colors['inactiveTaskText'] = self.taskConfig.inactiveTaskTextColor.color().name()

        self.horizontal_layout = self.settingsConfig.button_horizontal.isChecked()

        self.updateLayout() 

        # update buttons colors now
        for task in self.tasks:
            task.setButtonColor()

        self.saveState()

    def updateLayout(self):
        if(self.horizontal_layout):
          self.layout.setOrientation(Qt.Horizontal)
        else:
          self.layout.setOrientation(Qt.Vertical)

    def configCanceled(self):
        pass
    
    def callback(self):    
        numberOfTasks = len(self.tasks)      
        for i in range(numberOfTasks):	  
            task = self.tasks[i]
            task.stopTiming()
    
    #   CreateApplet method
    #   Note: do NOT modify it, needed by Plasma
def CreateApplet(parent):
    return TaskTimer(parent)
