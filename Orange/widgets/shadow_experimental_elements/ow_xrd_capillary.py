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

from PyMca.widgets.PlotWindow import PlotWindow

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

    start_angle = Setting(10)
    stop_angle = Setting(120)
    step = Setting(0.002)

    IMAGE_WIDTH = 920
    IMAGE_HEIGHT = 750

    want_main_area=1
    plot_canvas=None

    def __init__(self):
        super().__init__()

        upper_box = ShadowGui.widgetBox(self.controlArea, "Sample Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "capillary_diameter", "Capillary Diameter [mm]", valueType=float, orientation="horizontal")
        gui.comboBox(upper_box, self, "capillary_material", label="Capillary Material", items=["Glass", "Kapton"], sendSelectedValue=False, orientation="horizontal")
        gui.comboBox(upper_box, self, "sample_material", label="Material", items=["LaB6", "Si", "ZnO"], sendSelectedValue=False, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "packing_factor", "Packing Factor (0.0...1.0)", valueType=float, orientation="horizontal")

        upper_box = ShadowGui.widgetBox(self.controlArea, "Detector Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "detector_distance", "Detector Distance (cm)",  tooltip="Detector Distance (cm)", valueType=float, orientation="horizontal")

        gui.separator(upper_box)

        ShadowGui.lineEdit(upper_box, self, "slit_1_distance", "Slit 1 Distance from Detector (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "slit_1_vertical_aperture", "Slit 1 Vertical Aperture (um)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "slit_1_horizontal_aperture", "Slit 1 Horizontal Aperture (um)",  valueType=float, orientation="horizontal")

        gui.separator(upper_box)

        ShadowGui.lineEdit(upper_box, self, "slit_2_distance", "Slit 2 Distance from Detector (cm)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "slit_2_vertical_aperture", "Slit 2 Vertical Aperture (um)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "slit_2_horizontal_aperture", "Slit 2 Horizontal Aperture (um)",  valueType=float, orientation="horizontal")

        upper_box = ShadowGui.widgetBox(self.controlArea, "Scan Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "start_angle", "Start Angle (deg)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "stop_angle", "Stop Angle (deg)",  valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "step", "Step (deg)",  valueType=float, orientation="horizontal")

        upper_box = ShadowGui.widgetBox(self.controlArea, "Aberrations Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "horizontal_displacement", "Capillary H Displacement (um)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "vertical_displacement", "Capillary V Displacement (um)", valueType=float, orientation="horizontal")


        ShadowGui.widgetBox(self.controlArea, "", addSpace=True, orientation="vertical", height=100)

        button = gui.button(self.controlArea, self, "Simulate", callback=self.simulate)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

        self.image_box = gui.widgetBox(self.mainArea, "Plot Result", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH)

        gui.rubber(self.mainArea)


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

        self.information(0, "Running XRD Capillary Simulation")
        qApp.processEvents()

        self.progressBarSet(0)

        random_generator = random.Random()

        lattice_parameter = self.getLatticeParameter(self.sample_material)
        reflections = self.getReflections(self.sample_material)

        good_only = ST.getshcol(self.input_beam.beam, 10)

        rays = range(0, len(good_only))

        beam_intersection = Orange.shadow.ShadowBeam()
        beam_intersection.beam.rays  = copy.deepcopy(self.input_beam.beam.rays)

        rejected = 0

        R_c = self.capillary_diameter*0.5
        distance = self.detector_distance
        displacement_h = self.horizontal_displacement*0.0001
        displacement_v = self.vertical_displacement*0.0001

        in_out_coordinates_list = []

        self.information(0, "Calculating intersections with capillary")
        qApp.processEvents()

        self.progressBarSet(10)

        out_file_1 = open("intersection.dat","w")
        out_file_2 = open("origins.dat","w")

        for rayIndex in rays:
            if beam_intersection.beam.rays[rayIndex,9] == 0:
                rejected = rejected+1
            else:
                # costruzione intersezione con capillare + displacement del capillare
                alfa = self.input_beam.beam.rays[rayIndex,3]/self.input_beam.beam.rays[rayIndex,4]
                gamma = self.input_beam.beam.rays[rayIndex,5]/self.input_beam.beam.rays[rayIndex,4]
                X_pr = self.input_beam.beam.rays[rayIndex,0] + (distance/self.input_beam.beam.rays[rayIndex,4])*self.input_beam.beam.rays[rayIndex,3]
                Z_pr = self.input_beam.beam.rays[rayIndex,2] + (distance/self.input_beam.beam.rays[rayIndex,4])*self.input_beam.beam.rays[rayIndex,5]

                a = 1+gamma**2
                b = 2*displacement_h+2*gamma*Z_pr+2*displacement_v*gamma
                c = Z_pr**2 + displacement_h**2 + displacement_v**2 - R_c**2 + 2*displacement_v*Z_pr

                Discriminant = b**2 - 4*a*c

                if Discriminant <= 0.0:
                    rejected = rejected+1
                    beam_intersection.beam.rays[rayIndex,9] = 0
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

                    out_file_1.write(str(x1) + " " + str(y1) + " " + str(z1) + "\n")
                    out_file_1.write(str(x2) + " " + str(y2) + " " + str(z2) + "\n")
                    out_file_1.flush()

                    out_file_2.write(str(x_point) + " " + str(y_point) + " " + str(z_point) + "\n")
                    out_file_2.flush()

                    in_out_coordinates_list.append(InOutCoordinates(x1, y1, z1, x2, y2, z2))

                    beam_intersection.beam.rays[rayIndex,0] = x_point
                    beam_intersection.beam.rays[rayIndex,1] = y_point
                    beam_intersection.beam.rays[rayIndex,2] = z_point

        out_file_1.close()
        out_file_2.close()

        self.progressBarSet(40)

        self.information(0, "Calculating diffracted beam")
        qApp.processEvents()

        number_of_rays=((len(rays)-rejected) * len(reflections))

        beam_diffracted = Orange.shadow.ShadowBeam(number_of_rays=number_of_rays)

        out_file_4 = open("diffracted_points.dat", "w")

        for rayIndex in rays:
            if beam_intersection.beam.rays[rayIndex,9] == 1:
                reflection_index=-1

                for reflection in reflections:
                    reflection_index = reflection_index +1

                    new_ray_index = rayIndex + reflection_index

                    # calcolo rotazione del vettore d'onda pari all'angolo di bragg

                    k_mod = beam_intersection.beam.rays[rayIndex,10]

                    v_in = [beam_intersection.beam.rays[rayIndex,3],
                            beam_intersection.beam.rays[rayIndex,4],
                            beam_intersection.beam.rays[rayIndex,5]]

                    #
                    # calcolo dell'asse di rotazione: k x z/|k x z|
                    #

                    z_axis = [0, 0, 1]
                    asse_rot = ShadowMath.vector_normalize(ShadowMath.vectorial_product(v_in, z_axis))

                    twotheta_reflection = 2*self.calculateBraggAngle(k_mod, reflection.h, reflection.k, reflection.l, lattice_parameter)

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
                    Q_ro = [beam_intersection.beam.rays[rayIndex,0],
                            beam_intersection.beam.rays[rayIndex,1],
                            beam_intersection.beam.rays[rayIndex,2]]
                    #
                    # retta P = Q_ro + v t
                    #
                    # punto P0 minima distanza con il centro della sfera in 0,0,0
                    #
                    # (P0 - O) * v = 0 => P0 * v = 0 => (Q_ro + v t0) * v = 0
                    #
                    # => t0 = - Q_ro * v

                    t_0 = -1*ShadowMath.scalar_product(Q_ro, v_out)
                    P_0 = ShadowMath.vector_sum(Q_ro, ShadowMath.vector_multiply(v_out, t_0))

                    b = ShadowMath.vector_modulus(P_0)
                    a = math.sqrt(R_sp*R_sp - b*b)

                    P_1 = ShadowMath.vector_sum(Q_ro, ShadowMath.vector_multiply(v_out, t_0-a))
                    P_2 = ShadowMath.vector_sum(Q_ro, ShadowMath.vector_multiply(v_out, t_0+a))

                    # ok se P2 con z > 0

                    good_only = 0
                    if (P_2[2] >= 0): good_only = 1

                    #
                    # genesi del nuovo raggio diffratto attenuato dell'intensità relativa e dell'assorbimento
                    #

                    beam_diffracted.beam.rays[new_ray_index, 0]  = Q_ro[0]                                                                # X
                    beam_diffracted.beam.rays[new_ray_index, 1]  = Q_ro[1]                                                                # Y
                    beam_diffracted.beam.rays[new_ray_index, 2]  = Q_ro[2]                                                                # Z
                    beam_diffracted.beam.rays[new_ray_index, 3]  = v_out[0]                                                               # director cos x
                    beam_diffracted.beam.rays[new_ray_index, 4]  = v_out[1]                                                               # director cos y
                    beam_diffracted.beam.rays[new_ray_index, 5]  = v_out[2]                                                               # director cos z
                    beam_diffracted.beam.rays[new_ray_index, 6]  = beam_intersection.beam.rays[rayIndex,6]*reflection.relative_intensity  # Es_x
                    beam_diffracted.beam.rays[new_ray_index, 7]  = beam_intersection.beam.rays[rayIndex,7]*reflection.relative_intensity  # Es_y
                    beam_diffracted.beam.rays[new_ray_index, 8]  = beam_intersection.beam.rays[rayIndex,8]*reflection.relative_intensity  # Es_z
                    beam_diffracted.beam.rays[new_ray_index, 9]  = beam_intersection.beam.rays[rayIndex,9]                                # good/lost
                    beam_diffracted.beam.rays[new_ray_index, 10] = beam_intersection.beam.rays[rayIndex,10]                               # |k|
                    beam_diffracted.beam.rays[new_ray_index, 11] = beam_intersection.beam.rays[rayIndex,11]                               # ray index
                    beam_diffracted.beam.rays[new_ray_index, 12] = good_only                                                              # N.A.
                    beam_diffracted.beam.rays[new_ray_index, 13] = beam_intersection.beam.rays[rayIndex,12]                               # Es_phi
                    beam_diffracted.beam.rays[new_ray_index, 14] = beam_intersection.beam.rays[rayIndex,13]                               # Ep_phi
                    beam_diffracted.beam.rays[new_ray_index, 15] = beam_intersection.beam.rays[rayIndex,14]*reflection.relative_intensity # Ep_x
                    beam_diffracted.beam.rays[new_ray_index, 16] = beam_intersection.beam.rays[rayIndex,15]*reflection.relative_intensity # Ep_y
                    beam_diffracted.beam.rays[new_ray_index, 17] = beam_intersection.beam.rays[rayIndex,16]*reflection.relative_intensity # Ep_z

                    out_file_4.write(str(P_2[0]) + " " + str(P_2[1]) + " " + str(P_2[2]) + "\n")
                    out_file_4.flush()

        out_file_4.write(str(0) + " " + str(0) + " " + str(self.detector_distance) + "\n")
        out_file_4.write(str(0) + " " + str(0) + " " + str(-self.detector_distance) + "\n")
        out_file_4.write(str(0) + " " + str(self.detector_distance) + " " + str(0) + "\n")
        out_file_4.write(str(0) + " " + str(-self.detector_distance) + " " + str(0)+ "\n")
        out_file_4.write(str(self.detector_distance) + " " + str(0) + " " + str(0) + "\n")
        out_file_4.write(str(-self.detector_distance) + " " + str(0) + " " + str(0) + "\n")
        out_file_4.flush()

        out_file_4.close()

        self.progressBarSet(80)

        self.information(0, "Computing diffraction profile (2th vs Intensity)")
        qApp.processEvents()

        steps = range(0, math.floor((self.stop_angle-self.start_angle)/self.step))
        twotheta_angles = []
        counts = []

        for step_index in steps:
            twotheta_angles.append(math.radians(self.start_angle + step_index*self.step))
            counts.append(0)

        twotheta_angles = numpy.array(twotheta_angles)
        counts = numpy.array(counts)

        go = numpy.where(beam_diffracted.beam.rays[:,9] == 1)
        good_only = len(go[0])

        self.D_1 = self.slit_1_distance
        self.D_2 = self.slit_2_distance

        self.horizontal_acceptance_1 = self.slit_1_horizontal_aperture*1e-4*0.5
        self.vertical_acceptance_1 = self.slit_1_vertical_aperture*1e-4*0.5

        self.horizontal_acceptance_2 = self.slit_2_horizontal_aperture*1e-4*0.5
        self.vertical_acceptance_2 = self.slit_2_vertical_aperture*1e-4*0.5

        theta_slit = math.atan(self.vertical_acceptance_1/self.D_1)

        x_0 = beam_diffracted.beam.rays[go,0]
        y_0 = beam_diffracted.beam.rays[go,1]
        z_0 = beam_diffracted.beam.rays[go,2]

        v_x = beam_diffracted.beam.rays[go,3]
        v_y = beam_diffracted.beam.rays[go,4]
        v_z = beam_diffracted.beam.rays[go,5]

        Es_x = beam_diffracted.beam.rays[go,6]
        Es_y = beam_diffracted.beam.rays[go,7]
        Es_z = beam_diffracted.beam.rays[go,8]

        Ep_x = beam_diffracted.beam.rays[go,15]
        Ep_y = beam_diffracted.beam.rays[go,16]
        Ep_z = beam_diffracted.beam.rays[go,17]


        percentage_fraction = 20/good_only

        out_file_7 = open("slit_centers.dat", "w")
        out_file_8 = open("slit.dat","w")

        go_indexes = range(0, good_only)

        for go_index in go_indexes:

            x_0_i = x_0.item(go_index)
            y_0_i = y_0.item(go_index)
            z_0_i = z_0.item(go_index)

            v_x_i = v_x.item(go_index)
            v_y_i = v_y.item(go_index)
            v_z_i = v_z.item(go_index)

            Es_x_i = Es_x.item(go_index)
            Es_y_i = Es_y.item(go_index)
            Es_z_i = Es_z.item(go_index)
                       
            Ep_x_i = Ep_x.item(go_index)
            Ep_y_i = Ep_y.item(go_index)
            Ep_z_i = Ep_z.item(go_index)


            # calcolo dell'angolo di intercettato dal vettore con il piano xy
            #
            #

            theta_ray = math.atan(v_z_i/math.sqrt(v_x_i*v_x_i + v_y_i*v_y_i))

            theta_lim_inf = theta_ray-5*theta_slit
            theta_lim_sup = theta_ray+5*theta_slit

            # il ciclo sugli step del detector dovrebbe essere attorno a quest'angolo +- un fattore sufficiente di volte
            # l'angolo intercettato dalla prima slit


            twotheta_angles_effective = numpy.where(numpy.logical_and(twotheta_angles > theta_lim_inf, twotheta_angles < theta_lim_sup))

            angle_indexes = range(0, len(twotheta_angles_effective[0]))

            for angle_index in angle_indexes:
                twotheta_angle = twotheta_angles[twotheta_angles_effective].item(angle_index)

                intensity = self.calculateIntensity(twotheta_angle,
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
                                                    Ep_z_i,
                                                    out_file_8, out_file_7)

                position = numpy.where(twotheta_angles==twotheta_angle)

                counts[position[0]]=counts[position[0]]+intensity

            self.progressBarAdvance(percentage_fraction)

        out_file = open("XRD_Profile.xy","w")

        cursor = range(0, len(twotheta_angles))

        twotheta_angles_deg = []
        for angleIndex in cursor:
            twotheta_angle_deg = math.degrees(twotheta_angles[angleIndex])

            twotheta_angles_deg.append(twotheta_angle_deg)
            out_file.write(str(twotheta_angle_deg) + " " + str(counts[angleIndex]) + "\n")
            out_file.flush()

        self.plotResult(twotheta_angles_deg, counts)

        self.progressBarSet(100)

        out_file_7.close()
        out_file_8.close()
        out_file.close()

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

    def calculateAbsorption(self, distance ):
        return 1

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
                           Ep_z,
                           out_file_8, out_file_7):
        intensity = 0

        sin_twotheta = math.sin(twotheta_angle)
        cos_twotheta = math.cos(twotheta_angle)

        x_c_s1 = 0
        y_c_s1 = self.D_1*cos_twotheta
        z_c_s1 = self.D_1*sin_twotheta

        x_c_s2 = 0
        y_c_s2 = self.D_2*cos_twotheta
        z_c_s2 = self.D_2*sin_twotheta


        out_file_7.write(str(x_c_s1) + " " + str(y_c_s1) + " " + str(z_c_s1) + "\n")
        out_file_7.write(str(x_c_s2) + " " + str(y_c_s2) + " " + str(z_c_s2) + "\n")
        out_file_7.flush()

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

            out_file_8.write(str(x_1_int) + " " + str(y_1_int) + " " + str(z_1_int) + "\n")
            out_file_8.flush()

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