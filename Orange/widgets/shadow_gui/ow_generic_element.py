import os, sys
from Orange.widgets import gui
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPixmap, qApp

import Shadow.ShadowTools as ST

from Orange.widgets.shadow_gui import ow_automatic_element

class GenericElement(ow_automatic_element.AutomaticElement):

    IMAGE_WIDTH = 900
    IMAGE_HEIGHT = 600

    want_main_area=1

    def __init__(self):
        super().__init__()

        self.tabs = gui.tabWidget(self.mainArea)

        # graph tab
        self.tab1 = gui.createTabPage(self.tabs, "X,Z")
        self.tab2 = gui.createTabPage(self.tabs, "X',Z'")
        self.tab3 = gui.createTabPage(self.tabs, "X,X'")
        self.tab4 = gui.createTabPage(self.tabs, "Z,Z'")
        self.tab5 = gui.createTabPage(self.tabs, "Energy")

        self.label_plot_1 = gui.label(self.tab1, self, "", self.IMAGE_WIDTH)
        self.label_plot_2 = gui.label(self.tab2, self, "", self.IMAGE_WIDTH)
        self.label_plot_3 = gui.label(self.tab3, self, "", self.IMAGE_WIDTH)
        self.label_plot_4 = gui.label(self.tab4, self, "", self.IMAGE_WIDTH)
        self.label_plot_5 = gui.label(self.tab5, self, "", self.IMAGE_WIDTH)
        self.label_plot_1.setFixedHeight(self.IMAGE_HEIGHT)
        self.label_plot_2.setFixedHeight(self.IMAGE_HEIGHT)
        self.label_plot_3.setFixedHeight(self.IMAGE_HEIGHT)
        self.label_plot_4.setFixedHeight(self.IMAGE_HEIGHT)
        self.label_plot_5.setFixedHeight(self.IMAGE_HEIGHT)


        self.shadow_output = QtGui.QTextEdit()

        out_box = gui.widgetBox(self.mainArea, "Shadow Output", addSpace=True, orientation="horizontal")
        out_box.layout().addWidget(self.shadow_output)

        self.shadow_output.setFixedHeight(150)
        self.shadow_output.setFixedWidth(850)


    def plot_results(self, beam_out, progressBarValue=80):

       ####################### PLT1

       ST.plotxy(beam_out.beam,1,3,nolost=1,contour=6,nbins=100,nbins_h=100,calfwhm=1,title="X,Z", xtitle="X", ytitle="Z", noplot=1)
       #self.tab1.layout().addWidget(ST.plt.figure(dpi=None, facecolor='w', edgecolor='w', frameon=None).canvas)
       ST.plt.savefig("temp1.png", dpi=None, facecolor='w', edgecolor='w',
                  orientation='portrait', papertype=None, format=None,
                  transparent=False, bbox_inches=None, pad_inches=0.1,
                  frameon=None)

       pic1 = QPixmap("temp1.png")

       ratio = pic1.height()/pic1.width()

       self.label_plot_1.setFixedHeight(self.IMAGE_HEIGHT)
       self.label_plot_1.setPixmap(pic1.scaled(self.IMAGE_WIDTH, self.IMAGE_WIDTH*ratio, Qt.KeepAspectRatio, Qt.SmoothTransformation))

       self.progressBarSet(progressBarValue+4)

       ####################### PLT2

       ST.plotxy(beam_out.beam,4,6,nolost=1,contour=6,nbins=100,nbins_h=100,calfwhm=1,title="X',Z'",xtitle="X'", ytitle="Z'", noplot=1)
       ST.plt.savefig("temp2.png", dpi=None, facecolor='w', edgecolor='w',
                  orientation='portrait', papertype=None, format=None,
                  transparent=False, bbox_inches=None, pad_inches=0.1,
                  frameon=None)

       pic2 = QPixmap("temp2.png")

       ratio = pic2.height()/pic2.width()

       self.label_plot_2.setFixedHeight(self.IMAGE_HEIGHT)
       self.label_plot_2.setPixmap(pic2.scaled(self.IMAGE_WIDTH, self.IMAGE_WIDTH*ratio, Qt.KeepAspectRatio, Qt.SmoothTransformation))

       self.progressBarSet(progressBarValue+8)

       ####################### PLT3

       ST.plotxy(beam_out.beam,1,4,nolost=1,contour=6,nbins=100,nbins_h=100,calfwhm=1,title="X,X'", xtitle="X", ytitle="X'", noplot=1)
       ST.plt.savefig("temp3.png", dpi=None, facecolor='w', edgecolor='w',
                  orientation='portrait', papertype=None, format=None,
                  transparent=False, bbox_inches=None, pad_inches=0.1,
                  frameon=None)

       pic3 = QPixmap("temp3.png")

       ratio = pic3.height()/pic3.width()

       self.label_plot_3.setFixedHeight(self.IMAGE_HEIGHT)
       self.label_plot_3.setPixmap(pic3.scaled(self.IMAGE_WIDTH, self.IMAGE_WIDTH*ratio, Qt.KeepAspectRatio, Qt.SmoothTransformation))

       self.progressBarSet(progressBarValue+12)

       ####################### PLT4

       ST.plotxy(beam_out.beam,3,6,nolost=1,contour=6,nbins=100,nbins_h=100,calfwhm=1,title="Z,Z'",xtitle="Z", ytitle="Z'", noplot=1)
       ST.plt.savefig("temp4.png", dpi=None, facecolor='w', edgecolor='w',
                  orientation='portrait', papertype=None, format=None,
                  transparent=False, bbox_inches=None, pad_inches=0.1,
                  frameon=None)

       pic4 = QPixmap("temp4.png")

       ratio = pic4.height()/pic4.width()

       self.label_plot_4.setFixedHeight(self.IMAGE_HEIGHT)
       self.label_plot_4.setPixmap(pic4.scaled(self.IMAGE_WIDTH, self.IMAGE_WIDTH*ratio, Qt.KeepAspectRatio, Qt.SmoothTransformation))

       self.progressBarSet(progressBarValue+16)

       ####################### PLT5

       ST.histo1(beam_out.beam,11,nolost=1,nbins=100,ref=1,calfwhm=1,title="Energy",xtitle="Energy", ytitle="Rays", noplot=1)
       ST.plt.savefig("temp5.png", dpi=None, facecolor='w', edgecolor='w',
                  orientation='portrait', papertype=None, format=None,
                  transparent=False, bbox_inches=None, pad_inches=0.1,
                  frameon=None)

       pic5 = QPixmap("temp5.png")

       ratio = pic5.height()/pic5.width()

       self.label_plot_5.setFixedHeight(self.IMAGE_HEIGHT)
       self.label_plot_5.setPixmap(pic5.scaled(self.IMAGE_WIDTH, self.IMAGE_WIDTH*ratio, Qt.KeepAspectRatio, Qt.SmoothTransformation))

       self.progressBarSet(progressBarValue+20)

       os.remove("temp1.png")
       os.remove("temp2.png")
       os.remove("temp3.png")
       os.remove("temp4.png")
       os.remove("temp5.png")

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