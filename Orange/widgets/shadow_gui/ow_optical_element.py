import sys, math
from numpy import array
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication, qApp
from Orange.widgets.shadow_gui import ow_generic_element
from Orange.shadow.shadow_objects import EmittingStream, TTYGrabber
from Orange.shadow.shadow_util import ShadowGui

class GraphicalOptions:
    is_curved = False
    is_mirror=False
    is_screen_slit=False

    is_spheric= False
    is_ellipsoidal=False
    is_toroidal=False
    is_paraboloid=False
    is_hyperboloid=False
    is_cone=False
    is_codling_slit=False
    is_polynomial=False
    is_conic_coefficients=False

    def __init__(self, \
                 is_curved=False, \
                 is_mirror=False, \
                 is_screen_slit=False, \
                 is_spheric=False, \
                 is_ellipsoidal=False, \
                 is_toroidal=False, \
                 is_paraboloid=False, \
                 is_hyperboloid=False,\
                 is_cone=False, \
                 is_codling_slit=False, \
                 is_polynomial=False, \
                 is_conic_coefficients=False):
        self.is_curved = is_curved
        self.is_mirror=is_mirror
        self.is_screen_slit=is_screen_slit
        self.is_spheric=is_spheric
        self.is_ellipsoidal=is_ellipsoidal
        self.is_toroidal=is_toroidal
        self.is_paraboloid=is_paraboloid
        self.is_hyperboloid=is_hyperboloid
        self.is_cone=is_cone
        self.is_codling_slit=is_codling_slit
        self.is_polynomial=is_polynomial
        self.is_conic_coefficients=is_conic_coefficients


