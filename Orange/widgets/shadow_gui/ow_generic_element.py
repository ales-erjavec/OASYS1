import sys, numpy, gc
from Orange.widgets import gui
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, qApp

#from PyMca.widgets.PlotWindow import PlotWindow
from Orange.widgets.settings import Setting

import Shadow.ShadowTools as ST
from Orange.shadow.shadow_util import ShadowPlot, ShadowGui

from Orange.widgets.shadow_gui import ow_automatic_element

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class GenericElement(ow_automatic_element.AutomaticElement):

    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 545

    want_main_area=1
    view_type=Setting(2)

    plotted_beam=None
    tab=[]

    def __init__(self, show_automatic_box=True):
        super().__init__(show_automatic_box)

        view_box = ShadowGui.widgetBox(self.mainArea, "Plotting Style", addSpace=False, orientation="horizontal")

        view_box_1 = ShadowGui.widgetBox(view_box, "", addSpace=False, orientation="vertical", width=350)
        view_box_empty = ShadowGui.widgetBox(view_box, "", addSpace=False, orientation="vertical", width=450)

        self.view_type_combo = gui.comboBox(view_box_1, self, "view_type", label="Select level of Plotting",
                                            labelWidth=220,
                                            items=["Detailed Plot", "Preview", "None"],
                                            callback=self.set_PlotQuality, sendSelectedValue=False, orientation="horizontal")

        self.tabs = gui.tabWidget(self.mainArea)

        self.initializeTabs()

        self.shadow_output = QtGui.QTextEdit()

        out_box = gui.widgetBox(self.mainArea, "Shadow Output", addSpace=True, orientation="horizontal")
        out_box.layout().addWidget(self.shadow_output)

        self.shadow_output.setFixedHeight(150)
        self.shadow_output.setFixedWidth(750)

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)
        for index in indexes:
            self.tabs.removeTab(size-1-index)

        self.tab = [gui.createTabPage(self.tabs, "X,Z"),
                    gui.createTabPage(self.tabs, "X',Z'"),
                    gui.createTabPage(self.tabs, "X,X'"),
                    gui.createTabPage(self.tabs, "Z,Z'"),
                    gui.createTabPage(self.tabs, "Energy")]

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

        self.plot_canvas = [None, None, None, None, None]


    def set_PlotQuality(self):
        self.progressBarInit()

        if not self.plotted_beam==None:

            self.initializeTabs()
            self.plot_results(self.plotted_beam, 80)

        self.progressBarFinished()

    def replaceObject(self, index, object):
        if self.plot_canvas[index] is not None:
            self.tab[index].layout().removeWidget(self.plot_canvas[index])
        return_object = self.plot_canvas[index]
        self.plot_canvas[index] = object
        self.tab[index].layout().addWidget(self.plot_canvas[index])

        return return_object

    def replace_fig(self, figure_canvas_index, plot):
        old_figure=None

        if not plot is None:
            old_figure = self.replaceObject(figure_canvas_index, FigureCanvas(plot.figure))
        else:
            if self.plot_canvas[figure_canvas_index] is not None:
                self.tab[figure_canvas_index].layout().removeWidget(self.plot_canvas[figure_canvas_index])
                old_figure=self.plot_canvas[figure_canvas_index]

        if not old_figure is None:
            old_figure.figure.clf()
            old_figure = None
            ST.plt.close("all")
            gc.collect()

    def replace_plot(self, plot_canvas_index, plot):
        old_figure = self.replaceObject(plot_canvas_index, plot)

        if not old_figure is None:
            old_figure = None
            ST.plt.close("all")
            gc.collect()


    def plot_xy_fast(self, beam_out, progressBarValue, var_x, var_y, plot_canvas_index, title, xtitle, ytitle):

        plot = ShadowPlot.plotxy_preview(beam_out.beam,var_x,var_y,nolost=1,contour=0,nbins=50,nbins_h=50,calfwhm=1,title=title, xtitle=xtitle, ytitle=ytitle, noplot=1)

        if not plot is None:
            self.replace_fig(plot_canvas_index, plot)
            self.progressBarSet(progressBarValue)

        '''
        x, y, good_only = ST.getshcol(beam_out.beam, (var_x, var_y, 10))

        t = numpy.where(good_only == 1)

        if not len(t)==0:
            plot = PlotWindow(roi=True, control=True, position=True)
            plot.setDefaultPlotLines(False)
            plot.setActiveCurveColor(color='darkblue')
            plot.addCurve(x[t], y[t], title, symbol=',', color='blue') #'+', '^',
            plot.setGraphXLabel(xtitle)
            plot.setGraphYLabel(ytitle)
            plot.setDrawModeEnabled(True, 'rectangle')
            plot.setZoomModeEnabled(True)

            self.replace_plot(plot_canvas_index, plot)
            self.progressBarSet(progressBarValue)
        '''
    def plot_xy(self, beam_out, progressBarValue, var_x, var_y, figure_canvas_index, title, xtitle, ytitle):
        plot = ST.plotxy(beam_out.beam,var_x,var_y,nolost=1,contour=6,nbins=100,nbins_h=100,calfwhm=1,title=title, xtitle=xtitle, ytitle=ytitle, noplot=1)

        if not plot is None:
            self.replace_fig(figure_canvas_index, plot)
            self.progressBarSet(progressBarValue)

    def plot_histo(self, beam_out, progressBarValue, var, figure_canvas_index, title, xtitle, ytitle):
        plot = ST.histo1(beam_out.beam,var,nolost=1,nbins=100,ref=1,calfwhm=1,title=title, xtitle=xtitle, ytitle=ytitle, noplot=1)

        if not plot is None:
            self.replace_fig(figure_canvas_index, plot)
            self.progressBarSet(progressBarValue)

    def plot_results(self, beam_out, progressBarValue=80):
        if not self.view_type == 2:

            self.view_type_combo.setEnabled(False)

            if self.view_type == 1:
                self.plot_xy_fast(beam_out, progressBarValue+4, 1, 3, plot_canvas_index=0, title="X,Z", xtitle="X", ytitle="Z")
                self.plot_xy_fast(beam_out, progressBarValue+8, 4, 6, plot_canvas_index=1, title="X',Z'", xtitle="X'", ytitle="Z'")
                self.plot_xy_fast(beam_out, progressBarValue+12, 1, 4, plot_canvas_index=2, title="X,X'", xtitle="X", ytitle="X'")
                self.plot_xy_fast(beam_out, progressBarValue+16, 3, 6, plot_canvas_index=3, title="Z,Z'", xtitle="Z", ytitle="Z'")
            elif self.view_type == 0:
                self.plot_xy(beam_out, progressBarValue+4, 1, 3, figure_canvas_index=0, title="X,Z", xtitle="X", ytitle="Z")
                self.plot_xy(beam_out, progressBarValue+8, 4, 6, figure_canvas_index=1, title="X',Z'", xtitle="X'", ytitle="Z'")
                self.plot_xy(beam_out, progressBarValue+12, 1, 4, figure_canvas_index=2, title="X,X'", xtitle="X", ytitle="X'")
                self.plot_xy(beam_out, progressBarValue+16, 3, 6, figure_canvas_index=3, title="Z,Z'", xtitle="Z", ytitle="Z'")

            self.plot_histo(beam_out, progressBarValue+20, 11, figure_canvas_index=4, title="Energy",xtitle="Energy", ytitle="Rays")

            self.view_type_combo.setEnabled(True)

        self.plotted_beam = beam_out

    def writeStdOut(self, text):
        cursor = self.shadow_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.shadow_output.setTextCursor(cursor)
        self.shadow_output.ensureCursorVisible()
        qApp.processEvents()

    def onReceivingInput(self):
        self.initializeTabs()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = GenericElement()
    ow.show()
    a.exec_()
    ow.saveSettings()