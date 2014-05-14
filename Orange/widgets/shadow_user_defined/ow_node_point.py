import Orange
import sys
from Orange.widgets import widget
from Orange.widgets import gui
from PyQt4 import QtGui
from Orange.widgets.settings import Setting
from Orange.shadow.shadow_util import ShadowGui
from Orange.shadow.shadow_objects import ShadowTriggerIn

import Orange.canvas.resources as resources

class LoopPoint(widget.OWWidget):

    name = "Loop Point"
    description = "User Defined: LoopPoint"
    icon = "icons/point.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "User Defined"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Trigger", Orange.shadow.ShadowTriggerIn, "passTrigger")]

    outputs = [{"name":"Trigger",
                "type":Orange.shadow.ShadowTriggerOut,
                "doc":"Trigger",
                "id":"Trigger"}]
    want_main_area = 0

    is_looping_point = Setting(0)
    send_new_beam = Setting(0)
    number_of_new_beams = Setting(1)
    current_new_beam = 0

    process_last = True

    image_path = resources.package_dirname("Orange.widgets.shadow_user_defined") + "/icons/distances.png"

    def __init__(self):
        self.setFixedWidth(590)
        self.setFixedHeight(150)

        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Loop Management", addSpace=True, orientation="vertical", width=560, height=120)

        ShadowGui.lineEdit(left_box_1, self, "number_of_new_beams", "Number of new Beams", labelWidth=350, valueType=int, orientation="horizontal")

        self.le_current_new_beam = ShadowGui.lineEdit(left_box_1, self, "current_new_beam", "Current New Beam", labelWidth=350, valueType=int, orientation="horizontal")
        self.le_current_new_beam.setReadOnly(True)
        font = QtGui.QFont(self.le_current_new_beam.font())
        font.setBold(True)
        self.le_current_new_beam.setFont(font)
        palette = QtGui.QPalette(self.le_current_new_beam.palette()) # make a copy of the palette
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor('dark blue'))
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(243, 240, 160))
        self.le_current_new_beam.setPalette(palette)

    def passTrigger(self, trigger):
        if self.is_looping_point == 1:
            if trigger.interrupt:
                self.current_new_beam = 0
                self.send("Trigger", ShadowTriggerIn(new_beam=False))
            elif trigger.new_beam:
                if self.current_new_beam < self.number_of_new_beams:
                    self.current_new_beam += 1
                    self.send("Trigger", trigger)
                else:
                    self.current_new_beam = 0
                    self.send("Trigger", ShadowTriggerIn(new_beam=False))
        else:
            self.send("Trigger", trigger)

if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    ow = LoopPoint()
    ow.show()
    a.exec_()
    ow.saveSettings()