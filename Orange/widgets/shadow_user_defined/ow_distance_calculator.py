import math
from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting
from Orange.shadow.shadow_util import ShadowGui
import Orange.canvas.resources as resources

from PyQt4 import QtGui

class MonochromatorDistanceCalculator(widget.OWWidget):

    name = "Monochromator Distance Calculator"
    description = "User Defined: Monochromator Distance Calculator"
    icon = "icons/distance_calculator.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "User Defined"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 0

    vertical_quote = Setting(0.0)
    total_distance = Setting(0.0)
    bragg_angle = Setting(0.0)

    d_1 = 0.0
    d_2 = 0.0

    image_path = resources.package_dirname("Orange.widgets.shadow_user_defined") + "/icons/distances.png"

    def __init__(self):
        self.setFixedWidth(590)
        self.setFixedHeight(580)

        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Optical Parameters", addSpace=True, orientation="vertical", width=570, height=500)

        figure_box = ShadowGui.widgetBox(left_box_1, "", addSpace=True, orientation="horizontal", width=550, height=350)

        label = QtGui.QLabel("")
        label.setPixmap(QtGui.QPixmap(self.image_path))

        figure_box.layout().addWidget(label)

        ShadowGui.lineEdit(left_box_1, self, "vertical_quote", "Vertical Distance (H) [cm]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "total_distance", "First Crystal - Mirror Distance (D) [cm]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "bragg_angle", "First Crystal Reflection Angle [deg]", labelWidth=300, valueType=float, orientation="horizontal")

        gui.separator(left_box_1, height=20)

        le = ShadowGui.lineEdit(left_box_1, self, "d_1", "Crystal to Crystal Distance (d_1) [cm]", labelWidth=300, valueType=float, orientation="horizontal")
        le.setReadOnly(True)
        font = QtGui.QFont(le.font())
        font.setBold(True)
        le.setFont(font)
        palette = QtGui.QPalette(le.palette()) # make a copy of the palette
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor('dark blue'))
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(243, 240, 160))
        le.setPalette(palette)

        le = ShadowGui.lineEdit(left_box_1, self, "d_2", "Crystal to Mirror Distance (d_2) [cm]", labelWidth=300, valueType=float, orientation="horizontal")
        le.setReadOnly(True)
        font = QtGui.QFont(le.font())
        font.setBold(True)
        le.setFont(font)
        palette = QtGui.QPalette(le.palette()) # make a copy of the palette
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor('dark blue'))
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(243, 240, 160))
        le.setPalette(palette)

        button = gui.button(self.controlArea, self, "Calculate Distances", callback=self.calculate)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

    def calculate(self):
        twotheta = math.radians(2*(90-self.bragg_angle))

        self.d_1 = self.vertical_quote/math.sin(twotheta)
        self.d_2 = self.total_distance - self.vertical_quote/math.tan(twotheta)

