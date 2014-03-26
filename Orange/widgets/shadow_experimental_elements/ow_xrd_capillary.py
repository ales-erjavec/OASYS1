import sys, math, copy, numpy, random, gc
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication, qApp

import Shadow
import Shadow.ShadowTools as ST

from Orange.widgets.shadow_gui import ow_automatic_element
from Orange.shadow.shadow_util import ShadowGui, ShadowMath
from Orange.shadow.argonne11bm_absorption import Absorb as Absorption

from PyMca.widgets.PlotWindow import PlotWindow

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
    capillary_material = Setting(0)
    sample_material = Setting(0)
    packing_factor = Setting(0.6)

    horizontal_displacement = Setting(0)
    vertical_displacement = Setting(0)
    calculate_absorption = Setting(0)

    shift_2theta = Setting(0)

    slit_angular_misalignement = Setting(0)
    slit_1_vertical_displacement = Setting(0)
    slit_2_vertical_displacement = Setting(0)

    detector_distance = Setting(95)
    slit_1_distance = Setting(0)
    slit_1_vertical_aperture = Setting(0)
    slit_1_horizontal_aperture = Setting(0)
    slit_2_distance = Setting(0)
    slit_2_vertical_aperture = Setting(0)
    slit_2_horizontal_aperture = Setting(0)

    start_angle = Setting(10)
    stop_angle = Setting(120)
    step = Setting(0.002)

    set_number_of_peaks = Setting(0)
    number_of_peaks = Setting(1)
    angular_acceptance = Setting(0.5)

    IMAGE_WIDTH = 965
    IMAGE_HEIGHT = 825

    want_main_area=1
    plot_canvas=None

    def __init__(self):
        super().__init__()

        tabs = gui.tabWidget(self.controlArea)

        tab_setting = ShadowGui.createTabPage(tabs, "Simulation Settings")
        tab_reflections = ShadowGui.createTabPage(tabs, "Diffraction Settings")

        box_1 = ShadowGui.widgetBox(tab_setting, "Sample Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_1, self, "capillary_diameter", "Capillary Diameter [mm]", valueType=float, orientation="horizontal")
        gui.comboBox(box_1, self, "capillary_material", label="Capillary Material", items=["Glass", "Kapton"], sendSelectedValue=False, orientation="horizontal")
        gui.comboBox(box_1, self, "sample_material", label="Material", items=["LaB6", "Si", "ZnO"], sendSelectedValue=False, orientation="horizontal")
        ShadowGui.lineEdit(box_1, self, "packing_factor", "Packing Factor (0.0...1.0)", valueType=float, orientation="horizontal")

        box_2 = ShadowGui.widgetBox(tab_setting, "Detector Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_2, self, "detector_distance", "Detector Distance (cm)",  tooltip="Detector Distance (cm)", valueType=float, orientation="horizontal")

        gui.separator(box_2)

        ShadowGui.lineEdit(box_2, self, "slit_1_distance", "Slit 1 Distance from Goniometer Center (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_2, self, "slit_1_vertical_aperture", "Slit 1 Vertical Aperture (um)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_2, self, "slit_1_horizontal_aperture", "Slit 1 Horizontal Aperture (um)",  valueType=float, orientation="horizontal")

        gui.separator(box_2)

        ShadowGui.lineEdit(box_2, self, "slit_2_distance", "Slit 2 Distance from Goniometer Center (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_2, self, "slit_2_vertical_aperture", "Slit 2 Vertical Aperture (um)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_2, self, "slit_2_horizontal_aperture", "Slit 2 Horizontal Aperture (um)",  valueType=float, orientation="horizontal")

        box_3 = ShadowGui.widgetBox(tab_setting, "Scan Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_3, self, "start_angle", "Start Angle (deg)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_3, self, "stop_angle", "Stop Angle (deg)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_3, self, "step", "Step (deg)",  valueType=float, orientation="horizontal")

        box_4 = ShadowGui.widgetBox(tab_setting, "Aberrations Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_4, self, "horizontal_displacement", "Capillary H Displacement (um)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_4, self, "vertical_displacement", "Capillary V Displacement (um)", valueType=float, orientation="horizontal")
        gui.comboBox(box_4, self, "calculate_absorption", label="Calculate Absorption", items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")

        #####################

        box_5 = ShadowGui.widgetBox(tab_reflections, "Diffraction Parameters", addSpace=True, orientation="vertical")

        gui.comboBox(box_5, self, "set_number_of_peaks", label="set Number of Peaks?", callback=self.setNumberOfPeaks, items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")
        self.le_number_of_peaks = ShadowGui.lineEdit(box_5, self, "number_of_peaks", "Number of Peaks", valueType=float, orientation="horizontal")
        gui.separator(box_5)

        self.setNumberOfPeaks()

        ShadowGui.widgetBox(self.controlArea, "", addSpace=True, orientation="vertical", height=40)

        button = gui.button(self.controlArea, self, "Simulate", callback=self.simulate)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

        self.image_box = gui.widgetBox(self.mainArea, "Plot Result", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH)

        gui.rubber(self.mainArea)


    def setNumberOfPeaks(self):
        self.le_number_of_peaks.setEnabled(self.set_number_of_peaks==1)

    def replaceObject(self, object):
        if self.plot_canvas is not None:
            self.image_box.layout().removeWidget(self.plot_canvas)
        return_object = self.plot_canvas
        self.plot_canvas = object
        self.image_box.layout().addWidget(self.plot_canvas)

    def replace_plot(self, plot):
        old_figure = self.replaceObject(plot)

        if not old_figure is None:
            old_figure = None
            ST.plt.close("all")
            gc.collect()

    def plotResult(self, tth, counts):

        if not len(tth)==0:
            plot = PlotWindow(roi=True, control=True, position=True)
            plot.setDefaultPlotLines(True)
            plot.setActiveCurveColor(color='darkblue')
            plot.addCurve(tth, counts, "XRD Diffraction pattern", symbol=',', color='blue') #'+', '^',
            plot.setGraphXLabel("2Theta (deg)")
            plot.setGraphYLabel("Intensity (arbitrary units)")
            plot.setDrawModeEnabled(True, 'rectangle')
            plot.setZoomModeEnabled(True)

            self.replace_plot(plot)

    def simulate(self):

        log_file = open("log.txt", "w")

        self.progressBarInit()

        self.information(0, "Running XRD Capillary Simulation")
        qApp.processEvents()

        self.progressBarSet(0)

        go = numpy.where(self.input_beam.beam.rays[:,9] == 1)

        go_input_beam = Orange.shadow.ShadowBeam()
        go_input_beam.beam.rays = copy.deepcopy(self.input_beam.beam.rays[go])

        random_generator = random.Random()

        lattice_parameter = self.getLatticeParameter(self.sample_material)
        reflections = self.getReflections(self.sample_material, self.number_of_peaks)

        number_of_rays = len(go_input_beam.beam.rays)

        rays = range(0, number_of_rays)

        capillary_radius = self.capillary_diameter*0.5
        distance = self.detector_distance
        displacement_h = self.horizontal_displacement*0.0001
        displacement_v = self.vertical_displacement*0.0001

        log_file.write("1: inzio calcolo\n")
        log_file.flush()

        massAttenuationCoefficient = 1.0

        if self.calculate_absorption :
            k_avg = numpy.average(numpy.array(go_input_beam.beam.rays[:, 9]))
            wavelength = 2*math.pi/k_avg
            massAttenuationCoefficient = self.getMassAttenuationCoefficient(wavelength, self.packing_factor)

        self.information(0, "Calculating intersections with capillary")
        qApp.processEvents()

        diffracted_rays = []

        percentage_fraction = 50/number_of_rays
        bar_value = 0

        log_file.write("2: reflections " + str(len(reflections)) + "\n")
        log_file.flush()

        for rayIndex in rays:

            # costruzione intersezione con capillare + displacement del capillare
            alfa = go_input_beam.beam.rays[rayIndex,3]/go_input_beam.beam.rays[rayIndex,4]
            gamma = go_input_beam.beam.rays[rayIndex,5]/go_input_beam.beam.rays[rayIndex,4]
            X_pr = go_input_beam.beam.rays[rayIndex,0] + (distance/go_input_beam.beam.rays[rayIndex,4])*go_input_beam.beam.rays[rayIndex,3]
            Z_pr = go_input_beam.beam.rays[rayIndex,2] + (distance/go_input_beam.beam.rays[rayIndex,4])*go_input_beam.beam.rays[rayIndex,5]

            a = 1+gamma**2
            b = 2*displacement_h+2*gamma*Z_pr+2*displacement_v*gamma
            c = Z_pr**2 + displacement_h**2 + displacement_v**2 - capillary_radius**2 + 2*displacement_v*Z_pr

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

                entry_point = [x1, y1, z1]

                random_value = random_generator.random()

                # calcolo di un punto casuale sul segmento congiungente.

                x_point = x1 + (x2 - x1)*random_value
                y_point = y1 + (y2 - y1)*random_value
                z_point = z1 + (z2 - z1)*random_value

                reflection_index=-1

                for reflection in reflections:
                    reflection_index = reflection_index +1

                    # calcolo rotazione del vettore d'onda pari all'angolo di bragg

                    k_mod = go_input_beam.beam.rays[rayIndex,10]

                    v_in = [go_input_beam.beam.rays[rayIndex,3],
                            go_input_beam.beam.rays[rayIndex,4],
                            go_input_beam.beam.rays[rayIndex,5]]

                    #
                    # calcolo dell'asse di rotazione: k x z/|k x z|
                    #

                    z_axis = [0, 0, 1]
                    asse_rot = ShadowMath.vector_normalize(ShadowMath.vectorial_product(v_in, z_axis))

                    twotheta_reflection = 2*self.calculateBraggAngle(k_mod, reflection.h, reflection.k, reflection.l, lattice_parameter)

                    if math.degrees(twotheta_reflection) > self.start_angle and math.degrees(twotheta_reflection)  < self.stop_angle:
                        #
                        # calcolo del vettore ruotato di 2theta bragg, con la formula di Rodrigues:
                        #
                        # k_diffracted = k * cos(2th) + (k x asse_rot) * sin(2th) + k(k . asse_rot)(1 - cos(2th))
                        #                                                                       |
                        #                                                                       =0
                        # vx vy vz
                        # ax ay az
                        #

                        v_out = ShadowMath.vector_sum(ShadowMath.vector_multiply(v_in, math.cos(twotheta_reflection)),
                                                      ShadowMath.vector_multiply(ShadowMath.vectorial_product(asse_rot, v_in), math.sin(twotheta_reflection)))

                        k_out = ShadowMath.vector_multiply(v_out, k_mod)

                        # intersezione raggi con sfera di raggio distanza con il detector. le intersezioni con Z < 0 vengono rigettate

                        R_sp = self.detector_distance
                        origin_point = [x_point, y_point, z_point]
                        #
                        # retta P = origin_point + v t
                        #
                        # punto P0 minima distanza con il centro della sfera in 0,0,0
                        #
                        # (P0 - O) * v = 0 => P0 * v = 0 => (origin_point + v t0) * v = 0
                        #
                        # => t0 = - origin_point * v

                        t_0 = -1*ShadowMath.scalar_product(origin_point, v_out)
                        P_0 = ShadowMath.vector_sum(origin_point, ShadowMath.vector_multiply(v_out, t_0))

                        b = ShadowMath.vector_modulus(P_0)
                        a = math.sqrt(R_sp*R_sp - b*b)

                        P_1 = ShadowMath.vector_sum(origin_point, ShadowMath.vector_multiply(v_out, t_0-a))
                        P_2 = ShadowMath.vector_sum(origin_point, ShadowMath.vector_multiply(v_out, t_0+a))

                        absorption = 1
                        if (self.calculate_absorption == 1):
                            absorption = self.calculateAbsorption(massAttenuationCoefficient, entry_point, origin_point, v_out, capillary_radius)

                        # ok se P2 con z > 0

                        attenuation_factor = math.sqrt(reflection.relative_intensity*absorption)

                        if (P_2[2] >= 0):
                            #
                            # genesi del nuovo raggio diffratto attenuato dell'intensità relativa e dell'assorbimento
                            #

                            diffracted_ray = numpy.zeros(18)

                            diffracted_ray[0]  = origin_point[0]                                                                # X
                            diffracted_ray[1]  = origin_point[1]                                                                # Y
                            diffracted_ray[2]  = origin_point[2]                                                                # Z
                            diffracted_ray[3]  = v_out[0]                                                               # director cos x
                            diffracted_ray[4]  = v_out[1]                                                               # director cos y
                            diffracted_ray[5]  = v_out[2]                                                               # director cos z
                            diffracted_ray[6]  = go_input_beam.beam.rays[rayIndex,6]*attenuation_factor  # Es_x
                            diffracted_ray[7]  = go_input_beam.beam.rays[rayIndex,7]*attenuation_factor  # Es_y
                            diffracted_ray[8]  = go_input_beam.beam.rays[rayIndex,8]*attenuation_factor  # Es_z
                            diffracted_ray[9]  = go_input_beam.beam.rays[rayIndex,9]                                # good/lost
                            diffracted_ray[10] = go_input_beam.beam.rays[rayIndex,10]                               # |k|
                            diffracted_ray[11] = go_input_beam.beam.rays[rayIndex,11]                               # ray index
                            diffracted_ray[12] = 1                                                                  # good only
                            diffracted_ray[13] = go_input_beam.beam.rays[rayIndex,12]                               # Es_phi
                            diffracted_ray[14] = go_input_beam.beam.rays[rayIndex,13]                               # Ep_phi
                            diffracted_ray[15] = go_input_beam.beam.rays[rayIndex,14]*attenuation_factor # Ep_x
                            diffracted_ray[16] = go_input_beam.beam.rays[rayIndex,15]*attenuation_factor # Ep_y
                            diffracted_ray[17] = go_input_beam.beam.rays[rayIndex,16]*attenuation_factor # Ep_z

                            diffracted_rays.append(diffracted_ray)

            bar_value += percentage_fraction
            self.progressBarSet(bar_value)

        log_file.write("3: numero raggi diffratti" + str(len(diffracted_rays)) +  "\n")
        log_file.flush()

        ################################
        # ARRAYS FOR OUTPUT AND PLOTS

        steps = range(0, math.floor((self.stop_angle-self.start_angle)/self.step))
        twotheta_angles = []
        counts = []

        for step_index in steps:
            twotheta_angles.append(self.start_angle + step_index*self.step)
            counts.append(0)

        twotheta_angles = numpy.array(twotheta_angles)
        counts = numpy.array(counts)

        ################################
        # VALUES TO BE CALCULATED ONCE

        self.D_1 = self.slit_1_distance
        self.D_2 = self.slit_2_distance

        self.horizontal_acceptance_1 = self.slit_1_horizontal_aperture*1e-4*0.5
        self.vertical_acceptance_1 = self.slit_1_vertical_aperture*1e-4*0.5

        self.horizontal_acceptance_2 = self.slit_2_horizontal_aperture*1e-4*0.5
        self.vertical_acceptance_2 = self.slit_2_vertical_aperture*1e-4*0.5

        theta_slit = math.atan(self.vertical_acceptance_1/self.D_1)

        ################################

        number_of_rays=len(diffracted_rays)
        rays = range(0, number_of_rays)

        percentage_fraction = 50/number_of_rays

        beam_diffracted = Orange.shadow.ShadowBeam(number_of_rays=number_of_rays)

        max_position = len(twotheta_angles) - 1

        for rayIndex in rays:
            diffracted_ray = diffracted_rays[rayIndex]

            x_0_i = diffracted_ray[0]
            y_0_i = diffracted_ray[1]
            z_0_i = diffracted_ray[2]

            v_x_i = diffracted_ray[3]
            v_y_i = diffracted_ray[4]
            v_z_i = diffracted_ray[5]

            Es_x_i = diffracted_ray[6]
            Es_y_i = diffracted_ray[7]
            Es_z_i = diffracted_ray[8]

            Ep_x_i = diffracted_ray[15]
            Ep_y_i = diffracted_ray[16]
            Ep_z_i = diffracted_ray[17]

            #
            # calcolo dell'angolo di intercettato dal vettore con il piano xy
            #

            theta_ray = math.atan(v_z_i/math.sqrt(v_x_i*v_x_i + v_y_i*v_y_i))

            theta_lim_inf = math.degrees(theta_ray-3*theta_slit)
            theta_lim_sup = math.degrees(theta_ray+3*theta_slit)

            # il ciclo sugli step del detector dovrebbe essere attorno a quest'angolo +- un fattore sufficiente di volte
            # l'angolo intercettato dalla prima slit

            if (theta_lim_inf < self.stop_angle and theta_lim_sup > self.start_angle):
                n_steps_inf = math.floor((max(theta_lim_inf, self.start_angle)-self.start_angle)/self.step)
                n_steps_sup = math.ceil((min(theta_lim_sup, self.stop_angle)-self.start_angle)/self.step)

                steps_between_limits = range(0, n_steps_sup - n_steps_inf)

                for n_step in steps_between_limits:
                    twotheta_angle = self.start_angle + (n_steps_inf + n_step)*self.step

                    intensity = self.calculateIntensity(math.radians(twotheta_angle),
                                                        x_0_i,
                                                        y_0_i,
                                                        z_0_i,
                                                        v_x_i,
                                                        v_y_i,
                                                        v_z_i,
                                                        Es_x_i,
                                                        Es_y_i,
                                                        Es_z_i,
                                                        Ep_x_i,
                                                        Ep_y_i,
                                                        Ep_z_i)

                    position = min(n_steps_inf + n_step, max_position)

                    counts[position]=counts[position]+intensity

            bar_value += percentage_fraction
            self.progressBarSet(bar_value)

        out_file = open("XRD_Profile.xy","w")

        cursor = range(0, len(twotheta_angles))

        for angleIndex in cursor:
            out_file.write(str(twotheta_angles[angleIndex]) + " " + str(counts[angleIndex]) + "\n")
            out_file.flush()

        self.plotResult(twotheta_angles, counts)

        self.progressBarSet(100)

        out_file.close()
        log_file.close()

        self.information()
        qApp.processEvents()

        self.progressBarFinished()
        qApp.processEvents()

        self.send("Beam", beam_diffracted)

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

    def calculateAbsorption(self, mass_attenuation_coefficient, entry_point, origin_point, direction_versor, capillary_radius):

        #
        # calcolo intersezione con superficie del capillare:
        #
        # x = xo + x' t
        # y = yo + y' t
        # z = zo + z' t
        #
        # (y-dh)^2 + (z-dv)^2 = (Dc/2)^2
        #

        c_1 = direction_versor[1]/direction_versor[0]
        c_2 = direction_versor[2]/direction_versor[0]

        k_1 = origin_point[1]-c_1*origin_point[0]
        k_2 = origin_point[2]-c_2*origin_point[0]

        a = (c_1*c_1 + c_2*c_2)
        b = 2*(c_1*k_1 + c_2*k_2)
        c = k_1*k_1 + k_2*k_2 - capillary_radius*capillary_radius

        x_1 = (-b + math.sqrt(b*b + 4*a*c))/(2*a)
        x_2 = (-b - math.sqrt(b*b + 4*a*c))/(2*a)

        exit_point = [0, 0, 0]
        x_sol = 0

        if (numpy.sign((x_1-origin_point[0]))==numpy.sign(direction_versor[0])): # solo semiretta in avanti -> t > 0
            x_sol = x_1
        else:
            x_sol = x_2

        exit_point[0] = x_sol
        exit_point[1] = origin_point[1] + c_1 * x_sol
        exit_point[2] = origin_point[2] + c_2 * x_sol

        distance = ShadowMath.point_distance(entry_point, origin_point) + ShadowMath.point_distance(origin_point, exit_point)

        return math.exp(-mass_attenuation_coefficient*distance)

    def calculateIntensity(self, twotheta_angle, 
                           x_0, 
                           y_0, 
                           z_0, 
                           v_x, 
                           v_y, 
                           v_z,                                                           
                           Es_x,
                           Es_y,
                           Es_z,                                                        
                           Ep_x,
                           Ep_y,
                           Ep_z):
        intensity = 0

        sin_twotheta = math.sin(twotheta_angle)
        cos_twotheta = math.cos(twotheta_angle)

        x_c_s1 = 0
        y_c_s1 = self.D_1*cos_twotheta
        z_c_s1 = self.D_1*sin_twotheta

        x_c_s2 = 0
        y_c_s2 = self.D_2*cos_twotheta
        z_c_s2 = self.D_2*sin_twotheta

        # intersezione del raggio con il piano intercettato dalla slit
        y_1_int = (self.D_1-(z_0-(v_z/v_y)*y_0)*sin_twotheta)/(cos_twotheta+(v_z/v_y)*sin_twotheta)
        z_1_int = z_0+(v_z/v_y)*(y_1_int-y_0)
        x_1_int = x_0+(v_x/v_z)*(y_1_int-y_0)

        d_1_x = x_1_int-x_c_s1
        d_1_y = y_1_int-y_c_s1
        d_1_z = z_1_int-z_c_s1

        dist_yz = math.sqrt(d_1_y*d_1_y + d_1_z*d_1_z)
        dist_x  = abs(d_1_x)

        if dist_x <= self.horizontal_acceptance_1 and dist_yz <= self.vertical_acceptance_1:

            # intersezione del raggio con il piano intercettato dalla slit
            y_2_int = (self.D_2-(z_0-(v_z/v_y)*y_0)*sin_twotheta)/(cos_twotheta+(v_z/v_y)*sin_twotheta)
            z_2_int = z_0+(v_z/v_y)*(y_2_int-y_0)
            x_2_int = x_0+(v_x/v_z)*(y_2_int-y_0)

            d_2_x = x_2_int-x_c_s2
            d_2_y = y_2_int-y_c_s2
            d_2_z = z_2_int-z_c_s2

            dist_yz = math.sqrt(d_2_y*d_2_y + d_2_z*d_2_z)
            dist_x  = abs(d_2_x)

            if dist_x <= self.horizontal_acceptance_2 and dist_yz <= self.vertical_acceptance_2:
                intensity = (Es_x*Es_x + Es_y*Es_y + Es_z*Es_z) + (Ep_x*Ep_x + Ep_y*Ep_y + Ep_z*Ep_z)

        return intensity


    def getMassAttenuationCoefficient(self, wavelength, packing_factor):

        absorption = Absorption.Absorb(Wave=wavelength, Packing=packing_factor)
        absorption.SetElems(self.getChemicalFormula(self.sample_material))

        return absorption.ComputeMassAttenuationCoefficient()

    def getChemicalFormula(self, material):
        if material == 0: # LaB6
            return "LaB6"
        elif material ==1: #Si
            return "Si"
        else:
            return -1

    def getLatticeParameter(self, material):
        if material == 0: # LaB6
            return 4.15689 #Angstrom
        elif material ==1: #Si
            return 5.43123 #Angstrom
        else:
            return -1

    def getReflections(self, material, number_of_peaks):
        reflections = []

        if material == 0: # LaB6
            if(number_of_peaks > 0): reflections.append(Reflection(1,0,0,0.54))
            if(number_of_peaks > 1): reflections.append(Reflection(1,1,0,1.00 ))
            if(number_of_peaks > 2): reflections.append(Reflection(1,1,1,0.41))
            if(number_of_peaks > 3): reflections.append(Reflection(2,0,0,0.22))
            if(number_of_peaks > 4): reflections.append(Reflection(2,1,0,0.46))
            if(number_of_peaks > 5): reflections.append(Reflection(2,1,1,0.24))
            if(number_of_peaks > 6): reflections.append(Reflection(2,2,0,0.08))
            if(number_of_peaks > 7): reflections.append(Reflection(3,0,0,0.23))
            if(number_of_peaks > 8): reflections.append(Reflection(3,1,0,0.16))
            if(number_of_peaks > 9): reflections.append(Reflection(3,1,1,0.10))
            if(number_of_peaks > 10): reflections.append(Reflection(2,2,2,0.02))
            if(number_of_peaks > 11): reflections.append(Reflection(3,2,0,0.06))
            if(number_of_peaks > 12): reflections.append(Reflection(3,2,1,0.13))
            if(number_of_peaks > 13): reflections.append(Reflection(4,0,0,0.02))
            if(number_of_peaks > 14): reflections.append(Reflection(4,1,0,0.08))
            if(number_of_peaks > 15): reflections.append(Reflection(3,3,0,0.07))
            if(number_of_peaks > 16): reflections.append(Reflection(3,3,1,0.03))
            if(number_of_peaks > 17): reflections.append(Reflection(4,2,0,0.04))
            if(number_of_peaks > 18): reflections.append(Reflection(4,2,1,0.09))
            if(number_of_peaks > 19): reflections.append(Reflection(3,3,2,0.03))
            if(number_of_peaks > 20): reflections.append(Reflection(4,2,2,0.03))
            if(number_of_peaks > 21): reflections.append(Reflection(5,0,0,0.03))
            if(number_of_peaks > 22): reflections.append(Reflection(5,1,0,0.10))
            if(number_of_peaks > 23): reflections.append(Reflection(5,1,1,0.06))
        elif material == 1: # Si
            if(number_of_peaks > 0): reflections.append(Reflection(1,1,1))
            if(number_of_peaks > 1): reflections.append(Reflection(2,2,0))
            if(number_of_peaks > 2): reflections.append(Reflection(3,1,1))
            if(number_of_peaks > 3): reflections.append(Reflection(4,0,0))
            if(number_of_peaks > 4): reflections.append(Reflection(3,3,1))
            if(number_of_peaks > 5): reflections.append(Reflection(4,2,2))
            if(number_of_peaks > 6): reflections.append(Reflection(5,1,1))
            if(number_of_peaks > 7): reflections.append(Reflection(4,4,0))
            if(number_of_peaks > 8): reflections.append(Reflection(5,3,1))
            if(number_of_peaks > 9): reflections.append(Reflection(6,2,0))
            if(number_of_peaks > 10): reflections.append(Reflection(5,3,3))
        else:
            return None


        return reflections

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