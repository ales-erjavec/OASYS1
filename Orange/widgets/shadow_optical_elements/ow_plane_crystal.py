import sys
import Orange
import Orange.shadow
from Orange.widgets import gui
from PyQt4.QtGui import QApplication

import Shadow
from Orange.widgets.shadow_gui import ow_plane_element, ow_optical_element


class PlaneCrystal(ow_plane_element.PlaneElement):

    name = "Plane Crystal"
    description = "Shadow OE: Plane Crystal"
    icon = "icons/plane_crystal.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 7
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    def __init__(self):
        graphical_Options=ow_optical_element.GraphicalOptions(is_mirror=False)

        super().__init__(graphical_Options)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def instantiateShadowOE(self):
        return Orange.shadow.ShadowOpticalElement.create_plane_crystal()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = PlaneCrystal()
    ow.show()
    a.exec_()
    ow.saveSettings()