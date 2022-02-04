#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------- #
# Copyright (c) 2021, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2021. UChicago Argonne, LLC. This software was produced       #
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
# ----------------------------------------------------------------------- #
import numpy

from orangewidget.widget import OWAction
from oasys.widgets import widget

from matplotlib.pyplot import rcParams
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from matplotlib.figure import Figure
from oasys.widgets.gui import FigureCanvas3D

from oasys.widgets import gui as oasysgui

from orangewidget import gui
from orangewidget.settings import Setting

from PyQt5.QtCore import QRect
from PyQt5.Qt import QApplication

pixels_to_inches = 1/rcParams['figure.dpi']

class OpticalElementsColors:
    MIRROR = (0, 0, 1, 0.1)
    CRYSTAL = (0, 1, 0, 0.1)
    GRATING = (1, 0, 0, 0.1)

class Orientations:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class AspectRatioModifier:
    def __init__(self,
                 element_expansion_factor  = [1.0, 1.0, 1.0], # length,   width, thickness
                 layout_reduction_factor = [1.0, 1.0, 1.0]  # distance, shift, height
                 ):
        self.element_expansion_factor  = element_expansion_factor
        self.layout_reduction_factor = layout_reduction_factor

DEFAULT_AZIM = -23.1
DEFAULT_ELEV = 27.9

