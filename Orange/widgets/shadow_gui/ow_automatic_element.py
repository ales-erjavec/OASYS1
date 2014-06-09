import sys

from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QRect
from Orange.shadow.shadow_util import ConfirmDialog

class AutomaticElement(widget.OWWidget):

    want_main_area=1

    is_automatic_run = Setting(True)
    trace_shadow = Setting(False)

    MAX_WIDTH = 1450
    MAX_HEIGHT = 880

    def __init__(self, show_automatic_box=True):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.83, self.MAX_WIDTH)),
                               round(min(geom.height()*0.885, self.MAX_HEIGHT))))

        box = gui.widgetBox(self.controlArea, "General Options", addSpace=True, orientation="horizontal")

        if show_automatic_box :
            gui.checkBox(box, self, 'is_automatic_run', 'Automatic Execution')

        gui.checkBox(box, self, 'trace_shadow', 'Trace Shadow')


    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = AutomaticElement()
    ow.show()
    a.exec_()
    ow.saveSettings()