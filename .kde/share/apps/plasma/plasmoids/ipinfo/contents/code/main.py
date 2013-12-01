# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from commands import *

class IpAddr(plasmascript.Applet):
  def __init__(self, parent, args=None):
    plasmascript.Applet.__init__(self, parent)

  def updateInfo(self):
    self.iptext = getoutput("curl --connect-timeout 1 -s checkip.dyndns.org|sed -e 's/.*Current IP Address: //' -e 's/<.*$//'")
    if self.iptext == "":
      self.label.setText("Keine Verbindung")
    else:
      self.label.setText(self.iptext)

  def init(self):
    self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
    
    self.theme = Plasma.Svg(self)
    self.theme.setImagePath("widgets/background")
    self.setBackgroundHints(Plasma.Applet.DefaultBackground)
    
    self.layout = QGraphicsGridLayout(self.applet)
    
    self.icon = Plasma.IconWidget(self.applet)
    self.icon.setIcon("applications-internet")
    
    self.label = Plasma.Label(self.applet)
    self.label.setText("Keine Verbindung")
    
    self.layout.addItem(self.icon, 0, 0)
    self.layout.addItem(self.label, 0, 1)
    
    self.setLayout(self.layout)
    self.resize(150, 48)
    
    self.timer = QTimer(self.applet)
    self.timer.setInterval(5000)
    self.connect(self.timer, SIGNAL("timeout()"), self.updateInfo)
    self.timer.start()

def CreateApplet(parent):
  return IpAddr(parent)
