import sys, numpy
import Orange
from PyQt4 import QtGui
from PyQt4.QtGui import qApp
from Orange.widgets import gui
from Orange.widgets.settings import Setting

import Shadow.ShadowTools as ST

from Orange.shadow.shadow_util import ShadowGui, ConfirmDialog
from Orange.shadow.shadow_objects import ShadowBeam, EmittingStream, TTYGrabber
from Orange.widgets.shadow_gui.ow_automatic_element import AutomaticElement

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas, Figure

class PlotXY(AutomaticElement):

    name = "Plot XY"
    description = "Plotting Tools: Plot XY"
    icon = "icons/plot_xy.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
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

    x_column_index=Setting(0)
    y_column_index=Setting(2)

    x_range=Setting(0)
    x_range_min=Setting(0.0)
    x_range_max=Setting(0)

    y_range=Setting(0.0)
    y_range_min=Setting(0.0)
    y_range_max=Setting(0.0)

    rays=Setting(1)
    cartesian_axis=Setting(1)
    plot_type=Setting(0)

    number_of_bins=Setting(75)
    histogram_fwhm=Setting(0)
    binning_for_contour=Setting(25)

    title=Setting("X,Z")

    keep_result=Setting(0)

    def __init__(self):
        super().__init__()

        tabs_setting = gui.tabWidget(self.controlArea)
        tabs_setting.setFixedWidth(380)

        gui.button(self.controlArea, self, "Refresh", callback=self.plot_results)

        # graph tab
        tab_gen = ShadowGui.createTabPage(tabs_setting, "General")
        tab_his = ShadowGui.createTabPage(tabs_setting, "Histograms")
        tab_col = ShadowGui.createTabPage(tabs_setting, "Color")

        incremental_box = ShadowGui.widgetBox(tab_gen, "Screen Position Settings", addSpace=True, orientation="horizontal", height=80)

        gui.checkBox(incremental_box, self, "keep_result", "Keep Result")
        gui.button(incremental_box, self, "Clear", callback=self.clearResults)

        screen_box = ShadowGui.widgetBox(tab_gen, "Incremental Result", addSpace=True, orientation="vertical", height=140)

        self.image_plane_combo = gui.comboBox(screen_box, self, "image_plane", label="Position of the Image",
                                            items=["On Image Plane", "Retraced"],
                                            callback=self.set_ImagePlane, sendSelectedValue=False, orientation="horizontal")

        self.image_plane_box = ShadowGui.widgetBox(screen_box, "", addSpace=True, orientation="vertical", width=350, height=110)
        self.image_plane_box_empty = ShadowGui.widgetBox(screen_box, "", addSpace=True, orientation="vertical", width=350, height=110)

        ShadowGui.lineEdit(self.image_plane_box, self, "image_plane_new_position", "Image Plane new Position", labelWidth=220, valueType=float, orientation="horizontal")

        gui.comboBox(self.image_plane_box, self, "image_plane_rel_abs_position", label="Position Type", labelWidth=250,
                     items=["Absolute", "Relative"], sendSelectedValue=False, orientation="horizontal")

        self.set_ImagePlane()

        general_box = ShadowGui.widgetBox(tab_gen, "General Settings", addSpace=True, orientation="vertical", height=400)

        ShadowGui.lineEdit(general_box, self, "title", "Title", labelWidth=150, valueType=str, orientation="horizontal")

        gui.separator(general_box, width=350)

        self.x_column = gui.comboBox(general_box, self, "x_column_index", label="X Column",labelWidth=250,
                                     items=["1: X",
                                            "2: Y",
                                            "3: Z",
                                            "4: X'",
                                            "5: Y'",
                                            "6: Z'",
                                            "11: Energy"],
                                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(general_box, self, "x_range", label="X Range", labelWidth=250,
                                     items=["<Default>",
                                            "Set.."],
                                     callback=self.set_XRange, sendSelectedValue=False, orientation="horizontal")

        self.xrange_box = ShadowGui.widgetBox(general_box, "", addSpace=True, orientation="vertical", width=350, height=110)
        self.xrange_box_empty = ShadowGui.widgetBox(general_box, "", addSpace=True, orientation="vertical", width=350, height=110)

        ShadowGui.lineEdit(self.xrange_box, self, "x_range_min", "X min", labelWidth=220, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.xrange_box, self, "x_range_max", "X max", labelWidth=220, valueType=float, orientation="horizontal")

        self.set_XRange()

        self.y_column = gui.comboBox(general_box, self, "y_column_index", label="Y Column",labelWidth=250,
                                     items=["1: X",
                                            "2: Y",
                                            "3: Z",
                                            "4: X'",
                                            "5: Y'",
                                            "6: Z'",
                                            "11: Energy"],
                                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(general_box, self, "y_range", label="Y Range",labelWidth=250,
                                     items=["<Default>",
                                            "Set.."],
                                     callback=self.set_YRange, sendSelectedValue=False, orientation="horizontal")

        self.yrange_box = ShadowGui.widgetBox(general_box, "", addSpace=True, orientation="vertical", width=350, height=150)
        self.yrange_box_empty = ShadowGui.widgetBox(general_box, "", addSpace=True, orientation="vertical", width=350, height=150)

        ShadowGui.lineEdit(self.yrange_box, self, "y_range_min", "Y min", labelWidth=220, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(self.yrange_box, self, "y_range_max", "Y max", labelWidth=220, valueType=float, orientation="horizontal")

        self.set_YRange()


        gui.comboBox(general_box, self, "rays", label="Rays", labelWidth=250,
                                     items=["All rays",
                                            "Good Only",
                                            "Lost Only"],
                                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(general_box, self, "cartesian_axis", label="Cartesian Axis",labelWidth=300,
                                     items=["No",
                                            "Yes"],
                                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(general_box, self, "plot_type", label="Plot Type",labelWidth=200,
                                     items=["Scattered",
                                            "Contour without Ref",
                                            "Contour with Ref",
                                            "Color Contour without Ref",
                                            "Color Contour with Ref",
                                            "Pixelized without Ref",
                                            "Pixelized with Ref"],
                                     sendSelectedValue=False, orientation="horizontal")

        histograms_box = ShadowGui.widgetBox(tab_his, "Histograms settings", addSpace=True, orientation="vertical", height=550)

        ShadowGui.lineEdit(histograms_box, self, "number_of_bins", "Number of Bins", labelWidth=250, valueType=int, orientation="horizontal")

        gui.comboBox(histograms_box, self, "histogram_fwhm", label="Histogram FWHM",labelWidth=300,
                     items=["No", "Yes"],
                     sendSelectedValue=False, orientation="horizontal")

        ShadowGui.lineEdit(histograms_box, self, "binning_for_contour", "Binning for CONTOURS", labelWidth=250, valueType=int, orientation="horizontal")

        self.image_box = gui.widgetBox(self.mainArea, "Plot Result", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH)

        self.plot_canvas = FigureCanvas(Figure())
        self.image_box.layout().addWidget(self.plot_canvas)

        self.shadow_output = QtGui.QTextEdit()

        out_box = gui.widgetBox(self.mainArea, "Shadow Output", addSpace=True, orientation="horizontal")
        out_box.layout().addWidget(self.shadow_output)
        out_box.setFixedWidth(self.IMAGE_WIDTH)

        self.shadow_output.setFixedHeight(100)
        self.shadow_output.setFixedWidth(self.IMAGE_WIDTH-50)

    def clearResults(self):
        if ConfirmDialog.confirmed(parent=self):
            self.input_beam = ShadowBeam()
            if self.plot_canvas is not None:
                self.image_box.layout().removeWidget(self.plot_canvas)

            self.plot_canvas = FigureCanvas(Figure())
            self.image_box.layout().addWidget(self.plot_canvas)

    def set_ImagePlane(self):
        self.image_plane_box.setVisible(self.image_plane==1)
        self.image_plane_box_empty.setVisible(self.image_plane==0)

    def set_XRange(self):
        self.xrange_box.setVisible(self.x_range == 1)
        self.xrange_box_empty.setVisible(self.x_range == 0)

    def set_YRange(self):
        self.yrange_box.setVisible(self.y_range == 1)
        self.yrange_box_empty.setVisible(self.y_range == 0)

    def replace_fig(self, plot):
        if self.plot_canvas is not None:
            self.image_box.layout().removeWidget(self.plot_canvas)

        if not plot is None:
            self.plot_canvas = FigureCanvas(plot.figure)
            self.image_box.layout().addWidget(self.plot_canvas)

    def plot_xy(self, var_x, var_y, title, xtitle, ytitle):

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

            xrange = None
            yrange = None

            if self.cartesian_axis == 1:

                x_max = 0
                y_max = 0
                x_min = 0
                y_min = 0

                x, y, good_only = ST.getshcol(beam_to_plot, (var_x, var_y, 10))

                go = numpy.where(good_only == 1)
                lo = numpy.where(good_only == 0)

                if self.rays == 0:
                    x_max = numpy.array(x[0:], float).max()
                    y_max = numpy.array(y[0:], float).max()
                    x_min = numpy.array(x[0:], float).min()
                    y_min = numpy.array(y[0:], float).min()
                elif self.rays == 1:
                    x_max = numpy.array(x[go], float).max()
                    y_max = numpy.array(y[go], float).max()
                    x_min = numpy.array(x[go], float).min()
                    y_min = numpy.array(y[go], float).min()
                elif self.rays == 2:
                    x_max = numpy.array(x[lo], float).max()
                    y_max = numpy.array(y[lo], float).max()
                    x_min = numpy.array(x[lo], float).min()
                    y_min = numpy.array(y[lo], float).min()

                temp = numpy.array([x_max, y_max, x_min, y_min], float)

                xrange = [temp.min(), temp.max()]
                yrange = [temp.min(), temp.max()]

            if self.x_range == 1:
                xrange = [self.x_range_min, self.x_range_max]

            if self.y_range == 1:
                yrange = [self.y_range_min, self.y_range_max]

            plot = ST.plotxy(beam=beam_to_plot,
                             cols1=var_x,
                             cols2=var_y,
                             nolost=self.rays,
                             contour=self.plot_type,
                             nbins=int(self.binning_for_contour),
                             nbins_h=int(self.number_of_bins),
                             calfwhm=self.histogram_fwhm,
                             title=title,
                             xtitle=xtitle,
                             ytitle=ytitle,
                             xrange=xrange,
                             yrange=yrange,
                             noplot=1)

            self.replace_fig(plot)
        except Exception as exception:
            self.error(0, exception.args[0])
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                exception.args[0],
                QtGui.QMessageBox.Ok)

    def plot_results(self):

        self.error()

        sys.stdout = EmittingStream(textWritten=self.writeStdOut)
        if self.trace_shadow:
            grabber = TTYGrabber()
            grabber.start()

        if not self.input_beam == None:

            if self.x_column_index == 6: x = 11
            else: x = self.x_column_index + 1

            if self.y_column_index == 6: y = 11
            else: y = self.y_column_index + 1

            auto_x_title = self.x_column.currentText().split(":", 2)[1]
            auto_y_title = self.y_column.currentText().split(":", 2)[1]

            if self.title is None or str(self.title).strip()=="":
                   self.title = auto_x_title + "," + auto_y_title

            self.plot_xy(x, y, title=self.title, xtitle=auto_x_title, ytitle=auto_y_title)

        if self.trace_shadow:
            grabber.stop()

            for row in grabber.ttyData:
               self.writeStdOut(row)

        qApp.processEvents()

    def setBeam(self, beam):
        if self.keep_result==1 and not self.input_beam is None:
            self.input_beam = ShadowBeam.mergeBeams(self.input_beam, beam)
        else:
            self.input_beam = beam

        if (self.input_beam.oe_number==0): # IS THE SOURCE
            self.image_plane = 0
            self.set_ImagePlane()
            self.image_plane_combo.setEnabled(False)
            
        if self.is_automatic_run:
           self.plot_results()

    def writeStdOut(self, text):
        cursor = self.shadow_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.shadow_output.setTextCursor(cursor)
        self.shadow_output.ensureCursorVisible()
        qApp.processEvents()
