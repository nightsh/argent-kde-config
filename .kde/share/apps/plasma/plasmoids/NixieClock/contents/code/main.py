#!/usr/bin/env python
#nixiePath = ".kde/share/apps/plasma/plasmoids/NixieClock/contents/code/images/"

#############################################################################
# Nixie Clock astronomical time utility
# Written by Charles Figura, Warburg College
# Ported/rewritten from Qt3 to Qt4, for use as KDE4 plasmoid
# Written 2009/03/05
#############################################################################
# Next Todo:
#   chime when timer finishes
#   Optimize for less intensive running...
#   Local time mouseover displays current location
#   Allow choice between JDN and RJD (JDN-2400000)?
#############################################################################
# Version 0.5 - 2009/03/11
# Rewrote to allow for easy conversion to plasmoid.
# Modified location list to dictionary
# Added Help/About dialogs
#############################################################################
# Done:
# - Toggle which clocks are displayed
# - Toggle local date vs. UTDate
# - Fix image directory path
# - Port to Plasmoid
# - Check for ST/DT switch.  Do this every cycle?  That seems wasteful.  Need to test this one - set computer date...
# - Set up timer
# - don't allow update when timer is running
# - timer activates when click on 'tmr'
# - timer counts UP
# - on countup, click on increment (any digit) should zero FIRST (allow choice)
# - save view preferences (which clocks to show/hide), restore on startup.
# - move set/add location routines to conf, OUT of widget (and similar)
# - when timer is on t+ and set to zero, clicking counts UP instead of down (stopwatch mode)
# - check over the timer reset.  Move click action to the display itself?
#############################################################################

# General imports
import sys
from math import modf
from time import localtime,time
from PyQt4 import QtCore, QtGui
from functools import partial

# Plasma imports
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdecore import KStandardDirs

## PLASMOID CREATION/INSTALLATION INSTRUCTIONS
## plasmoid/NixieClock $ zip -r ../NixieClock.zip .
## plasmoid $ plasmapkg -i NixieClock.zip
## plasmoid $ plasmoidviewer NixieClock
## removal:
## plasmoid $ plasmapkg -r NixieClock ; rm NixieClock.zip


# Global definitions:
QtOrange = QtGui.QColor(237,149,10)
LT = 0
UTC = 1
LST = 2
JD = 3
GD = 4
TMR = 5

#############################################################################
# This section contains nuts & bolts calculational functions
#############################################################################

def jdNow():
    return 2440588 + time()/86400 - 0.5

def jd2utc_date(jd):
    #convert Julian day number to Gregorian calendar date
    d = jd+0.5
    z = int(d)
    F = d-z
    if (z<2299161):
        A = z
    else:
        a = int((z-1867216.25)/36524.25)
        A = z + 1 + a - int(a/4)
    B = A + 1524
    C = int((B-122.1)/365.25)
    D = int(365.25*C)
    E = int((B-D)/30.6001)
    day = B-D-int(30.6001*E)+F
    if (E<14):
        month = E-1
    else:
        month = E-13
    if (month > 2):
        year = C - 4716
    else:
        year = C - 4715
    return year,month,day

def jd2utc_time(jd):
    year, month, day = jd2utc_date(jd)
    hour = (jd - int(jd)) * 24.0 + 12.0
    minute, hour = modf(hour)
    minute *= 60.0
    second, minute = modf(minute)
    second *=60.0
    return int(hour)%24, int(minute), second

def jd2utc(jd):
    year,month,day = jd2utc_date(jd)
    hour,minute,second = jd2utc_time(jd)
    if second > 59.5:
        second = 0.0
        minute += 1
        if minute > 59.5:
            minute = 0.0
            hour += 1
    day = int(day)
    
    if hour < 0:
        second = 60+second
        minute = 60+minute
        hour = 23+hour
        day -= 1
    return year, month, day,hour,minute,second

def s2hms10(seconds):
    # take a time in s10 (10*#seconds)
    hours = int(seconds)/3600
    seconds -= hours*3600
    minutes = int(seconds)/60
    seconds -= minutes*60
    seconds = int(round(seconds*10))
    return hours,minutes,seconds

#############################################################################
# This section contains the clock class
#############################################################################

