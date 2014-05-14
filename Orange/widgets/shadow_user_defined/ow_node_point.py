import Orange
import sys
from Orange.widgets import widget
from Orange.widgets import gui
from PyQt4 import QtGui
from Orange.widgets.settings import Setting
from Orange.shadow.shadow_util import ShadowGui
from Orange.shadow.shadow_objects import ShadowTrigger

import Orange.canvas.resources as resources

class NodePoint(widget.OWWidget):

    name = "Node Point"
    description = "User Defined: NodePoint"
    icon = "icons/point.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "User Defined"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Trigger", Orange.shadow.ShadowTrigger, "passTrigger")]

    outputs = [{"name":"Trigger",
                "type":Orange.shadow.ShadowTrigger,
                "doc":"Trigger",
                "id":"Trigger"}]
    want_main_area = 0

    is_looping_point = Setting(0)
    send_new_beam = Setting(0)
    number_of_new_beams = Setting(1)
    current_new_beam = 0

    image_path = resources.package_dirname("Orange.widgets.shadow_user_defined") + "/icons/distances.png"

    def __init__(self):
        self.setFixedWidth(590)
        self.setFixedHeight(200)

        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Node Parameters", addSpace=True, orientation="vertical", width=570, height=180)

        gui.checkBox(left_box_1, self, "is_looping_point", "Looping Point", callback=self.setLoopingPoint)

        gui.separator(left_box_1)

        self.box_simulation = ShadowGui.widgetBox(left_box_1, "Loop Management", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(self.box_simulation, self, "number_of_new_beams", "Number of new Beams", labelWidth=350, valueType=int, orientation="horizontal")

        self.le_current_new_beam = ShadowGui.lineEdit(self.box_simulation, self, "current_new_beam", "Current New Beam", labelWidth=350, valueType=int, orientation="horizontal")
        self.le_current_new_beam.setReadOnly(True)
        font = QtGui.QFont(self.le_current_new_beam.font())
        font.setBold(True)
        self.le_current_new_beam.setFont(font)
        palette = QtGui.QPalette(self.le_current_new_beam.palette()) # make a copy of the palette
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor('dark blue'))
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(243, 240, 160))
        self.le_current_new_beam.setPalette(palette)

        self.setLoopingPoint()

    def setLoopingPoint(self):
        self.box_simulation.setVisible(self.is_looping_point==1)

    def passTrigger(self, trigger):
        if self.is_looping_point == 1:
            if trigger.interrupt:
                self.current_new_beam = 0
                self.send("Trigger", ShadowTrigger(new_beam=False))
            elif trigger.new_beam:
                if self.current_new_beam < self.number_of_new_beams:
                    self.current_new_beam += 1
                    self.send("Trigger", trigger)
                else:
                    self.current_new_beam = 0
                    self.send("Trigger", ShadowTrigger(new_beam=False))
        else:
            self.send("Trigger", trigger)

if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    ow = NodePoint()
    ow.show()
    a.exec_()
    ow.saveSettings()