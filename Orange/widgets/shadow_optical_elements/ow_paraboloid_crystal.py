import sys
from numpy import array
import Orange
import Orange.shadow
from Orange.widgets import gui
from PyQt4.QtGui import QApplication

from Orange.widgets.shadow_gui import ow_paraboloid_element, ow_optical_element

class ParaboloidCrystal(ow_paraboloid_element.ParaboloidElement):

    name = "Paraboloid Crystal"
    description = "Shadow OE: Paraboloid Crystal"
    icon = "icons/paraboloid_crystal.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 9
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]

    def __init__(self):
        graphical_Options=ow_optical_element.GraphicalOptions(is_mirror=False)

        super().__init__(graphical_Options)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    ################################################################
    #
    #  SHADOW MANAGEMENT
    #
    ################################################################

    def instantiateShadowOE(self):
        return Orange.shadow.ShadowOpticalElement.create_paraboloid_crystal()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = ParaboloidCrystal()
    ow.show()
    a.exec_()
    ow.saveSettings()