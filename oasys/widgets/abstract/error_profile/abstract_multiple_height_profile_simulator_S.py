#!/usr/bin/env python
# -*- coding: utf-8 -*-
# #########################################################################
# Copyright (c) 2020, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2020. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

import os, sys

import numpy
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QSizePolicy
from PyQt5.QtGui import QTextCursor, QFont, QPalette, QColor, QPixmap
from srxraylib.metrology import profiles_simulation
from matplotlib import cm
from oasys.widgets.gui import FigureCanvas3D
from matplotlib.figure import Figure

from orangewidget import gui, widget
from orangewidget.settings import Setting

from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.widgets.gui import ConfirmDialog
from oasys.util.oasys_util import EmittingStream
from oasys.util.error_profile_util import ErrorProfileInputParameters, calculate_heigth_profile

try:
    from mpl_toolkits.mplot3d import Axes3D  # necessario per caricare i plot 3D
except:
    pass

class OWAbstractMultipleHeightProfileSimulatorS(OWWidget):
    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 800

    IMAGE_WIDTH = 890
    IMAGE_HEIGHT = 785

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 718

    xx = None
    yy = None
    zz = None

    kind_of_profile_x = Setting(0)
    kind_of_profile_y = Setting(0)

    step_x = Setting(0.0)
    step_y = Setting(0.0)

    dimension_x = Setting(0.0)
    dimension_y = Setting(0.0)

    power_law_exponent_beta_x = Setting(3.0)
    power_law_exponent_beta_y = Setting(3.0)

    correlation_length_x = Setting(30.0)
    correlation_length_y = Setting(30.0)

    error_type_x = Setting(profiles_simulation.FIGURE_ERROR)
    error_type_y = Setting(profiles_simulation.FIGURE_ERROR)

    rmx_x = None # for calculations
    rms_x_from = Setting(1.0)
    rms_x_to = Setting(10.0)
    rms_x_step = Setting(1.0)

    montecarlo_seed_x = Setting(8787)

    rms_y = Setting(1.0)

    montecarlo_seed_y = Setting(8788)

    heigth_profile_1D_file_name_x= Setting("mirror_1D_x.dat")
    delimiter_x = Setting(0)
    conversion_factor_x_x = Setting(0.1)
    conversion_factor_x_y = Setting(1e-6)

    center_x = Setting(1)
    modify_x = Setting(0)
    new_length_x = Setting(0.0)
    filler_value_x = Setting(0.0)

    renormalize_x = 1

    heigth_profile_1D_file_name_y = Setting("mirror_1D_y.dat")
    delimiter_y = Setting(0)
    conversion_factor_y_x = Setting(0.1)
    conversion_factor_y_y = Setting(1e-6)

    center_y = Setting(1)
    modify_y = Setting(0)
    new_length_y = Setting(0.0)
    filler_value_y = Setting(0.0)

    renormalize_y = Setting(0)

    heigth_profile_file_name = Setting('height_error_profile.hdf5')

    inputs=[("DABAM 1D Profile", numpy.ndarray, "receive_dabam_profile")]

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Calculate Height Profile", self)
        self.runaction.triggered.connect(self.calculate_heigth_profile_ni)
        self.addAction(self.runaction)

        self.runaction = widget.OWAction("Generate Height Profile File", self)
        self.runaction.triggered.connect(self.generate_heigth_profile_file_ni)
        self.addAction(self.runaction)

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width() * 0.05),
                               round(geom.height() * 0.05),
                               round(min(geom.width() * 0.98, self.MAX_WIDTH)),
                               round(min(geom.height() * 0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Calculate Height\nProfile", callback=self.calculate_heigth_profile)
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Generate Height\nProfile File", callback=self.generate_heigth_profile_file)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette)  # assign new palette
        button.setFixedHeight(45)
        button.setFixedWidth(150)

        button = gui.button(button_box, self, "Reset Fields", callback=self.call_reset_settings)
        font = QFont(button.font())
        font.setItalic(True)
        button.setFont(font)
        palette = QPalette(button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Red'))
        button.setPalette(palette)  # assign new palette
        button.setFixedHeight(45)

        gui.separator(self.controlArea)

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        tab_input = oasysgui.createTabPage(tabs_setting, "Input Parameters")
        tab_out = oasysgui.createTabPage(tabs_setting, "Output")

        tabs_input = oasysgui.tabWidget(tab_input)
        tab_length = oasysgui.createTabPage(tabs_input, "Length")
        tab_width = oasysgui.createTabPage(tabs_input, "Width")
        tab_usa = oasysgui.createTabPage(tabs_setting, "Use of the Widget")
        tab_usa.setStyleSheet("background-color: white;")

        usage_box = oasysgui.widgetBox(tab_usa, "", addSpace=True, orientation="horizontal")

        label = QLabel("")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setPixmap(QPixmap(self.get_usage_path()))

        usage_box.layout().addWidget(label)

        #/ ---------------------------------------

        input_box_l = oasysgui.widgetBox(tab_length, "Calculation Parameters", addSpace=False, orientation="vertical")

        gui.comboBox(input_box_l, self, "kind_of_profile_y", label="Kind of Profile", labelWidth=260,
                     items=["Fractal", "Gaussian", "User File"],
                     callback=self.set_KindOfProfileY, sendSelectedValue=False, orientation="horizontal")

        gui.separator(input_box_l)

        self.kind_of_profile_y_box_1 = oasysgui.widgetBox(input_box_l, "", addSpace=False, orientation="vertical", height=350)

        self.le_dimension_y = oasysgui.lineEdit(self.kind_of_profile_y_box_1, self, "dimension_y", "Dimensions",
                           labelWidth=260, valueType=float, orientation="horizontal")
        self.le_step_y = oasysgui.lineEdit(self.kind_of_profile_y_box_1, self, "step_y", "Step",
                           labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.kind_of_profile_y_box_1, self, "montecarlo_seed_y", "Monte Carlo initial seed", labelWidth=260,
                           valueType=int, orientation="horizontal")

        self.kind_of_profile_y_box_1_1 = oasysgui.widgetBox(self.kind_of_profile_y_box_1, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.kind_of_profile_y_box_1_1, self, "power_law_exponent_beta_y", "Beta Value",
                           labelWidth=260, valueType=float, orientation="horizontal")

        self.kind_of_profile_y_box_1_2 = oasysgui.widgetBox(self.kind_of_profile_y_box_1, "", addSpace=False, orientation="vertical")

        self.le_correlation_length_y = oasysgui.lineEdit(self.kind_of_profile_y_box_1_2, self, "correlation_length_y", "Correlation Length",
                           labelWidth=260, valueType=float, orientation="horizontal")

        gui.separator(self.kind_of_profile_y_box_1)

        gui.comboBox(self.kind_of_profile_y_box_1, self, "error_type_y", label="Normalization to", labelWidth=270,
                     items=["Figure Error (nm)", "Slope Error (" + "\u03BC" + "rad)"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_y_box_1, self, "rms_y", "Rms Value",
                           labelWidth=260, valueType=float, orientation="horizontal")

        self.kind_of_profile_y_box_2 = oasysgui.widgetBox(input_box_l, "", addSpace=False, orientation="vertical", height=390)

        select_file_box_2 = oasysgui.widgetBox(self.kind_of_profile_y_box_2, "", addSpace=False, orientation="horizontal")

        self.le_heigth_profile_1D_file_name_y = oasysgui.lineEdit(select_file_box_2, self, "heigth_profile_1D_file_name_y", "1D Profile File Name",
                                                        labelWidth=120, valueType=str, orientation="horizontal")

        gui.button(select_file_box_2, self, "...", callback=self.selectFile1D_Y)

        gui.comboBox(self.kind_of_profile_y_box_2, self, "delimiter_y", label="Fields delimiter", labelWidth=260,
                     items=["Spaces", "Tabs"], sendSelectedValue=False, orientation="horizontal")

        self.le_conversion_factor_y_x = oasysgui.lineEdit(self.kind_of_profile_y_box_2, self, "conversion_factor_y_x", "Conversion from file to meters\n(Abscissa)",
                                                          labelWidth=260,
                                                          valueType=float, orientation="horizontal")

        self.le_conversion_factor_y_y = oasysgui.lineEdit(self.kind_of_profile_y_box_2, self, "conversion_factor_y_y", "Conversion from file to meters\n(Height Profile Values)",
                                                          labelWidth=260,
                                                          valueType=float, orientation="horizontal")

        gui.separator(self.kind_of_profile_y_box_2)

        gui.comboBox(self.kind_of_profile_y_box_2, self, "center_y", label="Center Profile in the middle of O.E.", labelWidth=300,
                     items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(self.kind_of_profile_y_box_2, self, "modify_y", label="Modify Length?", labelWidth=150,
                     items=["No", "Rescale to new length", "Fit to new length (fill or cut)"], callback=self.set_ModifyY, sendSelectedValue=False, orientation="horizontal")

        self.modify_box_2_1 = oasysgui.widgetBox(self.kind_of_profile_y_box_2, "", addSpace=False, orientation="vertical", height=60)

        self.modify_box_2_2 = oasysgui.widgetBox(self.kind_of_profile_y_box_2, "", addSpace=False, orientation="vertical", height=60)
        self.le_new_length_y_1 = oasysgui.lineEdit(self.modify_box_2_2, self, "new_length_y", "New Length", labelWidth=300, valueType=float, orientation="horizontal")

        self.modify_box_2_3 = oasysgui.widgetBox(self.kind_of_profile_y_box_2, "", addSpace=False, orientation="vertical", height=60)
        self.le_new_length_y_2 = oasysgui.lineEdit(self.modify_box_2_3, self, "new_length_y", "New Length", labelWidth=300, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.modify_box_2_3, self, "filler_value_y", "Filler Value (if new length > profile length) [nm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.set_ModifyY()

        gui.comboBox(self.kind_of_profile_y_box_2, self, "renormalize_y", label="Renormalize to different RMS", labelWidth=260,
                     items=["No", "Yes"], callback=self.set_KindOfProfileY, sendSelectedValue=False, orientation="horizontal")

        self.kind_of_profile_y_box_2_1 = oasysgui.widgetBox(self.kind_of_profile_y_box_2, "", addSpace=False, orientation="vertical")

        gui.comboBox(self.kind_of_profile_y_box_2_1, self, "error_type_y", label="Normalization to", labelWidth=270,
                     items=["Figure Error (nm)", "Slope Error (" + "\u03BC" + "rad)"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_y_box_2_1, self, "rms_y", "Rms Value",
                           labelWidth=260, valueType=float, orientation="horizontal")


        self.set_KindOfProfileY()

        #/ ---------------------------------------

        input_box_w = oasysgui.widgetBox(tab_width, "Calculation Parameters", addSpace=False, orientation="vertical")


        gui.comboBox(input_box_w, self, "kind_of_profile_x", label="Kind of Profile", labelWidth=260,
                     items=["Fractal", "Gaussian", "User File"],
                     callback=self.set_KindOfProfileX, sendSelectedValue=False, orientation="horizontal")

        gui.separator(input_box_w)

        self.kind_of_profile_x_box_1 = oasysgui.widgetBox(input_box_w, "", addSpace=False, orientation="vertical", height=350)

        self.le_dimension_x = oasysgui.lineEdit(self.kind_of_profile_x_box_1, self, "dimension_x", "Dimensions",
                          labelWidth=260, valueType=float, orientation="horizontal")
        self.le_step_x = oasysgui.lineEdit(self.kind_of_profile_x_box_1, self, "step_x", "Step",
                          labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.kind_of_profile_x_box_1, self, "montecarlo_seed_x", "Monte Carlo initial seed",
                          labelWidth=260, valueType=int, orientation="horizontal")

        self.kind_of_profile_x_box_1_1 = oasysgui.widgetBox(self.kind_of_profile_x_box_1, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.kind_of_profile_x_box_1_1, self, "power_law_exponent_beta_x", "Beta Value",
                           labelWidth=260, valueType=float, orientation="horizontal")

        self.kind_of_profile_x_box_1_2 = oasysgui.widgetBox(self.kind_of_profile_x_box_1, "", addSpace=False, orientation="vertical")

        self.le_correlation_length_x = oasysgui.lineEdit(self.kind_of_profile_x_box_1_2, self, "correlation_length_x", "Correlation Length",
                           labelWidth=260, valueType=float, orientation="horizontal")

        gui.separator(self.kind_of_profile_x_box_1)

        gui.comboBox(self.kind_of_profile_x_box_1, self, "error_type_x", label="Normalization to", labelWidth=270,
                     items=["Figure Error (nm)", "Slope Error (" + "\u03BC" + "rad)"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_x_box_1, self, "rms_x_from", "Rms Value From",
                           labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_x_box_1, self, "rms_x_to", "Rms Value To",
                           labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_x_box_1, self, "rms_x_step", "Rms Value Step",
                           labelWidth=260, valueType=float, orientation="horizontal")

        ##----------------------------------

        self.kind_of_profile_x_box_2 = oasysgui.widgetBox(input_box_w, "", addSpace=False, orientation="vertical", height=390)

        select_file_box_1 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=False, orientation="horizontal")

        self.le_heigth_profile_1D_file_name_x = oasysgui.lineEdit(select_file_box_1, self, "heigth_profile_1D_file_name_x", "1D Profile File Name",
                                                        labelWidth=120, valueType=str, orientation="horizontal")

        gui.button(select_file_box_1, self, "...", callback=self.selectFile1D_X)

        gui.comboBox(self.kind_of_profile_x_box_2 , self, "delimiter_x", label="Fields delimiter", labelWidth=260,
                     items=["Spaces", "Tabs"], sendSelectedValue=False, orientation="horizontal")

        self.le_conversion_factor_x_x = oasysgui.lineEdit(self.kind_of_profile_x_box_2, self, "conversion_factor_x_x", "Conversion from file to meters\n(Abscissa)",
                                                          labelWidth=260,
                                                          valueType=float, orientation="horizontal")

        self.le_conversion_factor_x_y = oasysgui.lineEdit(self.kind_of_profile_x_box_2, self, "conversion_factor_x_y", "Conversion from file to meters\n(Height Profile Values)",
                                                          labelWidth=260,
                                                          valueType=float, orientation="horizontal")

        gui.separator(self.kind_of_profile_x_box_2)

        gui.comboBox(self.kind_of_profile_x_box_2, self, "center_x", label="Center Profile in the middle of O.E.", labelWidth=300,
                     items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(self.kind_of_profile_x_box_2, self, "modify_x", label="Modify Length?", labelWidth=150,
                     items=["No", "Rescale to new length", "Fit to new length (fill or cut)"], callback=self.set_ModifyX, sendSelectedValue=False, orientation="horizontal")

        self.modify_box_1_1 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=False, orientation="vertical", height=60)

        self.modify_box_1_2 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=False, orientation="vertical", height=60)
        self.le_new_length_x_1 = oasysgui.lineEdit(self.modify_box_1_2, self, "new_length_x", "New Length", labelWidth=300, valueType=float, orientation="horizontal")

        self.modify_box_1_3 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=False, orientation="vertical", height=60)
        self.le_new_length_x_2 = oasysgui.lineEdit(self.modify_box_1_3, self, "new_length_x", "New Length", labelWidth=300, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.modify_box_1_3, self, "filler_value_x", "Filler Value (if new length > profile length) [nm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.set_ModifyX()

        cb = gui.comboBox(self.kind_of_profile_x_box_2, self, "renormalize_x", label="Renormalize to different RMS", labelWidth=260,
                     items=["No", "Yes"], callback=self.set_KindOfProfileX, sendSelectedValue=False, orientation="horizontal")
        cb.setEnabled(False)

        self.kind_of_profile_x_box_2_1 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=False, orientation="vertical")

        gui.comboBox(self.kind_of_profile_x_box_2_1, self, "error_type_x", label="Normalization to", labelWidth=270,
                     items=["Figure Error (nm)", "Slope Error (" + "\u03BC" + "rad)"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_x_box_2_1, self, "rms_x_from", "Rms Value From",
                           labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_x_box_2_1, self, "rms_x_to", "Rms Value To",
                           labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_x_box_2_1, self, "rms_x_step", "Rms Value Step",
                           labelWidth=260, valueType=float, orientation="horizontal")

        self.set_KindOfProfileX()

        #/ ---------------------------------------

        self.output_box = oasysgui.widgetBox(tab_input, "Outputs", addSpace=False, orientation="vertical")

        self.select_file_box = oasysgui.widgetBox(self.output_box, "", addSpace=False, orientation="horizontal")

        self.le_heigth_profile_file_name = oasysgui.lineEdit(self.select_file_box, self, "heigth_profile_file_name", "Output File Name",
                                                        labelWidth=120, valueType=str, orientation="horizontal")

        gui.button(self.select_file_box, self, "...", callback=self.selectFile)

        self.shadow_output = oasysgui.textArea()

        out_box = oasysgui.widgetBox(tab_out, "System Output", addSpace=True, orientation="horizontal", height=680)
        out_box.layout().addWidget(self.shadow_output)

        gui.rubber(self.controlArea)

        self.figure = Figure(figsize=(10, 7))
        self.figure.patch.set_facecolor('white')

        self.axis = self.figure.add_subplot(111, projection='3d')

        self.axis.set_zlabel("Z [nm]")

        self.figure_canvas = FigureCanvas3D(ax=self.axis, fig=self.figure)
        self.figure_canvas.setFixedWidth(self.IMAGE_WIDTH)
        self.figure_canvas.setFixedHeight(self.IMAGE_HEIGHT)

        self.mainArea.layout().addWidget(self.figure_canvas)

        gui.rubber(self.mainArea)

    def after_change_workspace_units(self):
        self.si_to_user_units = 1.0

        self.axis.set_xlabel("X [" + self.get_axis_um() + "]")
        self.axis.set_ylabel("Y [" + self.get_axis_um() + "]")

        label = self.le_dimension_y.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_step_y.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_correlation_length_y.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")

        label = self.le_dimension_x.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_step_x.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_correlation_length_x.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")

        label = self.le_conversion_factor_y_x.parent().layout().itemAt(0).widget()
        label.setText("Conversion from file to meters\n(Abscissa)")
        label = self.le_conversion_factor_y_y.parent().layout().itemAt(0).widget()
        label.setText("Conversion from file to meters\n(Height Profile Values)")
        label = self.le_conversion_factor_x_x.parent().layout().itemAt(0).widget()
        label.setText("Conversion from file to meters\n(Abscissa)")
        label = self.le_conversion_factor_x_y.parent().layout().itemAt(0).widget()
        label.setText("Conversion from file to meters\n(Height Profile Values)")

        label = self.le_new_length_y_1.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_new_length_y_2.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_new_length_x_1.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_new_length_x_2.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")

    def set_KindOfProfileX(self):
        self.kind_of_profile_x_box_1.setVisible(self.kind_of_profile_x<2)
        self.kind_of_profile_x_box_1_1.setVisible(self.kind_of_profile_x==0)
        self.kind_of_profile_x_box_1_2.setVisible(self.kind_of_profile_x==1)
        self.kind_of_profile_x_box_2.setVisible(self.kind_of_profile_x==2)
        self.kind_of_profile_x_box_2_1.setVisible(self.kind_of_profile_x==2 and self.renormalize_x==1)

    def set_KindOfProfileY(self):
        self.kind_of_profile_y_box_1.setVisible(self.kind_of_profile_y<2)
        self.kind_of_profile_y_box_1_1.setVisible(self.kind_of_profile_y==0)
        self.kind_of_profile_y_box_1_2.setVisible(self.kind_of_profile_y==1)
        self.kind_of_profile_y_box_2.setVisible(self.kind_of_profile_y==2)
        self.kind_of_profile_y_box_2_1.setVisible(self.kind_of_profile_y==2 and self.renormalize_y==1)

    def set_ModifyY(self):
        self.modify_box_2_1.setVisible(self.modify_y == 0)
        self.modify_box_2_2.setVisible(self.modify_y == 1)
        self.modify_box_2_3.setVisible(self.modify_y == 2)

    def set_ModifyX(self):
        self.modify_box_1_1.setVisible(self.modify_x == 0)
        self.modify_box_1_2.setVisible(self.modify_x == 1)
        self.modify_box_1_3.setVisible(self.modify_x == 2)

    def receive_dabam_profile(self, dabam_profile):
        if not dabam_profile is None:
            try:
                file_name = "dabam_profile_" + str(id(self)) + ".dat"

                file = open(file_name, "w")

                for element in dabam_profile:
                    file.write(str(element[0]) + " " + str(element[1]) + "\n")

                file.flush()
                file.close()

                self.kind_of_profile_y = 2
                self.heigth_profile_1D_file_name_y = file_name
                self.delimiter_y = 0
                self.conversion_factor_y_x = 1.0
                self.conversion_factor_y_y = 1.0

                self.set_KindOfProfileY()

            except Exception as exception:
                QMessageBox.critical(self, "Error", exception.args[0], QMessageBox.Ok)

                if self.IS_DEVELOP: raise exception

    def calculate_heigth_profile_ni(self):
        self.calculate_heigth_profile(not_interactive_mode=True)

    def calculate_heigth_profile(self, not_interactive_mode=False):
        try:
            sys.stdout = EmittingStream(textWritten=self.writeStdOut)

            self.check_fields()

            rms_x_values = numpy.arange(self.rms_x_from, self.rms_x_to + self.rms_x_step, self.rms_x_step)

            self.xx = []
            self.yy = []
            self.zz = []

            for rms_x in rms_x_values:
                input_parameters = ErrorProfileInputParameters(widget=self)
                input_parameters.rms_x = rms_x

                xx, yy, zz = calculate_heigth_profile(input_parameters)

                self.xx.append(xx) # to user units
                self.yy.append(yy) # to user units
                self.zz.append(zz) # to user units

            self.axis.clear()

            x_to_plot, y_to_plot = numpy.meshgrid(self.xx[-1], self.yy[-1])
            z_to_plot = self.zz[-1] * 1e9 / self.si_to_user_units #nm

            self.axis.plot_surface(x_to_plot, y_to_plot, z_to_plot,
                                   rstride=1, cstride=1, cmap=cm.autumn, linewidth=0.5, antialiased=True)

            sloperms = profiles_simulation.slopes(self.zz[-1].T, self.xx[-1], self.yy[-1], return_only_rms=1)

            title = ' First Profile: \n' + \
                    ' Slope error rms in X direction: %f $\mu$rad' % (sloperms[0]*1e6) + '\n' + \
                    ' Slope error rms in Y direction: %f $\mu$rad' % (sloperms[1]*1e6) + '\n' + \
                    ' Figure error rms in X direction: %f nm' % (round(self.zz[-1][0, :].std()*1e9/self.si_to_user_units, 6)) + '\n' + \
                    ' Figure error rms in Y direction: %f nm' % (round(self.zz[-1][:, 0].std()*1e9/self.si_to_user_units, 6))

            self.axis.set_xlabel("X [" + self.get_axis_um()+ "]")
            self.axis.set_ylabel("Y [" + self.get_axis_um() + "]")
            self.axis.set_zlabel("Z [nm]")
            self.axis.set_title(title)
            self.axis.mouse_init()

            if not not_interactive_mode:
                self.figure_canvas.draw()

                QMessageBox.information(self, "QMessageBox.information()",
                                        "Height Profile calculated: if the result is satisfactory,\nclick \'Generate Height Profile File\' to complete the operation ",
                                        QMessageBox.Ok)
        except Exception as exception:
            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)
            if self.IS_DEVELOP: raise exception

    def generate_heigth_profile_file_ni(self):
        self.generate_heigth_profile_file(not_interactive_mode=True)

    def generate_heigth_profile_file(self, not_interactive_mode=False):
        if not self.zz is None and not self.yy is None and not self.xx is None:
            try:
                congruence.checkDir(self.heigth_profile_file_name)

                sys.stdout = EmittingStream(textWritten=self.writeStdOut)

                height_profile_file_names = []
                profile_number = 0

                heigth_profile_file_name = congruence.checkFileName(self.heigth_profile_file_name)

                for zz, xx, yy in zip(self.zz, self.xx, self.yy):
                    profile_number += 1

                    outFile = heigth_profile_file_name + "_S_" + str(profile_number) + self.get_file_format()

                    self.write_error_profile_file(zz, xx, yy, outFile=outFile)

                    height_profile_file_names.append(outFile)

                if not not_interactive_mode:
                    QMessageBox.information(self, "QMessageBox.information()",
                                            "Height Profile files written on disk",
                                            QMessageBox.Ok)

                dimension_x = self.dimension_x
                dimension_y = self.dimension_y

                if self.kind_of_profile_x == 2: #user defined
                    dimension_x = (self.xx[0][-1] - self.xx[0][0])
                if self.kind_of_profile_y == 2: #user defined
                    dimension_y = (self.yy[0][-1] - self.yy[0][0])

                self.send_data(height_profile_file_names, dimension_x, dimension_y)

            except Exception as exception:
                QMessageBox.critical(self, "Error",
                                     exception.args[0],
                                     QMessageBox.Ok)

    def call_reset_settings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass

    def check_fields(self):
        if self.kind_of_profile_y < 2:
            self.dimension_y = congruence.checkStrictlyPositiveNumber(self.dimension_y, "Dimension Y")
            self.step_y = congruence.checkStrictlyPositiveNumber(self.step_y, "Step Y")
            if self.kind_of_profile_y == 0: self.power_law_exponent_beta_y = congruence.checkPositiveNumber(self.power_law_exponent_beta_y, "Beta Value Y")
            if self.kind_of_profile_y == 1: self.correlation_length_y = congruence.checkStrictlyPositiveNumber(self.correlation_length_y, "Correlation Length Y")
            self.rms_y = congruence.checkPositiveNumber(self.rms_y, "Rms Y")

            self.montecarlo_seed_y = congruence.checkPositiveNumber(self.montecarlo_seed_y, "Monte Carlo initial seed y")
        else:
            congruence.checkFile(self.heigth_profile_1D_file_name_y)
            self.conversion_factor_y_x = congruence.checkStrictlyPositiveNumber(self.conversion_factor_y_x, "Conversion from file to workspace units(Abscissa)")
            self.conversion_factor_y_y = congruence.checkStrictlyPositiveNumber(self.conversion_factor_y_y, "Conversion from file to workspace units (Height Profile Values)")
            if self.modify_y > 0:
                self.new_length_y = congruence.checkStrictlyPositiveNumber(self.new_length_y, "New Length")
            if self.renormalize_y == 1:
                self.rms_y = congruence.checkPositiveNumber(self.rms_y, "Rms Y")

        if self.kind_of_profile_x < 2:
            self.dimension_x = congruence.checkStrictlyPositiveNumber(self.dimension_x, "Dimension X")
            self.step_x = congruence.checkStrictlyPositiveNumber(self.step_x, "Step X")
            if self.kind_of_profile_x == 0: self.power_law_exponent_beta_x = congruence.checkPositiveNumber(self.power_law_exponent_beta_x, "Beta Value X")
            if self.kind_of_profile_x == 1: self.correlation_length_x = congruence.checkStrictlyPositiveNumber(self.correlation_length_x, "Correlation Length X")
            self.rms_x_from = congruence.checkPositiveNumber(self.rms_x_from, "Rms X From")
            self.rms_x_to = congruence.checkPositiveNumber(self.rms_x_to, "Rms X To")
            self.rms_x_step = congruence.checkPositiveNumber(self.rms_x_step, "Rms X Step")
            congruence.checkGreaterThan(self.rms_x_to, self.rms_x_from, "Rms X To", "Rms X From")
            congruence.checkLessOrEqualThan(self.rms_x_step, self.rms_x_to-self.rms_x_from, "Rms X Step", "Range of Rms Values")

            self.montecarlo_seed_x = congruence.checkPositiveNumber(self.montecarlo_seed_x, "Monte Carlo initial seed X")
        else:
            congruence.checkFile(self.heigth_profile_1D_file_name_x)
            self.conversion_factor_x_x = congruence.checkStrictlyPositiveNumber(self.conversion_factor_x_x, "Conversion from file to workspace units(Abscissa)")
            self.conversion_factor_x_y = congruence.checkStrictlyPositiveNumber(self.conversion_factor_x_y, "Conversion from file to workspace units (Height Profile Values)")
            if self.modify_x > 0:
                self.new_length_x = congruence.checkStrictlyPositiveNumber(self.new_length_x, "New Length")
            if self.renormalize_x == 1:
                self.rms_x_from = congruence.checkPositiveNumber(self.rms_x_from, "Rms X From")
                self.rms_x_to = congruence.checkPositiveNumber(self.rms_x_to, "Rms X To")
                self.rms_x_step = congruence.checkPositiveNumber(self.rms_x_step, "Rms X Step")
                congruence.checkGreaterThan(self.rms_x_to, self.rms_x_from, "Rms X To", "Rms X From")
                congruence.checkLessOrEqualThan(self.rms_x_step, self.rms_x_to-self.rms_x_from, "Rms X Step", "Range of Rms Values")

        congruence.checkDir(self.heigth_profile_file_name)

    def writeStdOut(self, text):
        cursor = self.shadow_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.shadow_output.setTextCursor(cursor)
        self.shadow_output.ensureCursorVisible()

    def selectFile1D_X(self):
        self.le_heigth_profile_1D_file_name_x.setText(oasysgui.selectFileFromDialog(self, self.heigth_profile_1D_file_name_x, "Select 1D Height Profile File", file_extension_filter="Data Files (*.dat *.txt)"))

    def selectFile1D_Y(self):
        self.le_heigth_profile_1D_file_name_y.setText(oasysgui.selectFileFromDialog(self, self.heigth_profile_1D_file_name_y, "Select 1D Height Profile File", file_extension_filter="Data Files (*.dat *.txt)"))

    def selectFile(self):
        self.le_heigth_profile_file_name.setText(oasysgui.selectFileFromDialog(self, self.heigth_profile_file_name, "Select Output File", file_extension_filter="Data Files (*.dat)"))

    def get_usage_path(self):
        pass

    def write_error_profile_file(self, zz, xx, yy, outFile):
        raise NotImplementedError("This method is abstract")

    def send_data(self, height_profile_file_names, dimension_x, dimension_y):
        raise NotImplementedError("This method is abstract")

    def get_axis_um(self):
        return "m"

    def get_file_format(self):
        return ".hdf5"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWAbstractMultipleHeightProfileSimulatorS()
    w.show()
    app.exec()
    w.saveSettings()