class Chrono:
    # This class contains the time and visible parameters for each time display
    def __init__(self,label):
        self.label = label
        self.digits = [0,0,0,0,0,0,0,0,0,0]
        self.time = 0
        self.visible = True

    def setDigits(self,digits):
        self.digits = digits

    def toggleVisible(self):
        self.visible = not self.visible

class Clock:
    def __init__(self):
        self.filename = nixiePath+"nixieClock.conf"
        self.atlas = []
        self.siteList = {}
        
        self.initChronos()
        
        # set initial parameters
        if not self.readConf():
            self.setDefault()

        margin = 2 #(one pixel margin on either side)
        self.width = 250+margin
        self.height = 6*32+margin #160+32+2
        self.ymax = self.height
        global width
        width = self.width
        global height
        height = self.height

        # Load a single pixmap set:
        filenames = ["nix0.xpm","nix1.xpm","nix2.xpm","nix3.xpm","nix4.xpm",
                     "nix5.xpm","nix6.xpm","nix7.xpm","nix8.xpm","nix9.xpm",
                     "nixc.xpm","nixd.xpm"]
        global pixmaps
        pixmaps = []
        for filename in filenames:
            fullpath = nixiePath+filename
            image = QtGui.QImage(fullpath)
            pixmaps.append(QtGui.QPixmap(23,32).fromImage(image))

    def initChronos(self):
        chronos = []
        chronos.append(Chrono("LT"))
        chronos.append(Chrono("UTC"))
        chronos.append(Chrono("LST"))
        chronos.append(Chrono("JD"))
        label = "UGD"# if clock.useUGD else "GD"
        chronos.append(Chrono(label))
        label = "TMR"# if clock.useTP else "TMR"
        chronos.append(Chrono(label))
        chronos[TMR].zeroTime = chronos[TMR].digits,chronos[TMR].time
        chronos[TMR].redoTime = chronos[TMR].zeroTime
        chronos[TMR].remain = chronos[TMR].time
        chronos[TMR].start = False
        self.chronos = chronos
        
    def updateChronos(self):
        # Update the time on each clock
        
        def digitsplit(a):
            z = []
            for item in a:
                b = []
                while item > 0:
                    b.insert(0,item%10)
                    item = int(item/10)
                while len(b)<2:
                    b.insert(0,0)
                z += b
            return z

        chronos = self.chronos
        jd = jdNow()
        yr,mo,dy,hr,mn,sc = jd2utc(jd)

        # Check for standard/daylight savings time
        if self.dst != localtime()[8]:
            self.setSite()

        # Update UTC clock & local clock
        ms = digitsplit([mn,int(sc)])
        if ms[-1] != chronos[1].digits[-1]:
            nh = digitsplit([(24+hr+self.timeZoneOffset)%24])
            #if chronos[LT].visible:
            chronos[LT].setDigits(nh+ms)
            if chronos[UTC].visible:
                chronos[UTC].setDigits(digitsplit([hr])+ms)
            
        # Update LST clock
        if chronos[LST].visible:
            dj = jd-2451545.0
            gmst = 280.46061837 + 360.98564736629*dj
            lmst = (gmst + clock.siteLong) % 360
            h = int (lmst/15)
            foo = 4 * (lmst - h*15)
            m = int (foo)
            foo = 60 *(foo-m)
            s = int (foo)
            lst = digitsplit([h,m,s])
            if lst[-1] != chronos[LST].digits[-1]:
                chronos[LST].setDigits(lst)

        # Update JD clock
        if chronos[JD].visible:
            jd = int(100*jd)
            z = digitsplit([jd])
            if z != chronos[JD].digits:
                chronos[JD].setDigits(z)
            
        # Update GD clock
        if chronos[GD].visible:
            yr = yr % 100
            if not self.useUGD:
                # i.e. if we're using local gregorian date
                if hr + clock.timeZoneOffset < 0:
                    dy = dy - 1
            z = digitsplit([yr,mo,dy])
            if z != chronos[GD].digits:
                chronos[GD].setDigits(z)
            
        # Update the timer
        if chronos[TMR].visible and chronos[TMR].start:
            now = time()
            elapsed = now - chronos[TMR].start
            chronos[TMR].remain -= elapsed
            chronos[TMR].start=now
            z = digitsplit(s2hms10(abs(chronos[TMR].remain)))
            
            while len(z)<7:
                z.insert(0,0)
            chronos[TMR].digits = z
            if chronos[TMR].remain <= 0:
                if clock.useTP:
                    chronos[TMR].label = "TMR +"
                else:
                    chronos[TMR].start = False
                    chronos[TMR].digits = [0,0,0,0,0,0,0]

    def incrementTimerDigit(self,digit):
        # set the timer
        tmr = self.chronos[TMR]
        
        z = tmr.digits[digit]
        if digit%2 == 0:
            z = (z+1)%6
        else:
            z = (z+1)%10
        i = 0
        newDigits = []
        timevector=[36000,3600,600,60,10,1,0.10]
        remain=0
        for i in range(len(timevector)):
            if i == digit:
                newDigits.append(z)
            elif i == len(tmr.digits)-1:
                newDigits.append(0)
            else:
                newDigits.append(tmr.digits[i])
            remain += newDigits[i]*timevector[i]
        tmr.setDigits(newDigits)
        tmr.remain = remain
        tmr.redoTime = newDigits,remain
        
    def addSite(self,siteName,siteLong,siteZone,siteZoNa):
        self.siteList[siteName] = [siteLong,siteZone,siteZoNa]
        self.setSite(siteName)
        
    def setDefault(self):
        # Called if there's no configuration file found
        siteName = 'Waverly, IA'
        siteLong = -92.492222
        siteZone = -6
        siteZoNa = "CST"
        self.addSite(siteName,siteLong,siteZone,siteZoNa)
        
    def readConf(self):
        
        # Test
        #fooFile = open("foo.bar",'w')
        #fooFile.write("BLAHBLAH")
        #fooFile.close()

        try:
            locFile = open(self.filename)	
        except:
            print "%s: No configuration file found" % self.filename
            return

        lines = locFile.readlines()
        locFile.close()
        
        displayconfs = lines[0:8]
        params = []
        for line in displayconfs:
            pieces = line.split("\t")
            params.append(eval(pieces[1]))
        self.setView(params)

        defaultSite = lines[8].split("=")[1].strip()
        lines = lines[9:]
        for line in lines:
            a = line.replace("\n","")
            a = a.split("\t")
            self.siteList[a[0]] = [float(a[1]),int(a[2]),a[3]]
        self.setSite(defaultSite)
        return True
        
    def setView(self,a):
        for i in range(len(self.chronos)):
            self.chronos[i].visible = a[i]
        self.useUGD = a[6]
        self.useTP = a[7]
        self.chronos[GD].label = "UGD" if self.useUGD else "LGD"
        self.chronos[TMR].label = "TMR -" if self.useTP else "TMR"
        self.writeConf
        
    def setSite(self,site=False):
        # setSite should be called when changing site OR DST status
        if site:
            self.siteName = site
            self.siteLong = self.siteList[site][0]
            self.siteZone = self.siteList[site][1]
            zoNa = self.siteList[site][2]
        else:
            zoNa = chronos[0].label
        self.dst = localtime()[8]
        self.timeZoneOffset = self.siteZone + self.dst
        if self.dst == 1:
            zoNa = zoNa[0]+"D"+zoNa[2]
        else:
            zoNa = self.zoNa[0]+"S"+zoNa[2]
        self.zoneName = zoNa
        self.chronos[LT].label = zoNa
        self.writeConf()
        
    def writeConf(self):
        chronos = self.chronos
        defaultSite = self.siteName
        siteList = self.siteList

        locFile = open(self.filename,'w')
        # Write out view configs
        locFile.write("%s\t%s\n" % ("showLT",chronos[0].visible))
        locFile.write("%s\t%s\n" % ("showUTC",chronos[UTC].visible))
        locFile.write("%s\t%s\n" % ("showLST",chronos[LST].visible))
        locFile.write("%s\t%s\n" % ("showJD",chronos[3].visible))
        locFile.write("%s\t%s\n" % ("showDate",chronos[4].visible))
        locFile.write("%s\t%s\n" % ("showTMR",chronos[TMR].visible))
        locFile.write("%s\t%s\n" % ("useUGD",self.useUGD))
        locFile.write("%s\t%s\n" % ("useTP",self.useTP))
        
        # Write out default location
        locFile.write("defaultSite = %s\n" % defaultSite)

        # Write out site list
        for site in sorted(set(siteList)):
            locFile.write("%s\t%f\t%d\t%s\n" % (site,siteList[site][0],
                                                siteList[site][1],
                                                siteList[site][2]))
        locFile.close()

