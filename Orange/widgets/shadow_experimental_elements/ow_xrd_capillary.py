import sys, math, copy, numpy, random
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication, qApp

import Shadow
import Shadow.ShadowTools as ST

from Orange.widgets.shadow_gui import ow_automatic_element
from Orange.shadow.shadow_util import ShadowGui


class XRDCapillary(ow_automatic_element.AutomaticElement):

    printout = 0

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
    capillary_material = Setting(0)
    sample_material = Setting(0)
    packing_factor = Setting(0.6)

    horizontal_displacement = Setting(0)
    vertical_displacement = Setting(0)

    detector_distance = Setting(95)
    slit_1_distance = Setting(0)
    slit_1_vertical_aperture = Setting(0)
    slit_1_horizontal_aperture = Setting(0)
    slit_2_distance = Setting(0)
    slit_2_vertical_aperture = Setting(0)
    slit_2_horizontal_aperture = Setting(0)

    is_automatic_run = Setting(True)

    def __init__(self):
        super().__init__()

        upper_box = ShadowGui.widgetBox(self.controlArea, "Sample Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "capillary_diameter", "Capillary Diameter [mm]", tooltip="Capillary Diameter [mm]", valueType=float, orientation="horizontal")
        gui.comboBox(upper_box, self, "capillary_material", label="Capillary Material", items=["Glass", "Kapton"], sendSelectedValue=False, orientation="horizontal")
        gui.comboBox(upper_box, self, "sample_material", label="Material", items=["LaB6", "Si", "ZnO"], sendSelectedValue=False, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "packing_factor", "Packing Factor (0.0...1.0)", tooltip="Packing Factor", valueType=float, orientation="horizontal")

        upper_box = ShadowGui.widgetBox(self.controlArea, "Detector Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "detector_distance", "Detector Distance (cm)",  tooltip="Detector Distance (cm)", valueType=float, orientation="horizontal")

        gui.separator(upper_box)

        ShadowGui.lineEdit(upper_box, self, "slit_1_distance", "Slit 1 Distance (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "slit_1_vertical_aperture", "Slit 1 Vertical Aperture (um)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "slit_1_horizontal_aperture", "Slit 1 Horizontal Aperture (um)",  valueType=float, orientation="horizontal")

        gui.separator(upper_box)

        ShadowGui.lineEdit(upper_box, self, "slit_2_distance", "Slit 2 Distance (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "slit_2_vertical_aperture", "Slit 2 Vertical Aperture (um)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "slit_2_horizontal_aperture", "Slit 2 Horizontal Aperture (um)",  valueType=float, orientation="horizontal")

        upper_box = ShadowGui.widgetBox(self.controlArea, "Aberrations Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "horizontal_displacement", "Capillary H Displacement (um)",  tooltip="Capillary H Displacement (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "vertical_displacement", "Capillary V Displacement (um)",  tooltip="Capillary V Displacement (cm)", valueType=float, orientation="horizontal")

        ShadowGui.widgetBox(self.controlArea, "", addSpace=True, orientation="vertical", height=250)

        button = gui.button(self.controlArea, self, "Simulate", callback=self.simulate)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def simulate(self):

        self.information(0, "Running XRD Capillary Simulation")
        qApp.processEvents()

        self.progressBarSet(0)

        random_generator = random.Random()

        lattice_parameter = self.getLatticeParameter(self.sample_material)
        reflections = self.getReflections(self.sample_material)

        good_only = ST.getshcol(self.input_beam.beam, 10)

        rays = range(0, len(good_only))

        beam_dummy = Orange.shadow.ShadowBeam()
        beam_dummy.beam.rays  = copy.deepcopy(self.input_beam.beam.rays)

        rejected = 0

        R_c = self.capillary_diameter*0.5
        distance = self.detector_distance
        displacement_h = self.horizontal_displacement*0.0001
        displacement_v = self.vertical_displacement*0.0001

        in_out_coordinates_list = []

        self.information(0, "Calculating intersections with capillary")
        qApp.processEvents()

        self.progressBarSet(10)

        for rayIndex in rays:
            if beam_dummy.beam.rays[rayIndex,9] == 0:
                rejected = rejected+1
            else:
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
                    beam_dummy.beam.rays[rayIndex,9] = 0
                else:
                    y1 = ((-b) - math.sqrt(Discriminant))/(2*a)
                    x1 = alfa*y1 + X_pr
                    z1 = gamma*y1 + Z_pr
                    y2 = ((-b) + math.sqrt(Discriminant))/(2*a)
                    x2 = alfa*y2 + X_pr
                    z2 = gamma*y2 + Z_pr

                    random_value = random_generator.random()

                    # calcolo di un punto casuale sul segmento congiungente.

                    x_point = x1 + (x2 - x1)*random_value
                    y_point = y1 + (y2 - y1)*random_value
                    z_point = z1 + (z2 - z1)*random_value


                    in_out_coordinates_list.append(InOutCoordinates(x1, y1, z1, x2, y2, z2))

                    beam_dummy.beam.rays[rayIndex,0] = x_point
                    beam_dummy.beam.rays[rayIndex,1] = y_point
                    beam_dummy.beam.rays[rayIndex,2] = z_point

        self.progressBarSet(40)

        self.information(0, "Calculating diffracted beam")
        qApp.processEvents()

        beam_out = Orange.shadow.ShadowBeam(number_of_rays=((len(rays)-rejected) * len(reflections)))

        for rayIndex in rays:
            if beam_dummy.beam.rays[rayIndex,9] == 1:
                reflection_index=-1

                for reflection in reflections:
                   reflection_index = reflection_index +1

                   new_ray_index = rayIndex + reflection_index

                   # calcolo rotazione del vettore d'onda pari all'angolo di bragg

                   cos_x = beam_dummy.beam.rays[rayIndex,3]
                   cos_y = beam_dummy.beam.rays[rayIndex,4]
                   cos_z = beam_dummy.beam.rays[rayIndex,5]

                   k_mod = beam_dummy.beam.rays[rayIndex,10]

                   k_x = k_mod*cos_x
                   k_y = k_mod*cos_y
                   k_z = k_mod*cos_z

                   #
                   # calcolo dell'asse di rotazione: k x z
                   #
                   asse_rot_x = k_y/math.sqrt(k_x*k_x+k_y*k_y)
                   asse_rot_y = -k_y/math.sqrt(k_x*k_x+k_y*k_y)
                   asse_rot_z = 0

                   twotheta_reflection = 2*self.calculateBraggAngle(k_mod, reflection.h, reflection.k, reflection.l, lattice_parameter)

                   #
                   # calcolo del vettore ruotato di 2theta bragg, con la formula di Rodrigues:
                   #
                   # k_diffracted = k * cos(2th) + (k x asse_rot) * sin(2th) + k(k . asse_rot)(1 - cos(2th))
                   #                                                                       |
                   #                                                                      =0
                   #

                   k_vect_asse_rot_x = k_y*asse_rot_z-k_z*asse_rot_y
                   k_vect_asse_rot_y = k_z*asse_rot_x-k_x*asse_rot_z
                   k_vect_asse_rot_z = k_x*asse_rot_y-k_y*asse_rot_x

                   k_diffracted_x = k_x*math.cos(twotheta_reflection)+k_vect_asse_rot_x*math.sin(twotheta_reflection)
                   k_diffracted_y = k_y*math.cos(twotheta_reflection)+k_vect_asse_rot_y*math.sin(twotheta_reflection)
                   k_diffracted_z = k_z*math.cos(twotheta_reflection)+k_vect_asse_rot_z*math.sin(twotheta_reflection)

                   #
                   # calcolo dei coseni direttori - N.B. |k_diffracted| = |k|
                   #

                   cos_a_diffracted = k_diffracted_x/k_mod
                   cos_b_diffracted = k_diffracted_y/k_mod
                   cos_c_diffracted = k_diffracted_z/k_mod

                   #
                   # genesi del nuovo raggio diffratto attenuato dell'intensità relativa e dell'assorbimento
                   #

                   beam_out.beam.rays[new_ray_index, 0] = beam_dummy.beam.rays[rayIndex,0]                                 # X
                   beam_out.beam.rays[new_ray_index, 1] = beam_dummy.beam.rays[rayIndex,1]                                 # Y
                   beam_out.beam.rays[new_ray_index, 2] = beam_dummy.beam.rays[rayIndex,2]                                 # Z
                   beam_out.beam.rays[new_ray_index, 3] = cos_a_diffracted                                                 # director cos x
                   beam_out.beam.rays[new_ray_index, 4] = cos_b_diffracted                                                 # director cos y
                   beam_out.beam.rays[new_ray_index, 5] = cos_c_diffracted                                                 # director cos z
                   beam_out.beam.rays[new_ray_index, 6] = beam_dummy.beam.rays[rayIndex,6]*reflection.relative_intensity   # Es_x
                   beam_out.beam.rays[new_ray_index, 7] = beam_dummy.beam.rays[rayIndex,7]*reflection.relative_intensity   # Es_y
                   beam_out.beam.rays[new_ray_index, 8] = beam_dummy.beam.rays[rayIndex,8]*reflection.relative_intensity   # Es_z
                   beam_out.beam.rays[new_ray_index, 9] = beam_dummy.beam.rays[rayIndex,9]                                 # good/lost
                   beam_out.beam.rays[new_ray_index, 10] = beam_dummy.beam.rays[rayIndex,10]                               # |k|
                   beam_out.beam.rays[new_ray_index, 11] = beam_dummy.beam.rays[rayIndex,11]                               # ray index
                   beam_out.beam.rays[new_ray_index, 12] = 0                                                               # N.A.
                   beam_out.beam.rays[new_ray_index, 13] = beam_dummy.beam.rays[rayIndex,12]                               # Es_phi
                   beam_out.beam.rays[new_ray_index, 14] = beam_dummy.beam.rays[rayIndex,13]                               # Ep_phi
                   beam_out.beam.rays[new_ray_index, 15] = beam_dummy.beam.rays[rayIndex,14]*reflection.relative_intensity # Ep_x
                   beam_out.beam.rays[new_ray_index, 16] = beam_dummy.beam.rays[rayIndex,15]*reflection.relative_intensity # Ep_y
                   beam_out.beam.rays[new_ray_index, 17] = beam_dummy.beam.rays[rayIndex,16]*reflection.relative_intensity # Ep_z

        self.progressBarSet(80)

        self.information(0, "Computing diffraction profile (2th vs Intensity)")
        qApp.processEvents()

        # calcolo del pattern di diffrazione




        self.progressBarSet(100)

        self.information()
        qApp.processEvents()

        self.progressBarFinished()

        self.send("Beam", beam_out)

    def setBeam(self, beam):
        self.input_beam = beam

        if self.is_automatic_run:
           self.simulate()

    def calculateBraggAngle(self, k_modulus, h, k, l, a):

        #
        # k = 2 pi / lambda
        #
        # lambda = 2 pi / k = 2 d sen(th)
        #
        # sen(th) = lambda / (2  d)
        #
        # d = a/sqrt(h^2 + k^2 + l^2)
        #
        # sen(th) = (sqrt(h^2 + k^2 + l^2) * lambda)/(2 a)

        wl = (2*math.pi/k_modulus)*1e+8

        return math.asin((wl*math.sqrt(h*h+k*k+l*l))/(2*a))

    def calculateAbsorption(self, distance, ):
        return None

    def getRandomPoint(self):
        return None

    def getMaterialDensity(self, material):
        if material == 0:
            return 4.835*self.packing_factor
        else:
            return -1

    def getLatticeParameter(self, material):
        if material == 0: # LaB6
            return 4.15689 #Angstrom
        elif material ==1: #Si
            return 5.43123 #Angstrom
        else:
            return -1

    def getReflections(self, material):
        reflections = []

        if material == 0: # LaB6
            reflections.append(Reflection(1,0,0))
            reflections.append(Reflection(1,1,0))
            reflections.append(Reflection(1,1,1))
            reflections.append(Reflection(2,0,0))
            reflections.append(Reflection(2,1,0))
            reflections.append(Reflection(2,1,1))
            reflections.append(Reflection(2,2,0))
            reflections.append(Reflection(3,0,0))
            reflections.append(Reflection(3,1,0))
            reflections.append(Reflection(3,1,1))
            reflections.append(Reflection(2,2,2))
            reflections.append(Reflection(3,2,0))
            reflections.append(Reflection(3,2,1))
            reflections.append(Reflection(4,0,0))
            reflections.append(Reflection(4,1,0))
            reflections.append(Reflection(3,3,0))
            reflections.append(Reflection(3,3,1))
            reflections.append(Reflection(4,2,0))
            reflections.append(Reflection(4,2,1))
            reflections.append(Reflection(3,3,2))
            reflections.append(Reflection(4,2,2))
            reflections.append(Reflection(5,0,0))
            reflections.append(Reflection(5,1,0))
            reflections.append(Reflection(5,1,1))
        elif material == 1: # Si
            reflections.append(Reflection(1,1,1))
            reflections.append(Reflection(2,2,0))
            reflections.append(Reflection(3,1,1))
            reflections.append(Reflection(4,0,0))
            reflections.append(Reflection(3,3,1))
            reflections.append(Reflection(4,2,2))
            reflections.append(Reflection(5,1,1))
            reflections.append(Reflection(4,4,0))
            reflections.append(Reflection(5,3,1))
            reflections.append(Reflection(6,2,0))
            reflections.append(Reflection(5,3,3))
        else:
            return None

        return reflections

class InOutCoordinates:
    x1=0
    x2=0
    y1=0
    y2=0
    z1=0
    z2=0

    def __init__(self, x1, y1, z1, x2, y2, z2):
        self.x1=x1
        self.y1=y1
        self.z1=z1
        self.x2=x2
        self.y2=y2
        self.z2=z2

class Reflection:
    h=0
    k=0
    l=0
    relative_intensity=1.0

    def __init__(self, h, k, l, relative_intensity=1.0):
        self.h=h
        self.k=k
        self.l=l
        self.relative_intensity=relative_intensity


if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = XRDCapillary()
    ow.show()
    a.exec_()
    ow.saveSettings()