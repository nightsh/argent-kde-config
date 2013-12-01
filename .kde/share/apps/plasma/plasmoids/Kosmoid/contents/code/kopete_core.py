# -*- coding: utf-8 -*-

"""
    Kosmoid - a plasmoid for showing your kopete contacts 
    
    Copyright (C) 2012  Sebastian Schultz

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
--    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import getopt
import sys
import os.path
import dbus
import dbus.service
from dbus.mainloop.qt import DBusQtMainLoop
from PyQt4.QtCore import *
from PyQt4.QtGui import * 
from PyKDE4.kdeui import KApplication
ENCODING = 'utf8'

class KopeteCore(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.timer = QTimer()
        self.contacts = {}
        DBusQtMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.timer.start(2500)
        try:
            self._kopete = self.bus.get_object('org.kde.kopete', '/Kopete')
        except dbus.exceptions.DBusException:
            self._kopete = None
        self.updateContacts()

    def reload(self):
        try:
            self._kopete = self.bus.get_object("org.kde.kopete", "/Kopete")
        except dbus.exceptions.DBusException:
            self._kopete = None
        self.updateContacts()

    def contactChanged(self, contact):
        print("contactchanged",contact)
        self.updateContacts()
        #self.emit(SIGNAL("contactChanged(s)"),contact)
        self.emit(SIGNAL("messageReceived(ss)"), contact, self._kopete.contactProperties(contact)["pending_messages"])

    def accounts(self):
        return self._kopete.accounts()
        
    def connectedAccounts(self):
        ca = []
        for a in self.accounts():
          for p in self.protocols():
              if self._kopete.isConnected(p, a) == True:
                  ca = ca + [(p, a)]
        return ca
        
    def protocols(self):
        return self._kopete.protocols()
    
    def openChat(self, contact):
        self._kopete.openChat(contact)
    
    def getContacts(self):
        #dbusContacts = self._kopete.contacts()    # all contacts 
        dbusContacts = self._kopete.contactsByFilter('online') # only contacts:  online|reachable|filecapable|away
        contacts = []
        for id in dbusContacts:
            props = self._kopete.contactProperties(id)
            alias = unicode(props["display_name"])
            status = unicode(props["status"])
            picture = unicode(props["picture"])
            messages = props["pending_messages"]
            status_message = unicode(props["status_message"])
            idle_time =  props["idle_time"]/60
            c = ((id, alias, status, picture, status_message, messages, idle_time))
            contacts.append(c)    
        return contacts

    def updateContacts(self):
        if (self._kopete):
            contacts = self.getContacts()
            con_dict = {}
            for c in contacts:
                con_dict.setdefault(c[0], c)
            self.contacts = con_dict