#############################################################################
# This section contains configuration-associated popup classes
#############################################################################

class ConfigurationDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self,None)#,"LongitudeDialog")
        layout = QtGui.QVBoxLayout(self)
        widget = ConfigurationWidget(self)
        self.setWindowTitle("Configuration")
        layout.addWidget(widget)

class ConfigurationWidget(QtGui.QWidget):
    def __init__(self,parent):

        QtGui.QWidget.__init__(self,parent)
        layout = QtGui.QVBoxLayout(self)

        chronos = clock.chronos
        
        self.showLT = QtGui.QCheckBox(self)
        self.showLT.setText("Show Local Time")
        layout.addWidget(self.showLT)
        if chronos[LT].visible:
            self.showLT.setCheckState(QtCore.Qt.Checked)
        self.connect(self.showLT,QtCore.SIGNAL("clicked()"),
                    partial(self.toggleClock,LT))

        self.showUTC = QtGui.QCheckBox(self)
        self.showUTC.setText("Show UTC")
        layout.addWidget(self.showUTC)
        if chronos[UTC].visible:
            self.showUTC.setCheckState(QtCore.Qt.Checked)
        self.connect(self.showUTC,QtCore.SIGNAL("clicked()"),
                     partial(self.toggleClock,UTC))
        
        self.showLST = QtGui.QCheckBox(self)
        self.showLST.setText("Show LST")
        layout.addWidget(self.showLST)
        if chronos[LST].visible:
            self.showLST.setCheckState(QtCore.Qt.Checked)
        self.connect(self.showLST,QtCore.SIGNAL("clicked()"),
                     partial(self.toggleClock,LST))

        self.showJD = QtGui.QCheckBox(self)
        self.showJD.setText("Show Julian Day")
        layout.addWidget(self.showJD)
        if chronos[JD].visible:
            self.showJD.setCheckState(QtCore.Qt.Checked)
        self.connect(self.showJD,QtCore.SIGNAL("clicked()"),
                     partial(self.toggleClock,JD))

        self.showDate = QtGui.QCheckBox(self)
        self.showDate.setText("Show Date")
        layout.addWidget(self.showDate)
        if chronos[GD].visible:
            self.showDate.setCheckState(QtCore.Qt.Checked)
        self.connect(self.showDate,QtCore.SIGNAL("clicked()"),
                     partial(self.toggleClock,GD))

        self.useUGD = QtGui.QCheckBox(self)
        self.useUGD.setText("Use UT Date")
        layout.addWidget(self.useUGD)
        if clock.useUGD:
            self.useUGD.setCheckState(QtCore.Qt.Checked)
        self.connect(self.useUGD,QtCore.SIGNAL("clicked()"),self.toggleUGD)

        self.showTmr = QtGui.QCheckBox(self)
        self.showTmr.setText("Show Timer")
        layout.addWidget(self.showTmr)
        if chronos[TMR].visible:
            self.showTmr.setCheckState(QtCore.Qt.Checked)
        self.connect(self.showTmr,QtCore.SIGNAL("clicked()"),
                     partial(self.toggleClock,TMR))

        self.useTP = QtGui.QCheckBox(self)
        self.useTP.setText("Show T+ Timer")
        layout.addWidget(self.useTP)
        if clock.useTP:
            self.useTP.setCheckState(QtCore.Qt.Checked)
        self.connect(self.useTP,QtCore.SIGNAL("clicked()"),self.toggleTP)

        self.locButton = QtGui.QPushButton("Set Location",self)
        layout.addWidget(self.locButton)
        self.connect(self.locButton,QtCore.SIGNAL("clicked()"),self.setLoc)

        self.helpButton = QtGui.QPushButton("Help",self)
        layout.addWidget(self.helpButton)
        self.connect(self.helpButton,QtCore.SIGNAL("clicked()"),self.help)

        self.aboutButton = QtGui.QPushButton("About",self)
        layout.addWidget(self.aboutButton)
        self.connect(self.aboutButton,QtCore.SIGNAL("clicked()"),self.about)

    def help(self):
        helpText = ("<h3>Help</h3><hr>"
                    "<p>UTC:  Universal Coordinated Time</p><hr>"
                    "<p>LST:  Local Sidereal Time: Right Ascension of local meridian</p><hr>"
                    "<p>JD:   Julian Day Number: # days since BCE 12:00, 4713/01/01</p><hr>"
                    "<p>UGD/LGD:  Gregorian Date: Time at 0 degrees Longitude</p>"
                    "<ul>"
                    "<li>UGD: universal date, based on UTC"
                    "<li>LGD: local date, based on current location"
                    "</ul><hr>"
                    "<p>TMR:  Timer.  There are two timer modes:</p>"
                    "<ul>"
                    "<li>Normal: Countdown mode, stops at zero."
                    "<li>T+: T minus/T plus.  Countdown and stopwatch mode."
                    "</ul>"
                    "<p>Left-click on digits increment time.</p>"
                    "<p>Right-click on TMR starts/stops/resets clock</p>"
                    "<p>Center-click on digits zeroes time.</p><hr>"
                    "<p>Locations:</p>"
                    "<ul>"
                    "<li>Time zones relative to UTC"
                    "<li>Longitudes west of prime meridian are negative."
                    "</ul>")
        QtGui.QMessageBox.information(None,"Nixie Clock",helpText,"Dismiss")
        
    def about(self):
        QtGui.QMessageBox.information(None,"Nixie Clock",
                                      "<h3>Nixie Tube Astronomical Clock</h3><hr>"
                                      "<p>written by Charlie Figura</p>"
                                      "<i>(charles.figura@wartburg.edu)</i><hr>"
                                      "<p>Version 0.5 2009/03/12</p>","Dismiss")

    def toggleClock(self,n):
        if clock.ymax > 32 or not clock.chronos[n].visible:
            # If we're showing more than one clock OR we're toggling a clock on,
            # go ahead and toggle.  Otherwise, no fair turning OFF the last one.
            clock.chronos[n].toggleVisible()
            clock.writeConf()
        self.parent().accept()

    def toggleUGD(self):
        clock.useUGD = not clock.useUGD
        clock.chronos[GD].label = "UGD" if clock.useUGD else "LGD"
        clock.writeConf()
        self.parent().accept()

    def toggleTP(self):
        clock.useTP = not clock.useTP
        clock.chronos[TMR].label = "TMR -" if clock.useTP else "TMR"
        clock.writeConf()
        self.parent().accept()

    def setLoc(self):
        d = LongitudeDialog()
        d.setModal(True)
        d.show()
        z = d.exec_()
        self.parent().accept()
        
class LongitudeDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self,None)#,"LongitudeDialog")
        layout = QtGui.QVBoxLayout(self)
        widget = LongitudeWidget(self)
        self.setWindowTitle("Set Longitude")
        layout.addWidget(widget)

class LongitudeWidget(QtGui.QWidget):
    def __init__(self,parent):

        QtGui.QWidget.__init__(self,parent)
        layout = QtGui.QGridLayout(self)
        label = QtGui.QLabel("Location:",self)
        layout.addWidget(label,0,0)
        self.locationPulldown = QtGui.QComboBox(self)
        
        i = 0
        self.siteNames = sorted(set(clock.siteList))
        for site in self.siteNames:
            self.locationPulldown.insertItem(i,site)
            i += 1
        defaultIndex = self.siteNames.index(clock.siteName)
        self.locationPulldown.setCurrentIndex(defaultIndex)

        layout.addWidget(self.locationPulldown,0,1,1,3)
        self.connect(self.locationPulldown,
                     QtCore.SIGNAL("activated(int)"), self.setLocation)
        self.addButton = QtGui.QPushButton("Add",self)
        self.connect(self.addButton,QtCore.SIGNAL("clicked()"),
                     self.addLocation)

        layout.addWidget(self.addButton,2,2)
        self.cancelButton = QtGui.QPushButton("Cancel",self)
        self.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),
                     self.parent().reject)
        layout.addWidget(self.cancelButton,3,2)
        
        label = QtGui.QLabel("New location:",self)
        layout.addWidget(label,1,0)
        label = QtGui.QLabel("Name:",self)
        layout.addWidget(label,2,0)
        self.newLocationName = QtGui.QLineEdit(self)#,"newLocation")
        layout.addWidget(self.newLocationName,2,1)
        self.newLocationName.setMaxLength(30)

        label = QtGui.QLabel("Longitude:",self)
        layout.addWidget(label,3,0)
        self.newLocationLong = QtGui.QLineEdit(self)#,"newLocation")
        layout.addWidget(self.newLocationLong,3,1)
        self.newLocationLong.setMaxLength(30)

        label = QtGui.QLabel("Time Zone:",self)
        layout.addWidget(label,4,0)
        self.newLocationZone = QtGui.QLineEdit(self)
        layout.addWidget(self.newLocationZone,4,1)
        self.newLocationZone.setMaxLength(30)

        label = QtGui.QLabel("Zone Name:",self)
        layout.addWidget(label,5,0)
        self.newLocationZoNa = QtGui.QLineEdit(self)#,"newZoNa")
        layout.addWidget(self.newLocationZoNa,5,1)
        self.newLocationZoNa.setMaxLength(3)

        siteName = clock.siteName
        self.newLocationName.setText(siteName)
        self.newLocationLong.setText("%s" % clock.siteList[siteName][0])
        self.newLocationZone.setText("%s" % clock.siteList[siteName][1])
        self.newLocationZoNa.setText("%s" % clock.siteList[siteName][2])
        
    def setLocation(self,index):
        clock.setSite(self.siteNames[index])
        self.parent().accept()
        
    def addLocation(self):
        siteName = str(self.newLocationName.text())
        siteLong = float(self.newLocationLong.text())
        siteZone = int(self.newLocationZone.text())
        siteZoNa = str(self.newLocationZoNa.text())
        clock.addSite(siteName,siteLong,siteZone,siteZoNa)
        self.parent().accept()
        
