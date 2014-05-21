import sys, math, os, numpy
from Orange.widgets import widget
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, qApp

from Orange.shadow.shadow_util import ShadowGui

class DCMSurfaceConverter(widget.OWWidget):

    name = "DCM Surface Converter"
    description = "User Defined: DCMSurfaceConverter"
    icon = "icons/dcm_surface_converter.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 3
    category = "User Defined"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 0

    number_of_x_cells = Setting(240)
    number_of_y_cells = Setting(80)

    x_min = Setting(0.0)
    x_max = Setting(0.0)
    y_min = Setting(0.0)
    y_max = Setting(0.0)

    surface_file_name=Setting("")

    debug_mode = False

    def __init__(self):
        self.setFixedWidth(590)
        self.setFixedHeight(340)

        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Ansys Surface", addSpace=True, orientation="vertical")

        select_file_box = ShadowGui.widgetBox(left_box_1, "", addSpace=True, orientation="horizontal", height=50)

        self.le_surface_file_name = ShadowGui.lineEdit(select_file_box, self, "surface_file_name", "Surface File Name", labelWidth=150, valueType=str, orientation="horizontal")
        self.le_surface_file_name.setFixedWidth(300)

        pushButton = gui.button(select_file_box, self, "...")
        pushButton.clicked.connect(self.selectSurfaceFile)

        ShadowGui.lineEdit(left_box_1, self, "number_of_x_cells", "Number of X cells", labelWidth=300, valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "number_of_y_cells", "Number of Y cells", labelWidth=300, valueType=int, orientation="horizontal")

        ShadowGui.lineEdit(left_box_1, self, "x_min", "X Min", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "x_max", "X Max", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "y_min", "Y Min", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "y_max", "Y Max", labelWidth=300, valueType=float, orientation="horizontal")

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

        step_x = (self.x_max - self.x_min)/self.number_of_x_cells
        step_y = (self.y_max - self.y_min)/self.number_of_y_cells

        y_values = []

        for n_step in range(0, self.number_of_y_cells+1):
           y_values.append(self.y_min + n_step*step_y)

        x_values = []

        for n_step in range(0, self.number_of_x_cells+1):
           x_values.append(self.x_min + n_step*step_x)

        out_file.write(self.string_format(12, self.number_of_x_cells+1, 0) + self.string_format(12, self.number_of_y_cells+1, 0) +"\n")

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

        points, min_value = self.readInputFile()

        self.progressBarSet(20)

        barstep = 80/len(x_values)

        for x_value in x_values:
            row = self.string_format(16, x_value, 8)

            first = True
            for y_value in y_values:
                z_values = []
                previous_z = 0.0
                for point in points:
                    if (x_value == self.x_min and y_value == self.y_min) or \
                       (x_value == self.x_min and y_value == self.y_max) or \
                       (x_value == self.x_max and y_value == self.y_min) or \
                       (x_value == self.x_max and y_value == self.y_max):
                        x_liminf = x_value-2*(step_x)
                        x_limsup = x_value+2*(step_x)
                        y_liminf = y_value-2*(step_y)
                        y_limsup = y_value+2*(step_y)
                    else:
                        x_liminf = x_value-(step_x)
                        x_limsup = x_value+(step_x)
                        y_liminf = y_value-(step_y)
                        y_limsup = y_value+(step_y)

                    if point[0] >= x_liminf \
                            and point[0] <= x_limsup \
                            and point[1] >= y_liminf \
                            and point[1] <= y_limsup :
                        z_values.append(point[2])

                if len(z_values) == 0:
                    z_value = previous_z
                else:
                    z_value = numpy.average(z_values)

                if self.debug_mode:
                    self.out_file_2.write(str(x_value) + " " + str(y_value) + " " + str(z_value) + "\n")
                    self.out_file_2.flush()

                if first:
                    row += self.string_format(16, z_value-min_value, 8)
                    first = False
                else:
                    row = self.string_format(16, z_value-min_value, 8)

                previous_z = z_value

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
        min_value = 0.0

        if len(rows) > 0:
            for row in rows:
                values = row.split('\t')

                try:
                    x_val = round(float(values[0].strip())*100, 8)
                    quote = float(values[1].strip())
                    y_val = round(float(values[2].strip())*100, 8)
                    z_val = round(float(values[3].strip())*100, 8)

                    if z_val < min_value: min_value = z_val

                    point = [x_val, y_val, z_val]

                    if quote == 0.077696:
                        points.append(point)

                        if self.debug_mode:
                            self.out_file_3.write(str(point[0]) + " " + str(point[1]) + " " + str(point[2]) + "\n")
                            self.out_file_3.flush()
                except:
                    pass

        return points, min_value

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = DCMSurfaceConverter()
    ow.show()
    a.exec_()
    ow.saveSettings()