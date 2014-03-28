import sys, math, copy, numpy, random, gc
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication, qApp

import Shadow.ShadowTools as ST

from Orange.widgets.shadow_gui import ow_automatic_element
from Orange.shadow.shadow_util import ShadowGui, ShadowMath, ShadowPhysics
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

#    outputs = [{"name":"Beam",
#                "type":Orange.shadow.ShadowBeam,
#                "doc":"Shadow Beam",
#                "id":"beam"}]

    TABS_AREA_HEIGHT = 550
    TABS_AREA_WIDTH = 442
    CONTROL_AREA_WIDTH = 450

    IMAGE_WIDTH = 920
    IMAGE_HEIGHT = 825

    capillary_diameter = Setting(0.3)
    capillary_material = Setting(0)
    sample_material = Setting(0)
    packing_factor = Setting(0.6)

    horizontal_displacement = Setting(0)
    vertical_displacement = Setting(0)
    calculate_absorption = Setting(0)
    normalization_factor = Setting(100)

    shift_2theta = Setting(0)

    slit_1_vertical_displacement = Setting(0)
    slit_2_vertical_displacement = Setting(0)
    slit_1_horizontal_displacement = Setting(0)
    slit_2_horizontal_displacement = Setting(0)

    detector_distance = Setting(95)
    slit_1_distance = Setting(0)
    slit_1_vertical_aperture = Setting(0)
    slit_1_horizontal_aperture = Setting(0)
    slit_2_distance = Setting(0)
    slit_2_vertical_aperture = Setting(0)
    slit_2_horizontal_aperture = Setting(0)

    start_angle_na = Setting(10)
    stop_angle_na = Setting(120)
    step = Setting(0.002)
    start_angle = 0
    stop_angle = 0

    set_number_of_peaks = Setting(0)
    number_of_peaks = Setting(1)

    incremental = Setting(0)
    number_of_executions = Setting(1)
    current_execution = 0
    keep_result = Setting(0)

    add_background = Setting(0)
    n_sigma=Setting(0)
    add_chebyshev = Setting(0)
    cheb_coeff_0 = Setting(0)
    cheb_coeff_1 = Setting(0)
    cheb_coeff_2 = Setting(0)
    cheb_coeff_3 = Setting(0)
    cheb_coeff_4 = Setting(0)
    cheb_coeff_5 = Setting(0)

    add_expdecay = Setting(0)
    expd_coeff_0 = Setting(0)
    expd_coeff_1 = Setting(0)
    expd_coeff_2 = Setting(0)
    expd_coeff_3 = Setting(0)
    expd_coeff_4 = Setting(0)
    expd_coeff_5 = Setting(0)
    expd_decayp_0 = Setting(0)
    expd_decayp_1 = Setting(0)
    expd_decayp_2 = Setting(0)
    expd_decayp_3 = Setting(0)
    expd_decayp_4 = Setting(0)
    expd_decayp_5 = Setting(0)

    want_main_area=1
    plot_canvas=None

    twotheta_angles = []
    counts = []

    log_file = None

    def __init__(self):
        super().__init__()

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        tabs = ShadowGui.tabWidget(self.controlArea, height=self.TABS_AREA_HEIGHT, width=self.TABS_AREA_WIDTH)

        self.tab_diffraction = ShadowGui.createTabPage(tabs, "Diffraction")
        self.tab_goniometer = ShadowGui.createTabPage(tabs, "Goniometer")
        self.tab_aberrations = ShadowGui.createTabPage(tabs, "Aberrations")
        self.tab_background = ShadowGui.createTabPage(tabs, "Background")

        box_2theta_arm = ShadowGui.widgetBox(self.tab_goniometer, "2Theta Arm Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_2theta_arm, self, "detector_distance", "Detector Distance (cm)",  tooltip="Detector Distance (cm)", valueType=float, orientation="horizontal")

        gui.separator(box_2theta_arm)

        ShadowGui.lineEdit(box_2theta_arm, self, "slit_1_distance", "Slit 1 Distance from Goniometer Center (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_2theta_arm, self, "slit_1_vertical_aperture", "Slit 1 Vertical Aperture (um)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_2theta_arm, self, "slit_1_horizontal_aperture", "Slit 1 Horizontal Aperture (um)",  valueType=float, orientation="horizontal")

        gui.separator(box_2theta_arm)

        ShadowGui.lineEdit(box_2theta_arm, self, "slit_2_distance", "Slit 2 Distance from Goniometer Center (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_2theta_arm, self, "slit_2_vertical_aperture", "Slit 2 Vertical Aperture (um)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_2theta_arm, self, "slit_2_horizontal_aperture", "Slit 2 Horizontal Aperture (um)",  valueType=float, orientation="horizontal")

        box_scan = ShadowGui.widgetBox(self.tab_goniometer, "Scan Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_scan, self, "start_angle_na", "Start Angle (deg)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_scan, self, "stop_angle_na", "Stop Angle (deg)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_scan, self, "step", "Step (deg)",  valueType=float, orientation="horizontal")

        #####################

        box_sample = ShadowGui.widgetBox(self.tab_diffraction, "Sample Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_sample, self, "capillary_diameter", "Capillary Diameter [mm]", valueType=float, orientation="horizontal")
        gui.comboBox(box_sample, self, "capillary_material", label="Capillary Material", items=["Glass", "Kapton"], sendSelectedValue=False, orientation="horizontal")
        gui.comboBox(box_sample, self, "sample_material", label="Material", items=["LaB6", "Si", "ZnO"], sendSelectedValue=False, orientation="horizontal")
        ShadowGui.lineEdit(box_sample, self, "packing_factor", "Packing Factor (0.0...1.0)", valueType=float, orientation="horizontal")

        box_diffraction = ShadowGui.widgetBox(self.tab_diffraction, "Diffraction Parameters", addSpace=True, orientation="vertical")

        gui.comboBox(box_diffraction, self, "set_number_of_peaks", label="set Number of Peaks?", callback=self.setNumberOfPeaks, items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")
        self.le_number_of_peaks = ShadowGui.lineEdit(box_diffraction, self, "number_of_peaks", "Number of Peaks", valueType=int, orientation="horizontal")
        gui.separator(box_diffraction)

        self.setNumberOfPeaks()

        #####################

        box_capillary = ShadowGui.widgetBox(self.tab_aberrations, "Capillary Aberrations", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_capillary, self, "horizontal_displacement", "Capillary H Displacement (um)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_capillary, self, "vertical_displacement", "Capillary V Displacement (um)", valueType=float, orientation="horizontal")
        gui.separator(box_capillary)
        gui.comboBox(box_capillary, self, "calculate_absorption", label="Calculate Absorption", callback=self.setAbsorption, items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")
        self.le_normalization_factor = ShadowGui.lineEdit(box_capillary, self, "normalization_factor", "Normalization Factor", valueType=float, orientation="horizontal")

        self.setAbsorption()

        box_gon_aberrations = ShadowGui.widgetBox(self.tab_aberrations, "Goniometer Aberrations", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(box_gon_aberrations, self, "shift_2theta", "Shift 2Theta (deg)", valueType=float, orientation="horizontal")
        gui.separator(box_gon_aberrations)
        ShadowGui.lineEdit(box_gon_aberrations, self, "slit_1_vertical_displacement", "Slit 1 V Displacement (um)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_gon_aberrations, self, "slit_2_vertical_displacement", "Slit 2 V Displacement (um)", valueType=float, orientation="horizontal")
        gui.separator(box_gon_aberrations)
        ShadowGui.lineEdit(box_gon_aberrations, self, "slit_1_horizontal_displacement", "Slit 1 H Displacement (um)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(box_gon_aberrations, self, "slit_2_horizontal_displacement", "Slit 2 H Displacement (um)", valueType=float, orientation="horizontal")

        #####################

        box_background = ShadowGui.widgetBox(self.tab_background, "Background Parameters", addSpace=True, orientation="vertical", height=510, width=420)

        gui.comboBox(box_background, self, "add_background", label="Add Background", items=["No", "Yes"], callback=self.setAddBackground, sendSelectedValue=False, orientation="horizontal")

        gui.separator(box_background)

        self.box_background_1 = ShadowGui.widgetBox(box_background, "", addSpace=True, orientation="vertical")

        gui.comboBox(self.box_background_1, self, "n_sigma", label="Noise (Nr. Sigma)", items=["0.5", "1", "1.5", "2", "2.5", "3"], sendSelectedValue=False, orientation="horizontal")

        self.box_background_2 = ShadowGui.widgetBox(box_background, "", addSpace=True, orientation="horizontal")

        self.box_chebyshev = ShadowGui.widgetBox(self.box_background_2, "Chebyshev", addSpace=True, orientation="vertical")
        gui.checkBox(self.box_chebyshev, self, "add_chebyshev", "add Background", callback=self.setChebyshev)
        gui.separator(self.box_chebyshev)
        self.box_chebyshev_2 = ShadowGui.widgetBox(self.box_chebyshev, "", addSpace=True, orientation="vertical")
        ShadowGui.lineEdit(self.box_chebyshev_2, self, "cheb_coeff_0", "A0", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_chebyshev_2, self, "cheb_coeff_1", "A1", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_chebyshev_2, self, "cheb_coeff_2", "A2", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_chebyshev_2, self, "cheb_coeff_3", "A3", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_chebyshev_2, self, "cheb_coeff_4", "A4", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_chebyshev_2, self, "cheb_coeff_5", "A5", valueType=float, orientation="horizontal")
         
        self.box_expdecay = ShadowGui.widgetBox(self.box_background_2, "Exp Decay", addSpace=True, orientation="vertical")
        gui.checkBox(self.box_expdecay, self, "add_expdecay", "add Background", callback=self.setExpDecay)
        gui.separator(self.box_expdecay)
        self.box_expdecay_2 = ShadowGui.widgetBox(self.box_expdecay, "", addSpace=True, orientation="vertical")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_coeff_0", "A0", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_coeff_1", "A1", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_coeff_2", "A2", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_coeff_3", "A3", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_coeff_4", "A4", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_coeff_5", "A5", valueType=float, orientation="horizontal")
        gui.separator(self.box_expdecay_2)
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_decayp_0", "H0", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_decayp_1", "H1", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_decayp_2", "H2", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_decayp_3", "H3", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_decayp_4", "H4", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_expdecay_2, self, "expd_decayp_5", "H5", valueType=float, orientation="horizontal")

        self.setAddBackground()

        #####################

        box_simulation = ShadowGui.widgetBox(self.controlArea, "Simulation", addSpace=True, orientation="vertical", height=145)

        gui.checkBox(box_simulation, self, "keep_result", "Keep Result (Diffraction + Background")
        gui.checkBox(box_simulation, self, "incremental", "Incremental Diffraction Simulation", callback=self.setIncremental)
        self.le_number_of_executions = ShadowGui.lineEdit(box_simulation, self, "number_of_executions", "Number of Executions", valueType=int, orientation="horizontal")

        self.setIncremental()

        gui.separator(box_simulation, height=10)
        self.le_current_execution = ShadowGui.lineEdit(box_simulation, self, "current_execution", "Current Execution", valueType=int, orientation="horizontal")
        self.le_current_execution.setReadOnly(True)

        button = gui.button(self.controlArea, self, "Simulate", callback=self.simulate)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

        self.image_box = gui.widgetBox(self.mainArea, "Plot Result", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH)

        gui.rubber(self.mainArea)

    def setBeam(self, beam):
        self.input_beam = beam

        if self.is_automatic_run:
           self.simulate()

    ############################################################
    # GUI MANAGEMENT METHODS
    ############################################################

    def setTabsEnabled(self, enabled=True):
        self.tab_diffraction.setEnabled(enabled)
        self.tab_goniometer.setEnabled(enabled)
        self.tab_aberrations.setEnabled(enabled)
        self.tab_background.setEnabled(enabled)

    def setIncremental(self):
        self.le_number_of_executions.setEnabled(self.incremental==1)

    def setAbsorption(self):
        self.le_normalization_factor.setEnabled(self.calculate_absorption==1)

    def setNumberOfPeaks(self):
        self.le_number_of_peaks.setEnabled(self.set_number_of_peaks==1)

    def setAddBackground(self):
        self.box_background_1.setVisible(self.add_background==1)
        self.box_background_2.setVisible(self.add_background==1)
        self.setChebyshev()
        self.setExpDecay()
    
    def setChebyshev(self):
        self.box_chebyshev_2.setEnabled(self.add_chebyshev==1)
        
    def setExpDecay(self):
        self.box_expdecay_2.setEnabled(self.add_expdecay==1)

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

    def plotResult(self):

        if not len(self.twotheta_angles)==0:
            plot = PlotWindow(roi=True, control=True, position=True)
            plot.setDefaultPlotLines(True)
            plot.setActiveCurveColor(color='darkblue')
            plot.addCurve(self.twotheta_angles, self.counts, "XRD Diffraction pattern", symbol=',', color='blue') #'+', '^',
            plot.setGraphXLabel("2Theta (deg)")
            plot.setGraphYLabel("Intensity (arbitrary units)")
            plot.setDrawModeEnabled(True, 'rectangle')
            plot.setZoomModeEnabled(True)

            self.replace_plot(plot)

    ############################################################
    # MAIN METHOD - SIMULATION ALGORITHM
    ############################################################

    def simulate(self):

        self.setTabsEnabled(False)

        executions = range(0,1)

        if (self.incremental==1):
            executions = range(0, self.number_of_executions)

        self.log_file = open("log.txt", "w")

        ################################
        # VALUE CALCULATED ONCE

        go = numpy.where(self.input_beam.beam.rays[:,9] == 1)

        go_input_beam = Orange.shadow.ShadowBeam()
        go_input_beam.beam.rays = copy.deepcopy(self.input_beam.beam.rays[go])

        random_generator = random.Random()

        lattice_parameter = self.getLatticeParameter(self.sample_material)
        reflections = self.getReflections(self.sample_material, self.number_of_peaks)

        number_of_input_rays = len(go_input_beam.beam.rays)
        input_rays = range(0, number_of_input_rays)

        self.log_file.write("numero raggi input: " + str(number_of_input_rays) +  "\n")
        self.log_file.flush()

        # distances in CM

        capillary_radius = self.capillary_diameter*0.1*0.5
        displacement_h = self.horizontal_displacement*1e-4
        displacement_v = self.vertical_displacement*1e-4

        self.D_1 = self.slit_1_distance
        self.D_2 = self.slit_2_distance

        self.horizontal_acceptance_1 = self.slit_1_horizontal_aperture*1e-4*0.5
        self.vertical_acceptance_1 = self.slit_1_vertical_aperture*1e-4*0.5

        self.horizontal_acceptance_2 = self.slit_2_horizontal_aperture*1e-4*0.5
        self.vertical_acceptance_2 = self.slit_2_vertical_aperture*1e-4*0.5

        self.slit_1_vertical_displacement_cm = self.slit_1_vertical_displacement*1e-4
        self.slit_2_vertical_displacement_cm = self.slit_2_vertical_displacement*1e-4
        self.slit_1_horizontal_displacement_cm = self.slit_1_horizontal_displacement*1e-4
        self.slit_2_horizontal_displacement_cm = self.slit_2_horizontal_displacement*1e-4

        theta_slit = math.atan(self.vertical_acceptance_1/self.D_1)

        ################################
        # ARRAYS FOR OUTPUT AND PLOTS

        steps = range(0, math.floor((self.stop_angle_na-self.start_angle_na)/self.step))

        self.start_angle = self.start_angle_na + self.shift_2theta
        self.stop_angle = self.stop_angle_na + self.shift_2theta

        if self.keep_result == 0 or len(self.twotheta_angles) == 0:
            self.twotheta_angles = []
            self.counts = []

            for step_index in steps:
                self.twotheta_angles.append(self.start_angle + step_index*self.step)
                self.counts.append(0)

            self.twotheta_angles = numpy.array(self.twotheta_angles)
            self.counts = numpy.array(self.counts)

        ################################
        # EXECUTION CYCLES

        for execution in executions:

            self.le_current_execution.setText(str(execution+1))

            self.progressBarInit()

            self.information(0, "Running XRD Capillary Simulation")
            qApp.processEvents()

            self.progressBarSet(0)

            self.log_file.write(str(execution) + ": inizio calcolo\n")
            self.log_file.flush()

            self.information(0, "Calculating intersections with capillary")
            qApp.processEvents()

            diffracted_rays = []

            percentage_fraction = 50/number_of_input_rays
            bar_value = 0

            self.log_file.write(str(execution) + ": reflections " + str(len(reflections)) + "\n")
            self.log_file.flush()

            for ray_index in input_rays:
                # costruzione intersezione con capillare + displacement del capillare

                x_0 = go_input_beam.beam.rays[ray_index, 0]
                y_0 = go_input_beam.beam.rays[ray_index, 1]
                z_0 = go_input_beam.beam.rays[ray_index, 2]

                if (y_0**2 + z_0**2 < capillary_radius**2):
                    v_0_x = go_input_beam.beam.rays[ray_index, 3]
                    v_0_y = go_input_beam.beam.rays[ray_index, 4]
                    v_0_z = go_input_beam.beam.rays[ray_index, 5]

                    k_1 = v_0_y/v_0_x
                    k_2 = v_0_z/v_0_x

                    a = (k_1**2 + k_2**2)
                    b = 2*(k_1*(y_0+displacement_h) + k_2*(z_0+displacement_v))
                    c = (y_0**2 + z_0**2 + 2*displacement_h*y_0 + 2*displacement_v*z_0) - capillary_radius**2 + (displacement_h**2 + displacement_v**2)

                    discriminant = b**2 - 4*a*c

                    if discriminant > 0.0:
                        x_sol_1 = (-b - math.sqrt(discriminant))/(2*a)
                        x_1 = x_0 + x_sol_1
                        y_1 = y_0 + k_1*x_sol_1
                        z_1 = z_0 + k_2*x_sol_1

                        x_sol_2 = (-b + math.sqrt(discriminant))/(2*a)
                        x_2 = x_0 + x_sol_2
                        y_2 = y_0 + k_1*x_sol_2
                        z_2 = z_0 + k_2*x_sol_2

                        entry_point = [x_1, y_1, z_1]

                        random_value = random_generator.random()

                        # calcolo di un punto casuale sul segmento congiungente.

                        x_point = x_1 + (x_2 - x_1)*random_value
                        y_point = y_1 + (y_2 - y_1)*random_value
                        z_point = z_1 + (z_2 - z_1)*random_value

                        reflection_index=-1

                        k_mod = go_input_beam.beam.rays[ray_index,10]

                        v_in = [v_0_x, v_0_y, v_0_z]
                        z_axis = [0, 0, 1]

                        #
                        # calcolo dell'asse di rotazione: k x z/|k x z|
                        #
                        asse_rot = ShadowMath.vector_normalize(ShadowMath.vectorial_product(v_in, z_axis))

                        for reflection in reflections:
                            reflection_index = reflection_index +1

                            # calcolo rotazione del vettore d'onda pari all'angolo di bragg

                            twotheta_reflection = 2*self.calculateBraggAngle(k_mod, reflection.h, reflection.k, reflection.l, lattice_parameter)

                            if math.degrees(twotheta_reflection) > self.start_angle and math.degrees(twotheta_reflection) < self.stop_angle:
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

                                # ok se P2 con z > 0
                                if (P_2[2] >= 0):

                                    #
                                    # genesi del nuovo raggio diffratto attenuato dell'intensità relativa e dell'assorbimento
                                    #

                                    diffracted_ray = numpy.zeros(19)

                                    diffracted_ray[0]  = origin_point[0]                       # X
                                    diffracted_ray[1]  = origin_point[1]                       # Y
                                    diffracted_ray[2]  = origin_point[2]                       # Z
                                    diffracted_ray[3]  = v_out[0]                              # director cos x
                                    diffracted_ray[4]  = v_out[1]                              # director cos y
                                    diffracted_ray[5]  = v_out[2]                              # director cos z
                                    diffracted_ray[6]  = go_input_beam.beam.rays[ray_index,6]  # Es_x
                                    diffracted_ray[7]  = go_input_beam.beam.rays[ray_index,7]  # Es_y
                                    diffracted_ray[8]  = go_input_beam.beam.rays[ray_index,8]  # Es_z
                                    diffracted_ray[9]  = go_input_beam.beam.rays[ray_index,9]  # good/lost
                                    diffracted_ray[10] = go_input_beam.beam.rays[ray_index,10] # |k|
                                    diffracted_ray[11] = go_input_beam.beam.rays[ray_index,11] # ray index
                                    diffracted_ray[12] = 1                                     # good only
                                    diffracted_ray[13] = go_input_beam.beam.rays[ray_index,12] # Es_phi
                                    diffracted_ray[14] = go_input_beam.beam.rays[ray_index,13] # Ep_phi
                                    diffracted_ray[15] = go_input_beam.beam.rays[ray_index,14] # Ep_x
                                    diffracted_ray[16] = go_input_beam.beam.rays[ray_index,15] # Ep_y
                                    diffracted_ray[17] = go_input_beam.beam.rays[ray_index,16] # Ep_z

                                    ray_intensity = diffracted_ray[6]**2 + diffracted_ray[7]**2 + diffracted_ray[8]**2 + \
                                                    diffracted_ray[15]**2 + diffracted_ray[16]**2 + diffracted_ray[17]**2

                                    reduction_factor = reflection.relative_intensity

                                    if (self.calculate_absorption == 1):
                                        reduction_factor = reduction_factor*self.calculateAbsorption(k_mod, entry_point, origin_point, v_out, capillary_radius, displacement_h, displacement_v)

                                    diffracted_ray[18] = ray_intensity*reduction_factor

                                    diffracted_rays.append(diffracted_ray)

                bar_value += percentage_fraction
                self.progressBarSet(bar_value)

            self.log_file.write(str(execution) + ": numero raggi diffratti: " + str(len(diffracted_rays)) +  "\n")
            self.log_file.flush()

            ################################

            number_of_diffracted_rays=len(diffracted_rays)

            if (number_of_diffracted_rays > 0):
                diffracted_rays_set = range(0, number_of_diffracted_rays)

                percentage_fraction = 50/number_of_diffracted_rays

                beam_diffracted = Orange.shadow.ShadowBeam(number_of_rays=number_of_diffracted_rays)

                max_position = len(self.twotheta_angles) - 1

                for ray_index in diffracted_rays_set:
                    diffracted_ray = diffracted_rays[ray_index]

                    x_0_i = diffracted_ray[0]
                    y_0_i = diffracted_ray[1]
                    z_0_i = diffracted_ray[2]

                    v_x_i = diffracted_ray[3]
                    v_y_i = diffracted_ray[4]
                    v_z_i = diffracted_ray[5]

                    intensity_i = diffracted_ray[18]

                    #
                    # calcolo dell'angolo di intercettato dal vettore con il piano xy
                    #

                    theta_ray = math.atan(v_z_i/math.sqrt(v_x_i**2 + v_y_i**2))

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

                            if (self.isCollectedRay(math.radians(twotheta_angle), x_0_i, y_0_i, z_0_i, v_x_i, v_y_i, v_z_i)):
                                position = min(n_steps_inf + n_step, max_position)

                                self.counts[position] += intensity_i

                    bar_value += percentage_fraction
                    self.progressBarSet(bar_value)

                self.plotResult()


        if self.add_background ==  1:
            self.information(0, "Adding Background")
            qApp.processEvents()

            self.calculateBackground(0)
            self.plotResult()

        out_file = open("XRD_Profile.xy","w")

        cursor = range(0, len(self.twotheta_angles))

        for angle_index in cursor:
            out_file.write(str(self.twotheta_angles[angle_index]) + " " + str(self.counts[angle_index]) + "\n")
            out_file.flush()

        self.log_file.close()
        out_file.close()

        self.progressBarSet(100)
        self.setTabsEnabled(True)

        self.information()
        qApp.processEvents()

        self.progressBarFinished()
        qApp.processEvents()


    ############################################################
    # ACCESSORY METHODS
    ############################################################

    def getMassAttenuationCoefficient(self, path, wavelength):

        absorption = Absorption.Absorb(Radius=path, Wave=wavelength, Packing=self.packing_factor)
        absorption.SetElems(self.getChemicalFormula(self.sample_material))

        return absorption.ComputeMassAttenuationCoefficient()

    ############################################################

    def getChemicalFormula(self, material):
        if material == 0: # LaB6
            return "LaB6"
        elif material ==1: #Si
            return "Si"
        else:
            return -1

    ############################################################

    def getLatticeParameter(self, material):
        if material == 0: # LaB6
            return 4.15689 #Angstrom
        elif material ==1: #Si
            return 5.43123 #Angstrom
        else:
            return -1

    ############################################################

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

    ############################################################

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

        return math.asin((wl*math.sqrt(h**2+k**2+l**2))/(2*a))

    ############################################################

    def calculateAbsorption(self, k_mod, entry_point, origin_point, direction_versor, capillary_radius, displacement_h, displacement_v):

        distance = 0
        absorption = 0

        #
        # calcolo intersezione con superficie del capillare:
        #
        # x = xo + x' t
        # y = yo + y' t
        # z = zo + z' t
        #
        # (y-dh)^2 + (z-dv)^2 = (Dc/2)^2
        #

        x_0 = origin_point[0]
        y_0 = origin_point[1]
        z_0 = origin_point[2]

        k_1 = direction_versor[1]/direction_versor[0]
        k_2 = direction_versor[2]/direction_versor[0]

        #
        # parametri a b c per l'equazione a(x-x0)^2 + b(x-x0) + c = 0
        #

        a = (k_1**2 + k_2**2)
        b = 2*(k_1*(y_0+displacement_h) + k_2*(z_0+displacement_v))
        c = (y_0**2 + z_0**2 + 2*displacement_h*y_0 + 2*displacement_v*z_0) - capillary_radius**2 + (displacement_h**2 + displacement_v**2)

        discriminant = b**2 - 4*a*c

        if (discriminant > 0):

            # equazioni risolte per x-x0
            x_1 = (-b + math.sqrt(discriminant))/(2*a) # (x-x0)_1
            x_2 = (-b - math.sqrt(discriminant))/(2*a) # (x-x0)_2

            x_sol = 0
            y_sol = 0
            z_sol = 0


            # solutions only with z > 0 and
            # se y-y0 > 0 allora il versore deve avere y' > 0
            # se y-y0 < 0 allora il versore deve avere y' < 0

            z_1 = z_0 + k_2*x_1

            find_solution = False

            if (z_1 >= 0 or (z_1 < 0 and direction_versor[1] > 0)):
                if (numpy.sign((k_1*x_1))==numpy.sign(direction_versor[1])):
                    x_sol = x_1 + x_0
                    y_sol = y_0 + k_1*x_1
                    z_sol = z_1

                    find_solution = True

            if not find_solution:
                z_2 = z_0 + k_2*x_2

                if (z_2 >= 0 or (z_1 < 0 and direction_versor[1] > 0)):
                    if (numpy.sign((k_1*x_2))==numpy.sign(direction_versor[1])):
                        x_sol = x_2 + x_0
                        y_sol = y_0 + k_1*x_2
                        z_sol = z_2

                        find_solution = True

            if find_solution:
                wavelength = (2*math.pi/k_mod)*1e+8 # in Angstrom

                exit_point = [x_sol, y_sol, z_sol]

                distance = min((ShadowMath.point_distance(entry_point, origin_point) + ShadowMath.point_distance(origin_point, exit_point))*10, capillary_radius*2*10) #in mm

                mass_attenuation_coefficient = self.getMassAttenuationCoefficient(distance*0.5, wavelength)
                absorption = math.exp(-2*mass_attenuation_coefficient)*self.normalization_factor
            else:
                absorption = 0 # kill the ray
                self.log_file.write("WARNING: ray gives no solutions for absorption - typing entry point and origin point\n")
                self.log_file.write(str(entry_point[0]) + " " + str(entry_point[1]) + " " + str(entry_point[2]) + "\n")
                self.log_file.write(str(x_0) + " " + str(y_0) + " " + str(z_0) + "\n")

        return absorption

    ############################################################

    def isCollectedRay(self, twotheta_angle,
                           x_0, 
                           y_0, 
                           z_0, 
                           v_x, 
                           v_y, 
                           v_z):
        is_collected_ray = False

        sin_twotheta = math.sin(twotheta_angle)
        cos_twotheta = math.cos(twotheta_angle)

        x_c_s1 = self.slit_1_horizontal_displacement_cm
        y_c_s1 = self.D_1*cos_twotheta - self.slit_1_vertical_displacement_cm*sin_twotheta
        z_c_s1 = self.D_1*sin_twotheta + self.slit_1_vertical_displacement_cm*cos_twotheta

        x_c_s2 = self.slit_2_horizontal_displacement_cm
        y_c_s2 = self.D_2*cos_twotheta - self.slit_2_vertical_displacement_cm*sin_twotheta
        z_c_s2 = self.D_2*sin_twotheta + self.slit_2_vertical_displacement_cm*cos_twotheta

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
                is_collected_ray= True

        return is_collected_ray

    ############################################################
        
    def calculateBackground(self, bar_value):

        percentage_fraction = 50/len(self.twotheta_angles)

        cursor = range(0, len(self.twotheta_angles))
        random_generator = random.Random()

        self.n_sigma = 0.5*(1 + self.n_sigma)

        for angle_index in cursor:
            
            background = 0
            if (self.add_chebyshev==1):
                coefficients = [self.cheb_coeff_0, self.cheb_coeff_1, self.cheb_coeff_2, self.cheb_coeff_3, self.cheb_coeff_4, self.cheb_coeff_5]
                
                background += ShadowPhysics.ChebyshevBackgroundNoised(coefficients=coefficients, 
                                                                      twotheta=self.twotheta_angles[angle_index],
                                                                      n_sigma=self.n_sigma,
                                                                      random_generator=random_generator)
                
            if (self.add_expdecay==1):
                coefficients = [self.expd_coeff_0, self.expd_coeff_1, self.expd_coeff_2, self.expd_coeff_3, self.expd_coeff_4, self.expd_coeff_5]
                decayparams = [self.expd_decayp_0, self.expd_decayp_1, self.expd_decayp_2, self.expd_decayp_3, self.expd_decayp_4, self.expd_decayp_5]
                
                background += ShadowPhysics.ExpDecayBackgroundNoised(coefficients=coefficients,
                                                                     decayparams=decayparams,
                                                                     twotheta=self.twotheta_angles[angle_index],
                                                                     n_sigma=self.n_sigma,
                                                                     random_generator=random_generator)
            self.counts[angle_index] += background

        bar_value += percentage_fraction
        self.progressBarSet(bar_value)


    ############################################################

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