#############################################################################
# This section contains Clock Display Widget
#############################################################################
    
class NixieClockDisplay(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)

        self.timerId = 0

        # set up the GraphicsScene size and other issues...
        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(0,0, width, height)
        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        self.clockWidget = ClockWidget(self)
        scene.addItem(self.clockWidget)
        self.clockWidget.setPos(1,1)
            
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setMinimumSize(width, height)
        self.setWindowTitle(self.tr("NixieClock"))

        self.startTimer(1000/10)

    def mousePressEvent(self, event):
        ex,ey,ebutton = event.x(),event.y(),event.button() 
        # Right click anywhere opens configuration dialog
        if ebutton == QtCore.Qt.RightButton:
            d = ConfigurationDialog()
            d.setModal(True)
            d.show()
            z = d.exec_()
        # Otherwise, any click in timer box controls timer
        elif (clock.chronos[TMR].visible and (ey > (clock.ymax-32))):
            self.timerSet(ex,ey,ebutton)

    def timerSet(self,ex,ey,ebutton):
        # If the timer is showing and you click on the timer bank
        # (which is always at the bottom of the widget)
        tmr = clock.chronos[TMR]
        # Left click on the timer box starts/stops the clock.  Period.
        if ex < 53 and ebutton == QtCore.Qt.LeftButton:
            # if you click on 'TMR':
            if tmr.start:
                # if the timer is running, stop it.
                tmr.start=False
            elif (tmr.remain > 0 and not clock.useTP) or clock.useTP:
                # if the timer is not running, start it -
                # set tmr.start to the start time
                tmr.start = time()
            else :
                # if the timer is NOT running and there's no time left,
                # reset to last-used countdown time
                tmr.digits,tmr.remain = tmr.redoTime
            
        elif ex > 53 and ebutton == QtCore.Qt.LeftButton and not tmr.start:
            # if you left click on numbers and we're not running, set clock.
            x = ex-53
            if 0<x<23: digit = 0
            elif 23<x<46: digit = 1
            elif 57<x<80: digit = 2
            elif 80<x<103: digit = 3
            elif 114<x<137: digit = 4
            elif 137<x<160: digit = 5
            # elif 171<x<194: digit = 6
            # Don't allow 10th second setting, just zero tenths.
            else: return
            if clock.useTP: self.label = "TMR -"
            clock.incrementTimerDigit(digit)
        elif ex > 53 and ebutton == QtCore.Qt.MidButton and not tmr.start:
            # Center click (both buttons) zeroes clock if timer is not running
            tmr.digits,tmr.remain = tmr.zeroTime
            if clock.useTP: self.label = "TMR -"
            self.update()
            
    def timerEvent(self, event):
        # Update clocks
        clock.updateChronos()

        # Redraw the widget
        self.clockWidget.update()
        
    def drawBackground(self, painter, rect):
        # Fill.
        sceneRect = self.sceneRect()
        painter.fillRect(rect.intersect(sceneRect),
                         QtGui.QBrush(QtCore.Qt.black))