class OpticalElement(ow_generic_element.GenericElement):
    input_beam = None

    NONE_SPECIFIED = "NONE SPECIFIED"

    ONE_ROW_HEIGHT = 65
    TWO_ROW_HEIGHT = 110
    THREE_ROW_HEIGHT = 170

    TABS_AREA_HEIGHT = 480
    CONTROL_AREA_HEIGHT = 450
    CONTROL_AREA_WIDTH = 460
    INNER_BOX_WIDTH_L3=387
    INNER_BOX_WIDTH_L2=400
    INNER_BOX_WIDTH_L1=418
    INNER_BOX_WIDTH_L0=442

    graphical_options=None

    source_plane_distance = Setting(10.0)
    image_plane_distance = Setting(20.0)
    incidence_angle_deg = Setting(88.0)
    incidence_angle_mrad = Setting(0.0)
    reflection_angle_deg = Setting(88.0)
    reflection_angle_mrad = Setting(0.0)
    mirror_orientation_angle = Setting(0.0)

    ##########################################
    # BASIC SETTING
    ##########################################

    surface_shape_parameters = Setting(0)
    spherical_radius = Setting(0.0)

    torus_major_radius = Setting(0.0)
    torus_minor_radius = Setting(0.0)
    toroidal_mirror_pole_location=Setting(0.0)

    ellipse_hyperbola_semi_major_axis=Setting(0.0)
    ellipse_hyperbola_semi_minor_axis=Setting(0.0)
    angle_of_majax_and_pole=Setting(0.0)

    paraboloid_parameter=Setting(0.0)
    focus_location=Setting(0.0)

    focii_and_continuation_plane = Setting(0)

    object_side_focal_distance = Setting(0.0)
    image_side_focal_distance = Setting(0.0)
    incidence_angle_respect_to_normal = Setting(0.0)

    surface_curvature = Setting(0)
    is_cylinder = Setting(1)
    cylinder_orientation = Setting(0.0)
    reflectivity_type = Setting(0)
    source_of_reflectivity = Setting(0)
    file_prerefl = Setting("reflec.dat")
    alpha = Setting(0.0)
    gamma = Setting(0.0)
    file_prerefl_m = Setting("reflec.dat")
    m_layer_tickness = Setting(0.0)

    is_infinite = Setting(0)
    mirror_shape = Setting(0)
    dim_x_plus = Setting(0.0)
    dim_x_minus = Setting(0.0)
    dim_y_plus = Setting(0.0)
    dim_y_minus = Setting(0.0)

    file_crystal_parameters = Setting("reflec.dat")
    crystal_auto_setting = Setting(0)
    units_in_use = Setting(0)
    photon_energy = Setting(5.0)
    photon_wavelength = Setting(5000.0)

    mosaic_crystal = Setting(0)
    angle_spread_FWHM = Setting(0.0)
    thickness = Setting(0.0)
    seed_for_mosaic = Setting(1626261131)

    johansson_geometry = Setting(0)
    johansson_radius = Setting(0.0)

    asymmetric_cut = Setting(0)
    planes_angle = Setting(0.0)
    below_onto_bragg_planes = Setting(-1)

    ##########################################
    # ADVANCED SETTING
    ##########################################

    modified_surface = Setting(0)

    # surface error
    ms_type_of_defect = Setting(0)
    ms_defect_file_name = Setting(NONE_SPECIFIED)
    ms_ripple_wavel_x = Setting(0.0)
    ms_ripple_wavel_y = Setting(0.0)
    ms_ripple_ampli_x = Setting(0.0)
    ms_ripple_ampli_y = Setting(0.0)
    ms_ripple_phase_x = Setting(0.0)
    ms_ripple_phase_y = Setting(0.0)

    # faceted surface
    ms_file_facet_descr = Setting(NONE_SPECIFIED)
    ms_lattice_type = Setting(0)
    ms_orientation = Setting(0)
    ms_intercept_to_use = Setting(0)
    ms_facet_width_x = Setting(10.0)
    ms_facet_phase_x = Setting(0.0)
    ms_dead_width_x_minus = Setting(0.0)
    ms_dead_width_x_plus = Setting(0.0)
    ms_facet_width_y = Setting(10.0)
    ms_facet_phase_y = Setting(0.0)
    ms_dead_width_y_minus = Setting(0.0)
    ms_dead_width_y_plus = Setting(0.0)

    # surface roughness
    ms_file_surf_roughness = Setting(NONE_SPECIFIED)
    ms_roughness_rms_x = Setting(0.0)
    ms_roughness_rms_y = Setting(0.0)

    # kumakhov lens
    ms_specify_rz2 = Setting(0)
    ms_file_with_parameters_rz = Setting(NONE_SPECIFIED)
    ms_file_with_parameters_rz2 = Setting(NONE_SPECIFIED)
    ms_save_intercept_bounces = Setting(0)

    # segmented mirror
    ms_number_of_segments_x = Setting(1)
    ms_number_of_segments_y = Setting(1)
    ms_length_of_segments_x = Setting(0.0)
    ms_length_of_segments_y = Setting(0.0)
    ms_file_orientations = Setting(NONE_SPECIFIED)
    ms_file_polynomial = Setting(NONE_SPECIFIED)

    #####

    mirror_movement = Setting(0)

    mm_mirror_offset_x = Setting(0.0)
    mm_mirror_rotation_x = Setting(0.0)
    mm_mirror_offset_y = Setting(0.0)
    mm_mirror_rotation_y = Setting(0.0)
    mm_mirror_offset_z = Setting(0.0)
    mm_mirror_rotation_z = Setting(0.0)

    #####

    source_movement = Setting(0)
    sm_angle_of_incidence = Setting(0.0)
    sm_distance_from_mirror = Setting(0.0)
    sm_z_rotation = Setting(0.0)
    sm_offset_x_mirr_ref_frame = Setting(0.0)
    sm_offset_y_mirr_ref_frame = Setting(0.0)
    sm_offset_z_mirr_ref_frame = Setting(0.0)
    sm_offset_x_source_ref_frame = Setting(0.0)
    sm_offset_y_source_ref_frame = Setting(0.0)
    sm_offset_z_source_ref_frame = Setting(0.0)
    sm_rotation_around_x = Setting(0.0)
    sm_rotation_around_y = Setting(0.0)
    sm_rotation_around_z = Setting(0.0)

    #####

    file_to_write_out = Setting(3)
    write_out_inc_ref_angles = Setting(0)

    ##########################################
    # SCREEN/SLIT SETTING
    ##########################################

    aperturing = Setting(0)
    open_slit_solid_stop = Setting(0)
    aperture_shape = Setting(0)
    slit_width_xaxis = Setting(0.0)
    slit_height_zaxis = Setting(0.0)
    slit_center_xaxis = Setting(0.0)
    slit_center_zaxis = Setting(0.0)
    external_file_with_coordinate=Setting(NONE_SPECIFIED)
    absorption = Setting(0)
    thickness = Setting(0.0)
    opt_const_file_name = Setting(NONE_SPECIFIED)

    want_main_area=1

    def __init__(self, graphical_options = GraphicalOptions()):
        super().__init__()

        self.graphical_options = graphical_options

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        upper_box = ShadowGui.widgetBox(self.controlArea, "Optical Element Orientation", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "source_plane_distance", "Source Plane Distance [cm]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "image_plane_distance", "Image Plane Distance [cm]", labelWidth=300, valueType=float, orientation="horizontal")

        if self.graphical_options.is_screen_slit:
            box_aperturing = ShadowGui.widgetBox(self.controlArea, "Screen/Slit Shape", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L0, height=240)

            gui.comboBox(box_aperturing, self, "aperturing", label="Aperturing", labelWidth=370, \
                         items=["No", "Yes"], \
                         callback=self.set_Aperturing, sendSelectedValue=False, orientation="horizontal")

            gui.separator(box_aperturing, width=self.INNER_BOX_WIDTH_L0)

            self.box_aperturing_shape = ShadowGui.widgetBox(box_aperturing, "", addSpace=False, orientation="vertical")

            gui.comboBox(self.box_aperturing_shape, self, "open_slit_solid_stop", label="Open slit/Solid stop", labelWidth=300, \
                         items=["aperture/slit", "obstruction/stop"], \
                         sendSelectedValue=False, orientation="horizontal")

            gui.comboBox(self.box_aperturing_shape, self, "aperture_shape", label="Aperture shape", labelWidth=284, \
                         items=["Rectangular", "Ellipse", "External"], \
                         callback=self.set_ApertureShape, sendSelectedValue=False, orientation="horizontal")


            self.box_aperturing_shape_1 = ShadowGui.widgetBox(self.box_aperturing_shape, "", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.box_aperturing_shape_1, self, "external_file_with_coordinate", "External file with coordinate", labelWidth=185, valueType=str, orientation="horizontal")

            self.box_aperturing_shape_2 = ShadowGui.widgetBox(self.box_aperturing_shape, "", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.box_aperturing_shape_2, self, "slit_width_xaxis", "Slit width/x-axis", labelWidth=300, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.box_aperturing_shape_2, self, "slit_height_zaxis", "Slit height/z-axis", labelWidth=300, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.box_aperturing_shape_2, self, "slit_center_xaxis", "Slit center/x-axis", labelWidth=300, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.box_aperturing_shape_2, self, "slit_center_zaxis", "Slit center/z-axis", labelWidth=300, valueType=float, orientation="horizontal")

            self.set_Aperturing()

            box_absorption = ShadowGui.widgetBox(self.controlArea, "Absorption Parameters", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L0, height=130)

            gui.comboBox(box_absorption, self, "absorption", label="Absorption", labelWidth=370, \
                         items=["No", "Yes"], \
                         callback=self.set_Absorption, sendSelectedValue=False, orientation="horizontal")

            gui.separator(box_absorption, width=self.INNER_BOX_WIDTH_L0)

            self.box_absorption_1 = ShadowGui.widgetBox(box_absorption, "", addSpace=False, orientation="vertical")
            self.box_absorption_1_empty = ShadowGui.widgetBox(box_absorption, "", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.box_absorption_1, self, "thickness", "Thickness [cm]", labelWidth=340, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.box_absorption_1, self, "opt_const_file_name", "Opt. const. file name", labelWidth=185, valueType=str, orientation="horizontal")

            self.set_Absorption()

            ShadowGui.widgetBox(self.controlArea, "", addSpace=False, orientation="vertical", height=225)

        else:
            self.calculate_incidence_angle_mrad()
            self.calculate_reflection_angle_mrad()

            self.incidence_angle_deg_le = ShadowGui.lineEdit(upper_box, self, "incidence_angle_deg", "Incident Angle respect to the normal [deg]", labelWidth=300, callback=self.calculate_incidence_angle_mrad, valueType=float, orientation="horizontal")
            self.incidence_angle_rad_le = ShadowGui.lineEdit(upper_box, self, "incidence_angle_mrad", "... or with respect to the surface [mrad]", labelWidth=300, callback=self.calculate_incidence_angle_deg, valueType=float, orientation="horizontal")
            self.reflection_angle_deg_le = ShadowGui.lineEdit(upper_box, self, "reflection_angle_deg", "Reflection Angle respect to the normal [deg]", labelWidth=300, callback=self.calculate_reflection_angle_mrad, valueType=float, orientation="horizontal")
            self.reflection_angle_rad_le = ShadowGui.lineEdit(upper_box, self, "reflection_angle_mrad", "... or with respect to the surface [mrad]", labelWidth=300, callback=self.calculate_reflection_angle_deg, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(upper_box, self, "mirror_orientation_angle", "Mirror Orientation Angle [deg]", tooltip="Mirror Orientation Angle [deg]", labelWidth=300, valueType=float, orientation="horizontal")

            tabs_setting = ShadowGui.tabWidget(self.controlArea, height=self.TABS_AREA_HEIGHT)

            # graph tab
            tab_bas = ShadowGui.createTabPage(tabs_setting, "Basic Setting")
            tab_adv = ShadowGui.createTabPage(tabs_setting, "Advanced Setting")

            tabs_basic_setting = gui.tabWidget(tab_bas)

            if self.graphical_options.is_curved: tab_bas_shape = ShadowGui.createTabPage(tabs_basic_setting, "Surface Shape")
            if self.graphical_options.is_mirror: tab_bas_refl = ShadowGui.createTabPage(tabs_basic_setting, "Reflectivity")
            else: tab_bas_crystal = ShadowGui.createTabPage(tabs_basic_setting, "Crystal")
            tab_bas_dim = ShadowGui.createTabPage(tabs_basic_setting, "Dimensions")

            ##########################################
            #
            # TAB 1.1 - SURFACE SHAPE
            #
            ##########################################


            if graphical_options.is_curved:
                surface_box = ShadowGui.widgetBox(tab_bas_shape, "Surface Shape Parameter", addSpace=False, orientation="vertical")

                gui.comboBox(surface_box, self, "surface_shape_parameters", label="Type", labelWidth=300, items=["internal/calculated", "external/user_defined"], callback=self.set_IntExt_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.surface_box_ext = ShadowGui.widgetBox(surface_box, "", addSpace=True, orientation="vertical", height=150)
                gui.separator(self.surface_box_ext, width=self.INNER_BOX_WIDTH_L2)

                if self.graphical_options.is_spheric:
                    ShadowGui.lineEdit(self.surface_box_ext, self, "spherical_radius", "Spherical Radius [cm]", labelWidth=250, valueType=float, orientation="horizontal")
                elif self.graphical_options.is_toroidal:
                    ShadowGui.lineEdit(self.surface_box_ext, self, "torus_major_radius", "Torus Major Radius [cm]", labelWidth=250, valueType=float, orientation="horizontal")
                    ShadowGui.lineEdit(self.surface_box_ext, self, "torus_minor_radius", "Torus Minor Radius [cm]", labelWidth=250, valueType=float, orientation="horizontal")
                elif self.graphical_options.is_hyperboloid or self.graphical_options.is_ellipsoidal:
                    ShadowGui.lineEdit(self.surface_box_ext, self, "ellipse_hyperbola_semi_major_axis", "Ellipse/Hyperbola semi-major Axis [cm]", labelWidth=250, valueType=float, orientation="horizontal")
                    ShadowGui.lineEdit(self.surface_box_ext, self, "ellipse_hyperbola_semi_minor_axis", "Ellipse/Hyperbola semi-minor Axis [cm]", labelWidth=250, valueType=float, orientation="horizontal")
                    ShadowGui.lineEdit(self.surface_box_ext, self, "angle_of_majax_and_pole", "Angle of MajAx and Pole [cm]", labelWidth=250, valueType=float, orientation="horizontal")
                elif self.graphical_options.is_paraboloid:
                    ShadowGui.lineEdit(self.surface_box_ext, self, "paraboloid_parameter", "Paraboloid parameter", labelWidth=250, valueType=float, orientation="horizontal")

                #TODO ALTRE FORME ATTENZIONE!!!!!

                self.surface_box_int = ShadowGui.widgetBox(surface_box, "", addSpace=True, orientation="vertical", height=150)

                gui.comboBox(self.surface_box_int, self, "focii_and_continuation_plane", label="Focii and Continuation Plane", labelWidth=300, items=["Coincident", "Different"], callback=self.set_FociiCont_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.surface_box_int_2 = ShadowGui.widgetBox(self.surface_box_int, "", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L2)
                self.surface_box_int_2_empty = ShadowGui.widgetBox(self.surface_box_int, "", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L2)

                self.w_object_side_focal_distance = ShadowGui.lineEdit(self.surface_box_int_2, self, "object_side_focal_distance", "Object Side_Focal Distance [cm]", labelWidth=260, valueType=float, orientation="horizontal")
                self.w_image_side_focal_distance = ShadowGui.lineEdit(self.surface_box_int_2, self, "image_side_focal_distance", "Image Side_Focal Distance [cm]", labelWidth=260, valueType=float, orientation="horizontal")
                self.w_incidence_angle_respect_to_normal = ShadowGui.lineEdit(self.surface_box_int_2, self, "incidence_angle_respect_to_normal", "Incidence Angle Respect to Normal [deg]", labelWidth=260, valueType=float, orientation="horizontal")

                if self.graphical_options.is_paraboloid:
                    gui.comboBox(self.surface_box_int, self, "focus_location", label="Focus location", labelWidth=300, items=["Image", "Source"], sendSelectedValue=False, orientation="horizontal")

                self.set_IntExt_Parameters()

                if self.graphical_options.is_toroidal:
                    surface_box_thorus = ShadowGui.widgetBox(surface_box, "", addSpace=True, orientation="vertical")

                    gui.comboBox(surface_box_thorus, self, "toroidal_mirror_pole_location", label="Torus pole location", labelWidth=150, \
                                 items=["lower/outer (concave/concave)", \
                                        "lower/inner (concave/convex)", \
                                        "upper/inner (convex/concave)", \
                                        "upper/outer (convex/convex)"], \
                                 sendSelectedValue=False, orientation="horizontal")

                surface_box_2 = ShadowGui.widgetBox(tab_bas_shape, "Cylinder Parameter", addSpace=True, orientation="vertical", height=125)

                gui.comboBox(surface_box_2, self, "surface_curvature", label="Surface Curvature", items=["Concave", "Convex"], labelWidth=300, sendSelectedValue=False, orientation="horizontal")
                gui.comboBox(surface_box_2, self, "is_cylinder", label="Cylindrical", items=["No", "Yes"], labelWidth=350, callback=self.set_isCyl_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.surface_box_cyl = ShadowGui.widgetBox(surface_box_2, "", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L2)
                self.surface_box_cyl_empty = ShadowGui.widgetBox(surface_box_2, "", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L2)

                ShadowGui.lineEdit(self.surface_box_cyl, self, "cylinder_orientation", "Cylinder Orientation (deg) [CCW from X axis]", labelWidth=300, valueType=float, orientation="horizontal")

                self.set_isCyl_Parameters()

            ##########################################
            #
            # TAB 1.2 - REFLECTIVITY/CRYSTAL
            #
            ##########################################

            if self.graphical_options.is_mirror:
                refl_box = ShadowGui.widgetBox(tab_bas_refl, "Reflectivity Parameter", addSpace=False, orientation="vertical", height=190)

                gui.comboBox(refl_box, self, "reflectivity_type", label="Reflectivity", \
                             items=["Not considered", "Full Polarization dependence", "No Polarization dependence (scalar)"], \
                             callback=self.set_Refl_Parameters, sendSelectedValue=False, orientation="horizontal")

                gui.separator(refl_box, width=self.INNER_BOX_WIDTH_L2, height=10)

                self.refl_box_pol = ShadowGui.widgetBox(refl_box, "", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L2)
                self.refl_box_pol_empty = ShadowGui.widgetBox(refl_box, "", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L2)

                gui.comboBox(self.refl_box_pol, self, "source_of_reflectivity", label="Source of Reflectivity", labelWidth=185, \
                             items=["file generated by PREREFL", "electric susceptibility", "file generated by pre_mlayer"], \
                             callback=self.set_ReflSource_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.refl_box_pol_1 = ShadowGui.widgetBox(self.refl_box_pol, "", addSpace=True, orientation="vertical")

                gui.separator(self.refl_box_pol_1, width=self.INNER_BOX_WIDTH_L2,)
                ShadowGui.lineEdit(self.refl_box_pol_1, self, "file_prerefl", "File Name", labelWidth=125, valueType=str, orientation="horizontal")

                self.refl_box_pol_2 = gui.widgetBox(self.refl_box_pol, "", addSpace=False, orientation="vertical")

                ShadowGui.lineEdit(self.refl_box_pol_2, self, "alpha", "Alpha [epsilon=(1-alpha)+i gamma]", labelWidth=300, valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.refl_box_pol_2, self, "gamma", "Gamma [epsilon=(1-alpha)+i gamma]", labelWidth=300, valueType=float, orientation="horizontal")

                self.refl_box_pol_3 = gui.widgetBox(self.refl_box_pol, "", addSpace=True, orientation="vertical")

                ShadowGui.lineEdit(self.refl_box_pol_3, self, "file_prerefl_m", "File Name", labelWidth=125, valueType=str, orientation="horizontal")
                gui.comboBox(self.refl_box_pol_3, self, "m_layer_tickness", label="Mlayer thickness vary as cosine", labelWidth=350, \
                             items=["No", "Yes"], \
                             sendSelectedValue=False, orientation="horizontal")

                self.set_Refl_Parameters()
            else:
                tabs_crystal_setting = gui.tabWidget(tab_bas_crystal)

                tab_cryst_1 = ShadowGui.createTabPage(tabs_crystal_setting, "Diffraction Settings")
                tab_cryst_2 = ShadowGui.createTabPage(tabs_crystal_setting, "Geometric Setting")

                crystal_box = ShadowGui.widgetBox(tab_cryst_1, "Diffraction Parameters", addSpace=True, orientation="vertical", height=180)

                ShadowGui.lineEdit(crystal_box, self, "file_crystal_parameters", "File with crystal parameters", valueType=str, orientation="horizontal")

                gui.comboBox(crystal_box, self, "crystal_auto_setting", label="Auto setting", labelWidth=350, \
                             items=["No", "Yes"], \
                             callback=self.set_Autosetting, sendSelectedValue=False, orientation="horizontal")

                gui.separator(crystal_box, width=self.INNER_BOX_WIDTH_L3, height=10)

                self.autosetting_box = ShadowGui.widgetBox(crystal_box, "", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L3)
                self.autosetting_box_empty = ShadowGui.widgetBox(crystal_box, "", addSpace=True, orientation="vertical", width=self.INNER_BOX_WIDTH_L3)

                self.autosetting_box_units = ShadowGui.widgetBox(self.autosetting_box, "", addSpace=True, orientation="vertical")

                gui.comboBox(self.autosetting_box_units, self, "units_in_use", label="Units in use", labelWidth=300, \
                             items=["eV", "Angstroms"], \
                             callback=self.set_UnitsInUse, sendSelectedValue=False, orientation="horizontal")

                self.autosetting_box_units_1 = ShadowGui.widgetBox(self.autosetting_box_units, "", addSpace=False, orientation="vertical")

                ShadowGui.lineEdit(self.autosetting_box_units_1, self, "photon_energy", "Set photon energy [eV]", labelWidth=300, valueType=float, orientation="horizontal")

                self.autosetting_box_units_2 = ShadowGui.widgetBox(self.autosetting_box_units, "", addSpace=False, orientation="vertical")

                ShadowGui.lineEdit(self.autosetting_box_units_2, self, "photon_wavelength", "Set wavelength [Å]", labelWidth=300, valueType=float, orientation="horizontal")

                self.set_Autosetting()

                mosaic_box = ShadowGui.widgetBox(tab_cryst_2, "Geometric Parameters", addSpace=True, orientation="vertical", height=280)

                gui.comboBox(mosaic_box, self, "mosaic_crystal", label="Mosaic Crystal", labelWidth=350, \
                             items=["No", "Yes"], \
                             callback=self.set_Mosaic, sendSelectedValue=False, orientation="horizontal")

                gui.separator(mosaic_box, width=self.INNER_BOX_WIDTH_L3, height=10)

                self.mosaic_box_1 = ShadowGui.widgetBox(mosaic_box, "", addSpace=False, orientation="vertical")

                self.asymmetric_cut_box = ShadowGui.widgetBox(self.mosaic_box_1, "", addSpace=False, orientation="vertical", height=110)

                gui.comboBox(self.asymmetric_cut_box, self, "asymmetric_cut", label="Asymmetric cut", labelWidth=350, \
                             items=["No", "Yes"], \
                             callback=self.set_AsymmetricCut, sendSelectedValue=False, orientation="horizontal")

                self.asymmetric_cut_box_1 = ShadowGui.widgetBox(self.asymmetric_cut_box, "", addSpace=False, orientation="vertical", width=self.INNER_BOX_WIDTH_L3)
                self.asymmetric_cut_box_1_empty = ShadowGui.widgetBox(self.asymmetric_cut_box, "", addSpace=False, orientation="vertical", width=self.INNER_BOX_WIDTH_L3)

                ShadowGui.lineEdit(self.asymmetric_cut_box_1, self, "planes_angle", "Planes angle [deg]", labelWidth=250, valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.asymmetric_cut_box_1, self, "below_onto_bragg_planes", "Below[-1]/onto[1] bragg planes", labelWidth=330, valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.asymmetric_cut_box_1, self, "thickness", "Thickness [cm]", labelWidth=250, valueType=float, orientation="horizontal")

                gui.separator(self.mosaic_box_1)

                self.johansson_box = ShadowGui.widgetBox(self.mosaic_box_1, "", addSpace=False, orientation="vertical", height=100)

                gui.comboBox(self.johansson_box, self, "johansson_geometry", label="Johansson Geometry", labelWidth=350, \
                             items=["No", "Yes"], \
                             callback=self.set_JohanssonGeometry, sendSelectedValue=False, orientation="horizontal")

                self.johansson_box_1 = ShadowGui.widgetBox(self.johansson_box, "", addSpace=False, orientation="vertical", width=self.INNER_BOX_WIDTH_L3)
                self.johansson_box_1_empty = ShadowGui.widgetBox(self.johansson_box, "", addSpace=False, orientation="vertical", width=self.INNER_BOX_WIDTH_L3)

                ShadowGui.lineEdit(self.johansson_box_1, self, "johansson_radius", "Johansson radius", labelWidth=250, valueType=float, orientation="horizontal")

                self.mosaic_box_2 = ShadowGui.widgetBox(mosaic_box, "", addSpace=False, orientation="vertical")

                ShadowGui.lineEdit(self.mosaic_box_2, self, "angle_spread_FWHM", "Angle spread FWHM [deg]", labelWidth=250, valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.mosaic_box_2, self, "thickness", "Thickness [cm]", labelWidth=250, valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.mosaic_box_2, self, "seed_for_mosaic", "Seed for mosaic [>10^5]", labelWidth=250, valueType=float, orientation="horizontal")

                self.set_Mosaic()

            ##########################################
            #
            # TAB 1.3 - DIMENSIONS
            #
            ##########################################

            dimension_box = ShadowGui.widgetBox(tab_bas_dim, "Dimensions", addSpace=False, orientation="vertical", height=210)

            gui.comboBox(dimension_box, self, "is_infinite", label="Limits Check", \
                         items=["Infinite o.e. dimensions", "Finite o.e. dimensions"], \
                         callback=self.set_Dim_Parameters, sendSelectedValue=False, orientation="horizontal")

            gui.separator(dimension_box, width=self.INNER_BOX_WIDTH_L2, height=10)

            self.dimdet_box = ShadowGui.widgetBox(dimension_box, "", addSpace=False, orientation="vertical", width=self.INNER_BOX_WIDTH_L2)
            self.dimdet_box_empty = ShadowGui.widgetBox(dimension_box, "", addSpace=False, orientation="vertical", width=self.INNER_BOX_WIDTH_L2)

            gui.comboBox(self.dimdet_box, self, "mirror_shape", label="Shape selected", labelWidth=250, \
                         items=["Rectangular", "Full ellipse", "Ellipse with hole"], \
                         sendSelectedValue=False, orientation="horizontal")

            ShadowGui.lineEdit(self.dimdet_box, self, "dim_x_plus", "X(+) Half Width / Int Maj Ax [cm]", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.dimdet_box, self, "dim_x_minus", "X(-) Half Width / Int Maj Ax [cm]", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.dimdet_box, self, "dim_y_plus", "Y(+) Half Width / Int Min Ax [cm]", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.dimdet_box, self, "dim_y_minus", "Y(-) Half Width / Int Min Ax [cm]", labelWidth=250, valueType=float, orientation="horizontal")

            self.set_Dim_Parameters()

            ##########################################
            ##########################################
            # ADVANCED SETTINGS
            ##########################################
            ##########################################

            tabs_advanced_setting = gui.tabWidget(tab_adv)

            tab_adv_mod_surf = ShadowGui.createTabPage(tabs_advanced_setting, "Modified Surface")
            tab_adv_mir_mov = ShadowGui.createTabPage(tabs_advanced_setting, "Mirror Movement")
            tab_adv_sou_mov = ShadowGui.createTabPage(tabs_advanced_setting, "Source Movement")
            tab_adv_misc = ShadowGui.createTabPage(tabs_advanced_setting, "Output Files")

            ##########################################
            #
            # TAB 2.1 - Modified Surface
            #
            ##########################################

            mod_surf_box = ShadowGui.widgetBox(tab_adv_mod_surf, "Modified Surface Parameters", addSpace=False, orientation="vertical", height=370, width=self.INNER_BOX_WIDTH_L1)

            gui.comboBox(mod_surf_box, self, "modified_surface", label="Modification Type", labelWidth=270, \
                         items=["None", "Surface Error", "Faceted Surface", "Surface Roughness", "Kumakhov Lens", "Segmented Mirror"], \
                         callback=self.set_ModifiedSurface, sendSelectedValue=False, orientation="horizontal")

            gui.separator(mod_surf_box, width=self.INNER_BOX_WIDTH_L1, height=10)

            # SURFACE ERROR

            self.surface_error_box =  ShadowGui.widgetBox(mod_surf_box, box="", addSpace=False, orientation="vertical")

            type_of_defect_box = ShadowGui.widgetBox(self.surface_error_box, "", addSpace=False, orientation="vertical")

            gui.comboBox(type_of_defect_box, self, "ms_type_of_defect", label="Type of Defect", labelWidth=270, \
                         items=["sinusoidal", "gaussian", "external spline"], \
                         callback=self.set_TypeOfDefect, sendSelectedValue=False, orientation="horizontal")

            self.mod_surf_err_box_1 = ShadowGui.widgetBox(self.surface_error_box, "", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.mod_surf_err_box_1, self, "ms_defect_file_name", "File name", labelWidth=125, valueType=str, orientation="horizontal")

            self.mod_surf_err_box_2 = ShadowGui.widgetBox(self.surface_error_box, "", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.mod_surf_err_box_2, self, "ms_ripple_wavel_x", "Ripple Wavel. X", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_err_box_2, self, "ms_ripple_wavel_y", "Ripple Wavel. Y", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_err_box_2, self, "ms_ripple_ampli_x", "Ripple Ampli. X", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_err_box_2, self, "ms_ripple_ampli_y", "Ripple Ampli. Y", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_err_box_2, self, "ms_ripple_phase_x", "Ripple Phase X", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_err_box_2, self, "ms_ripple_phase_y", "Ripple Phase Y", labelWidth=250, valueType=float, orientation="horizontal")

            # FACETED SURFACE

            self.faceted_surface_box =  ShadowGui.widgetBox(mod_surf_box, box="", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_file_facet_descr", "File w/ facet descr.", labelWidth=125, valueType=str, orientation="horizontal")

            gui.comboBox(self.faceted_surface_box, self, "ms_lattice_type", label="Lattice Type", labelWidth=270, \
                         items=["rectangle", "hexagonal"], sendSelectedValue=False, orientation="horizontal")

            gui.comboBox(self.faceted_surface_box, self, "ms_orientation", label="Orientation", labelWidth=270, \
                         items=["y-axis", "other"], sendSelectedValue=False, orientation="horizontal")

            gui.comboBox(self.faceted_surface_box, self, "ms_intercept_to_use", label="Intercept to use", labelWidth=270, \
                         items=["2nd first", "2nd closest", "closest", "farthest"], sendSelectedValue=False, orientation="horizontal")


            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_facet_width_x", "Facet width (in X)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_facet_phase_x", "Facet phase in X (0-360)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_dead_width_x_minus", "Dead width (abs, for -X)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_dead_width_x_plus", "Dead width (abs, for +X)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_facet_width_y", "Facet width (in Y)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_facet_phase_y", "Facet phase in Y (0-360)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_dead_width_y_minus", "Dead width (abs, for -Y)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.faceted_surface_box, self, "ms_dead_width_y_plus", "Dead width (abs, for +Y)", labelWidth=250, valueType=float, orientation="horizontal")

            # SURFACE ROUGHNESS

            self.surface_roughness_box =  ShadowGui.widgetBox(mod_surf_box, box="", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.surface_roughness_box, self, "ms_file_surf_roughness", "Surface Roughness File w/ PSD fn", valueType=str, orientation="horizontal")
            ShadowGui.lineEdit(self.surface_roughness_box, self, "ms_roughness_rms_y", "Roughness RMS in Y (Å)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.surface_roughness_box, self, "ms_roughness_rms_x", "Roughness RMS in X (Å)", labelWidth=250, valueType=float, orientation="horizontal")

            # KUMAKHOV LENS

            self.kumakhov_lens_box =  ShadowGui.widgetBox(mod_surf_box, box="", addSpace=False, orientation="vertical")

            gui.comboBox(self.kumakhov_lens_box, self, "ms_specify_rz2", label="Specify r(z)^2", labelWidth=350, \
                         items=["No", "Yes"], callback=self.set_SpecifyRz2, sendSelectedValue=False, orientation="horizontal")

            self.kumakhov_lens_box_1 =  ShadowGui.widgetBox(self.kumakhov_lens_box, box="", addSpace=False, orientation="vertical")
            self.kumakhov_lens_box_2 =  ShadowGui.widgetBox(self.kumakhov_lens_box, box="", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.kumakhov_lens_box_1, self, "ms_file_with_parameters_rz", "File with parameters (r(z))", labelWidth=185, valueType=str, orientation="horizontal")
            ShadowGui.lineEdit(self.kumakhov_lens_box_2, self, "ms_file_with_parameters_rz2", "File with parameters (r(z)^2)", labelWidth=185, valueType=str, orientation="horizontal")

            gui.comboBox(self.kumakhov_lens_box, self, "ms_save_intercept_bounces", label="Save intercept and bounces", labelWidth=350, \
                         items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")

            # SEGMENTED MIRROR

            self.segmented_mirror_box =  ShadowGui.widgetBox(mod_surf_box, box="", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.segmented_mirror_box, self, "ms_number_of_segments_x", "Number of segments (X)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.segmented_mirror_box, self, "ms_length_of_segments_x", "Length of segments (X)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.segmented_mirror_box, self, "ms_number_of_segments_y", "Number of segments (Y)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.segmented_mirror_box, self, "ms_length_of_segments_y", "Length of segments (Y)", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.segmented_mirror_box, self, "ms_file_orientations", "File w/ orientations", labelWidth=155, valueType=str, orientation="horizontal")
            ShadowGui.lineEdit(self.segmented_mirror_box, self, "ms_file_polynomial", "File w/ polynomial", labelWidth=155, valueType=str, orientation="horizontal")

            self.set_ModifiedSurface()

            ##########################################
            #
            # TAB 2.2 - Mirror Movement
            #
            ##########################################

            mir_mov_box = ShadowGui.widgetBox(tab_adv_mir_mov, "Mirror Movement Parameters", addSpace=False, orientation="vertical", height=230, width=self.INNER_BOX_WIDTH_L1)

            gui.comboBox(mir_mov_box, self, "mirror_movement", label="Mirror Movement", labelWidth=350, \
                         items=["No", "Yes"], \
                         callback=self.set_MirrorMovement, sendSelectedValue=False, orientation="horizontal")

            gui.separator(mir_mov_box, width=self.INNER_BOX_WIDTH_L1, height=10)

            self.mir_mov_box_1 = ShadowGui.widgetBox(mir_mov_box, "", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_offset_x", "Mirror Offset X", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_rotation_x", "Mirror Rotation X", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_offset_y", "Mirror Offset Y", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_rotation_y", "Mirror Rotation Z", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_offset_z", "Mirror Offset Z", labelWidth=250, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_rotation_z", "Mirror Rotation Z", labelWidth=250, valueType=float, orientation="horizontal")

            self.set_MirrorMovement()

           ##########################################
            #
            # TAB 2.3 - Source Movement
            #
            ##########################################

            sou_mov_box = ShadowGui.widgetBox(tab_adv_sou_mov, "Source Movement Parameters", addSpace=False, orientation="vertical", height=400, width=self.INNER_BOX_WIDTH_L1)

            gui.comboBox(sou_mov_box, self, "source_movement", label="Source Movement", labelWidth=350, \
                         items=["No", "Yes"], \
                         callback=self.set_SourceMovement, sendSelectedValue=False, orientation="horizontal")

            gui.separator(sou_mov_box, width=self.INNER_BOX_WIDTH_L1, height=10)

            self.sou_mov_box_1 = ShadowGui.widgetBox(sou_mov_box, "", addSpace=False, orientation="vertical")

            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_angle_of_incidence", "Angle of Incidence [deg]", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_distance_from_mirror", "Distance from mirror [cm]", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_z_rotation", "Z-rotation [deg]", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_x_mirr_ref_frame", "offset X [cm] in MIRROR reference frame", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_y_mirr_ref_frame", "offset Y [cm] in MIRROR reference frame", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_z_mirr_ref_frame", "offset Z [cm] in MIRROR reference frame", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_x_source_ref_frame", "offset X [cm] in SOURCE reference frame", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_y_source_ref_frame", "offset Y [cm] in SOURCE reference frame", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_z_source_ref_frame", "offset Z [cm] in SOURCE reference frame", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_rotation_around_x", "rotation [CCW, deg] around X", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_rotation_around_y", "rotation [CCW, deg] around Y", labelWidth=270, valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_rotation_around_z", "rotation [CCW, deg] around Z", labelWidth=270, valueType=float, orientation="horizontal")

            self.set_SourceMovement()

            ##########################################
            #
            # TAB 2.4 - Other
            #
            ##########################################

            adv_other_box = ShadowGui.widgetBox(tab_adv_misc, "Optional file output", addSpace=False, orientation="vertical")

            gui.comboBox(adv_other_box, self, "file_to_write_out", label="Files to write out", labelWidth=310, \
                         items=["All", "Mirror", "Image", "None"], \
                         sendSelectedValue=False, orientation="horizontal")

            gui.comboBox(adv_other_box, self, "write_out_inc_ref_angles", label="Write out Incident/Reflected angles [angle.xx]", labelWidth=350, \
                         items=["No", "Yes"], \
                         sendSelectedValue=False, orientation="horizontal")

        button = gui.button(self.controlArea, self, "Run Shadow/trace", callback=self.traceOpticalElement)
        button.setFixedHeight(45)

    ############################################################
    #
    # GRAPHIC USER INTERFACE MANAGEMENT
    #
    ############################################################

    # TAB 1.1

    def set_IntExt_Parameters(self):
        self.surface_box_int.setVisible(self.surface_shape_parameters == 0)
        self.surface_box_ext.setVisible(self.surface_shape_parameters == 1)
        if self.surface_shape_parameters == 0: self.set_FociiCont_Parameters()

    def set_FociiCont_Parameters(self):
        self.surface_box_int_2.setVisible(self.focii_and_continuation_plane == 1)
        self.surface_box_int_2_empty.setVisible(self.focii_and_continuation_plane == 0)

    def set_isCyl_Parameters(self):
        self.surface_box_cyl.setVisible(self.is_cylinder == 1)
        self.surface_box_cyl_empty.setVisible(self.is_cylinder == 0)

    # TAB 1.2

    def set_Refl_Parameters(self):
        self.refl_box_pol.setVisible(self.reflectivity_type != 0)
        self.refl_box_pol_empty.setVisible(self.reflectivity_type == 0)
        if self.reflectivity_type != 0: self.set_ReflSource_Parameters()

    def set_ReflSource_Parameters(self):
        self.refl_box_pol_1.setVisible(self.source_of_reflectivity == 0)
        self.refl_box_pol_2.setVisible(self.source_of_reflectivity == 1)
        self.refl_box_pol_3.setVisible(self.source_of_reflectivity == 2)

    def set_Autosetting(self):
        self.autosetting_box_empty.setVisible(self.crystal_auto_setting == 0)
        self.autosetting_box.setVisible(self.crystal_auto_setting == 1)

        if self.crystal_auto_setting == 0:
            self.incidence_angle_deg_le.setEnabled(True)
            self.incidence_angle_rad_le.setEnabled(True)
            self.reflection_angle_deg_le.setEnabled(True)
            self.reflection_angle_rad_le.setEnabled(True)
        else:
            self.incidence_angle_deg_le.setEnabled(False)
            self.incidence_angle_rad_le.setEnabled(False)
            self.reflection_angle_deg_le.setEnabled(False)
            self.reflection_angle_rad_le.setEnabled(False)
            self.set_UnitsInUse()

    def set_UnitsInUse(self):
        self.autosetting_box_units_1.setVisible(self.units_in_use == 0)
        self.autosetting_box_units_2.setVisible(self.units_in_use == 1)

    def set_Mosaic(self):
        self.mosaic_box_1.setVisible(self.mosaic_crystal == 0)
        self.mosaic_box_2.setVisible(self.mosaic_crystal == 1)

        if self.mosaic_crystal == 0:
            self.set_AsymmetricCut()
            self.set_JohanssonGeometry()

    def set_AsymmetricCut(self):
        self.asymmetric_cut_box_1.setVisible(self.asymmetric_cut == 1)
        self.asymmetric_cut_box_1_empty.setVisible(self.asymmetric_cut == 0)

    def set_JohanssonGeometry(self):
        self.johansson_box_1.setVisible(self.johansson_geometry == 1)
        self.johansson_box_1_empty.setVisible(self.johansson_geometry == 0)

    # TAB 1.3

    def set_Dim_Parameters(self):
        self.dimdet_box.setVisible(self.is_infinite == 1)
        self.dimdet_box_empty.setVisible(self.is_infinite == 0)

    # TAB 2

    def set_SourceMovement(self):
        self.sou_mov_box_1.setVisible(self.source_movement == 1)

    def set_MirrorMovement(self):
        self.mir_mov_box_1.setVisible(self.mirror_movement == 1)

    def set_TypeOfDefect(self):
        self.mod_surf_err_box_1.setVisible(self.ms_type_of_defect != 0)
        self.mod_surf_err_box_2.setVisible(self.ms_type_of_defect == 0)

    def set_ModifiedSurface(self):
        self.surface_error_box.setVisible(self.modified_surface == 1)
        self.faceted_surface_box.setVisible(self.modified_surface == 2)
        self.surface_roughness_box.setVisible(self.modified_surface == 3)
        self.kumakhov_lens_box.setVisible(self.modified_surface == 4)
        self.segmented_mirror_box.setVisible(self.modified_surface == 5)
        if self.modified_surface == 1: self.set_TypeOfDefect()
        if self.modified_surface == 4: self.set_SpecifyRz2()

    def set_SpecifyRz2(self):
        self.kumakhov_lens_box_1.setVisible(self.ms_specify_rz2 == 0)
        self.kumakhov_lens_box_2.setVisible(self.ms_specify_rz2 == 1)


    def set_ApertureShape(self):
        self.box_aperturing_shape_1.setVisible(self.aperture_shape == 2)
        self.box_aperturing_shape_2.setVisible(self.aperture_shape != 2)

    def set_Aperturing(self):
            self.box_aperturing_shape.setVisible(self.aperturing == 1)

            if self.aperturing == 1: self.set_ApertureShape()

    def set_Absorption(self):
        self.box_absorption_1_empty.setVisible(self.absorption == 0)
        self.box_absorption_1.setVisible(self.absorption == 1)

    ############################################################
    #
    # USER INPUT MANAGEMENT
    #
    ############################################################

    def calculate_incidence_angle_mrad(self):
        self.incidence_angle_mrad = round(math.radians(90-self.incidence_angle_deg)*1000, 2)

    def calculate_reflection_angle_mrad(self):
        self.reflection_angle_mrad = round(math.radians(90-self.reflection_angle_deg)*1000, 2)

    def calculate_incidence_angle_deg(self):
        self.incidence_angle_deg = round(math.degrees(0.5*math.pi-(self.incidence_angle_mrad/1000)), 3)

    def calculate_reflection_angle_deg(self):
        self.reflection_angle_deg = round(math.degrees(0.5*math.pi-(self.reflection_angle_mrad/1000)), 3)

    def populateFields(self, shadow_oe = Orange.shadow.ShadowOpticalElement.create_empty_oe()):

        if self.graphical_options.is_screen_slit:
            shadow_oe.oe.setFrameOfReference(self.source_plane_distance, \
                                             self.image_plane_distance, \
                                             0, \
                                             180, \
                                             0)
        else:
            shadow_oe.oe.setFrameOfReference(self.source_plane_distance, \
                                             self.image_plane_distance, \
                                             self.incidence_angle_deg, \
                                             self.reflection_angle_deg, \
                                             self.mirror_orientation_angle)

            #####################################
            # BASIC SETTING
            #####################################

            if self.graphical_options.is_curved:
                if self.is_cylinder:
                   shadow_oe.oe.setCylindric(cyl_ang=self.cylinder_orientation)
                else:
                   shadow_oe.oe.unsetCylinder()
            else:
               shadow_oe.oe.unsetCylinder()

            if self.surface_shape_parameters == 0:

               #IMPLEMENTATION OF THE AUTOMATIC CALCULATION OF THE SAGITTAL FOCUSING FOR CYLINDERS
               if (self.is_cylinder and self.cylinder_orientation==90):
                   if self.graphical_options.is_spheric:
                       shadow_oe.oe.F_EXT=1

                       # RADIUS = (2 F1 F2 sin (theta)) /( F1+F2)

                       if self.focii_and_continuation_plane == 0:
                          self.spherical_radius = ((2*self.source_plane_distance*self.image_plane_distance)/(self.source_plane_distance+self.image_plane_distance))*math.sin(self.reflection_angle_mrad)
                       else:
                          self.spherical_radius = ((2*self.object_side_focal_distance*self.image_side_focal_distance)/(self.object_side_focal_distance+self.image_side_focal_distance))*math.sin(round(math.radians(90-self.incidence_angle_respect_to_normal), 2))

                       shadow_oe.oe.RMIRR = self.spherical_radius
                   else:
                       print("ERROR") #TODO: ERROR MANAGEMENT - OPERATION NOT SUPPORTED
               else:
                   if self.focii_and_continuation_plane == 0:
                      shadow_oe.oe.setAutoFocus(f_default=1)
                   else:
                      shadow_oe.oe.setAutoFocus(f_default=0, \
                                                ssour=self.object_side_focal_distance, \
                                                simag=self.image_side_focal_distance, \
                                                theta=self.incidence_angle_respect_to_normal)
                   if self.graphical_options.is_paraboloid: shadow_oe.oe.F_SIDE=self.focus_location
            else:
               shadow_oe.oe.F_EXT=1
               if self.graphical_options.is_spheric:
                   shadow_oe.oe.RMIRR = self.spherical_radius
               elif self.graphical_options.is_toroidal:
                   shadow_oe.oe.RMAJ=self.torus_major_radius
                   shadow_oe.oe.RMIN=self.torus_minor_radius
               elif self.graphical_options.is_hyperboloid or self.graphical_options.is_ellipsoidal:
                   shadow_oe.oe.AXMAJ=self.ellipse_hyperbola_semi_major_axis
                   shadow_oe.oe.AXMIN=self.ellipse_hyperbola_semi_minor_axis
                   shadow_oe.oe.ELL_THE=self.angle_of_majax_and_pole
               elif self.graphical_options.is_paraboloid:
                   shadow_oe.oe.PARAM=self.paraboloid_parameter

               #TODO ALTRE FORME ATTENZIONE!!!!!

            if self.graphical_options.is_toroidal: shadow_oe.oe.F_TORUS=self.toroidal_mirror_pole_location

            if self.surface_curvature == 0:
               shadow_oe.oe.setConcave()
            else:
               shadow_oe.oe.setConvex()

            if self.graphical_options.is_mirror:
                if self.reflectivity_type == 0:
                   shadow_oe.oe.unsetReflectivity()
                elif self.reflectivity_type == 1:
                    if self.source_of_reflectivity == 0:
                        shadow_oe.oe.setReflectivityFull(f_refl=0, file_refl=bytes(self.file_prerefl, 'utf-8'))
                    elif self.source_of_reflectivity == 1:
                        shadow_oe.oe.setReflectivityFull(f_refl=1, rparams=[self.alpha, self.gamma])
                    elif self.source_of_reflectivity == 2:
                        shadow_oe.oe.setReflectivityFull(f_refl=2, file_refl=bytes(self.file_prerefl_m, 'utf-8'), f_thick=self.m_layer_tickness)
                elif self.reflectivity_type == 2:
                    if self.source_of_reflectivity == 0:
                        shadow_oe.oe.setReflectivityScalar(f_refl=0, file_refl=bytes(self.file_prerefl, 'utf-8'))
                    elif self.source_of_reflectivity == 1:
                        shadow_oe.oe.setReflectivityScalar(f_refl=1, rparams=[self.alpha, self.gamma])
                    elif self.source_of_reflectivity == 2:
                        shadow_oe.oe.setReflectivityScalar(f_refl=2, file_refl=bytes(self.file_prerefl_m, 'utf-8'), f_thick=self.m_layer_tickness)
            else:
                shadow_oe.oe.unsetReflectivity()
                shadow_oe.oe.setCrystal(file_refl=bytes(self.file_crystal_parameters, 'utf-8'))

                if self.crystal_auto_setting == 0:
                    shadow_oe.oe.F_CENTRAL=0
                else:
                    shadow_oe.oe.setAutoTuning(f_phot_cent=self.units_in_use, phot_cent=self.photon_energy, r_lambda=self.photon_wavelength)

                if self.mosaic_crystal==1:
                    shadow_oe.oe.setMosaic(mosaic_seed=self.seed_for_mosaic, spread_mos=self.angle_spread_FWHM, thickness=self.thickness)
                else:
                    if self.asymmetric_cut == 1:
                        shadow_oe.oe.F_BRAGG_A=1
                        shadow_oe.oe.A_BRAGG=self.planes_angle
                        shadow_oe.oe.ORDER=self.below_onto_bragg_planes
                        shadow_oe.oe.THICKNESS=self.thickness
                    if self.johansson_geometry == 1:
                        shadow_oe.oe.F_JOHANSSON=1
                        shadow_oe.oe.R_JOHANSSON=self.johansson_radius

            if self.is_infinite == 0:
                shadow_oe.oe.FHIT_C = 0
            else:
                shadow_oe.oe.setDimensions(fshape=(self.mirror_shape+1), \
                                           params=array([self.dim_y_plus, self.dim_y_minus,self.dim_x_plus, self.dim_x_minus]))

            #####################################
            # ADVANCED SETTING
            #####################################

            shadow_oe.oe.FDUMMY=self.modified_surface

            if self.modified_surface == 1:
                 if self.ms_type_of_defect == 0:
                     shadow_oe.oe.setRipple(f_g_s=0, xyAmpWavPha=array([self.ms_ripple_ampli_x, \
                                                                        self.ms_ripple_wavel_x, \
                                                                        self.ms_ripple_phase_x, \
                                                                        self.ms_ripple_ampli_y, \
                                                                        self.ms_ripple_wavel_y, \
                                                                        self.ms_ripple_phase_y]))
                 else:
                     shadow_oe.oe.setRipple(f_g_s=self.ms_type_of_defect, file_rip=bytes(self.ms_defect_file_name, 'utf-8'))
            elif self.modified_surface == 2:
                shadow_oe.oe.FILE_FAC=bytes(self.ms_file_facet_descr, 'utf-8')
                shadow_oe.oe.F_FAC_LATT=self.ms_lattice_type
                shadow_oe.oe.F_FAC_ORIENT=self.ms_orientation
                shadow_oe.oe.F_POLSEL=self.ms_lattice_type+1
                shadow_oe.oe.RFAC_LENX=self.ms_facet_width_x
                shadow_oe.oe.RFAC_PHAX=self.ms_facet_phase_x
                shadow_oe.oe.RFAC_DELX1=self.ms_dead_width_x_minus
                shadow_oe.oe.RFAC_DELX2=self.ms_dead_width_x_plus
                shadow_oe.oe.RFAC_LENY=self.ms_facet_width_y
                shadow_oe.oe.RFAC_PHAY=self.ms_facet_phase_y
                shadow_oe.oe.RFAC_DELY1=self.ms_dead_width_y_minus
                shadow_oe.oe.RFAC_DELY2=self.ms_dead_width_y_plus
            elif self.modified_surface == 3:
                shadow_oe.oe.FILE_ROUGH=bytes(self.ms_file_surf_roughness, 'utf-8')
                shadow_oe.oe.ROUGH_X=self.ms_roughness_rms_x
                shadow_oe.oe.ROUGH_Y=self.ms_roughness_rms_y
            elif self.modified_surface == 4:
                shadow_oe.oe.F_KOMA_CA=self.ms_specify_rz2
                shadow_oe.oe.FILE_KOMA=bytes(self.ms_file_with_parameters_rz, 'utf-8')
                shadow_oe.oe.FILE_KOMA_CA=bytes(self.ms_file_with_parameters_rz2, 'utf-8')
                shadow_oe.oe.F_KOMA_BOUNCE=self.ms_save_intercept_bounces
            elif self.modified_surface == 5:
                shadow_oe.oe.ISEG_XNUM=self.ms_number_of_segments_x
                shadow_oe.oe.ISEG_YNUM=self.ms_number_of_segments_y
                shadow_oe.oe.SEG_LENX=self.ms_length_of_segments_x
                shadow_oe.oe.SEG_LENY=self.ms_length_of_segments_y
                shadow_oe.oe.FILE_SEGMENT=bytes(self.ms_file_orientations, 'utf-8')
                shadow_oe.oe.FILE_SEGP=bytes(self.ms_file_polynomial, 'utf-8')

            if self.mirror_movement == 1:
                 shadow_oe.oe.F_MOVE=1
                 shadow_oe.oe.OFFX=self.mm_mirror_offset_x
                 shadow_oe.oe.OFFY=self.mm_mirror_offset_y
                 shadow_oe.oe.OFFZ=self.mm_mirror_offset_z
                 shadow_oe.oe.X_ROT=self.mm_mirror_rotation_x
                 shadow_oe.oe.Y_ROT=self.mm_mirror_rotation_y
                 shadow_oe.oe.Z_ROT=self.mm_mirror_rotation_z

            if self.source_movement == 1:
                 shadow_oe.oe.FSTAT=1
                 shadow_oe.oe.RTHETA=self.sm_angle_of_incidence
                 shadow_oe.oe.RDSOUR=self.sm_distance_from_mirror
                 shadow_oe.oe.ALPHA_S=self.sm_z_rotation
                 shadow_oe.oe.OFF_SOUX=self.sm_offset_x_mirr_ref_frame
                 shadow_oe.oe.OFF_SOUY=self.sm_offset_y_mirr_ref_frame
                 shadow_oe.oe.OFF_SOUZ=self.sm_offset_z_mirr_ref_frame
                 shadow_oe.oe.X_SOUR=self.sm_offset_x_source_ref_frame
                 shadow_oe.oe.Y_SOUR=self.sm_offset_y_source_ref_frame
                 shadow_oe.oe.Z_SOUR=self.sm_offset_z_source_ref_frame
                 shadow_oe.oe.X_SOUR_ROT=self.sm_rotation_around_x
                 shadow_oe.oe.Y_SOUR_ROT=self.sm_rotation_around_y
                 shadow_oe.oe.Z_SOUR_ROT=self.sm_rotation_around_z

            shadow_oe.oe.FWRITE=self.file_to_write_out
            shadow_oe.oe.F_ANGLE=self.write_out_inc_ref_angles

    def doSpecificSetting(self, shadow_oe):
        return None

    def checkFields(self):
        return True

    def writeCalculatedFields(self, shadow_oe):
        if self.surface_shape_parameters == 0:
            if self.graphical_options.is_spheric:
                self.spherical_radius = shadow_oe.oe.RMIRR
            elif self.graphical_options.is_toroidal:
                self.torus_major_radius = shadow_oe.oe.RMAJ
                self.torus_minor_radius = shadow_oe.oe.RMIN
        if self.crystal_auto_setting == 1:
            self.incidence_angle_mrad = round((math.pi*0.5-shadow_oe.oe.T_INCIDENCE)*1000, 2)
            self.reflection_angle_mrad = round((math.pi*0.5-shadow_oe.oe.T_REFLECTION)*1000, 2)
            self.calculate_incidence_angle_deg()
            self.calculate_reflection_angle_deg()

    def completeOperations(self, shadow_oe=None):
        self.information(0, "Running SHADOW")
        qApp.processEvents()

        sys.stdout = EmittingStream(textWritten=self.writeStdOut)
        grabber = TTYGrabber()
        grabber.start()

        self.progressBarSet(50)

        beam_out = Orange.shadow.ShadowBeam.traceFromOE(self.input_beam, shadow_oe)

        self.writeCalculatedFields(shadow_oe)

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

    def traceOpticalElement(self):

        if not self.input_beam is None:
            self.error()

            self.progressBarInit()

            shadow_oe = self.instantiateShadowOE()

            self.populateFields(shadow_oe)
            self.doSpecificSetting(shadow_oe)
            self.progressBarSet(10)

            if self.checkFields():
                self.completeOperations(shadow_oe)
            else:
                self.error(0, "Error on input")

            self.progressBarFinished()
        else:
            self.error(0, "No input beam, run the previous simulation first")
            self.close()
            
    def setBeam(self, beam):
        self.onReceivingInput()

        self.input_beam = beam

        if self.is_automatic_run:
           self.traceOpticalElement()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OpticalElement()
    ow.show()
    a.exec_()
    ow.saveSettings()