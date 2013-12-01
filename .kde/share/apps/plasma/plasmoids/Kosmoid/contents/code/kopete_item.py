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
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""


from PyKDE4.kdeui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from time import strftime, gmtime

class KopeteItem(QTreeWidgetItem):
    id = ""
    alias = ""
    status = ""
    avatar = ""
    status_message= ""
    messages = ""
    idle_time = ""
    
    Transparent = QColor(255,255,255,0)
    Gray1 = QColor(231,231,231,25)
    Gray2 = QColor(128,128,128,255)
    Black = QColor(0,0,0)
    White = QColor(255,255,255)
    
    bg_color1 = Transparent
    bg_color2 = Gray1
    
    fg_color_normal = White
    fg_color_idle = Gray2

    def __init__(self, parent, mail, alias, status, picture, status_message, messages, idle_time):
        QTreeWidgetItem.__init__(self)
        self.parent = parent
        self.imgPath = self.parent.imgPath
        self.id = mail
        self.alias = alias 
        self.status = status
        self.status_message = status_message
        self.messages = messages
        self.idle_time = idle_time
        
        self.setForeground(0,self.fg_color_normal)
        self.setForeground(1,self.fg_color_normal)
        self.setForeground(2,self.fg_color_normal)

        if picture == "":
            if status == "Online":
                self.avatar = "user-online"
            elif status == "Away":
                self.avatar = "user-away"
            elif status == "Busy":
                self.avatar = "user-busy"                
        else:
            self.avatar = picture
            
        idle = ''
        font = QFont() 
        if self.idle_time>0:
                self.avatar = "user-away-extended"
                font.setItalic(True)
                self.setForeground(0,self.fg_color_idle)
                self.setForeground(1,self.fg_color_idle)
                self.setForeground(2,self.fg_color_idle) 
                idle = '{0[0]}:{0[1]:0>2}'.format(divmod(self.idle_time,60))
        if len(messages) > 0:            
          self.avatar = "mail-unread"
    
        self.setIcon(0, KIcon(self.avatar))        
        
        self.setFont(1,font)        
        self.setText(1, self.alias)        
        self.setTextAlignment(1, Qt.AlignVCenter | Qt.AlignLeft)
        
        self.setFont(2,font)        
        self.setText(2, idle)        
        self.setTextAlignment(2, Qt.AlignVCenter | Qt.AlignRight)
    
    def compare(item1,item2):
        if item1.id>item2.id:
            return -1
        elif item1.id<item2.id:
            return 1
        else:
            return 0
        
    def set_color(self, position):
        # alternating background colors
        if position % 2 == 0:
            self.setBackground(0,self.bg_color1)
            self.setBackground(1,self.bg_color1)
            self.setBackground(2,self.bg_color1)
        else:
            self.setBackground(0,self.bg_color2)
            self.setBackground(1,self.bg_color2)
            self.setBackground(2,self.bg_color2)
