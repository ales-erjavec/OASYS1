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

    photon_energy_distribution = Setting(0)

    units=Setting(0)

    single_line_value = Setting(1000.0)
    number_of_lines = Setting(0)

    line_value_1 = Setting(1000.0)
    line_value_2 = Setting(1010.0)
    line_value_3 = Setting(0.0)
    line_value_4 = Setting(0.0)
    line_value_5 = Setting(0.0)
    line_value_6 = Setting(0.0)
    line_value_7 = Setting(0.0)
    line_value_8 = Setting(0.0)
    line_value_9 = Setting(0.0)
    line_value_10 = Setting(0.0)

    uniform_minimum = Setting(1000.0)
    uniform_maximum = Setting(1010.0)

    line_int_1 = Setting(0.0)
    line_int_2 = Setting(0.0)
    line_int_3 = Setting(0.0)
    line_int_4 = Setting(0.0)
    line_int_5 = Setting(0.0)
    line_int_6 = Setting(0.0)
    line_int_7 = Setting(0.0)
    line_int_8 = Setting(0.0)
    line_int_9 = Setting(0.0)
    line_int_10 = Setting(0.0)

    polarization = Setting(0)
    coherent_beam = Setting(0)
    phase_diff = Setting(0.0)
    polarization_degree = Setting(1.0)

    store_optical_paths=Setting(1) # REMOVED FROM GUI: 1 AS DEFAULT

    def __init__(self):
        super().__init__()

        tabs = ShadowGui.tabWidget(self.controlArea, height=650)

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

        left_box_3 = ShadowGui.widgetBox(tab_energy, "", addSpace=True, orientation="vertical", height=640)

        gui.separator(left_box_3)

        ######

        energy_wavelength_box = ShadowGui.widgetBox(left_box_3, "Energy/Wavelength", addSpace=True, orientation="vertical", height=430)

        gui.comboBox(energy_wavelength_box, self, "photon_energy_distribution", label="Photon Energy Distribution", labelWidth=300,
                     items=["Single Line", "Several Lines", "Uniform", "Relative Intensities"], orientation="horizontal", callback=self.set_PhotonEnergyDistribution)

        gui.separator(energy_wavelength_box)

        gui.comboBox(energy_wavelength_box, self, "units", label="Units", labelWidth=300,
                     items=["Energy/eV", "Wavelength/Å"], orientation="horizontal", callback=self.set_PhotonEnergyDistribution)

        gui.separator(energy_wavelength_box)

        self.ewp_box_5 = ShadowGui.widgetBox(energy_wavelength_box, "", addSpace=False, orientation="vertical")

        gui.comboBox(self.ewp_box_5, self, "number_of_lines", label="Number of Lines", labelWidth=350,
                     items=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], orientation="horizontal", callback=self.set_NumberOfLines)

        container =  ShadowGui.widgetBox(energy_wavelength_box, "", addSpace=False, orientation="horizontal")
        self.container_left =  ShadowGui.widgetBox(container, "", addSpace=False, orientation="vertical")
        self.container_right =  ShadowGui.widgetBox(container, "", addSpace=False, orientation="vertical")

        self.ewp_box_1 = ShadowGui.widgetBox(self.container_left, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.ewp_box_1, self, "single_line_value", "Value", labelWidth=300, valueType=float, orientation="horizontal")

        self.ewp_box_2 = ShadowGui.widgetBox(self.container_left, "Values", addSpace=True, orientation="vertical")

        self.le_line_value_1 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_1", "Line 1", valueType=float, orientation="horizontal")
        self.le_line_value_2 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_2", "Line 2", valueType=float, orientation="horizontal")
        self.le_line_value_3 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_3", "Line 3", valueType=float, orientation="horizontal")
        self.le_line_value_4 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_4", "Line 4", valueType=float, orientation="horizontal")
        self.le_line_value_5 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_5", "Line 5", valueType=float, orientation="horizontal")
        self.le_line_value_6 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_6", "Line 6", valueType=float, orientation="horizontal")
        self.le_line_value_7 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_7", "Line 7", valueType=float, orientation="horizontal")
        self.le_line_value_8 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_8", "Line 8", valueType=float, orientation="horizontal")
        self.le_line_value_9 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_9", "Line 9", valueType=float, orientation="horizontal")
        self.le_line_value_10 = ShadowGui.lineEdit(self.ewp_box_2, self, "line_value_10", "Line 10", valueType=float, orientation="horizontal")

        self.ewp_box_3 = ShadowGui.widgetBox(self.container_left, "", addSpace=False, orientation="vertical")

        ShadowGui.lineEdit(self.ewp_box_3, self, "uniform_minimum", "Minimum Energy/Wavelength", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.ewp_box_3, self, "uniform_maximum", "Maximum Energy/Wavelength", labelWidth=300, valueType=float, orientation="horizontal")

        self.ewp_box_4 = ShadowGui.widgetBox(self.container_right, "Relative Intensities", addSpace=True, orientation="vertical")
        
        self.le_line_int_1 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_1", "Int 1", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_2 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_2", "Int 2", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_3 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_3", "Int 3", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_4 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_4", "Int 4", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_5 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_5", "Int 5", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_6 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_6", "Int 6", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_7 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_7", "Int 7", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_8 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_8", "Int 8", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_9 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_9", "Int 9", labelWidth=100, valueType=float, orientation="horizontal")
        self.le_line_int_10 = ShadowGui.lineEdit(self.ewp_box_4, self, "line_int_10", "Int 10", labelWidth=100, valueType=float, orientation="horizontal")

        self.set_PhotonEnergyDistribution()

        polarization_box = ShadowGui.widgetBox(left_box_3, "Polarization", addSpace=True, orientation="vertical", height=150)

        gui.comboBox(polarization_box, self, "polarization", label="Polarization", labelWidth=355,
                     items=["No", "Yes"], orientation="horizontal", callback=self.set_Polarization)

        gui.separator(polarization_box)

        self.ewp_box_6 = ShadowGui.widgetBox(polarization_box, "", addSpace=True, orientation="vertical")

        gui.comboBox(self.ewp_box_6, self, "coherent_beam", label="Coherent Beam", labelWidth=355,
                     items=["No", "Yes"], orientation="horizontal")

        ShadowGui.lineEdit(self.ewp_box_6, self, "phase_diff", "Phase Difference [deg,0=linear,+90=ell/right]", labelWidth=330, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.ewp_box_6, self, "polarization_degree", "Polarization Degree [cos_s/(cos_s+sin_s)]", labelWidth=330, valueType=float, orientation="horizontal")

        self.set_Polarization()

        ##############################

        gui.separator(self.controlArea, height=50)

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

    def set_PhotonEnergyDistribution(self):
        self.ewp_box_1.setVisible(self.photon_energy_distribution == 0)
        self.ewp_box_2.setVisible(self.photon_energy_distribution == 1 or self.photon_energy_distribution == 3)
        self.ewp_box_3.setVisible(self.photon_energy_distribution == 2)
        self.ewp_box_4.setVisible(self.photon_energy_distribution == 3)
        self.ewp_box_5.setVisible(self.photon_energy_distribution == 1 or self.photon_energy_distribution == 3)

        if self.photon_energy_distribution == 3:
            self.le_line_value_1.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_2.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_3.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_4.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_5.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_6.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_7.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_8.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_9.parentWidget().children()[1].setFixedWidth(100)
            self.le_line_value_10.parentWidget().children()[1].setFixedWidth(100)
        else:
            self.le_line_value_1.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_2.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_3.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_4.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_5.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_6.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_7.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_8.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_9.parentWidget().children()[1].setFixedWidth(300)
            self.le_line_value_10.parentWidget().children()[1].setFixedWidth(300)

        self.container_right.setVisible(self.photon_energy_distribution == 3)

        self.set_NumberOfLines()

    def set_NumberOfLines(self):
        self.le_line_value_2.parentWidget().setVisible(self.number_of_lines >= 1)
        self.le_line_int_2.parentWidget().setVisible(self.number_of_lines >= 1)
        self.le_line_value_3.parentWidget().setVisible(self.number_of_lines >= 2)
        self.le_line_int_3.parentWidget().setVisible(self.number_of_lines >= 2)
        self.le_line_value_4.parentWidget().setVisible(self.number_of_lines >= 3)
        self.le_line_int_4.parentWidget().setVisible(self.number_of_lines >= 3)
        self.le_line_value_5.parentWidget().setVisible(self.number_of_lines >= 4)
        self.le_line_int_5.parentWidget().setVisible(self.number_of_lines >= 4)
        self.le_line_value_6.parentWidget().setVisible(self.number_of_lines >= 5)
        self.le_line_int_6.parentWidget().setVisible(self.number_of_lines >= 5)
        self.le_line_value_7.parentWidget().setVisible(self.number_of_lines >= 6)
        self.le_line_int_7.parentWidget().setVisible(self.number_of_lines >= 6)
        self.le_line_value_8.parentWidget().setVisible(self.number_of_lines >= 7)
        self.le_line_int_8.parentWidget().setVisible(self.number_of_lines >= 7)
        self.le_line_value_9.parentWidget().setVisible(self.number_of_lines >= 8)
        self.le_line_int_9.parentWidget().setVisible(self.number_of_lines >= 8)
        self.le_line_value_10.parentWidget().setVisible(self.number_of_lines == 9)
        self.le_line_int_10.parentWidget().setVisible(self.number_of_lines == 9)

    def set_Polarization(self):
        self.ewp_box_6.setVisible(self.polarization==1)

    def runShadowSource(self):

        self.progressBarInit()

        shadow_src = Orange.shadow.ShadowSource.create_src()

        shadow_src.src.NPOINT=self.number_of_rays
        shadow_src.src.ISTAR1=self.seed

        shadow_src.src.FGRID=self.sampling

        if self.sampling>0:
            shadow_src.src.IDO_VX = self.grid_points_in_xfirst
            shadow_src.src.IDO_VZ = self.grid_points_in_zfirst
            shadow_src.src.IDO_X_S = self.grid_points_in_x
            shadow_src.src.IDO_Y_S = self.grid_points_in_y
            shadow_src.src.IDO_Z_S = self.grid_points_in_z
            shadow_src.src.N_CIRCLE = self.radial_grid_points
            shadow_src.src.N_CONE = self.concentrical_grid_points

        shadow_src.src.FSOUR = self.spatial_type

        if self.spatial_type == 1:
            shadow_src.src.WXSOU = self.rect_width
            shadow_src.src.WZSOU = self.rect_height
        elif self.spatial_type == 2:
            shadow_src.src.WXSOU = self.ell_semiaxis_x
            shadow_src.src.WZSOU = self.ell_semiaxis_z
        elif self.spatial_type == 2:
            shadow_src.src.SIGMAX = self.gauss_sigma_x
            shadow_src.src.SIGMAZ = self.gauss_sigma_z

        if self.angular_distribution == 0 or \
           self.angular_distribution == 1:
            shadow_src.src.FDISTR = self.angular_distribution + 1
            shadow_src.src.HDIV1 = self.horizontal_div_x_plus
            shadow_src.src.HDIV2 = self.horizontal_div_x_minus
            shadow_src.src.VDIV1 = self.vertical_div_z_plus
            shadow_src.src.VDIV2 = self.vertical_div_z_minus
        elif self.angular_distribution == 2:
            shadow_src.src.FDISTR = 3
            shadow_src.src.HDIV1 = self.horizontal_lim_x_plus
            shadow_src.src.HDIV2 = self.horizontal_lim_x_minus
            shadow_src.src.VDIV1 = self.vertical_lim_z_plus
            shadow_src.src.VDIV2 = self.vertical_lim_z_minus
            shadow_src.src.SIGDIX = self.horizontal_sigma_x
            shadow_src.src.SIGDIZ = self.vertical_sigma_z
        elif self.angular_distribution == 3:
            shadow_src.src.FDISTR = 5
            shadow_src.src.CONE_MIN = self.cone_internal_half_aperture
            shadow_src.src.CONE_MAX = self.cone_external_half_aperture

        shadow_src.src.FSOURCE_DEPTH = self.depth

        if self.depth == 1:
            shadow_src.src.WYSOU = self.source_depth_y
        elif self.depth == 2:
            shadow_src.src.SIGMAY = self.sigma_y

        shadow_src.src.F_COLOR = self.photon_energy_distribution + 1
        shadow_src.src.F_PHOT = self.units

        if self.photon_energy_distribution == 0:
            shadow_src.src.PH1 = self.single_line_value
        elif self.photon_energy_distribution == 1:
            shadow_src.src.N_COLOR=self.number_of_lines
            shadow_src.src.PH1 = self.line_value_1
            shadow_src.src.PH2 = self.line_value_2
            shadow_src.src.PH3 = self.line_value_3
            shadow_src.src.PH4 = self.line_value_4
            shadow_src.src.PH5 = self.line_value_5
            shadow_src.src.PH6 = self.line_value_6
            shadow_src.src.PH7 = self.line_value_7
            shadow_src.src.PH8 = self.line_value_8
            shadow_src.src.PH9 = self.line_value_9
            shadow_src.src.PH10 = self.line_value_10
        elif self.photon_energy_distribution == 2:
            shadow_src.src.PH1 = self.uniform_minimum
            shadow_src.src.PH2 = self.uniform_maximum
        elif self.photon_energy_distribution == 3:
            shadow_src.src.N_COLOR=self.number_of_lines
            shadow_src.src.PH1 = self.line_value_1
            shadow_src.src.PH2 = self.line_value_2
            shadow_src.src.PH3 = self.line_value_3
            shadow_src.src.PH4 = self.line_value_4
            shadow_src.src.PH5 = self.line_value_5
            shadow_src.src.PH6 = self.line_value_6
            shadow_src.src.PH7 = self.line_value_7
            shadow_src.src.PH8 = self.line_value_8
            shadow_src.src.PH9 = self.line_value_9
            shadow_src.src.PH10 = self.line_value_10
            shadow_src.src.RL1 = self.line_int_1
            shadow_src.src.RL2 = self.line_int_2
            shadow_src.src.RL3 = self.line_int_3
            shadow_src.src.RL4 = self.line_int_4
            shadow_src.src.RL5 = self.line_int_5
            shadow_src.src.RL6 = self.line_int_6
            shadow_src.src.RL7 = self.line_int_7
            shadow_src.src.RL8 = self.line_int_8
            shadow_src.src.RL9 = self.line_int_9
            shadow_src.src.RL10 = self.line_int_10

        shadow_src.src.F_POLAR = self.polarization

        if self.polarization == 1:
            shadow_src.src.F_COHER = self.coherent_beam
            shadow_src.src.POL_ANGLE = self.phase_diff
            shadow_src.src.POL_DEG = self.polarization_degree

        shadow_src.src.F_OPD=self.store_optical_paths

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
