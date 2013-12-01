#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Kosmoid - a plasmoid for showing your kopete contacts 
    
    Copyright (C) 2012  Sebastian Schultz

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

-    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import * 
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyKDE4.kdecore import i18n
from PyKDE4.kdeui import KApplication
from kopete_core import KopeteCore
from kopete_item import KopeteItem
import sys
from stat import *
import os 
import dbus
from dbus.mainloop.qt import DBusQtMainLoop

class Kosmoid(plasmascript.Applet):
    def __init__(self,parent):
        plasmascript.Applet.__init__(self,parent)
        self._kopeteCore = KopeteCore()
        self._contactsInfo = {}

    def init(self):
        self.resize(200,345)
        self.imgPath = self.package().path() + "contents/images/"
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        
        #self.theme = Plasma.Svg(self)
        #self.theme.setImagePath("widgets/background")
        self.setBackgroundHints(Plasma.Applet.NoBackground)
        
        self.timer = QTimer()
                        
        self.contactsList = QTreeWidget()
        #self.contactsList.setStyleSheet("QTreeWidget {border: none;} QTreeView::item:hover {background-color: #5f5f5f;}")
        
        self.contactsList.setColumnCount(3)
        self.contactsList.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.contactsList.header().setResizeMode(1, QHeaderView.Stretch)
        self.contactsList.header().setResizeMode(2, QHeaderView.ResizeToContents)
        self.contactsList.header().setStretchLastSection(False)          
        self.contactsList.header().hide()
        
        self.contactsList.setIconSize(QSize(22, 22))
        self.contactsList.setRootIsDecorated(False)        
        self.contactsList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.contactsList.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        
        self.connect(self.timer, SIGNAL("timeout()"), self.reload)
        self.connect(self.contactsList, SIGNAL("itemClicked(QTreeWidgetItem *, int)"), self.startConversation)        
        
        # here we put the contact list and any other thing we want...        
        self.layout = QGridLayout()        
        self.layout.addWidget(self.contactsList)        
        #self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # groupbox which contains our list, it has to be changed
        groupBox = Plasma.GroupBox()
        groupBox.nativeWidget().setFlat(True)
        groupBox.nativeWidget().setLayout(self.layout)
        groupBox.nativeWidget().setContentsMargins(0, 0, 0, 0)
        
        self.layout = QGraphicsLinearLayout(self.applet)
        self.layout.setOrientation(Qt.Vertical)
        self.layout.addItem(groupBox)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.reload()
        
        self.timer.start(2500)
  
    def reload(self):
        self._kopeteCore.reload()
        self.setContacts()
        
    def setContacts(self, force=False):
        # extracts info about contacts from KopeteCore object
        items = []
        if self._kopeteCore._kopete == None:
            self.contactsList.clear()
            print 'kopete is not running'
            return
        elif (self._kopeteCore._kopete != None) and (len(self._kopeteCore.connectedAccounts())==0):
            self.contactsList.clear()
            print 'not connected to an account'
            return

        tempContactsInfo = {}
        for c in self._kopeteCore.contacts.values(): # get contacts
            id = c[0]
            alias = c[1]
            status = c[2]
            picture = c[3]
            status_message = c[4]
            messages = c[5]
            idle_time = c[6]
            item =  KopeteItem(self,id, alias, status, picture, status_message, messages, idle_time)
            tempContactsInfo[id] = (alias, status, picture, status_message, messages, idle_time)
            items.append(item)

        if (tempContactsInfo == self._contactsInfo) and not force:
            # update list only if contacts are changed
            return
        else:
            print 'contact list changed'
            self.contactsList.clear()
            self._contactsInfo = tempContactsInfo
            
        items.sort(cmp=KopeteItem.compare)
        i = 0
        for item in items:
            item.set_color(i)
            i = i+1
        self.contactsList.insertTopLevelItems(0, items)

    def startConversation(self, item, row):
        self.setContacts(force=True)
        if (item.id=="X") and (item.status=="Away"):
            self._kopeteCore._kopete.connectAll() #StopGap-Measure because we can't know which account to connect
            return
        try:
            self._kopeteCore.openChat(item.id)
        except:
            if self._kopeteCore._kopete == None:
                print("Launching kopete")
                try:
                    os.system("kopete")
                except:
                    pass
                self._kopeteCore.reload()    
    
        
def CreateApplet(parent):
    return Kosmoid(parent) 
