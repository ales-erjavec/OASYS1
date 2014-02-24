import copy
import Orange
from Orange.widgets import gui
from Orange.widgets.settings import Setting

import Shadow.ShadowTools as ST

from Orange.shadow.shadow_util import ShadowGui
from Orange.shadow.shadow_objects import ShadowBeam
from Orange.widgets.shadow_gui import ow_automatic_element

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas




class PlotXY(ow_automatic_element.AutomaticElement):

    name = "Plot XY"
    description = "Plotting Tools: Plot XY"
    icon = "icons/plot_xy.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Plotting Tools"
    keywords = ["data", "file", "load", "read"]


    inputs = [("Input Beam", Orange.shadow.ShadowBeam, "setBeam")]

    IMAGE_WIDTH = 900
    IMAGE_HEIGHT = 800

    want_main_area=1
    plot_canvas = None
    input_beam=None

    image_plane=Setting(0)
    image_plane_new_position=Setting(10)

    x_column_index=Setting(0)
    y_column_index=Setting(2)


    title=Setting("X,Z")

    def __init__(self):
        super().__init__()

        tabs_setting = gui.tabWidget(self.controlArea)
        tabs_setting.setFixedWidth(380)

        gui.button(self.controlArea, self, "Refresh", callback=self.plot_results)

        # graph tab
        tab_gen = ShadowGui.createTabPage(tabs_setting, "General")
        tab_his = ShadowGui.createTabPage(tabs_setting, "Histograms")
        tab_col = ShadowGui.createTabPage(tabs_setting, "Color")

        general_box = ShadowGui.widgetBox(tab_gen, "General Settings", addSpace=True, orientation="vertical", height=200)

        gui.comboBox(general_box, self, "image_plane", label="Position of the Image", \
                     items=["Previous OE Image Plane", "Different"], \
                     callback=self.set_ImagePlane, sendSelectedValue=False, orientation="horizontal")


        self.image_plane_box = ShadowGui.widgetBox(general_box, "", addSpace=True, orientation="vertical", height=70)
        self.image_plane_box_empty = ShadowGui.widgetBox(general_box, "", addSpace=True, orientation="vertical", height=70)

        ShadowGui.lineEdit(self.image_plane_box, self, "image_plane_new_position", "Image Plane new Position", valueType=float, orientation="horizontal")

        self.set_ImagePlane()

        self.x_column = gui.comboBox(general_box, self, "x_column_index", label="X Column", \
                                     items=["1: X", \
                                            "2: Y", \
                                            "3: Z", \
                                            "4: X'", \
                                            "5: Y'", \
                                            "6: Z'", \
                                            "11: Energy"], \
                                     sendSelectedValue=False, orientation="horizontal")

        self.y_column = gui.comboBox(general_box, self, "y_column_index", label="X Column", \
                                     items=["1: X", \
                                            "2: Y", \
                                            "3: Z", \
                                            "4: X'", \
                                            "5: Y'", \
                                            "6: Z'", \
                                            "11: Energy"], \
                                     sendSelectedValue=False, orientation="horizontal")

        ShadowGui.lineEdit(general_box, self, "title", "Title", valueType=str, orientation="horizontal")

        self.image_box = gui.widgetBox(self.mainArea, "Plot Result", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH)

    def set_ImagePlane(self):
        self.image_plane_box.setVisible(self.image_plane==1)
        self.image_plane_box_empty.setVisible(self.image_plane==0)

    def replace_fig(self, figure):
        if self.plot_canvas is not None:
            self.image_box.layout().removeWidget(self.plot_canvas)
        self.plot_canvas = FigureCanvas(figure)
        self.image_box.layout().addWidget(self.plot_canvas)


    def plot_xy(self, var_x, var_y, title, xtitle, ytitle):
        beam_to_plot = self.input_beam.beam

        if self.image_plane==1:
            historyItem=self.input_beam.getLastOE()

        #TODO RISOLVERE BUG
            if not historyItem is None:
                shadow_oe_new = copy.deepcopy(historyItem.shadow_oe)
                shadow_oe_new.oe.T_IMAGE = abs(self.image_plane_new_position)

                print("IMAGE: " + str(historyItem.shadow_oe.oe.T_IMAGE))
                print("OE NUMBER PREV: " + str(historyItem.input_beam.oe_number))
                print("OE NUMBER LAST: " + str(historyItem.output_beam.oe_number))

                new_shadow_beam = ShadowBeam.traceFromOENoHistory(historyItem.input_beam, shadow_oe_new)
                beam_to_plot = new_shadow_beam.beam

        plot = ST.plotxy(beam_to_plot,var_x,var_y,nolost=1,contour=6,nbins=100,nbins_h=100,calfwhm=1,title=title, xtitle=xtitle, ytitle=ytitle, noplot=1)
        self.replace_fig(plot.figure)

    def plot_results(self):
        if not self.input_beam == None:

            if self.x_column_index == 6: x = 11
            else: x = self.x_column_index + 1

            if self.y_column_index == 6: y = 11
            else: y = self.y_column_index + 1

            if self.title is None or str(self.title).strip()=="":
                   self.title = self.x_column.currentText()[2:] + "," + self.y_column.currentText()[2:]

            self.plot_xy(x, y, title=self.title, xtitle=self.x_column.currentText()[2:], ytitle=self.y_column.currentText()[2:])

    def setBeam(self, beam):
        self.input_beam = beam

        if self.is_automatic_run:
           self.plot_results()
