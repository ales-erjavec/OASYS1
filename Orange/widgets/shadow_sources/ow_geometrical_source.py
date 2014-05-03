import os, sys
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication, qApp, QScrollArea

from Orange.widgets.shadow_gui import ow_generic_element
from Orange.shadow.shadow_objects import EmittingStream, TTYGrabber
from Orange.shadow.shadow_util import ShadowGui

class GeometricalSource(ow_generic_element.GenericElement):

    name = "Geometrical Source"
    description = "Shadow Source: Geometrical Source"
    icon = "icons/geometrical.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Sources"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"Beam",
                "type":Orange.shadow.ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"}]


    want_main_area=1

    # TODO ELEMENTO DA FARE COMPLETAMENTE
    # TODO INSERIRE LIVELLI DI ASTRAZIONE COME PER OE

    sampling = Setting(0)

    number_of_rays=Setting(5000)
    seed=Setting(6775431)

    grid_points_in_xfirst = Setting(1)
    grid_points_in_zfirst = Setting(1)
    grid_points_in_x = Setting(1)
    grid_points_in_y = Setting(1)
    grid_points_in_z = Setting(1)
    radial_grid_points = Setting(0)
    concentrical_grid_points = Setting(0)

    spatial_type = Setting(0)

    rect_width = Setting(0.1)
    rect_height = Setting(0.2)
    ell_semiaxis_x = Setting(0.1)
    ell_semiaxis_z = Setting(0.2)
    gauss_sigma_x = Setting(0.001)
    gauss_sigma_z = Setting(0.001)


    angular_distribution = Setting(0)

    horizontal_div_x_plus = Setting(5.0e-7)
    horizontal_div_x_minus = Setting(5.0e-7)
    vertical_div_z_plus = Setting(5.0e-6)
    vertical_div_z_minus = Setting(5.0e-6)

    horizontal_lim_x_plus = Setting(5.0e-7)
    horizontal_lim_x_minus = Setting(5.0e-7)
    vertical_lim_z_plus = Setting(5.0e-6)
    vertical_lim_z_minus = Setting(5.0e-6)
    horizontal_sigma_x = Setting(0.001)
    vertical_sigma_z = Setting(0.0001)

    cone_internal_half_aperture = Setting(0.0)
    cone_external_half_aperture = Setting(0.0)

    depth = Setting(0)

    source_depth_y = Setting(0.2)
    sigma_y = Setting(0.001)

    store_optical_paths=Setting(1) # REMOVED FROM GUI: 1 AS DEFAULT

    def __init__(self):
        super().__init__()

        tabs = ShadowGui.tabWidget(self.controlArea, height=705)

        tab_montecarlo = ShadowGui.createTabPage(tabs, "Monte Carlo and Sampling")
        tab_geometry = ShadowGui.createTabPage(tabs, "Geometry")
        tab_energy = ShadowGui.createTabPage(tabs, "Energy and Polarization")

        ##############################
        # MONTECARLO

        left_box_1 = ShadowGui.widgetBox(tab_montecarlo, "Options", addSpace=True, orientation="vertical", height=280)

        gui.separator(left_box_1)

        gui.comboBox(left_box_1, self, "sampling", label="Sampling (space/divergence)", labelWidth=300,
                     items=["Random/Random", "Grid/Grid", "Grid/Random", "Random/Grid"], orientation="horizontal", callback=self.set_Sampling)

        gui.separator(left_box_1)

        self.sample_box_1 = ShadowGui.widgetBox(left_box_1, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.sample_box_1, self, "number_of_rays", "Number of Random Rays", labelWidth=300, valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(self.sample_box_1, self, "seed", "Seed", labelWidth=300, valueType=int, orientation="horizontal")

        self.sample_box_2 = ShadowGui.widgetBox(left_box_1, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.sample_box_2, self, "grid_points_in_xfirst", "Grid Points in X'", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.sample_box_2, self, "grid_points_in_zfirst", "Grid Points in Z'",  labelWidth=300, valueType=float, orientation="horizontal")

        self.sample_box_3 = ShadowGui.widgetBox(left_box_1, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.sample_box_3, self, "grid_points_in_x", "Grid Points in X", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.sample_box_3, self, "grid_points_in_y", "Grid Points in Y", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.sample_box_3, self, "grid_points_in_z", "Grid Points in Z",  labelWidth=300, valueType=float, orientation="horizontal")

        self.sample_box_4 = ShadowGui.widgetBox(left_box_1, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.sample_box_4, self, "radial_grid_points", "Radial Grid Points", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.sample_box_4, self, "concentrical_grid_points", "Concentrical Grid Points",  labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Sampling()

        ##############################
        # GEOMETRY

        left_box_2 = ShadowGui.widgetBox(tab_geometry, "", addSpace=True, orientation="vertical", height=550)

        gui.separator(left_box_2)

        ######

        spatial_type_box = ShadowGui.widgetBox(left_box_2, "Spatial Type", addSpace=True, orientation="vertical", height=120)

        gui.comboBox(spatial_type_box, self, "spatial_type", label="Spatial Type", labelWidth=355,
                     items=["Point", "Rectangle", "Ellipse", "Gaussian"], orientation="horizontal", callback=self.set_SpatialType)

        gui.separator(spatial_type_box)

        self.spatial_type_box_1 = ShadowGui.widgetBox(spatial_type_box, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.spatial_type_box_1, self, "rect_width", "Width [cm]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.spatial_type_box_1, self, "rect_height", "Height [cm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.spatial_type_box_2 = ShadowGui.widgetBox(spatial_type_box, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.spatial_type_box_2, self, "ell_semiaxis_x", "Semi-Axis X [cm]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.spatial_type_box_2, self, "ell_semiaxis_z", "Semi-Axis Z [cm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.spatial_type_box_3 = ShadowGui.widgetBox(spatial_type_box, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.spatial_type_box_3, self, "gauss_sigma_x", "Sigma X [cm]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.spatial_type_box_3, self, "gauss_sigma_z", "Sigma Z [cm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.set_SpatialType()

        angular_distribution_box = ShadowGui.widgetBox(left_box_2, "Angular Distribution", addSpace=True, orientation="vertical", height=230)

        gui.comboBox(angular_distribution_box, self, "angular_distribution", label="Angular Distribution", labelWidth=355,
                     items=["Flat", "Uniform", "Gaussian", "Conical"], orientation="horizontal", callback=self.set_AngularDistribution)

        gui.separator(angular_distribution_box)

        self.angular_distribution_box_1 = ShadowGui.widgetBox(angular_distribution_box, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.angular_distribution_box_1, self, "horizontal_div_x_plus", "Horizontal Divergence X(+) [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_1, self, "horizontal_div_x_minus", "Horizontal Divergence X(-) [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_1, self, "vertical_div_z_plus", "Vertical Divergence Z(+) [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_1, self, "vertical_div_z_minus", "Vertical Divergence Z(+) [rad]", labelWidth=300, valueType=float, orientation="horizontal")

        self.angular_distribution_box_2 = ShadowGui.widgetBox(angular_distribution_box, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.angular_distribution_box_2, self, "horizontal_lim_x_plus", "Horizontal Limit X(+) [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_2, self, "horizontal_lim_x_minus", "Horizontal Limit X(-) [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_2, self, "vertical_lim_z_plus", "Vertical Limit Z(+) [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_2, self, "vertical_lim_z_minus", "Vertical Limit Z(+) [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_2, self, "horizontal_sigma_x", "Horizontal Sigma [X] [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_2, self, "vertical_sigma_z", "Vertical Sigma [Z] [rad]", labelWidth=300, valueType=float, orientation="horizontal")

        self.angular_distribution_box_3 = ShadowGui.widgetBox(angular_distribution_box, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.angular_distribution_box_3, self, "cone_internal_half_aperture", "Cone Internal Half-Aperture [rad]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.angular_distribution_box_3, self, "cone_external_half_aperture", "Cone External Half-Aperture [rad]", labelWidth=300, valueType=float, orientation="horizontal")

        self.set_AngularDistribution()

        depth_box = ShadowGui.widgetBox(left_box_2, "Depth", addSpace=True, orientation="vertical", height=100)

        gui.comboBox(depth_box, self, "depth", label="Depth", labelWidth=355,
                     items=["Off", "Uniform", "Gaussian"], orientation="horizontal", callback=self.set_Depth)

        gui.separator(depth_box)

        self.depth_box_1 = ShadowGui.widgetBox(depth_box, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.depth_box_1, self, "source_depth_y", "Source Depth [Y] [cm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.depth_box_2 = ShadowGui.widgetBox(depth_box, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.depth_box_2, self, "sigma_y", "Sigma Y [cm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Depth()

        ##############################
        # ENERGY


        button = gui.button(self.controlArea, self, "Run Shadow/source", callback=self.runShadowSource)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

        #if (self.is_automatic_run):
        #    self.runShadowSource()

    def set_Sampling(self):
        self.sample_box_1.setVisible(self.sampling == 0)
        self.sample_box_2.setVisible(self.sampling == 1 or self.sampling == 3)
        self.sample_box_3.setVisible(self.sampling == 1 or self.sampling == 2)
        self.sample_box_4.setVisible(self.sampling == 1 or self.sampling == 3)

    def set_SpatialType(self):
        self.spatial_type_box_1.setVisible(self.spatial_type == 1)
        self.spatial_type_box_2.setVisible(self.spatial_type == 2)
        self.spatial_type_box_3.setVisible(self.spatial_type == 3)

    def set_AngularDistribution(self):
        self.angular_distribution_box_1.setVisible(self.angular_distribution == 0 or self.angular_distribution == 1)
        self.angular_distribution_box_2.setVisible(self.angular_distribution == 2)
        self.angular_distribution_box_3.setVisible(self.angular_distribution == 3)

    def set_Depth(self):
        self.depth_box_1.setVisible(self.depth == 1)
        self.depth_box_2.setVisible(self.depth == 2)

    def runShadowSource(self):

        self.progressBarInit()

        shadow_src = Orange.shadow.ShadowSource.create_src()

#        shadow_src.src.NPOINT=self.number_of_rays
#        shadow_src.src.ISTAR1=self.seed
#        shadow_src.src.PH1=self.e_min
#        shadow_src.src.PH2=self.e_max
#        shadow_src.src.F_OPD=self.store_optical_paths
#        shadow_src.src.F_SR_TYPE=self.sample_distribution_combo
#        shadow_src.src.F_POL=1+self.generate_polarization_combo

#        shadow_src.src.SIGMAX=self.sigma_x
#        shadow_src.src.SIGMAZ=self.sigma_z
#        shadow_src.src.EPSI_X=self.emittance_x
#        shadow_src.src.EPSI_Z=self.emittance_z
#        shadow_src.src.BENER=self.energy
#        shadow_src.src.EPSI_DX=self.distance_from_waist_x
#        shadow_src.src.EPSI_DZ=self.distance_from_waist_z

#        shadow_src.src.R_MAGNET=self.magnetic_radius
#        shadow_src.src.R_ALADDIN=self.magnetic_radius*100
#        shadow_src.src.HDIV1=self.horizontal_half_divergence_from
#        shadow_src.src.HDIV2=self.horizontal_half_divergence_to
#        shadow_src.src.VDIV1=self.max_vertical_half_divergence_from
#        shadow_src.src.VDIV2=self.max_vertical_half_divergence_to

#        shadow_src.src.FDISTR=4+2*self.calculation_mode_combo

        self.progressBarSet(10)

        self.information(0, "Running SHADOW")
        qApp.processEvents()

        sys.stdout = EmittingStream(textWritten=self.writeStdOut)
        grabber = TTYGrabber()
        grabber.start()

        self.progressBarSet(50)

        beam_out = Orange.shadow.ShadowBeam.traceFromSource(shadow_src)

        grabber.stop()

        for row in grabber.ttyData:
           self.writeStdOut(row)

        self.information(0, "Plotting Results")
        qApp.processEvents()

        self.progressBarSet(80)
        self.plot_results(beam_out)

        self.information()
        qApp.processEvents()

        self.send("Beam", beam_out)

        self.progressBarFinished()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = GeometricalSource()
    ow.show()
    a.exec_()
    ow.saveSettings()
