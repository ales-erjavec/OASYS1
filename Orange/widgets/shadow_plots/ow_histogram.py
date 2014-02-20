import sys, numpy
import Orange
from Orange.widgets import gui
from Orange.widgets.settings import Setting

import Shadow.ShadowTools as ST

from Orange.shadow.shadow_util import ShadowGui
from Orange.widgets.shadow_gui import ow_automatic_element

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class Histogram(ow_automatic_element.AutomaticElement):

    name = "Histogram"
    description = "Plotting Tools: Histogram"
    icon = "icons/histogram.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 2
    category = "Plotting Tools"
    keywords = ["data", "file", "load", "read"]


    inputs = [("Input Beam", Orange.shadow.ShadowBeam, "setBeam")]

    IMAGE_WIDTH = 900
    IMAGE_HEIGHT = 700

    want_main_area=1
    plot_canvas = None
    input_beam=None

    x_column_index=Setting(6)
    x_label=Setting("Energy")
    y_label=Setting("Rays")
    title=Setting("Energy")

    def __init__(self):
        super().__init__()

        tabs_setting = gui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(650)

        gui.button(self.controlArea, self, "Refresh", callback=self.plot_results)

        # graph tab
        tab_gen = gui.createTabPage(tabs_setting, "General")
        tab_his = gui.createTabPage(tabs_setting, "Histograms")
        tab_col = gui.createTabPage(tabs_setting, "Color")

        general_box = gui.widgetBox(tab_gen, "General Settings", addSpace=True, orientation="vertical")
        general_box.setFixedHeight(200)

        gui.comboBox(general_box, self, "x_column_index", label="Column", \
                     items=["1: X", \
                            "2: Y", \
                            "3: Z", \
                            "4: X'", \
                            "5: Y'", \
                            "6: Z'", \
                            "11: Energy"], \
                     sendSelectedValue=False, orientation="horizontal")


        ShadowGui.lineEdit(general_box, self, "x_label", "X Label", valueType=str, orientation="horizontal")
        ShadowGui.lineEdit(general_box, self, "y_label", "Y Label", valueType=str, orientation="horizontal")
        ShadowGui.lineEdit(general_box, self, "title", "Title", valueType=str, orientation="horizontal")

        self.image_box = gui.widgetBox(self.mainArea, "Plot Result", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH)


    def replace_fig(self, figure):
        if self.plot_canvas is not None:
            self.image_box.layout().removeWidget(self.plot_canvas)
        self.plot_canvas = FigureCanvas(figure)
        self.image_box.layout().addWidget(self.plot_canvas)


    def plot_histo(self, var, title, xtitle, ytitle):
        plot = ST.histo1(self.input_beam.beam,var,nolost=1,nbins=100,ref=1,calfwhm=1,title=title, xtitle=xtitle, ytitle=ytitle, noplot=1)

        self.replace_fig(plot.figure)


    def plot_results(self):
        if not self.input_beam == None:
            if self.x_column_index == 6: x = 11
            else: x = self.x_column_index + 1

            self.plot_histo(x, title=self.title, xtitle=self.x_label, ytitle=self.y_label)

    def setBeam(self, beam):
        self.input_beam = beam

        if self.is_automatic_run:
           self.plot_results()
