import os, sys
from Orange.widgets import gui
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPixmap, qApp

import Shadow.ShadowTools as ST

from Orange.widgets.shadow_gui import ow_automatic_element

import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class GenericElement(ow_automatic_element.AutomaticElement):

    IMAGE_WIDTH = 900
    IMAGE_HEIGHT = 600

    want_main_area=1

    def __init__(self):
        super().__init__()

        self.figure_canvas = [None, None, None, None, None]

        self.tabs = gui.tabWidget(self.mainArea)
        self.tab = [gui.createTabPage(self.tabs, "X,Z"),
                    gui.createTabPage(self.tabs, "X',Z'"),
                    gui.createTabPage(self.tabs, "X,X'"),
                    gui.createTabPage(self.tabs, "Z,Z'"),
                    gui.createTabPage(self.tabs, "Energy")]

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

        self.shadow_output = QtGui.QTextEdit()

        out_box = gui.widgetBox(self.mainArea, "Shadow Output", addSpace=True, orientation="horizontal")
        out_box.layout().addWidget(self.shadow_output)

        self.shadow_output.setFixedHeight(150)
        self.shadow_output.setFixedWidth(850)

    def replace_fig(self, figure_canvas_index, figure):
        if self.figure_canvas[figure_canvas_index] is not None:
            self.tab[figure_canvas_index].layout().removeWidget(self.figure_canvas[figure_canvas_index])
        self.figure_canvas[figure_canvas_index] = FigureCanvas(figure)
        self.tab[figure_canvas_index].layout().addWidget(self.figure_canvas[figure_canvas_index])


    def plot_xy(self, beam_out, progressBarValue, var_x, var_y, figure_canvas_index, title, xtitle, ytitle):
        plot = ST.plotxy(beam_out.beam,var_x,var_y,nolost=1,contour=6,nbins=100,nbins_h=100,calfwhm=1,title=title, xtitle=xtitle, ytitle=ytitle, noplot=1)

        self.replace_fig(figure_canvas_index, plot.figure)
        self.progressBarSet(progressBarValue)

    def plot_histo(self, beam_out, progressBarValue, var, figure_canvas_index, title, xtitle, ytitle):
        plot = ST.histo1(beam_out.beam,var,nolost=1,nbins=100,ref=1,calfwhm=1,title=title, xtitle=xtitle, ytitle=ytitle, noplot=1)

        self.replace_fig(figure_canvas_index, plot.figure)
        self.progressBarSet(progressBarValue)

    def plot_results(self, beam_out, progressBarValue=80):

        self.plot_xy(beam_out, progressBarValue+4, 1, 3, figure_canvas_index=0, title="X,Z", xtitle="X", ytitle="Z")
        self.plot_xy(beam_out, progressBarValue+8, 4, 6, figure_canvas_index=1, title="X',Z'", xtitle="X'", ytitle="Z'")
        self.plot_xy(beam_out, progressBarValue+12, 1, 4, figure_canvas_index=2, title="X,X'", xtitle="X", ytitle="X'")
        self.plot_xy(beam_out, progressBarValue+16, 3, 6, figure_canvas_index=3, title="Z,Z'", xtitle="Z", ytitle="Z'")
        self.plot_histo(beam_out, progressBarValue+20, 11, figure_canvas_index=4, title="Energy",xtitle="Energy", ytitle="Rays")


    def writeStdOut(self, text):
        cursor = self.shadow_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.shadow_output.setTextCursor(cursor)
        self.shadow_output.ensureCursorVisible()
        qApp.processEvents()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = GenericElement()
    ow.show()
    a.exec_()
    ow.saveSettings()