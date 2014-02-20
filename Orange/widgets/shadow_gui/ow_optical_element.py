import sys, math, array
from numpy import zeros
import Orange
import Orange.shadow
from Orange.widgets import widget, gui
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
    THREE_ROW_HEIGHT = 165

    graphical_options=None

    source_plane_distance = Setting(10)
    image_plane_distance = Setting(20)
    incidence_angle_deg = Setting(88)
    incidence_angle_mrad = Setting(0)
    reflection_angle_deg = Setting(88)
    reflection_angle_mrad = Setting(0)
    mirror_orientation_angle = Setting(0)

    ##########################################
    # BASIC SETTING
    ##########################################

    surface_shape_parameters = Setting(0)
    spherical_radius = Setting(0)

    torus_major_radius = Setting(0)
    torus_minor_radius = Setting(0)
    toroidal_mirror_pole_location=Setting(0)

    focii_and_continuation_plane = Setting(0)

    object_side_focal_distance = Setting(0)
    image_side_focal_distance = Setting(0)
    incidence_angle_respect_to_normal = Setting(0)

    surface_curvature = Setting(0)
    is_cylinder = Setting(1)
    cylinder_orientation = Setting(0)
    reflectivity_type = Setting(0)
    source_of_reflectivity = Setting(0)
    file_prerefl = Setting("reflec.dat")
    alpha = Setting(0)
    gamma = Setting(0)
    file_prerefl_m = Setting("reflec.dat")
    m_layer_tickness = Setting(0)

    is_infinite = Setting(0)
    mirror_shape = Setting(1)
    dim_x_plus = Setting(0)
    dim_x_minus = Setting(0)
    dim_y_plus = Setting(0)
    dim_y_minus = Setting(0)

    file_crystal_parameters = Setting("reflec.dat")
    crystal_auto_setting = Setting(0)
    units_in_use = Setting(0)
    photon_energy = Setting(5.0)
    photon_wavelength = Setting(5000.0)

    mosaic_crystal = Setting(0)
    angle_spread_FWHM = Setting(0)
    thickness = Setting(0)
    seed_for_mosaic = Setting(1626261131)

    johansson_geometry = Setting(0)
    johansson_radius = Setting(0)

    asymmetric_cut = Setting(0)
    planes_angle = Setting(0)
    below_onto_bragg_planes = Setting(-1)

    ##########################################
    # ADVANCED SETTING
    ##########################################

    modified_surface = Setting(0)

    # surface error
    ms_type_of_defect = Setting(0)
    ms_defect_file_name = Setting(NONE_SPECIFIED)
    ms_ripple_wavel_x = Setting(0)
    ms_ripple_wavel_y = Setting(0)
    ms_ripple_ampli_x = Setting(0)
    ms_ripple_ampli_y = Setting(0)
    ms_ripple_phase_x = Setting(0)
    ms_ripple_phase_y = Setting(0)

    # faceted surface
    ms_file_facet_descr = Setting(NONE_SPECIFIED)
    ms_lattice_type = Setting(0)
    ms_orientation = Setting(0)
    ms_intercept_to_use = Setting(0)
    ms_facet_width_x = Setting(10)
    ms_facet_phase_x = Setting(0)
    ms_dead_with_x_minus = Setting(0)
    ms_dead_width_x_plus = Setting(0)
    ms_facet_width_y = Setting(10)
    ms_facet_phase_y = Setting(0)
    ms_dead_with_y_minus = Setting(0)
    ms_dead_width_y_plus = Setting(0)

    # surface roughness
    ms_file_surf_roughness = Setting(NONE_SPECIFIED)
    ms_roughness_rms_x = Setting(0)
    ms_roughness_rms_y = Setting(0)

    # kumakhov lens
    ms_specify_r2 = Setting(0)
    ms_file_with_parameters_rz = Setting(NONE_SPECIFIED)
    ms_file_with_parameters_rz2 = Setting(NONE_SPECIFIED)
    ms_save_intercept_bounces = Setting(0)

    # segmented mirror
    ms_number_of_segments_x = Setting(1)
    ms_number_of_segments_y = Setting(1)
    ms_length_of_segments_x = Setting(0)
    ms_length_of_segments_y = Setting(0)
    ms_file_orientations = Setting(NONE_SPECIFIED)
    ms_file_polynomial = Setting(NONE_SPECIFIED)

    #####

    mirror_movement = Setting(0)

    mm_mirror_offset_x = Setting(0)
    mm_mirror_rotation_x = Setting(0)
    mm_mirror_offset_y = Setting(0)
    mm_mirror_rotation_y = Setting(0)
    mm_mirror_offset_z = Setting(0)
    mm_mirror_rotation_z = Setting(0)

    #####

    source_movement = Setting(0)
    sm_angle_of_incidence = Setting(0)
    sm_distance_from_mirror = Setting(0)
    sm_z_rotation = Setting(0)
    sm_offset_x_mirr_ref_frame = Setting(0)
    sm_offset_y_mirr_ref_frame = Setting(0)
    sm_offset_z_mirr_ref_frame = Setting(0)
    sm_offset_x_source_ref_frame = Setting(0)
    sm_offset_y_source_ref_frame = Setting(0)
    sm_offset_z_source_ref_frame = Setting(0)
    sm_rotation_around_x = Setting(0)
    sm_rotation_around_y = Setting(0)
    sm_rotation_around_z = Setting(0)

    #####

    file_to_write_out = Setting(3)
    write_out_inc_ref_angles = Setting(0)

    ##########################################
    # SCREEN/SLITS
    ##########################################

    exit_slit = Setting(0)
    es_slit_length = Setting(0)
    es_slit_width = Setting(0)
    es_slit_tilt = Setting(0)

    want_main_area=1

    def __init__(self, graphical_options = GraphicalOptions()):
        super().__init__()

        #TODO VERIFICARE LA POSSIBILITA DI CAMBIARE L'ALLINEAMTO DEI BOX E QUINDI EVITARE GLI HIDDEN

        self.graphical_options = graphical_options

        self.controlArea.setFixedWidth(500)

        upper_box = gui.widgetBox(self.controlArea, "Optical Element Orientation", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(upper_box, self, "source_plane_distance", "Source Plane Distance [cm]", tooltip="Source Plane Distance [cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(upper_box, self, "image_plane_distance", "Image Plane Distance [cm]", tooltip="Image Plane Distance [cm]", valueType=float, orientation="horizontal")

        if not self.graphical_options.is_screen_slit:
            incidence_angle_mrad = self.calculate_incidence_angle_mrad()
            reflection_angle_mrad = self.calculate_reflection_angle_mrad()

            ShadowGui.lineEdit(upper_box, self, "incidence_angle_deg", "Incident Angle respect to the normal [deg]", callback=self.calculate_incidence_angle_mrad, tooltip="Incident Angle respect to the normal [deg]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(upper_box, self, "incidence_angle_mrad", "... or with respect to the surface [mrad]", callback=self.calculate_incidence_angle_deg, tooltip="... or with respect to the surface [mrad]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(upper_box, self, "reflection_angle_deg", "Reflection Angle respect to the normal [deg]", callback=self.calculate_reflection_angle_mrad, tooltip="Reflection Angle respect to the normal [deg]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(upper_box, self, "reflection_angle_mrad", "... or with respect to the surface [mrad]", callback=self.calculate_incidence_angle_deg, tooltip="... or with respect to the surface [mrad]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(upper_box, self, "mirror_orientation_angle", "Mirror Orientation Angle [deg]", tooltip="Mirror Orientation Angle [deg]", valueType=float, orientation="horizontal")

            tabs_setting = gui.tabWidget(self.controlArea)
            tabs_setting.setFixedHeight(530)

            gui.button(self.controlArea, self, "Run Shadow/trace", callback=self.traceOpticalElement)

            # graph tab
            tab_bas = gui.createTabPage(tabs_setting, "Basic Setting")
            tab_adv = gui.createTabPage(tabs_setting, "Advanced Setting")
            tab_scr = gui.createTabPage(tabs_setting, "Exit Slits")

            tabs_basic_setting = gui.tabWidget(tab_bas)

            if self.graphical_options.is_curved: tab_bas_shape = gui.createTabPage(tabs_basic_setting, "Surface Shape")
            if self.graphical_options.is_mirror: tab_bas_refl = gui.createTabPage(tabs_basic_setting, "Reflectivity")
            else: tab_bas_crystal = gui.createTabPage(tabs_basic_setting, "Crystal")
            tab_bas_dim = gui.createTabPage(tabs_basic_setting, "Dimensions")

            ##########################################
            #
            # TAB 1.1 - SURFACE SHAPE
            #
            ##########################################


            if graphical_options.is_curved:
                surface_box = gui.widgetBox(tab_bas_shape, "Surface Shape Parameter", addSpace=False, orientation="vertical")
                surface_box.setFixedHeight(self.ONE_ROW_HEIGHT)
                gui.comboBox(surface_box, self, "surface_shape_parameters", label="Type", items=["internal/calculated", "external/user_defined"], callback=self.set_IntExt_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.surface_box_ext = gui.widgetBox(tab_bas_shape, " ", addSpace=False, orientation="vertical")

                if self.graphical_options.is_spheric:
                    self.surface_box_ext.setFixedHeight(self.ONE_ROW_HEIGHT)

                    ShadowGui.lineEdit(self.surface_box_ext, self, "spherical_radius", "Spherical Radius [cm]", valueType=float, orientation="horizontal")
                elif self.graphical_options.is_toroidal:
                    self.surface_box_ext.setFixedHeight(self.TWO_ROW_HEIGHT)
                    ShadowGui.lineEdit(self.surface_box_ext, self, "torus_major_radius", "Torus Major Radius [cm]", valueType=float, orientation="horizontal")
                    ShadowGui.lineEdit(self.surface_box_ext, self, "torus_minor_radius", "Torus Minor Radius [cm]", valueType=float, orientation="horizontal")


                self.surface_box_int = gui.widgetBox(tab_bas_shape, " ", addSpace=False, orientation="vertical")
                self.surface_box_int.setFixedHeight(self.ONE_ROW_HEIGHT)

                gui.comboBox(self.surface_box_int, self, "focii_and_continuation_plane", label="Focii and Continuation Plane", items=["Coincident", "Different"], callback=self.set_FociiCont_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.surface_box_int_2 = gui.widgetBox(tab_bas_shape, " ", addSpace=False, orientation="vertical")
                self.surface_box_int_2.setFixedHeight(self.TWO_ROW_HEIGHT)

                self.w_object_side_focal_distance = ShadowGui.lineEdit(self.surface_box_int_2, self, "object_side_focal_distance", "Object Side_Focal Distance [cm]", valueType=float, orientation="horizontal")
                self.w_image_side_focal_distance = ShadowGui.lineEdit(self.surface_box_int_2, self, "image_side_focal_distance", "Image Side_Focal Distance [cm]", valueType=float, orientation="horizontal")
                self.w_incidence_angle_respect_to_normal = ShadowGui.lineEdit(self.surface_box_int_2, self, "incidence_angle_respect_to_normal", "Incidence Angle Respect to Normal [deg]", valueType=float, orientation="horizontal")

                self.surface_box_int_ext_hidden = gui.widgetBox(tab_bas_shape, "", addSpace=False, orientation="vertical")

                if self.graphical_options.is_spheric:
                    self.surface_box_int_ext_hidden.setFixedHeight(self.TWO_ROW_HEIGHT)
                elif self.graphical_options.is_toroidal:
                    self.surface_box_int_ext_hidden.setFixedHeight(self.ONE_ROW_HEIGHT)

                self.set_IntExt_Parameters()

                if self.graphical_options.is_toroidal:
                    surface_box_thorus = gui.widgetBox(tab_bas_shape, " ", addSpace=False, orientation="vertical")
                    surface_box_thorus.setFixedHeight(self.ONE_ROW_HEIGHT)

                    gui.comboBox(surface_box_thorus, self, "toroidal_mirror_pole_location", label="Torus pole location", \
                                 items=["lower/outer (concave/concave)", \
                                        "lower/inner (concave/convex)", \
                                        "upper/inner (convex/concave)", \
                                        "upper/outer (convex/convex)"], \
                                 sendSelectedValue=False, orientation="horizontal")
                else:
                    surface_box_thorus_hidden = gui.widgetBox(tab_bas_shape, "", addSpace=False, orientation="vertical")
                    surface_box_thorus_hidden.setFixedHeight(self.ONE_ROW_HEIGHT)

                surface_box_2 = gui.widgetBox(tab_bas_shape, "Cylinder Parameter", addSpace=False, orientation="vertical")
                surface_box_2.setFixedHeight(100)

                gui.comboBox(surface_box_2, self, "surface_curvature", label="Surface Curvature", items=["Concave", "Convex"], sendSelectedValue=False, orientation="horizontal")
                gui.comboBox(surface_box_2, self, "is_cylinder", label="Cylindrical", items=["No", "Yes"], callback=self.set_isCyl_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.surface_box_cyl = gui.widgetBox(tab_bas_shape, " ", addSpace=False, orientation="vertical")
                self.surface_box_cyl.setFixedHeight(self.ONE_ROW_HEIGHT)

                ShadowGui.lineEdit(self.surface_box_cyl, self, "cylinder_orientation", "Cylinder Orientation (deg) [CCW from X axis]", valueType=float, orientation="horizontal")

                self.surface_box_cyl_hidden = gui.widgetBox(tab_bas_shape, "", addSpace=False, orientation="vertical")
                self.surface_box_cyl_hidden.setFixedHeight(60)

                self.set_isCyl_Parameters()

            ##########################################
            #
            # TAB 1.2 - REFLECTIVITY/CRYSTAL
            #
            ##########################################

            if self.graphical_options.is_mirror:
                refl_box = gui.widgetBox(tab_bas_refl, "Reflectivity Parameter", addSpace=False, orientation="vertical")
                refl_box.setFixedHeight(self.ONE_ROW_HEIGHT)

                gui.comboBox(refl_box, self, "reflectivity_type", label="Reflectivity", \
                             items=["Not considered", "Full Polarization dependence", "No Polarization dependence (scalar)"], \
                             callback=self.set_Refl_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.refl_box_pol_hidden = gui.widgetBox(tab_bas_refl, "", addSpace=False, orientation="vertical")
                self.refl_box_pol_hidden.setFixedHeight(175)

                self.refl_box_pol = gui.widgetBox(tab_bas_refl, " ", addSpace=False, orientation="vertical")
                self.refl_box_pol.setFixedHeight(self.ONE_ROW_HEIGHT)

                gui.comboBox(self.refl_box_pol, self, "source_of_reflectivity", label="Source of Reflectivity", \
                             items=["file generated by PREREFL", "electric susceptibility", "file generated by pre_mlayer"], \
                             callback=self.set_ReflSource_Parameters, sendSelectedValue=False, orientation="horizontal")

                self.refl_box_pol_1 = gui.widgetBox(tab_bas_refl, " ", addSpace=False, orientation="vertical")
                self.refl_box_pol_1.setFixedHeight(self.ONE_ROW_HEIGHT)

                ShadowGui.lineEdit(self.refl_box_pol_1, self, "file_prerefl", "File Name", valueType=str, orientation="horizontal")

                self.refl_box_pol_1_hidden = gui.widgetBox(tab_bas_refl, "", addSpace=False, orientation="vertical")
                self.refl_box_pol_1_hidden.setFixedHeight(30)

                self.refl_box_pol_2 = gui.widgetBox(tab_bas_refl, " ", addSpace=False, orientation="vertical")
                self.refl_box_pol_2.setFixedHeight(self.TWO_ROW_HEIGHT)

                ShadowGui.lineEdit(self.refl_box_pol_2, self, "alpha", "Alpha [epsilon=(1-alpha)+i gamma]", valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.refl_box_pol_2, self, "gamma", "Gamma [epsilon=(1-alpha)+i gamma]", valueType=float, orientation="horizontal")

                self.refl_box_pol_3 = gui.widgetBox(tab_bas_refl, " ", addSpace=False, orientation="vertical")
                self.refl_box_pol_3.setFixedHeight(self.TWO_ROW_HEIGHT)

                ShadowGui.lineEdit(self.refl_box_pol_3, self, "file_prerefl_m", "File Name", valueType=str, orientation="horizontal")
                gui.comboBox(self.refl_box_pol_3, self, "m_layer_tickness", label="Mlayer thickness vary as cosine", \
                             items=["No", "Yes"], \
                             sendSelectedValue=False, orientation="horizontal")

                self.set_Refl_Parameters()

                self.refl_box_hidden = gui.widgetBox(tab_bas_refl, "", addSpace=False, orientation="vertical")
                self.refl_box_hidden.setFixedHeight(280)
            else:
                tabs_crystal_setting = gui.tabWidget(tab_bas_crystal)

                tab_cryst_1 = gui.createTabPage(tabs_crystal_setting, "Diffraction Settings")
                tab_cryst_2 = gui.createTabPage(tabs_crystal_setting, "Geometric Setting")

                crystal_file_box = gui.widgetBox(tab_cryst_1, " ", addSpace=False, orientation="vertical")
                crystal_file_box.setFixedHeight(self.ONE_ROW_HEIGHT)

                ShadowGui.lineEdit(crystal_file_box, self, "file_crystal_parameters", "File with crystal parameters", valueType=str, orientation="horizontal")

                autosetting_box = gui.widgetBox(tab_cryst_1, " ", addSpace=False, orientation="vertical")
                autosetting_box.setFixedHeight(self.ONE_ROW_HEIGHT)

                gui.comboBox(autosetting_box, self, "crystal_auto_setting", label="Auto setting", \
                             items=["No", "Yes"], \
                             callback=self.set_Autosetting, sendSelectedValue=False, orientation="horizontal")

                self.autosetting_box_hidden = gui.widgetBox(tab_cryst_1, "", addSpace=False, orientation="vertical")
                self.autosetting_box_hidden.setFixedHeight(175)

                self.autosetting_box_units = gui.widgetBox(tab_cryst_1, " ", addSpace=False, orientation="vertical")
                self.autosetting_box_units.setFixedHeight(self.ONE_ROW_HEIGHT)

                gui.comboBox(self.autosetting_box_units, self, "units_in_use", label="Units in use", \
                             items=["eV", "Angstroms"], \
                             callback=self.set_UnitsInUse, sendSelectedValue=False, orientation="horizontal")

                self.autosetting_box_units_1 = gui.widgetBox(tab_cryst_1, " ", addSpace=False, orientation="vertical")
                self.autosetting_box_units_1.setFixedHeight(self.ONE_ROW_HEIGHT)

                ShadowGui.lineEdit(self.autosetting_box_units_1, self, "photon_energy", "Set photon energy [eV]", valueType=float, orientation="horizontal")

                self.autosetting_box_units_2 = gui.widgetBox(tab_cryst_1, " ", addSpace=False, orientation="vertical")
                self.autosetting_box_units_2.setFixedHeight(self.ONE_ROW_HEIGHT)

                ShadowGui.lineEdit(self.autosetting_box_units_2, self, "photon_wavelength", "Set wavelength [Å]", valueType=float, orientation="horizontal")

                self.set_Autosetting()

                crystal_box_hidden = gui.widgetBox(tab_cryst_1, "", addSpace=False, orientation="vertical")
                crystal_box_hidden.setFixedHeight(230)

                mosaic_box = gui.widgetBox(tab_cryst_2, " ", addSpace=False, orientation="vertical")
                mosaic_box.setFixedHeight(self.ONE_ROW_HEIGHT)

                gui.comboBox(mosaic_box, self, "mosaic_crystal", label="Mosaic Crystal", \
                             items=["No", "Yes"], \
                             callback=self.set_Mosaic, sendSelectedValue=False, orientation="horizontal")

                self.asymmetric_cut_box = gui.widgetBox(tab_cryst_2, " ", addSpace=False, orientation="vertical")
                self.asymmetric_cut_box.setFixedHeight(self.ONE_ROW_HEIGHT)

                gui.comboBox(self.asymmetric_cut_box, self, "asymmetric_cut", label="Asymmetric cut", \
                             items=["No", "Yes"], \
                             callback=self.set_AsymmetricCut, sendSelectedValue=False, orientation="horizontal")

                self.asymmetric_cut_box_1 = gui.widgetBox(tab_cryst_2, " ", addSpace=False, orientation="vertical")
                self.asymmetric_cut_box_1.setFixedHeight(self.THREE_ROW_HEIGHT)

                ShadowGui.lineEdit(self.asymmetric_cut_box_1, self, "planes_angle", "Planes angle [deg]", valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.asymmetric_cut_box_1, self, "below_onto_bragg_planes", "Below[-1]/onto[1] bragg planes", valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.asymmetric_cut_box_1, self, "thickness", "Thickness [cm]", valueType=float, orientation="horizontal")

                self.asymmetric_cut_box_1_hidden = gui.widgetBox(tab_cryst_2, "", addSpace=False, orientation="vertical")
                self.asymmetric_cut_box_1_hidden.setFixedHeight(self.THREE_ROW_HEIGHT+55)

                self.johansson_box = gui.widgetBox(tab_cryst_2, " ", addSpace=False, orientation="vertical")
                self.johansson_box.setFixedHeight(self.ONE_ROW_HEIGHT)

                gui.comboBox(self.johansson_box, self, "johansson_geometry", label="Johansson Geometry", \
                             items=["No", "Yes"], \
                             callback=self.set_JohanssonGeometry, sendSelectedValue=False, orientation="horizontal")

                self.johansson_box_1 = gui.widgetBox(tab_cryst_2, " ", addSpace=False, orientation="vertical")
                self.johansson_box_1.setFixedHeight(self.ONE_ROW_HEIGHT)

                ShadowGui.lineEdit(self.johansson_box_1, self, "johansson_radius", "Johansson radius", valueType=float, orientation="horizontal")

                self.johansson_box_1_hidden = gui.widgetBox(tab_cryst_2, "", addSpace=False, orientation="vertical")
                self.johansson_box_1_hidden.setFixedHeight(self.ONE_ROW_HEIGHT)

                self.mosaic_box_1 = gui.widgetBox(tab_cryst_2, " ", addSpace=False, orientation="vertical")
                self.mosaic_box_1.setFixedHeight(self.THREE_ROW_HEIGHT)

                ShadowGui.lineEdit(self.mosaic_box_1, self, "angle_spread_FWHM", "Angle spread FWHM [deg]", valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.mosaic_box_1, self, "thickness", "Thickness [cm]", valueType=float, orientation="horizontal")
                ShadowGui.lineEdit(self.mosaic_box_1, self, "seed_for_mosaic", "Seed for mosaic [>10^5]", valueType=float, orientation="horizontal")

                self.mosaic_box_1_hidden = gui.widgetBox(tab_cryst_2, "", addSpace=False, orientation="vertical")
                self.mosaic_box_1_hidden.setFixedHeight(200)

                self.set_Mosaic()

            ##########################################
            #
            # TAB 1.3 - DIMENSIONS
            #
            ##########################################

            dimension_box = gui.widgetBox(tab_bas_dim, "Dimensions", addSpace=False, orientation="vertical")
            dimension_box.setFixedHeight(self.ONE_ROW_HEIGHT)

            gui.comboBox(dimension_box, self, "is_infinite", label="Limits Check", \
                         items=["Infinite o.e. dimensions", "Finite o.e. dimensions"], \
                         callback=self.set_Dim_Parameters, sendSelectedValue=False, orientation="horizontal")

            self.dimdet_box_hidden = gui.widgetBox(tab_bas_dim, "", addSpace=False, orientation="vertical")
            self.dimdet_box_hidden.setFixedHeight(self.THREE_ROW_HEIGHT)

            self.dimdet_box = gui.widgetBox(tab_bas_dim, " ", addSpace=False, orientation="vertical")
            self.dimdet_box.setFixedHeight(self.THREE_ROW_HEIGHT)

            gui.comboBox(self.dimdet_box, self, "mirror_shape", label="Limits Check", \
                         items=["Rectangular", "Full ellipse", "Ellipse with hole"], \
                         sendSelectedValue=False, orientation="horizontal")

            ShadowGui.lineEdit(self.dimdet_box, self, "dim_x_plus", "X(+) Half Width / Int Maj Ax [cm]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.dimdet_box, self, "dim_x_minus", "X(-) Half Width / Int Maj Ax [cm]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.dimdet_box, self, "dim_y_plus", "Y(+) Half Width / Int Min Ax [cm]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.dimdet_box, self, "dim_y_minus", "Y(-) Half Width / Int Min Ax [cm]", valueType=float, orientation="horizontal")

            self.set_Dim_Parameters()

            self.dimension_box_hidden = gui.widgetBox(tab_bas_dim, "", addSpace=False, orientation="vertical")
            self.dimension_box_hidden.setFixedHeight(220)

            ##########################################
            ##########################################
            # ADVANCED SETTINGS
            ##########################################
            ##########################################

            tabs_advanced_setting = gui.tabWidget(tab_adv)

            tab_adv_mod_surf = gui.createTabPage(tabs_advanced_setting, "Modified Surface")
            tab_adv_mir_mov = gui.createTabPage(tabs_advanced_setting, "Mirror Movement")
            tab_adv_sou_mov = gui.createTabPage(tabs_advanced_setting, "Source Movement")
            tab_adv_misc = gui.createTabPage(tabs_advanced_setting, "Other")

            ##########################################
            #
            # TAB 2.1 - Modified Surface
            #
            ##########################################

            mod_surf_box = gui.widgetBox(tab_adv_mod_surf, " ", addSpace=False, orientation="vertical")
            mod_surf_box.setFixedHeight(self.ONE_ROW_HEIGHT)

            gui.comboBox(mod_surf_box, self, "modified_surface", label="Modified Surface", \
                         items=["None", "Surface Error", "Faceted Surface", "Surface Roughness", "Kumakhov Lens", "Segmented Mirror"], \
                         callback=self.set_ModifiedSurface, sendSelectedValue=False, orientation="horizontal")

            # NONE

            self.mod_surf_box_hidden =  gui.widgetBox(tab_adv_mod_surf, "", addSpace=False, orientation="vertical")
            self.mod_surf_box_hidden.setFixedHeight(400)

            # SURFACE ERROR

            self.type_of_defect_box = gui.widgetBox(tab_adv_mod_surf, " ", addSpace=False, orientation="vertical")
            self.type_of_defect_box.setFixedHeight(self.ONE_ROW_HEIGHT)

            gui.comboBox(self.type_of_defect_box, self, "ms_type_of_defect", label="Type of Defect", \
                         items=["sinusoidal", "gaussian", "external spline"], \
                         callback=self.set_TypeOfDefect, sendSelectedValue=False, orientation="horizontal")

            self.mod_surf_box_1 = gui.widgetBox(tab_adv_mod_surf, " ", addSpace=False, orientation="vertical")
            self.mod_surf_box_1.setFixedHeight(self.ONE_ROW_HEIGHT)

            ShadowGui.lineEdit(self.mod_surf_box_1, self, "ms_defect_file_name", "File name", valueType=str, orientation="horizontal")

            self.mod_surf_box_1_hidden =  gui.widgetBox(tab_adv_mod_surf, "", addSpace=False, orientation="vertical")
            self.mod_surf_box_1_hidden.setFixedHeight(300)

            self.mod_surf_box_2 = gui.widgetBox(tab_adv_mod_surf, " ", addSpace=False, orientation="vertical")
            self.mod_surf_box_2.setFixedHeight(200)

            ShadowGui.lineEdit(self.mod_surf_box_2, self, "ms_ripple_wavel_x", "Ripple Wavel. X", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_box_2, self, "ms_ripple_wavel_y", "Ripple Wavel. Y", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_box_2, self, "ms_ripple_ampli_x", "Ripple Ampli. X", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_box_2, self, "ms_ripple_ampli_y", "Ripple Ampli. Y", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_box_2, self, "ms_ripple_phase_x", "Ripple Phase X", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mod_surf_box_2, self, "ms_ripple_phase_y", "Ripple Phase Y", valueType=float, orientation="horizontal")

            self.mod_surf_box_2_hidden =  gui.widgetBox(tab_adv_mod_surf, "", addSpace=False, orientation="vertical")
            self.mod_surf_box_2_hidden.setFixedHeight(145)

            ####

            self.set_ModifiedSurface()

            ##########################################
            #
            # TAB 2.2 - Mirror Movement
            #
            ##########################################

            mir_mov_box = gui.widgetBox(tab_adv_mir_mov, " ", addSpace=False, orientation="vertical")
            mir_mov_box.setFixedHeight(self.ONE_ROW_HEIGHT)

            gui.comboBox(mir_mov_box, self, "mirror_movement", label="Mirror Movement", \
                         items=["No", "Yes"], \
                         callback=self.set_MirrorMovement, sendSelectedValue=False, orientation="horizontal")

            self.mir_mov_box_hidden =  gui.widgetBox(tab_adv_mir_mov, "", addSpace=False, orientation="vertical")
            self.mir_mov_box_hidden.setFixedHeight(400)

            self.mir_mov_box_1 = gui.widgetBox(tab_adv_mir_mov, " ", addSpace=False, orientation="vertical")
            self.mir_mov_box_1.setFixedHeight(200)

            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_offset_x", "Mirror Offset X", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_rotation_x", "Mirror Rotation X", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_offset_y", "Mirror Offset Y", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_rotation_y", "Mirror Rotation Z", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_offset_z", "Mirror Offset Z", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.mir_mov_box_1, self, "mm_mirror_rotation_z", "Mirror Rotation Z", valueType=float, orientation="horizontal")

            self.mir_mov_box_1_hidden =  gui.widgetBox(tab_adv_mir_mov, "", addSpace=False, orientation="vertical")
            self.mir_mov_box_1_hidden.setFixedHeight(200)

            self.set_MirrorMovement()

           ##########################################
            #
            # TAB 2.3 - Source Movement
            #
            ##########################################

            sou_mov_box = gui.widgetBox(tab_adv_sou_mov, " ", addSpace=False, orientation="vertical")
            sou_mov_box.setFixedHeight(self.ONE_ROW_HEIGHT)

            gui.comboBox(sou_mov_box, self, "source_movement", label="Source Movement", \
                         items=["No", "Yes"], \
                         callback=self.set_SourceMovement, sendSelectedValue=False, orientation="horizontal")

            self.sou_mov_box_hidden =  gui.widgetBox(tab_adv_sou_mov, "", addSpace=False, orientation="vertical")
            self.sou_mov_box_hidden.setFixedHeight(400)

            self.sou_mov_box_1 = gui.widgetBox(tab_adv_sou_mov, " ", addSpace=False, orientation="vertical")
            self.sou_mov_box_1.setFixedHeight(350)

            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_angle_of_incidence", "Angle of Incidence [deg]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_distance_from_mirror", "Distance from mirror [cm]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_z_rotation", "Z-rotation [deg]", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_x_mirr_ref_frame", "offset X [cm] in MIRROR reference frame", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_y_mirr_ref_frame", "offset Y [cm] in MIRROR reference frame", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_z_mirr_ref_frame", "offset Z [cm] in MIRROR reference frame", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_x_mirr_ref_frame", "offset X [cm] in MIRROR reference frame", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_y_mirr_ref_frame", "offset Y [cm] in MIRROR reference frame", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_offset_z_mirr_ref_frame", "offset Z [cm] in MIRROR reference frame", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_rotation_around_x", "rotation [CCW, deg] around X", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_rotation_around_y", "rotation [CCW, deg] around Y", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.sou_mov_box_1, self, "sm_rotation_around_z", "rotation [CCW, deg] around Z", valueType=float, orientation="horizontal")

            self.sou_mov_box_1_hidden =  gui.widgetBox(tab_adv_sou_mov, "", addSpace=False, orientation="vertical")
            self.sou_mov_box_1_hidden.setFixedHeight(50)

            self.set_SourceMovement()

            ##########################################
            #
            # TAB 2.4 - Other
            #
            ##########################################

            adv_other_box = gui.widgetBox(tab_adv_misc, "Optional file output", addSpace=False, orientation="vertical")
            adv_other_box.setFixedHeight(self.TWO_ROW_HEIGHT)

            gui.comboBox(adv_other_box, self, "file_to_write_out", label="Files to write out", \
                         items=["All", "Mirror", "Image", "None"], \
                         sendSelectedValue=False, orientation="horizontal")

            gui.comboBox(adv_other_box, self, "write_out_inc_ref_angles", label="Write out Incident/Reflected angles [angle.xx]", \
                         items=["No", "Yes"], \
                         sendSelectedValue=False, orientation="horizontal")

            self.adv_other_box_hidden =  gui.widgetBox(tab_adv_misc, "", addSpace=False, orientation="vertical")
            self.adv_other_box_hidden.setFixedHeight(350)

            ##########################################
            ##########################################
            # SLITS
            ##########################################
            ##########################################

            exit_slit_box = gui.widgetBox(tab_scr, " ", addSpace=False, orientation="vertical")
            exit_slit_box.setFixedHeight(self.ONE_ROW_HEIGHT)

            gui.comboBox(exit_slit_box, self, "exit_slit", label="Exit Slit", \
                         items=["No", "Yes"], \
                         callback=self.set_ExitSlit, sendSelectedValue=False, orientation="horizontal")

            self.exit_slit_box_hidden =  gui.widgetBox(tab_scr, "", addSpace=False, orientation="vertical")
            self.exit_slit_box_hidden.setFixedHeight(420)

            self.exit_slit_box_1 = gui.widgetBox(tab_scr, " ", addSpace=False, orientation="vertical")
            self.exit_slit_box_1.setFixedHeight(self.THREE_ROW_HEIGHT)

            ShadowGui.lineEdit(self.exit_slit_box_1, self, "es_slit_length", "Slit Length (Sagittal)", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.exit_slit_box_1, self, "es_slit_width", "Slit Width (Tangential)", valueType=float, orientation="horizontal")
            ShadowGui.lineEdit(self.exit_slit_box_1, self, "es_slit_tilt", "Slit Tilt (CCW, deg)", valueType=float, orientation="horizontal")

            self.exit_slit_box_1_hidden =  gui.widgetBox(tab_scr, "", addSpace=False, orientation="vertical")
            self.exit_slit_box_1_hidden.setFixedHeight(250)

            self.set_ExitSlit()

    ############################################################
    #
    # GRAPHIC USER INTERFACE MANAGEMENT
    #
    ############################################################

    def set_ExitSlit(self):
        if self.exit_slit == 0:
            self.exit_slit_box_hidden.setVisible(True)
            self.exit_slit_box_1.setVisible(False)
            self.exit_slit_box_1_hidden.setVisible(False)
        else:
            self.exit_slit_box_hidden.setVisible(False)
            self.exit_slit_box_1.setVisible(True)
            self.exit_slit_box_1_hidden.setVisible(True)

    def set_SourceMovement(self):
        if self.source_movement == 0:
            self.sou_mov_box_hidden.setVisible(True)
            self.sou_mov_box_1.setVisible(False)
            self.sou_mov_box_1_hidden.setVisible(False)
        else:
            self.sou_mov_box_hidden.setVisible(False)
            self.sou_mov_box_1.setVisible(True)
            self.sou_mov_box_1_hidden.setVisible(True)

    def set_MirrorMovement(self):
        if self.mirror_movement == 0:
            self.mir_mov_box_hidden.setVisible(True)
            self.mir_mov_box_1.setVisible(False)
            self.mir_mov_box_1_hidden.setVisible(False)
        else:
            self.mir_mov_box_hidden.setVisible(False)
            self.mir_mov_box_1.setVisible(True)
            self.mir_mov_box_1_hidden.setVisible(True)
        
    def set_TypeOfDefect(self):
        if self.ms_type_of_defect == 0:
           self.mod_surf_box_1.setVisible(False)
           self.mod_surf_box_1_hidden.setVisible(False)
           self.mod_surf_box_2.setVisible(True)
           self.mod_surf_box_2_hidden.setVisible(True)
        else:
           self.mod_surf_box_1.setVisible(True)
           self.mod_surf_box_1_hidden.setVisible(True)
           self.mod_surf_box_2.setVisible(False)
           self.mod_surf_box_2_hidden.setVisible(False)

    def set_ModifiedSurface(self):
        if self.modified_surface == 0:
            self.mod_surf_box_hidden.setVisible(True)
            self.type_of_defect_box.setVisible(False)
            self.mod_surf_box_1.setVisible(False)
            self.mod_surf_box_1_hidden.setVisible(False)
            self.mod_surf_box_2.setVisible(False)
            self.mod_surf_box_2_hidden.setVisible(False)
        elif self.modified_surface == 1:
            self.mod_surf_box_hidden.setVisible(False)
            self.type_of_defect_box.setVisible(True)
            self.set_TypeOfDefect()
        else:
            self.mod_surf_box_hidden.setVisible(True)
            self.type_of_defect_box.setVisible(False)
            self.mod_surf_box_1.setVisible(False)
            self.mod_surf_box_1_hidden.setVisible(False)
            self.mod_surf_box_2.setVisible(False)
            self.mod_surf_box_2_hidden.setVisible(False)

    # TAB 1.1

    def set_IntExt_Parameters(self):
        if self.surface_shape_parameters == 0:
            self.surface_box_int.setVisible(True)
            self.set_FociiCont_Parameters()

            self.surface_box_ext.setVisible(False)
        else:
            self.surface_box_int.setVisible(False)
            self.surface_box_int_2.setVisible(False)

            self.surface_box_ext.setVisible(True)
            self.surface_box_int_ext_hidden.setVisible(True)

    def set_FociiCont_Parameters(self):
        if self.focii_and_continuation_plane == 0:
            self.surface_box_int_2.setVisible(False)
            self.surface_box_int_ext_hidden.setVisible(True)
        else:
            self.surface_box_int_2.setVisible(True)
            self.surface_box_int_ext_hidden.setVisible(False)

    def set_isCyl_Parameters(self):
        if self.is_cylinder == 0:
            self.surface_box_cyl.setVisible(False)
            self.surface_box_cyl_hidden.setVisible(True)
        else:
            self.surface_box_cyl.setVisible(True)
            self.surface_box_cyl_hidden.setVisible(False)

    # TAB 1.2

    def set_Refl_Parameters(self):
        if self.reflectivity_type == 0:
            self.refl_box_pol_hidden.setVisible(True)
            self.refl_box_pol.setVisible(False)
            self.refl_box_pol_1.setVisible(False)
            self.refl_box_pol_1_hidden.setVisible(False)
            self.refl_box_pol_2.setVisible(False)
            self.refl_box_pol_3.setVisible(False)
        else:
            self.refl_box_pol_hidden.setVisible(False)
            self.refl_box_pol.setVisible(True)
            self.set_ReflSource_Parameters()

    def set_ReflSource_Parameters(self):
        if self.source_of_reflectivity == 0:
            self.refl_box_pol_1.setVisible(True)
            self.refl_box_pol_1_hidden.setVisible(True)
            self.refl_box_pol_2.setVisible(False)
            self.refl_box_pol_3.setVisible(False)
        elif self.source_of_reflectivity == 1:
            self.refl_box_pol_1.setVisible(False)
            self.refl_box_pol_1_hidden.setVisible(False)
            self.refl_box_pol_2.setVisible(True)
            self.refl_box_pol_3.setVisible(False)
        elif self.source_of_reflectivity == 2:
            self.refl_box_pol_1.setVisible(False)
            self.refl_box_pol_1_hidden.setVisible(False)
            self.refl_box_pol_2.setVisible(False)
            self.refl_box_pol_3.setVisible(True)

    def set_Autosetting(self):
        if self.crystal_auto_setting == 0:
            self.autosetting_box_hidden.setVisible(True)
            self.autosetting_box_units.setVisible(False)
            self.autosetting_box_units_1.setVisible(False)
            self.autosetting_box_units_2.setVisible(False)
        else:
            self.autosetting_box_hidden.setVisible(False)
            self.autosetting_box_units.setVisible(True)
            self.set_UnitsInUse()

    def set_UnitsInUse(self):
        if self.units_in_use == 0:
            self.autosetting_box_units_1.setVisible(True)
            self.autosetting_box_units_2.setVisible(False)
        else:
            self.autosetting_box_units_1.setVisible(False)
            self.autosetting_box_units_2.setVisible(True)

    def set_Mosaic(self):
        if self.mosaic_crystal == 0:
            self.mosaic_box_1.setVisible(False)
            self.mosaic_box_1_hidden.setVisible(False)
            self.asymmetric_cut_box.setVisible(True)
            self.set_AsymmetricCut()
            self.johansson_box.setVisible(True)
            self.set_JohanssonGeometry()
        else:
            self.mosaic_box_1.setVisible(True)
            self.mosaic_box_1_hidden.setVisible(True)
            self.asymmetric_cut_box.setVisible(False)
            self.asymmetric_cut_box_1.setVisible(False)
            self.asymmetric_cut_box_1_hidden.setVisible(False)
            self.johansson_box.setVisible(False)
            self.johansson_box_1.setVisible(False)
            self.johansson_box_1_hidden.setVisible(False)

    def set_AsymmetricCut(self):
        if self.asymmetric_cut == 0:
            self.asymmetric_cut_box_1.setVisible(False)
            self.asymmetric_cut_box_1_hidden.setVisible(True)
        else:
            self.asymmetric_cut_box_1.setVisible(True)
            self.asymmetric_cut_box_1_hidden.setVisible(False)

    def set_JohanssonGeometry(self):
         if self.johansson_geometry == 0:
            self.johansson_box_1.setVisible(False)
            self.johansson_box_1_hidden.setVisible(True)
         else:
            self.johansson_box_1.setVisible(True)
            self.johansson_box_1_hidden.setVisible(False)

    # TAB 1.3

    def set_Dim_Parameters(self):
        if self.is_infinite == 0:
            self.dimdet_box_hidden.setVisible(True)
            self.dimdet_box.setVisible(False)
        else:
            self.dimdet_box_hidden.setVisible(False)
            self.dimdet_box.setVisible(True)


    def calculate_incidence_angle_mrad(self):
        self.incidence_angle_mrad = math.radians(90-self.incidence_angle_deg)*1000

    def calculate_reflection_angle_mrad(self):
        self.reflection_angle_mrad = math.radians(90-self.reflection_angle_deg)*1000

    def calculate_incidence_angle_deg(self):
        self.incidence_angle_deg = 90-math.degrees(self.incidence_angle_mrad/1000)

    def calculate_reflection_angle_deg(self):
        self.reflection_angle_mrad = 90-math.degrees(self.reflection_angle_mrad/1000)

    def populateFields(self, shadow_oe = Orange.shadow.ShadowOpticalElement.create_empty_oe()):

        #TODO eliminare exit-slits
        #TODO disabilitare angoli incidenza e uscita se autotuning del cristallo
        #TODO se elementi curvi con parametri calcolati si possono modificare i campi con i dati del file end.xx

        # per scrivere i campi calcolati

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
               if self.focii_and_continuation_plane == 0:
                  shadow_oe.oe.setAutoFocus(1)
               else:
                  shadow_oe.oe.setAutoFocus(f_default=0, \
                                            ssour=self.object_side_focal_distance, \
                                            simag=self.image_side_focal_distance, \
                                            theta=self.incidence_angle_respect_to_normal)
            else:
               shadow_oe.oe.FEXT=1
               if self.graphical_options.is_spheric:
                   shadow_oe.oe.RMIRR = self.spherical_radius
               elif self.graphical_options.is_toroidal:
                   shadow_oe.oe.RMAJ=self.torus_major_radius
                   shadow_oe.oe.RMIN=self.torus_minor_radius
               ### TODO ALTRE FORME ATTENZIONE!!!!!

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
                shadow_oe.oe.setDimensions(fshape=self.mirror_shape, \
                                           params=[self.dim_x_plus, self.dim_x_minus, self.dim_y_plus, self.dim_y_minus])

            #####################################
            # ADVANCED SETTING
            #####################################

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

            if self.exit_slit == 1:
                 shadow_oe.oe.FSLIT=1
                 shadow_oe.oe.SLLEN=self.es_slit_length
                 shadow_oe.oe.SLWID=self.es_slit_width
                 shadow_oe.oe.SLTILT=self.es_slit_tilt

    def doSpecificSetting(self, shadow_oe):
        return None

    def checkFields(self):
        return True

    def completeOperations(self, shadow_oe=None):

        self.information(0, "Running SHADOW")
        qApp.processEvents()

        sys.stdout = EmittingStream(textWritten=self.writeStdOut)
        grabber = TTYGrabber()
        grabber.start()

        self.progressBarSet(50)

        beam_out = Orange.shadow.ShadowBeam.trace_from_oe(self.input_beam, shadow_oe)

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

        if not self.input_beam == None:
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
        self.input_beam = beam

        if self.is_automatic_run:
           self.traceOpticalElement()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OpticalElement()
    ow.show()
    a.exec_()
    ow.saveSettings()