import sys
import Orange
from Orange.widgets import widget, gui
from PyQt4 import QtGui

class Pin(widget.OWWidget):

    name = "Pin"
    description = "User Defined: Pin"
    icon = "icons/pin.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "User Defined"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Trigger", Orange.shadow.ShadowTriggerOut, "passTrigger")]

    outputs = [{"name":"Trigger",
                "type":Orange.shadow.ShadowTriggerOut,
                "doc":"Trigger",
                "id":"Trigger"}]

    want_main_area = 0
    want_control_area = 1

    def __init__(self):

         gui.label(self.controlArea, self, "SIMPLE PASSAGE POINT", orientation="horizontal")
         gui.rubber(self.controlArea)

    def passTrigger(self, trigger):
            self.send("Trigger", trigger)

if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    ow = Pin()
    ow.show()
    a.exec_()
    ow.saveSettings()