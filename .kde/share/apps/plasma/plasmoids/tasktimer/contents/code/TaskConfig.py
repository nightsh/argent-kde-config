'''
Created on Aug 6, 2009

@author: hardik
'''

from PyQt4.QtGui import QWidget
from config_ui import Ui_Form

class TaskConfig(QWidget,Ui_Form):

    def __init__(self,parent):
        QWidget.__init__(self)
        self.parent = parent
        self.setupUi(self)