class ClockWidget(QtGui.QGraphicsItem):
    # Clock template for Julian Day display (DDDDDDD.DD)
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, graphWidget):
        QtGui.QGraphicsItem.__init__(self)
        self.parent = graphWidget
        
    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(0,0,251,clock.ymax)

    def paint(self, painter, option, widget):
        y0 = 0
        for i in range(6):
            chrono = clock.chronos[i]
            if chrono.visible:
                x0 = 0#10
                # Paint the label
                font = painter.font()
                font.setBold(True)
                font.setPointSize(9)
                painter.setFont(font)
                painter.setPen(QtOrange)
                labelpos = QtCore.QPointF(x0,y0+19)
                painter.drawText(labelpos,chrono.label)
                if i == 3:
                    # Paint the digits
                    x0 = x0+33
                    painter.drawPixmap(x0+0,y0,pixmaps[chrono.digits[0]])
                    painter.drawPixmap(x0+23,y0,pixmaps[chrono.digits[1]])
                    painter.drawPixmap(x0+46,y0,pixmaps[chrono.digits[2]])
                    painter.drawPixmap(x0+69,y0,pixmaps[chrono.digits[3]])
                    painter.drawPixmap(x0+92,y0,pixmaps[chrono.digits[4]])
                    painter.drawPixmap(x0+115,y0,pixmaps[chrono.digits[5]])
                    painter.drawPixmap(x0+138,y0,pixmaps[chrono.digits[6]])
                    painter.drawPixmap(x0+161,y0+19,pixmaps[11])
                    painter.drawPixmap(x0+172,y0,pixmaps[chrono.digits[7]])
                    painter.drawPixmap(x0+195,y0,pixmaps[chrono.digits[8]])
                else:
                    # Paint the digits
                    x0 = x0+33+22
                    painter.drawPixmap(x0,y0,pixmaps[chrono.digits[0]])
                    painter.drawPixmap(x0+23,y0,pixmaps[chrono.digits[1]])
                    painter.drawPixmap(x0+46,y0,pixmaps[10])
                    painter.drawPixmap(x0+57,y0,pixmaps[chrono.digits[2]])
                    painter.drawPixmap(x0+80,y0,pixmaps[chrono.digits[3]])
                    painter.drawPixmap(x0+103,y0,pixmaps[10])
                    painter.drawPixmap(x0+114,y0,pixmaps[chrono.digits[4]])
                    painter.drawPixmap(x0+137,y0,pixmaps[chrono.digits[5]])
                    if i == 5:
                        painter.drawPixmap(x0+160,y0+19,pixmaps[11])
                        painter.drawPixmap(x0+171,y0,pixmaps[chrono.digits[6]])
                y0 += 32
                
        # Resize the window if necessary
        if clock.ymax != y0:
            clock.ymax = y0
            parent = self.parent
            parent.setSceneRect(0,0,width,clock.ymax)
            h,w = parent.sizeHint().height(),parent.sizeHint().width()
            parent.setFixedSize(w,h)
        
