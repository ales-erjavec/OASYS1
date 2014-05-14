import sys
import Orange
import Orange.shadow
from Orange.widgets import gui
from PyQt4.QtGui import QApplication

from Orange.widgets.shadow_gui import ow_spheric_element, ow_optical_element

class SphericCrystal(ow_spheric_element.SphericElement):

    name = "Spherical Crystal"
    description = "Shadow OE: Spherical Crystal"
    icon = "icons/spherical_crystal.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 8
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    def __init__(self):
        graphical_Options=ow_optical_element.GraphicalOptions(is_mirror=False)

        super().__init__(graphical_Options)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def instantiateShadowOE(self):
        return Orange.shadow.ShadowOpticalElement.create_spherical_crystal()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = SphericCrystal()
    ow.show()
    a.exec_()
    ow.saveSettings()