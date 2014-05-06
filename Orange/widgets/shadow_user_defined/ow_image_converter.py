import sys, numpy, math
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import qApp

from Orange.widgets.shadow_gui import ow_generic_element
from Orange.shadow.shadow_objects import EmittingStream, TTYGrabber, ShadowBeam
from Orange.shadow.shadow_util import ShadowGui

class ImageToBeamConverter(ow_generic_element.GenericElement):

    name = "Image To Beam"
    description = "User Defined: ImageToBeamConverter"
    icon = "icons/image_converter.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 2
    category = "User Defined"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"Beam",
                "type":Orange.shadow.ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"}]

    want_main_area=1

    image_file_name=Setting("")
    pixel_size = Setting(14.0)
    number_of_x_bins = Setting(10)
    number_of_z_bins = Setting(5)

    def __init__(self):
        super().__init__(show_automatic_box=False)

        left_box_1 = ShadowGui.widgetBox(self.controlArea, "CCD Image", addSpace=True, orientation="vertical")

        le = ShadowGui.lineEdit(left_box_1, self, "image_file_name", "Image File Name", labelWidth=120, valueType=str, orientation="horizontal")
        le.setFixedWidth(300)

        ShadowGui.lineEdit(left_box_1, self, "pixel_size", "Pixel Size [um]", labelWidth=200, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "number_of_x_bins", "Number of Bin per Pixel [x]", labelWidth=200, valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "number_of_z_bins", "Number of Bin per Pixel [z]", labelWidth=200, valueType=int, orientation="horizontal")

        gui.separator(self.controlArea, height=600)

        button = gui.button(self.controlArea, self, "Convert To Beam", callback=self.convertToBeam)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def convertToBeam(self):

        self.progressBarInit()

        self.progressBarSet(10)

        self.information(0, "Converting Image Map")
        qApp.processEvents()

        sys.stdout = EmittingStream(textWritten=self.writeStdOut)
        grabber = TTYGrabber()
        grabber.start()

        map = self.convertImageToXYMap()

        self.progressBarSet(50)

        beam_out = self.convertMapToBeam(map)

        grabber.stop()

        for row in grabber.ttyData:
           self.writeStdOut(row)

        self.information(0, "Plotting Results")
        qApp.processEvents()

        self.progressBarSet(80)
        self.plot_results(beam_out)

        self.information()
        qApp.processEvents()

        self.progressBarFinished()

        self.send("Beam", beam_out)


    def convertImageToXYMap(self):
        input_file = open(self.image_file_name, "r")

        map = []
        rows = input_file.readlines()

        if (len(rows) > 0):
            p0 = self.pixel_size*0.5*1e-4
            p0_bin_z = p0/self.number_of_z_bins
            p0_bin_x = p0/self.number_of_x_bins

            number_of_x_pixels = len(rows[0].split('	'))
            number_of_z_pixels = len(rows)

            if (number_of_x_pixels*number_of_z_pixels*self.number_of_x_bins*self.number_of_z_bins) > 500000: raise Exception("Number of Pixels too high (>500000)")

            x0 = -p0*number_of_x_pixels*0.5
            z0 = p0*number_of_z_pixels*0.5

            for z_index in range (0, len(rows)):
                values = rows[z_index].split('	')

                for z_pixel_bin_index in range(0, self.number_of_z_bins):
                    z = z0 - (p0*z_index + p0_bin_z*z_pixel_bin_index)
                    for x_index in range(0, len(values)):
                        for x_pixel_bin_index in range(0, self.number_of_x_bins):
                            x = x0 + p0*x_index + p0_bin_x*x_pixel_bin_index
                            point = ImagePoint(x, 0, z, float(values[x_index]))
                            map.append(point)

        return map

    def convertMapToBeam(self, map):

        number_of_rays = len(map)

        if number_of_rays == 0: return None

        beam_out = ShadowBeam(number_of_rays=number_of_rays)

        for index in range(0, number_of_rays):
            point = map[index]

            ray = beam_out.beam.rays[index]

            E_value = math.sqrt(point.value*0.5)

            ray[0]  = point.x                       # X
            ray[1]  = point.y                        # Y
            ray[2]  = point.z                        # Z
            ray[3]  = 0                             # director cos x
            ray[4]  = 1                              # director cos y
            ray[5]  = 0                             # director cos z
            ray[6]  = 0  # Es_x
            ray[7]  = E_value  # Es_y
            ray[8]  = 0  # Es_z
            ray[9]  = 1  # good/lost
            ray[10] = 2*math.pi/1.5e-8
            ray[11] = index # ray index
            ray[12] = 1                                     # good only
            ray[13] = math.pi*0.5 # Es_phi
            ray[14] = math.pi*0.5 # Ep_phi
            ray[15] = 0 # Ep_x
            ray[16] = E_value # Ep_y
            ray[17] = 0 # Ep_z

        return beam_out

class ImagePoint:

    x = 0.0
    y = 0.0
    z = 0.0
    value = 0.0

    def __init__(self, x=0.0, y=0.0, z=0.0, value=0.0):
       self.x = x
       self.y = y
       self.z = z
       self.value = value