#############################################################################
# This section contains Clock Display applet
#############################################################################

class NixieClockDisplay(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
 
    def init(self):
        global nixiePath

        nixiePath = self.package().path() + "contents/code/NixieDir/"
        self.x0 = 10 # 0 for non-plasmoid clock
        self.y0 = 10 # 0 for non-plasmoid clock
        global clock
        clock = Clock()
        self.resize(252+10+10,194+10+10)

        self.startTimer(1000/10)

    def paintInterface(self, painter, option, rect):
        y0 = self.y0
        for i in range(6):
            chrono = clock.chronos[i]
            if chrono.visible:
                x0 = self.x0
                # Paint the label
                font = painter.font()
                font.setBold(True)
                font.setPointSize(9)
                painter.setFont(font)
                painter.setPen(QtOrange)
                labelpos = QtCore.QPointF(x0,y0+19)
                painter.drawText(labelpos,chrono.label)
                if i == 3:
                    # Paint the digits
                    x0 = x0+33
                    painter.drawPixmap(x0+0,y0,pixmaps[chrono.digits[0]])
                    painter.drawPixmap(x0+23,y0,pixmaps[chrono.digits[1]])
                    painter.drawPixmap(x0+46,y0,pixmaps[chrono.digits[2]])
                    painter.drawPixmap(x0+69,y0,pixmaps[chrono.digits[3]])
                    painter.drawPixmap(x0+92,y0,pixmaps[chrono.digits[4]])
                    painter.drawPixmap(x0+115,y0,pixmaps[chrono.digits[5]])
                    painter.drawPixmap(x0+138,y0,pixmaps[chrono.digits[6]])
                    painter.drawPixmap(x0+161,y0+19,pixmaps[11])
                    painter.drawPixmap(x0+172,y0,pixmaps[chrono.digits[7]])
                    painter.drawPixmap(x0+195,y0,pixmaps[chrono.digits[8]])
                else:
                    # Paint the digits
                    x0 = x0+33+22
                    painter.drawPixmap(x0,y0,pixmaps[chrono.digits[0]])
                    painter.drawPixmap(x0+23,y0,pixmaps[chrono.digits[1]])
                    painter.drawPixmap(x0+46,y0,pixmaps[10])
                    painter.drawPixmap(x0+57,y0,pixmaps[chrono.digits[2]])
                    painter.drawPixmap(x0+80,y0,pixmaps[chrono.digits[3]])
                    painter.drawPixmap(x0+103,y0,pixmaps[10])
                    painter.drawPixmap(x0+114,y0,pixmaps[chrono.digits[4]])
                    painter.drawPixmap(x0+137,y0,pixmaps[chrono.digits[5]])
                    if i == 5:
                        painter.drawPixmap(x0+160,y0+19,pixmaps[11])
                        painter.drawPixmap(x0+171,y0,pixmaps[chrono.digits[6]])
                y0 += 32

        # Resize the window if necessary
        if clock.ymax != y0:
            clock.ymax = y0
            self.resize(252+2*self.x0,clock.ymax+self.y0)
            
    def showConfigurationInterface(self):
        d = ConfigurationDialog()
        d.setModal(True)
        d.show()
        z = d.exec_()

    def mousePressEvent(self, event):
        ex,ey,ebutton = event.pos().x(),event.pos().y(),event.button()
        # Right click anywhere opens configuration dialog
        # Otherwise, any click in timer box controls timer
        if (clock.chronos[TMR].visible and (ey > (clock.ymax-32))):
            self.timerSet(ex,ey,ebutton)

    def timerSet(self,ex,ey,ebutton):
        # If the timer is showing and you click on the timer bank
        # (which is always at the bottom of the widget)
        tmr = clock.chronos[TMR]
        # Left click on the timer box starts/stops the clock.  Period.
        # Probably need to modify ALL of these margins with self.x0
        x0 = self.x0
        if ex < x0+53 and ebutton == QtCore.Qt.LeftButton:
            # if you click on 'TMR':
            if tmr.start:
                # if the timer is running, stop it.
                tmr.start=False
            elif (tmr.remain > 0 and not clock.useTP) or clock.useTP:
                # if the timer is not running, start it -
                # set tmr.start to the start time
                tmr.start = time()
            else :
                # if the timer is NOT running and there's no time left,
                # reset to last-used countdown time
                tmr.digits,tmr.remain = tmr.redoTime

        elif ex > x0+53 and ebutton == QtCore.Qt.LeftButton and not tmr.start:
            # if you left click on numbers and we're not running, set clock.
            x = ex-53-x0
            if 0<x<23: digit = 0
            elif 23<x<46: digit = 1
            elif 57<x<80: digit = 2
            elif 80<x<103: digit = 3
            elif 114<x<137: digit = 4
            elif 137<x<160: digit = 5
            # elif 171<x<194: digit = 6
            # Don't allow 10th second setting, just zero tenths.
            else: return
            if clock.useTP: self.label = "TMR -"
            clock.incrementTimerDigit(digit)
        elif ex > 53 and ebutton == QtCore.Qt.MidButton and not tmr.start:
            # Center click (both buttons) zeroes clock if timer is not running
            tmr.digits,tmr.remain = tmr.zeroTime
            if clock.useTP: clock.chronos[TMR].label = "TMR -"
            self.update()

    def timerEvent(self, event):
        # Update clocks
        clock.updateChronos()
        # Redraw
        self.update()
        
def CreateApplet(parent):
    return NixieClockDisplay(parent)
