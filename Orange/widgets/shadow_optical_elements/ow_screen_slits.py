import sys
from numpy import array, zeros
import Orange
import Orange.shadow
from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication

import Shadow
from Orange.shadow.shadow_util import ShadowGui
from Orange.widgets.shadow_gui.ow_optical_element import OpticalElement, GraphicalOptions

class ScreenSlit(OpticalElement):

    name = "Screen-Slit"
    description = "Shadow OE: Screen/Slit"
    icon = "icons/screen_slits.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 6
    category = "Optical Elements"
    keywords = ["data", "file", "load", "read"]


    inputs = [("Input Beam", Orange.shadow.ShadowBeam, "setBeam")]

    outputs = [{"name":"Beam",
                "type":Orange.shadow.ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"}]

    aperturing = Setting(0)
    open_slit_solid_stop = Setting(0)
    aperture_shape = Setting(0)
    slit_width_xaxis = Setting(0)
    slit_height_zaxis = Setting(0)
    slit_center_xaxis = Setting(0)
    slit_center_zaxis = Setting(0)
    external_file_with_coordinate=Setting(OpticalElement.NONE_SPECIFIED)
    absorption = Setting(0)
    thickness = Setting(0)
    opt_const_file_name = Setting(OpticalElement.NONE_SPECIFIED)

    def __init__(self):
        graphical_Options=GraphicalOptions(is_screen_slit=True)

        super().__init__(graphical_Options)

        self.controlArea.setFixedHeight(800)

        box_aperturing = gui.widgetBox(self.controlArea, " ", addSpace=False, orientation="vertical")
        box_aperturing.setFixedHeight(OpticalElement.ONE_ROW_HEIGHT)

        gui.comboBox(box_aperturing, self, "aperturing", label="Aperturing", \
                     items=["No", "Yes"], \
                     callback=self.set_Aperturing, sendSelectedValue=False, orientation="horizontal")

        self.box_aperturing_1 = gui.widgetBox(self.controlArea, " ", addSpace=False, orientation="vertical")
        self.box_aperturing_1.setFixedHeight(OpticalElement.TWO_ROW_HEIGHT)

        gui.comboBox(self.box_aperturing_1, self, "open_slit_solid_stop", label="Open slit/Solid stop", \
                     items=["aperture/slit", "obstruction/stop"], \
                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(self.box_aperturing_1, self, "aperture_shape", label="Aperture shape", \
                     items=["Rectangular", "Ellipse", "External"], \
                     callback=self.set_ApertureShape, sendSelectedValue=False, orientation="horizontal")

        self.box_aperturing_1_hidden = gui.widgetBox(self.controlArea, "", addSpace=False, orientation="vertical")
        self.box_aperturing_1_hidden.setFixedHeight(373)

        self.box_aperturing_2 = gui.widgetBox(self.controlArea, " ", addSpace=False, orientation="vertical")
        self.box_aperturing_2.setFixedHeight(OpticalElement.ONE_ROW_HEIGHT)

        ShadowGui.lineEdit(self.box_aperturing_2, self, "external_file_with_coordinate", "External file with coordinate", valueType=str, orientation="horizontal")

        self.box_aperturing_2_hidden = gui.widgetBox(self.controlArea, "", addSpace=False, orientation="vertical")
        self.box_aperturing_2_hidden.setFixedHeight(OpticalElement.ONE_ROW_HEIGHT)

        self.box_aperturing_3 = gui.widgetBox(self.controlArea, " ", addSpace=False, orientation="vertical")
        self.box_aperturing_3.setFixedHeight(200)

        ShadowGui.lineEdit(self.box_aperturing_3, self, "slit_width_xaxis", "Slit width/x-axis", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_aperturing_3, self, "slit_height_zaxis", "Slit height/z-axis", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_aperturing_3, self, "slit_center_xaxis", "Slit center/x-axis", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_aperturing_3, self, "slit_center_zaxis", "Slit center/z-axis", valueType=float, orientation="horizontal")

        self.box_aperturing_3_hidden = gui.widgetBox(self.controlArea, "", addSpace=False, orientation="vertical")
        self.box_aperturing_3_hidden.setFixedHeight(195)

        self.set_Aperturing()

        box_absorption = gui.widgetBox(self.controlArea, " ", addSpace=False, orientation="vertical")
        box_absorption.setFixedHeight(OpticalElement.ONE_ROW_HEIGHT)

        gui.comboBox(box_absorption, self, "absorption", label="Absorption", \
                     items=["No", "Yes"], \
                     callback=self.set_Absorption, sendSelectedValue=False, orientation="horizontal")

        self.box_absorption_1 = gui.widgetBox(self.controlArea, " ", addSpace=False, orientation="vertical")
        self.box_absorption_1.setFixedHeight(OpticalElement.TWO_ROW_HEIGHT)

        ShadowGui.lineEdit(self.box_absorption_1, self, "thickness", "Thickness [cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.box_absorption_1, self, "opt_const_file_name", "Opt. const. file name", valueType=str, orientation="horizontal")

        self.box_absorption_1_hidden = gui.widgetBox(self.controlArea, "", addSpace=False, orientation="vertical")
        self.box_absorption_1_hidden.setFixedHeight(OpticalElement.TWO_ROW_HEIGHT-5)

        self.set_Absorption()

        box_hidden = gui.widgetBox(self.controlArea, "", addSpace=False, orientation="vertical")
        box_hidden.setFixedHeight(10)

        gui.button(self.controlArea, self, "Run Shadow/trace", callback=self.traceOpticalElement)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def set_ApertureShape(self):
        if self.aperture_shape == 2:
            self.box_aperturing_2.setVisible(True)
            self.box_aperturing_2_hidden.setVisible(False)
            self.box_aperturing_3.setVisible(False)
            self.box_aperturing_3_hidden.setVisible(True)
        else:
            self.box_aperturing_2.setVisible(False)
            self.box_aperturing_2_hidden.setVisible(True)
            self.box_aperturing_3.setVisible(True)
            self.box_aperturing_3_hidden.setVisible(False)

    def set_Aperturing(self):
        if self.aperturing == 0:
            self.box_aperturing_1.setVisible(False)
            self.box_aperturing_1_hidden.setVisible(True)
            self.box_aperturing_2.setVisible(False)
            self.box_aperturing_2_hidden.setVisible(False)
            self.box_aperturing_3.setVisible(False)
            self.box_aperturing_3_hidden.setVisible(False)
        else:
            self.box_aperturing_1.setVisible(True)
            self.box_aperturing_1_hidden.setVisible(False)
            self.set_ApertureShape()

    def set_Absorption(self):
        if self.absorption == 0:
            self.box_absorption_1.setVisible(False)
            self.box_absorption_1_hidden.setVisible(True)
        else:
            self.box_absorption_1.setVisible(True)
            self.box_absorption_1_hidden.setVisible(False)

    def instantiateShadowOE(self):
        return Orange.shadow.ShadowOpticalElement.create_screen_slit()

    def doSpecificSetting(self, shadow_oe):

        n_screen = 1
        i_screen = zeros(10)
        i_abs = zeros(10)
        i_slit = zeros(10)
        i_stop = zeros(10)
        k_slit = zeros(10)
        thick = zeros(10)
        file_abs = array(['', '', '', '', '', '', '', '', '', ''])
        rx_slit = zeros(10)
        rz_slit = zeros(10)
        sl_dis = zeros(10)
        file_src_ext = array(['', '', '', '', '', '', '', '', '', ''])
        cx_slit = zeros(10)
        cz_slit = zeros(10)

        i_abs[0] = self.absorption
        i_slit[0] = self.aperturing

        if self.aperturing == 1:
            i_stop[0] = self.open_slit_solid_stop
            k_slit[0] = self.aperture_shape

            if self.aperture_shape == 2:
                file_src_ext[0] = bytes(self.external_file_with_coordinate, 'utf-8')
            else:
                rx_slit[0] = self.slit_width_xaxis
                rz_slit[0] = self.slit_height_zaxis
                cx_slit[0] = self.slit_center_xaxis
                cz_slit[0] = self.slit_center_zaxis

        if self.absorption == 1:
            thick[0] = self.thickness
            file_abs[0] = bytes(self.opt_const_file_name, 'utf-8')

        shadow_oe.oe.setScreens(n_screen,
                                i_screen,
                                i_abs,
                                sl_dis,
                                i_slit,
                                i_stop,
                                k_slit,
                                thick,
                                file_abs,
                                rx_slit,
                                rz_slit,
                                cx_slit,
                                cz_slit,
                                file_src_ext)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = ScreenSlit()
    ow.show()
    a.exec_()
    ow.saveSettings()