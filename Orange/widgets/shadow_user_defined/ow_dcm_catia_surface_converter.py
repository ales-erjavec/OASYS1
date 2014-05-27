import sys, math, os, numpy
from scipy import interpolate
from Orange.widgets import widget
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, qApp

from Orange.shadow.shadow_util import ShadowGui

class DCMCatiaSurfaceConverter(widget.OWWidget):

    name = "DCM CATIA Surface Converter"
    description = "User Defined: DCMCatiaSurfaceConverter"
    icon = "icons/dcm_surface_converter.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 3
    category = "User Defined"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 0

    number_of_x_cells = Setting(121)
    number_of_y_cells = Setting(81)

    x_min = Setting(-6.0)
    x_max = Setting(6.0)
    y_min = Setting(-4.0)
    y_max = Setting(4.0)

    n_sigma_x = Setting(1.5)
    n_sigma_y = Setting(1.0)

    surface_file_name=Setting("")

    debug_mode = False

    def __init__(self):
        self.setFixedWidth(590)
        self.setFixedHeight(380)

        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Ansys Surface", addSpace=True, orientation="vertical")

        select_file_box = ShadowGui.widgetBox(left_box_1, "", addSpace=True, orientation="horizontal", height=50)

        self.le_surface_file_name = ShadowGui.lineEdit(select_file_box, self, "surface_file_name", "Surface File Name", labelWidth=150, valueType=str, orientation="horizontal")
        self.le_surface_file_name.setFixedWidth(300)

        pushButton = gui.button(select_file_box, self, "...")
        pushButton.clicked.connect(self.selectSurfaceFile)

        ShadowGui.lineEdit(left_box_1, self, "x_min", "X Min", labelWidth=350, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "x_max", "X Max", labelWidth=350, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "y_min", "Y Min", labelWidth=350, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "y_max", "Y Max", labelWidth=350, valueType=float, orientation="horizontal")

        gui.separator(left_box_1)

        ShadowGui.lineEdit(left_box_1, self, "number_of_x_cells", "Number of X cells", labelWidth=350, valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "number_of_y_cells", "Number of Y cells", labelWidth=350, valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "n_sigma_x", "N Sigma X", labelWidth=350, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "n_sigma_y", "N Sigma Y", labelWidth=350, valueType=float, orientation="horizontal")

        gui.separator(self.controlArea)

        button = gui.button(self.controlArea, self, "Convert To Shadow", callback=self.convertToShadow)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

    def selectSurfaceFile(self):
        self.le_surface_file_name.setText(QtGui.QFileDialog.getOpenFileName(self, "Open Textual Data", ".", "*.txt;*.dat"))

    def convertToShadow(self):

        self.progressBarInit()

        self.information(0, "Running DCM Surface Converter")
        qApp.processEvents()

        self.progressBarSet(0)

        out_file_name = os.getcwd() + "/Output/DCM_FEM_Surface.dat"
        out_file = open(out_file_name, "w")

        if self.debug_mode:
            out_file_name_2 = os.getcwd() + "/Output/dcm_surface_points.dat"
            self.out_file_2 = open(out_file_name_2, "w")

            out_file_name_3 = os.getcwd() + "/Output/dcm_surface_original_points.dat"
            self.out_file_3 = open(out_file_name_3, "w")

        step_x = (self.x_max - self.x_min)/(self.number_of_x_cells-1)
        step_y = (self.y_max - self.y_min)/(self.number_of_y_cells-1)

        y_values = []

        for n_step in range(0, self.number_of_y_cells):
           y_values.append(round(self.y_min + n_step*step_y, 2))

        x_values = []

        for n_step in range(0, self.number_of_x_cells):
           x_values.append(round(self.x_min + n_step*step_x, 2))

        out_file.write(self.string_format(12, self.number_of_x_cells, 0) + self.string_format(12, self.number_of_y_cells, 0) +"\n")

        counter = 0
        row = ""
        for y_value in y_values:
            row += self.string_format(16, y_value, 8)

            if counter < 4:
                counter += 1
            else:
                out_file.write(row + "\n")
                out_file.flush()
                row = ""
                counter = 0

        out_file.write(row + "\n")
        out_file.flush()

        self.progressBarSet(10)

        points = self.readInputFile()

        ########################################
        #
        # SMOOTH
        #
        ########################################

        self.progressBarSet(20)
        barstep = 75/len(y_values)

        values_by_y = []

        for y_value in y_values:

            value_by_y = ValuesByY(y_value)
            value_by_y.x_values = []
            value_by_y.z_values = []

            for x_value in x_values:
                z_values = []
                previous_z = 0.0
                for point in points:

                    sigma_x = 1.5
                    sigma_y = 1.0

                    if (x_value == self.x_min and y_value == self.y_min) or \
                       (x_value == self.x_min and y_value == self.y_max) or \
                       (x_value == self.x_max and y_value == self.y_min) or \
                       (x_value == self.x_max and y_value == self.y_max):
                        sigma_x = 2.0
                        sigma_y = 2.0

                    x_liminf = x_value-sigma_x*(step_x)
                    x_limsup = x_value+sigma_x*(step_x)
                    y_liminf = y_value-sigma_y*(step_y)
                    y_limsup = y_value+sigma_y*(step_y)

                    if point[0] >= x_liminf \
                            and point[0] <= x_limsup \
                            and point[1] >= y_liminf \
                            and point[1] <= y_limsup :
                        z_values.append(point[2]**2)

                if len(z_values) == 0:
                    z_value = previous_z
                else:
                    z_value = math.sqrt(numpy.average(z_values))

                value_by_y.x_values.append(x_value)
                value_by_y.z_values.append(z_value)

            value_by_y.interpolate()

            values_by_y.append(value_by_y)

            self.progressBarAdvance(barstep)

        ########################################
        #
        # SCRITTURA FILE OUT
        #
        ########################################

        barstep = 5/len(x_values)

        for x_value in x_values:
            row = self.string_format(16, x_value, 8)

            first = True
            for y_value in y_values:
                z_value = 0.0
                for value_by_y in values_by_y:
                    if value_by_y.y_value == y_value:
                        for index in range(0, len(value_by_y.x_values)):
                            if value_by_y.x_values[index] == x_value:
                                z_value = round(value_by_y.z_values_spline[index], 6)
                                break
                        else:
                            continue

                if self.debug_mode:
                    self.out_file_2.write(str(x_value) + " " + str(y_value) + " " + str(z_value) + "\n")
                    self.out_file_2.flush()

                if first:
                    row += self.string_format(16, z_value, 8)
                    first = False
                else:
                    row = self.string_format(16, z_value, 8)

                out_file.write(row + "\n")
                out_file.flush()

            self.progressBarAdvance(barstep)

        out_file.write(row + "\n")
        out_file.flush()
        out_file.close()

        if self.debug_mode:
            self.out_file_2.close()
            self.out_file_2.close()

        self.progressBarSet(100)

        self.information()
        qApp.processEvents()

        self.progressBarFinished()
        qApp.processEvents()


    def string_format(self, str_length, number, number_of_decimals):
        str_out = ""

        format_string = "%."+str(int(number_of_decimals))+"f"
        str_number =  format_string % number
        spaces = str_length - len(str_number)

        for space in range(0, spaces):
            str_out += " "

        str_out += str_number

        return str_out

    def readInputFile(self):
        input_file = open(self.surface_file_name, "r")

        rows = input_file.readlines()
        points = []

        if len(rows) > 0:
            for row in rows:
                values = row.split('\t')

                try:
                    x_val = round(float(values[0].strip())*100, 8)
                    y_val = round(float(values[1].strip())*100, 8)
                    z_val = round(float(values[2].strip())*100, 8)

                    point = [x_val, y_val, z_val]

                    points.append(point)

                    if self.debug_mode:
                        self.out_file_3.write(str(point[0]) + " " + str(point[1]) + " " + str(point[2]) + "\n")
                        self.out_file_3.flush()
                except:
                    pass

        return points

class ValuesByY:
    y_value = 0.0
    x_values = []
    z_values = []
    z_values_spline = []

    def __init__(self, y_value):
        self.y_value = y_value
        self.x_values = []
        self.z_values = []
        self.z_values_spline = []


    def interpolate(self):
        poly_fit = numpy.poly1d(numpy.polyfit(self.x_values, self.z_values, 5))
        self.z_values_spline = poly_fit(self.x_values)

class ValuesByX:
    x_value = 0.0
    y_values = []
    z_values = []

    def __init__(self, x_value):
        self.x_value = x_value
        self.y_values = []
        self.z_values = []


if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = DCMCatiaSurfaceConverter()
    ow.show()
    a.exec_()
    ow.saveSettings()