import sys
from numpy import array
import Orange
import Orange.shadow
from Orange.widgets import gui
from PyQt4.QtGui import QApplication

from Orange.widgets.shadow_gui import ow_hyperboloid_element, ow_optical_element

class HyperboloidCrystal(ow_hyperboloid_element.HyperboloidElement):

    name = "Hyperboloid Crystal"
    description = "Shadow OE: Hyperboloid Crystal"
    icon = "icons/hyperboloid_crystal.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 11
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]


    inputs = [("Input Beam", Orange.shadow.ShadowBeam, "setBeam")]

    outputs = [{"name":"Beam",
                "type":Orange.shadow.ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"}]

    ##########################################
    # BASIC SETTING
    ##########################################

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
        return Orange.shadow.ShadowOpticalElement.create_hyperboloid_crystal()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = HyperboloidCrystal()
    ow.show()
    a.exec_()
    ow.saveSettings()