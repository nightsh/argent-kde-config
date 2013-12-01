from PyQt4.QtGui import QWidget
from settings_ui import Ui_Form

class SettingsConfig(QWidget,Ui_Form):

    def __init__(self,parent):
        QWidget.__init__(self)
        self.parent = parent
        self.setupUi(self)