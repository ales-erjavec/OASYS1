import sys
import Orange
from PyQt4 import QtGui
from PyQt4.QtGui import qApp
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.shadow.shadow_objects import ShadowBeam, EmittingStream, TTYGrabber

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

    IMAGE_WIDTH = 920
    IMAGE_HEIGHT = 650

    want_main_area=1
    plot_canvas=None
    input_beam=None

    image_plane=Setting(0)
    image_plane_new_position=Setting(10.0)
    image_plane_rel_abs_position=Setting(0)

    x_column_index=Setting(11)

    title=Setting("Energy")


    def __init__(self):
        super().__init__()

        tabs_setting = gui.tabWidget(self.controlArea)
        tabs_setting.setFixedWidth(380)

        gui.button(self.controlArea, self, "Refresh", callback=self.plot_results)

        # graph tab
        tab_gen = ShadowGui.createTabPage(tabs_setting, "Histogram")

        general_box = ShadowGui.widgetBox(tab_gen, "General Settings", addSpace=True, orientation="vertical", height=200)

        gui.comboBox(general_box, self, "image_plane", label="Position of the Image",
                     items=["On Image Plane", "Retraced"],
                     callback=self.set_ImagePlane, sendSelectedValue=False, orientation="horizontal")


        self.image_plane_box = ShadowGui.widgetBox(general_box, "", addSpace=True, orientation="vertical", height=110)
        self.image_plane_box_empty = ShadowGui.widgetBox(general_box, "", addSpace=True, orientation="vertical", height=110)

        ShadowGui.lineEdit(self.image_plane_box, self, "image_plane_new_position", "Image Plane new Position", labelWidth=220, valueType=float, orientation="horizontal")

        gui.comboBox(self.image_plane_box, self, "image_plane_rel_abs_position", label="Position Type", labelWidth=250,
                     items=["Relative to O.E. position", "Relative to Image Plane position"], sendSelectedValue=False, orientation="horizontal")

        self.set_ImagePlane()

        self.x_column = gui.comboBox(general_box, self, "x_column_index", label="Column", labelWidth=250,
                                     items=["1: X",
                                            "2: Y",
                                            "3: Z",
                                            "4: X'",
                                            "5: Y'",
                                            "6: Z'",
                                            "11: Energy"],
                                     sendSelectedValue=False, orientation="horizontal")

        ShadowGui.lineEdit(general_box, self, "title", "Title", labelWidth=150, valueType=str, orientation="horizontal")

        self.image_box = gui.widgetBox(self.mainArea, "Plot Result", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH)

        self.shadow_output = QtGui.QTextEdit()

        out_box = gui.widgetBox(self.mainArea, "Shadow Output", addSpace=True, orientation="horizontal")
        out_box.layout().addWidget(self.shadow_output)
        out_box.setFixedWidth(self.IMAGE_WIDTH)

        self.shadow_output.setFixedHeight(100)
        self.shadow_output.setFixedWidth(self.IMAGE_WIDTH-50)

    def set_ImagePlane(self):
        self.image_plane_box.setVisible(self.image_plane==1)
        self.image_plane_box_empty.setVisible(self.image_plane==0)

    def replace_fig(self, plot):
        if self.plot_canvas is not None:
            self.image_box.layout().removeWidget(self.plot_canvas)
        if not plot is None:
            self.plot_canvas = FigureCanvas(plot.figure)
            self.image_box.layout().addWidget(self.plot_canvas)

    def plot_histo(self, var_x, title, xtitle, ytitle):
        beam_to_plot = self.input_beam.beam


        try:
            if self.image_plane==1:
                new_shadow_beam = self.input_beam.duplicate(history = False)

                dist = 0.0
                if self.image_plane_rel_abs_position == 1:
                    dist = abs(self.image_plane_new_position)
                else:
                    historyItem=self.input_beam.getOEHistory(oe_number=self.input_beam.oe_number)

                    if historyItem is None: raise Exception("Calculation impossible: Beam has no history")

                    dist = self.image_plane_new_position - historyItem.shadow_oe.oe.T_IMAGE

                new_shadow_beam.beam.retrace(dist)

                beam_to_plot = new_shadow_beam.beam

            plot = ST.histo1(beam_to_plot,var_x,nolost=1,nbins=100,ref=1,calfwhm=1,title=title, xtitle=xtitle, ytitle=ytitle, noplot=1)
            self.replace_fig(plot)
        except:
            pass

    def plot_results(self):

        sys.stdout = EmittingStream(textWritten=self.writeStdOut)
        grabber = TTYGrabber()
        grabber.start()


        if not self.input_beam == None:

            if self.x_column_index == 6: x = 11
            else: x = self.x_column_index + 1

            auto_title = self.x_column.currentText().split(":", 2)[1]

            if self.title is None or str(self.title).strip()=="":
                   self.title = auto_title

            self.plot_histo(x, title=self.title, xtitle=auto_title, ytitle="Rays")

        grabber.stop()

        for row in grabber.ttyData:
           self.writeStdOut(row)

        qApp.processEvents()

    def setBeam(self, beam):
        self.input_beam = beam

        if self.is_automatic_run:
           self.plot_results()

    def writeStdOut(self, text):
        cursor = self.shadow_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.shadow_output.setTextCursor(cursor)
        self.shadow_output.ensureCursorVisible()
        qApp.processEvents()