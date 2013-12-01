# -*- coding: utf-8 -*-
# WLAN-Monitor plasmoid by avocadohead. License: GPL
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from pythonwifi.iwlibs import Wireless, getNICnames
 
class WlanMonitor(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
 
    def init(self):
        self.setHasConfigurationInterface(False)
        self.label = Plasma.Label(self.applet)
        self.chart=Plasma.SignalPlotter(self.applet)
        self.chart.addPlot(QColor(255,0,0))   
        self.chart.addPlot(QColor(0,0,255))   
        self.chart.addPlot(QColor(0,255,0))     
        self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)
        self.layout.addItem(self.label)
        self.layout.addItem(self.chart)
        self.applet.setLayout(self.layout)
        self.resize(200, 200)
        self.setAspectRatioMode(1)
        self.startTimer(500)
       
    def timerEvent(self,event):
      self.update()
 
    def paintInterface(self, painter, option, rect):
        wifi=Wireless('wlan0')
        dump,qual,dump,dump=wifi.getStatistics()
        self.chart.addSample([qual.signallevel-qual.noiselevel,qual.quality,100+qual.signallevel])
	self.chart.setShowTopBar(False)
	self.chart.setShowVerticalLines(False)
	self.chart.setShowHorizontalLines(False)
	self.chart.setShowLabels(False)
	self.chart.setStackPlots(False)
	self.chart.setUseAutoRange(True)
	painter.save()
        painter.setPen(Qt.black)
        self.label.setText("ESSID: %s\nLink quality: %02d/100\nSignal level: %02ddB\nSignal/Noise: %02ddB"%(wifi.getEssid(),qual.quality,qual.signallevel,qual.signallevel-qual.noiselevel))
        painter.restore()
 
def CreateApplet(parent):
    return WlanMonitor(parent)

