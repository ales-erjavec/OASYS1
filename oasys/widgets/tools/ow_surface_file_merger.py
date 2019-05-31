import os, sys

import numpy
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QSizePolicy
from PyQt5.QtGui import QTextCursor, QFont, QPalette, QColor, QPixmap

from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from orangewidget import gui, widget
from orangewidget.settings import Setting

from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from oasys.util.oasys_objects import OasysPreProcessorData, OasysErrorProfileData, OasysSurfaceData

import oasys.util.oasys_util as OU

try:
    from mpl_toolkits.mplot3d import Axes3D  # necessario per caricare i plot 3D
except:
    pass

class OWSurfaceFileReader(OWWidget):
    name = "Surface File Merger"
    id = "surface_file_merger"
    description = "Surface File Merger"
    icon = "icons/surface_merger.png"
    author = "Luca Rebuffi"
    maintainer_email = "lrebuffi@anl.gov"
    priority = 5
    category = ""
    keywords = ["surface_file_mberger"]

    inputs = [("Surface Data #1", object, "set_input_1"),
              ("Surface Data #2", object, "set_input_2"),
              ]

    outputs = [{"name": "PreProcessor_Data",
                "type": OasysPreProcessorData,
                "doc": "PreProcessor Data",
                "id": "PreProcessor_Data"},
               {"name": "Surface_Data",
                "type": OasysSurfaceData,
                "doc": "Surface Data",
                "id": "Surface_Data"}]


    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 645

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 618

    xx = None
    yy = None
    zz = None

    xx_1 = None
    yy_1 = None
    zz_1 = None

    xx_2 = None
    yy_2 = None
    zz_2 = None

    surface_data = None
    preprocessor_data = None

    surface_file_name = Setting('merged_surface.hdf5')

    def __init__(self):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width() * 0.05),
                               round(geom.height() * 0.05),
                               round(min(geom.width() * 0.98, self.MAX_WIDTH)),
                               round(min(geom.height() * 0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Read Surface", callback=self.read_surface)
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Render Surface", callback=self.render_surface)
        button.setFixedHeight(45)

        input_box_l = oasysgui.widgetBox(self.controlArea, "Input", addSpace=True, orientation="horizontal", height=self.TABS_AREA_HEIGHT)

        self.le_surface_file_name = oasysgui.lineEdit(input_box_l, self, "surface_file_name", "Surface File Name",
                                                        labelWidth=120, valueType=str, orientation="horizontal")

        gui.button(input_box_l, self, "...", callback=self.selectSurfaceFile)


        self.figure = Figure(figsize=(600, 600))
        self.figure.patch.set_facecolor('white')

        self.axis = self.figure.add_subplot(111, projection='3d')

        self.axis.set_zlabel("Z [m]")

        self.figure_canvas = FigureCanvasQTAgg(self.figure)

        self.mainArea.layout().addWidget(self.figure_canvas)

        gui.rubber(self.mainArea)


    def set_input_1(self, data):
        if not data is None:
            if isinstance(data, OasysPreProcessorData):
                self.xx_1 = data.error_profile_data.surface_data.xx
                self.yy_1 = data.error_profile_data.surface_data.yy
                self.zz_1 = data.error_profile_data.surface_data.zz
            elif isinstance(data, OasysSurfaceData):
                self.xx_1 = data.xx
                self.yy_1 = data.yy
                self.zz_1 = data.zz
            else:
                QMessageBox.critical(self, "Error",
                                     "Data Type #1 not recognized",
                                     QMessageBox.Ok)

    def set_input_2(self, data):
        if not data is None:
            if isinstance(data, OasysPreProcessorData):
                self.xx_2 = data.error_profile_data.surface_data.xx
                self.yy_2 = data.error_profile_data.surface_data.yy
                self.zz_2 = data.error_profile_data.surface_data.zz
            elif isinstance(data, OasysSurfaceData):
                self.xx_2 = data.xx
                self.yy_2 = data.yy
                self.zz_2 = data.zz
            else:
                QMessageBox.critical(self, "Error",
                                     "Data Type #2 not recognized",
                                     QMessageBox.Ok)

    def compute(self, plot_data=False):
        try:
            if not self.xx_1 is None and not self.xx_2 is None:
                xx_1 = self.xx_1
                yy_1 = self.yy_1
                zz_1 = self.zz_1

                xx_2 = self.xx_2
                yy_2 = self.yy_2
                zz_2 = self.zz_2

                if not (len(xx_1) == len(xx_2) and
                        len(yy_1) == len(yy_1) and
                        round(xx_1[0], 6) == round(xx_2[0], 6) and
                        round(xx_1[-1], 6) == round(xx_2[-1], 6) and
                        round(yy_1[0], 6) == round(yy_2[0], 6) and
                        round(yy_1[-1], 6) == round(yy_2[-1], 6)):
                    raise ValueError("The two surfaces cannot be merged: dimensions or binning incompatible")

                xx = xx_2
                yy = yy_2
                zz = zz_2 + zz_1

                self.axis.clear()

                x_to_plot, y_to_plot = numpy.meshgrid(xx, yy)

                if plot_data:
                    self.axis.plot_surface(x_to_plot, y_to_plot, zz,
                                           rstride=1, cstride=1, cmap=cm.autumn, linewidth=0.5, antialiased=True)

                    self.axis.set_xlabel("X [m]")
                    self.axis.set_ylabel("Y [m]")
                    self.axis.set_zlabel("Z [m]")
                    self.axis.mouse_init()

                    self.figure_canvas.draw()

                if not (self.surface_file_name.endswith("hd5") or self.surface_file_name.endswith("hdf5") or self.surface_file_name.endswith("hdf")):
                    self.surface_file_name += ".hdf5"

                OU.write_surface_file(zz, xx, yy, self.surface_file_name)

                error_profile_x_dim = abs(xx[-1] - xx[0])
                error_profile_y_dim = abs(yy[-1] - yy[0])


                self.send("PreProcessor_Data", OasysPreProcessorData(error_profile_data=OasysErrorProfileData(surface_data=OasysSurfaceData(xx=xx,
                                                                                                                                            yy=yy,
                                                                                                                                            zz=zz,
                                                                                                                                            surface_data_file=self.surface_file_name),
                                                                                                              error_profile_x_dim=error_profile_x_dim,
                                                                                                              error_profile_y_dim=error_profile_y_dim)))
                self.send("Surface_Data", OasysSurfaceData(xx=xx,
                                                           yy=yy,
                                                           zz=zz,
                                                           surface_data_file=self.surface_file_name))

        except Exception as exception:
            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception


    def read_surface(self):
        self.compute(plot_data=False)

    def render_surface(self):
        self.compute(plot_data=True)

    def selectSurfaceFile(self):
        self.le_surface_file_name.setText(oasysgui.selectFileFromDialog(self, self.surface_file_name, "Select Input File", file_extension_filter="HDF5 Files (*.hdf5)"))


