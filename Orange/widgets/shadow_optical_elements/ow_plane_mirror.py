import sys
from numpy import array
import Orange
import Orange.shadow
from Orange.widgets import gui
from PyQt4.QtGui import QApplication

import Shadow
from Orange.widgets.shadow_gui import ow_plane_element, ow_optical_element


class PlaneMirror(ow_plane_element.PlaneElement):

    name = "Plane Mirror"
    description = "Shadow OE: Plane Mirror"
    icon = "icons/plane_mirror.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    def __init__(self):
        graphical_Options=ow_optical_element.GraphicalOptions(is_mirror=True)

        super().__init__(graphical_Options)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def instantiateShadowOE(self):
        return Orange.shadow.ShadowOpticalElement.create_plane_mirror()

    def doSpecificSetting(self, shadow_oe):
        return None

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = PlaneMirror()
    ow.show()
    a.exec_()
    ow.saveSettings()