class AbstractBeamlineRenderer(widget.OWWidget):

    want_main_area = 1

    WIDGET_WIDTH = 1900
    WIDGET_HEIGHT = 1000

    is_interactive = Setting(1)

    initial_height = Setting(1000.0)

    element_expansion_factor_lenght = Setting(1.0)
    element_expansion_factor_width = Setting(1.0)
    element_expansion_factor_thickness = Setting(1.0)

    layout_reduction_factor_distance = Setting(1.0)
    layout_reduction_factor_shift = Setting(1.0)
    layout_reduction_factor_height = Setting(1.0)

    use_range = Setting(0)
    range_min = Setting(0.0)
    range_max = Setting(200000.0)

    def __init__(self):
        super().__init__()

        action = OWAction("Render Beamline", self)
        action.triggered.connect(self.render_beamline)
        self.addAction(action)

        self.build_layout()

    def build_layout(self):
        self.warning(text="Widget under development: please do not report anomalies")

        geom = QApplication.desktop().availableGeometry()

        window_width = round(min(geom.width() * 0.98, self.WIDGET_WIDTH))
        window_height = round(min(geom.height() * 0.95, self.WIDGET_HEIGHT))
        control_area_width = 350

        self.setGeometry(QRect(round(geom.width() * 0.05),
                               round(geom.height() * 0.05),
                               window_width,
                               window_height))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal", width=control_area_width)

        gui.button(button_box, self, "Restore Default View and Values", callback=self.reset_default, height=45)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal", width=control_area_width)

        gui.button(button_box, self, "Reset Zoom/Shift", callback=self.reset_zoom_shift, height=25)
        gui.button(button_box, self, "Reset Rotation", callback=self.reset_rotation, height=25)

        gen_box = oasysgui.widgetBox(self.controlArea, "Options", addSpace=False, orientation="vertical", width=control_area_width)

        gui.checkBox(gen_box, self, "is_interactive", "Real time refresh active", labelWidth=200)

        beamline_box = oasysgui.widgetBox(gen_box, "Beamline", addSpace=False, orientation="vertical", height=90)

        oasysgui.lineEdit(beamline_box, self, "initial_height", "Beam vertical baseline [user units]", labelWidth=230, valueType=float, orientation="horizontal", callback=self.refresh)

        oe_exp_box = oasysgui.widgetBox(gen_box, "O.E. expansion (aesthetic)", addSpace=False, orientation="vertical", height=110)

        oasysgui.lineEdit(oe_exp_box, self, "element_expansion_factor_lenght", "O.E. lenght factor (\u22651)", labelWidth=230, valueType=float, orientation="horizontal", callback=self.refresh)
        oasysgui.lineEdit(oe_exp_box, self, "element_expansion_factor_width", "O.E. width factor (\u22651)", labelWidth=230, valueType=float, orientation="horizontal", callback=self.refresh)
        oasysgui.lineEdit(oe_exp_box, self, "element_expansion_factor_thickness", "O.E. thickness factor (\u22651)", labelWidth=230, valueType=float, orientation="horizontal", callback=self.refresh)

        oe_exp_box = oasysgui.widgetBox(gen_box, "Layout compression (aesthetic)", addSpace=False, orientation="vertical", height=110)

        oasysgui.lineEdit(oe_exp_box, self, "layout_reduction_factor_distance", "Layout distance factor (\u22641)", labelWidth=230, valueType=float, orientation="horizontal", callback=self.refresh)
        oasysgui.lineEdit(oe_exp_box, self, "layout_reduction_factor_shift", "Layout shift factor (\u22641)", labelWidth=230, valueType=float, orientation="horizontal", callback=self.refresh)
        oasysgui.lineEdit(oe_exp_box, self, "layout_reduction_factor_height", "Layout height factor (\u22641)", labelWidth=230, valueType=float, orientation="horizontal", callback=self.refresh)

        range_box = oasysgui.widgetBox(gen_box, "Range", addSpace=False, orientation="vertical", height=140)

        gui.comboBox(range_box, self, "use_range", label="Use Layout Longitudinal Range", labelWidth=350,
                     items=["No", "Yes"],
                     callback=self.set_range, sendSelectedValue=False, orientation="horizontal")

        gui.separator(range_box, height=5)

        self.range_box_1 = oasysgui.widgetBox(range_box, "", addSpace=False, orientation="vertical")
        oasysgui.lineEdit(self.range_box_1, self, "range_min", "Range Min [user units]", labelWidth=200, valueType=float, orientation="horizontal", callback=self.refresh)
        oasysgui.lineEdit(self.range_box_1, self, "range_max", "Range Max [user units]", labelWidth=200, valueType=float, orientation="horizontal", callback=self.refresh)

        self.set_range(do_refresh=False)

        gui.rubber(self.controlArea)

        figure_width = window_width - control_area_width - 30
        figure_height = window_height - 20

        self.figure, self.axis = create_plot(figsize=(figure_width * pixels_to_inches, figure_height * pixels_to_inches))

        self.figure_canvas = FigureCanvas3D(fig=self.figure, ax=self.axis)
        self.figure_canvas.setFixedWidth(figure_width)
        self.figure_canvas.setFixedHeight(figure_height)

        self.mainArea.layout().addWidget(self.figure_canvas)

        gui.rubber(self.mainArea)

    def refresh(self):
        if self.is_interactive: self.reset_all()

    def set_range(self, do_refresh=True):
        self.range_box_1.setVisible(self.use_range == 1)
        if do_refresh: self.refresh()

    def reset_default(self):
        self.initial_height = 1000.0
        self.element_expansion_factor_lenght = 1.0
        self.element_expansion_factor_width = 1.0
        self.element_expansion_factor_thickness = 1.0
        self.layout_reduction_factor_distance = 1.0
        self.layout_reduction_factor_shift = 1.0
        self.layout_reduction_factor_height = 1.0
        self.use_range = 0
        self.range_min = 0.0
        self.range_max = 200000.0

        self.reset_all()

    def reset_zoom_shift(self):
        self.render_beamline(reset_rotation=False)
        self.figure_canvas.draw()

    def reset_rotation(self):
        self.axis.view_init(azim=DEFAULT_AZIM, elev=DEFAULT_ELEV)
        self.figure_canvas.draw()

    def reset_all(self):
        self.render_beamline(reset_rotation=True)


    def render_beamline(self, reset_rotation=True):
        raise NotImplementedError()

    def add_source(self, centers, limits, length=2.3, height=0.0, canting=0.0, aspect_ration_modifier=AspectRatioModifier()):
        length *= aspect_ration_modifier.element_expansion_factor[0]
        height *= aspect_ration_modifier.layout_reduction_factor[2]
        canting *= aspect_ration_modifier.layout_reduction_factor[0]
    
        center = numpy.array([0, length / 2 + canting, height])
    
        if canting != 0.0:
            self.axis.scatter(0, 0, height, s=30, c='c', marker='x')
            self.axis.text(0, 0, height, "Section Center")
    
        self.axis.scatter(center[0], center[1], center[2], s=30, c='r')
        self.axis.text(center[0], center[1], center[2], "Source Center")
    
        centers[0, :] = center
        limits[0, 0, :] = numpy.array([0, 0])
        limits[0, 1, :] = numpy.array([numpy.min([0, length / 2 + canting]), numpy.max([0, length / 2 + canting])])
        limits[0, 2, :] = numpy.array([0, height])
    
    
    def add_optical_element(self, centers, limits, oe_index,
                            width, length, thickness, inclination,
                            distance, height, shift,
                            orientation=Orientations.UP, color=OpticalElementsColors.MIRROR,
                            aspect_ration_modifier=AspectRatioModifier()):
        length *= aspect_ration_modifier.element_expansion_factor[0]
        width *= aspect_ration_modifier.element_expansion_factor[1]
        thickness *= aspect_ration_modifier.element_expansion_factor[2]
        distance *= aspect_ration_modifier.layout_reduction_factor[0]
        shift *= aspect_ration_modifier.layout_reduction_factor[1]
        height *= aspect_ration_modifier.layout_reduction_factor[2]
    
        half_width = width / 2
        half_length = length / 2
    
        if orientation == Orientations.UP:
            vertexes = [[-half_width, -half_length * numpy.cos(inclination), -half_length * numpy.sin(inclination)],  # surface
                        [half_width, -half_length * numpy.cos(inclination), -half_length * numpy.sin(inclination)],  # surface
                        [-half_width, -(half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination)), -(half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination))],
                        [half_width, -(half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination)), -(half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination))],
                        [-half_width, half_length * numpy.cos(inclination), half_length * numpy.sin(inclination)],  # surface
                        [half_width, half_length * numpy.cos(inclination), half_length * numpy.sin(inclination)],  # surface
                        [-half_width, half_length * numpy.cos(inclination) + thickness * numpy.sin(inclination), half_length * numpy.sin(inclination) - thickness * numpy.cos(inclination)],
                        [half_width, half_length * numpy.cos(inclination) + thickness * numpy.sin(inclination), half_length * numpy.sin(inclination) - thickness * numpy.cos(inclination)]
                        ]
        elif orientation == Orientations.DOWN:
            vertexes = [[-half_width, -half_length * numpy.cos(inclination), -half_length * numpy.sin(inclination)],  # surface
                        [half_width, -half_length * numpy.cos(inclination), -half_length * numpy.sin(inclination)],  # surface
                        [-half_width, -(half_length * numpy.cos(inclination) + thickness * numpy.sin(inclination)), -half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination)],
                        [half_width, -(half_length * numpy.cos(inclination) + thickness * numpy.sin(inclination)), -half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination)],
                        [-half_width, half_length * numpy.cos(inclination), half_length * numpy.sin(inclination)],  # surface
                        [half_width, half_length * numpy.cos(inclination), half_length * numpy.sin(inclination)],  # surface
                        [-half_width, half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination), half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination)],
                        [half_width, half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination), half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination)]
                        ]
        elif orientation == Orientations.LEFT:
            vertexes = [[half_length * numpy.sin(inclination), -half_length * numpy.cos(inclination), -half_width],  # surface
                        [half_length * numpy.sin(inclination), -half_length * numpy.cos(inclination), half_width],  # surface
                        [half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination), -(half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination)), -half_width],
                        [half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination), -(half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination)), half_width],
                        [-half_length * numpy.sin(inclination), half_length * numpy.cos(inclination), -half_width],  # surface
                        [-half_length * numpy.sin(inclination), half_length * numpy.cos(inclination), half_width],  # surface
                        [-half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination), half_length * numpy.cos(inclination) + thickness * numpy.sin(inclination), -half_width],
                        [-half_length * numpy.sin(inclination) + thickness * numpy.cos(inclination), half_length * numpy.cos(inclination) + thickness * numpy.sin(inclination), half_width]
                        ]
        elif orientation == Orientations.RIGHT:
            vertexes = [[half_length * numpy.sin(inclination), -half_length * numpy.cos(inclination), -half_width],  # surface
                        [half_length * numpy.sin(inclination), -half_length * numpy.cos(inclination), half_width],  # surface
                        [half_length * numpy.sin(inclination) - thickness * numpy.cos(inclination), -half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination), -half_width],
                        [half_length * numpy.sin(inclination) - thickness * numpy.cos(inclination), -half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination), half_width],
                        [-half_length * numpy.sin(inclination), half_length * numpy.cos(inclination), -half_width],  # surface
                        [-half_length * numpy.sin(inclination), half_length * numpy.cos(inclination), half_width],  # surface
                        [-half_length * numpy.sin(inclination) - thickness * numpy.cos(inclination), half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination), -half_width],
                        [-half_length * numpy.sin(inclination) - thickness * numpy.cos(inclination), half_length * numpy.cos(inclination) - thickness * numpy.sin(inclination), half_width]
                        ]
    
        vertexes = numpy.array(vertexes)
        vertexes[:, 0] += shift
        vertexes[:, 1] += distance
        vertexes[:, 2] += height
    
        center = numpy.array([(vertexes[1, 0] + vertexes[0, 0]) / 2, (vertexes[4, 1] + vertexes[0, 1]) / 2, (vertexes[4, 2] + vertexes[0, 2]) / 2])
    
        edges = [[vertexes[0], vertexes[1], vertexes[3], vertexes[2]],
                 [vertexes[0], vertexes[1], vertexes[5], vertexes[4]],
                 [vertexes[2], vertexes[3], vertexes[7], vertexes[6]],
                 [vertexes[0], vertexes[2], vertexes[6], vertexes[4]],
                 [vertexes[1], vertexes[3], vertexes[7], vertexes[5]],
                 [vertexes[4], vertexes[5], vertexes[7], vertexes[6]]
                 ]
    
        faces = Poly3DCollection(edges, linewidths=1, edgecolors='k')
        faces.set_facecolor(color)
    
        self.axis.add_collection3d(faces)
    
        # Plot the points themselves to force the scaling of the self.axises
        self.axis.scatter(vertexes[:, 0], vertexes[:, 1], vertexes[:, 2], s=0)
    
        centers[oe_index, :] = center
        limits[oe_index, 0, :] = numpy.array([numpy.min(vertexes[:, 0]), numpy.max(vertexes[:, 0])])
        limits[oe_index, 1, :] = numpy.array([numpy.min(vertexes[:, 1]), numpy.max(vertexes[:, 1])])
        limits[oe_index, 2, :] = numpy.array([numpy.min(vertexes[:, 2]), numpy.max(vertexes[:, 2])])
    
        return center, limits
    
    
    def add_point(self, centers, limits, oe_index, distance, height, shift, label="Sample", aspect_ratio_modifier=AspectRatioModifier()):
        distance *= aspect_ratio_modifier.layout_reduction_factor[0]
        shift *= aspect_ratio_modifier.layout_reduction_factor[1]
        height *= aspect_ratio_modifier.layout_reduction_factor[2]
    
        self.axis.scatter(shift, distance, height, s=30, c='g', marker='x')
        self.axis.text(shift, distance, height, label)
    
        centers[oe_index, :] = numpy.array([shift, distance, height])
        limits[oe_index, 0, :] = numpy.array([shift, shift])
        limits[oe_index, 1, :] = numpy.array([distance, distance])
        limits[oe_index, 2, :] = numpy.array([height, height])
    
    
    def draw_radiation_lines(self, coords, color='b', rng=None):
        if not rng is None:
            cursor = numpy.where(numpy.logical_and(coords[:, 1] >= rng[0], coords[:, 1] <= rng[1]))
    
            self.axis.scatter(coords[cursor, 0], coords[cursor, 1], coords[cursor, 2], s=3, c=color)
            self.axis.plot(coords[cursor, 0][0], coords[cursor, 1][0], coords[cursor, 2][0], color=color, linewidth=1)
        else:
            self.axis.scatter(coords[:, 0], coords[:, 1], coords[:, 2], s=3, c=color)
            self.axis.plot(coords[:, 0], coords[:, 1], coords[:, 2], color=color, linewidth=1)

    def draw_central_radiation_line(self, centers, rng=None):
        self.draw_radiation_lines(centers, color='r', rng=rng)


def create_plot(figsize=(12, 7)):
    fig = Figure(figsize=figsize)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=1, hspace=1)
    fig.patch.set_facecolor('white')

    return fig, fig.add_subplot(111, projection='3d')

def initialize_arrays(number_of_elements):
    limits  = numpy.zeros((number_of_elements, 3, 2))
    centers = numpy.zeros((number_of_elements, 3))

    return centers, limits
