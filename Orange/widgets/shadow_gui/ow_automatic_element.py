import sys

from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, qApp

class AutomaticElement(widget.OWWidget):

    want_main_area=1

    is_automatic_run = Setting(True)

    def __init__(self):
        super().__init__()

        gui.checkBox(gui.widgetBox(self.controlArea, "General Options", addSpace=True, orientation="vertical"), \
                     self, 'is_automatic_run', 'Automatic Execution')

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = AutomaticElement()
    ow.show()
    a.exec_()
    ow.saveSettings()