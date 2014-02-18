import sys, math, copy
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.canvas.utils.environ import shadow_working_directory
from PyQt4.QtGui import QApplication

import Shadow
from Orange.widgets.shadow_gui import ow_automatic_element


class XRDCapillary(ow_automatic_element.AutomaticElement):

    name = "XRD Capillary"
    description = "Shadow OE: XRD Capillary"
    icon = "icons/xrd_capillary.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Experimental Elements"
    keywords = ["data", "file", "load", "read"]


    inputs = [("Input Beam", Orange.shadow.ShadowBeam, "setBeam")]

    outputs = [{"name":"Beam",
                "type":Orange.shadow.ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"}]

    capillary_diameter = Setting(0.3)
    capillary_material = Setting("glass")
    material_name = Setting("LaB6")
    material_density = Setting(4.835)
    packing_factor = Setting(0.6)

    horizontal_displacement = Setting(0)
    vertical_displacement = Setting(0)

    detector_distance = Setting(95)

    is_automatic_run = Setting(True)

    def __init__(self):
        super().__init__()

        upper_box = gui.widgetBox(self.controlArea, "Simulation Parameters", addSpace=True, orientation="vertical")

        gui.lineEdit(upper_box, self, "capillary_diameter", "Capillary Diameter [mm]", tooltip="Capillary Diameter [mm]", valueType=float, orientation="horizontal")
        gui.comboBox(upper_box, self, "capillary_material", label="Capillary Material", items=["Glass", "Kapton"], sendSelectedValue=True)
        gui.lineEdit(upper_box, self, "material_name", "Material Name", tooltip="Material Name", valueType=str, orientation="horizontal")
        gui.lineEdit(upper_box, self, "material_density", "Material Density (g*cm-3)", tooltip="Material Density (g*cm-3)", valueType=float, orientation="horizontal")
        gui.lineEdit(upper_box, self, "packing_factor", "Packing Factor (0.0...1.0)", tooltip="Packing Factor", valueType=float, orientation="horizontal")

        gui.widgetLabel(upper_box)

        gui.lineEdit(upper_box, self, "detector_distance", "Detector Distance (cm)",  tooltip="Detector Distance (cm)", valueType=float, orientation="horizontal")
        gui.lineEdit(upper_box, self, "horizontal_displacement", "Capillary H Displacement (um)",  tooltip="Capillary H Displacement (cm)", valueType=float, orientation="horizontal")
        gui.lineEdit(upper_box, self, "vertical_displacement", "Capillary V Displacement (um)",  tooltip="Capillary V Displacement (cm)", valueType=float, orientation="horizontal")

        gui.button(self.controlArea, self, "Simulate", callback=self.simulate)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def simulate(self):

        rays = range(0, self.input_beam.beam.rays.size())

        beam_out = Orange.shadow.ShadowBeam()
        
        beam_dummy = Orange.shadow.ShadowBeam()
        beam_dummy.beam.rays  = copy.deepcopy(self.input_beam.beam.rays)

        rejected = 0

        R_c = self.capillary_diameter*0.5
        distance = self.detector_distance
        displacement_h = self.horizontal_displacement*0.0001
        displacement_v = self.vertical_displacement*0.0001

        for rayIndex in rays:
            if beam_dummy.beam.rays[rayIndex,9] == 1:
                # costruzione spot all'altezza del detector
                beam_dummy.beam.rays[rayIndex,0] = self.input_beam.beam.rays[rayIndex,0] + (distance/self.input_beam.beam.rays[rayIndex,4])*self.input_beam.beam.rays[rayIndex,3]
                beam_dummy.beam.rays[rayIndex,1] = self.input_beam.beam.rays[rayIndex,1] + distance
                beam_dummy.beam.rays[rayIndex,2] = self.input_beam.beam.rays[rayIndex,2] + (distance/self.input_beam.beam.rays[rayIndex,4])*self.input_beam.beam.rays[rayIndex,5]

                # costruzione intersezione con capillare + displacement del capillare
                alfa = self.input_beam.beam.rays[rayIndex,3]/self.input_beam.beam.rays[rayIndex,4]
                gamma = self.input_beam.beam.rays[rayIndex,5]/self.input_beam.beam.rays[rayIndex,4]
                X_pr = beam_dummy.beam.rays[rayIndex,0]
                Z_pr = beam_dummy.beam.rays[rayIndex,2]

                a = 1+gamma**2
                b = 2*displacement_h+2*gamma*Z_pr+2*displacement_v*gamma
                c = Z_pr**2 + displacement_h**2 + displacement_v**2 - R_c**2 + 2*displacement_v*Z_pr

                Discriminant = b**2 - 4*a*c

                if Discriminant <= 0.0:
                    rejected = rejected+1
                else:
                    y1 = ((-b) - math.sqrt(Discriminant))/(2*a)
                    x1 = alfa*y1 + X_pr
                    z1 = gamma*y1 + Z_pr
                    y2 = ((-b) + math.sqrt(Discriminant))/(2*a)
                    x2 = alfa*y2 + X_pr
                    z2 = gamma*y2 + Z_pr

                    self.calculate_diffraction(x1, y1, z1, x2, y2, z2)

        #self.plot_results(beam_out)

        self.send("Beam", beam_out)

    def calculateDiffraction(self, x1, y1, z1, x2, y2, z2):
        print("ciao")

    def setBeam(self, beam):
        self.input_beam = beam

        if self.is_automatic_run:
           self.simulate()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = XRDCapillary()
    ow.show()
    a.exec_()
    ow.saveSettings()