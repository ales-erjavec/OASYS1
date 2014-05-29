import os, sys
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, qApp, QPalette, QColor, QFont

from Orange.widgets.shadow_gui import ow_generic_element
from Orange.shadow.shadow_objects import EmittingStream, TTYGrabber
from Orange.shadow.shadow_util import ShadowGui, ConfirmDialog

class BendingMagnet(ow_generic_element.GenericElement):

    name = "Bending Magnet"
    description = "Shadow Source: Bending Magnet"
    icon = "icons/bending_magnet.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 2
    category = "Sources"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Trigger", Orange.shadow.ShadowTriggerOut, "sendNewBeam")]

    outputs = [{"name":"Beam",
                "type":Orange.shadow.ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"}]

    number_of_rays=Setting(5000)
    seed=Setting(6775431)
    e_min=Setting(5000)
    e_max=Setting(100000)
    store_optical_paths=Setting(1) # REMOVED FROM GUI: 1 AS DEFAULT
    sample_distribution_combo=Setting(0) # REMOVED FROM GUI: 0 AS DEFAULT
    generate_polarization_combo=Setting(2)

    sigma_x=Setting(0.0078)
    sigma_z=Setting(0.0036)
    emittance_x=Setting(3.8E-7)
    emittance_z=Setting(3.8E-9)
    energy=Setting(6.04)
    distance_from_waist_x=Setting(0.0)
    distance_from_waist_z=Setting(0.0)

    magnetic_radius=Setting(25.1772)
    magnetic_field=Setting(0.8)
    horizontal_half_divergence_from=Setting(0.0005)
    horizontal_half_divergence_to=Setting(0.0005)
    max_vertical_half_divergence_from=Setting(1.0)
    max_vertical_half_divergence_to=Setting(1.0)

    calculation_mode_combo=Setting(0)

    want_main_area=1

    def __init__(self):
        super().__init__(show_automatic_box=False)

        left_box_1 = ShadowGui.widgetBox(self.controlArea, "Monte Carlo and Energy Spectrum", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_1, self, "number_of_rays", "Number of Rays", tooltip="Number of Rays", labelWidth=300, valueType=int, orientation="horizontal")

        ShadowGui.lineEdit(left_box_1, self, "seed", "Seed", tooltip="Seed", labelWidth=300, valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "e_min", "Minimum Energy (eV)", tooltip="Minimum Energy (eV)", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "e_max", "Maximum Energy (eV)", tooltip="Maximum Energy (eV)", labelWidth=300, valueType=float, orientation="horizontal")
        gui.comboBox(left_box_1, self, "generate_polarization_combo", label="Generate Polarization", items=["Only Parallel", "Only Perpendicular", "Total"], labelWidth=300, orientation="horizontal")

        left_box_2 = ShadowGui.widgetBox(self.controlArea, "Machine Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_2, self, "sigma_x", "Sigma X [cm]", labelWidth=300, tooltip="Sigma X [cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "sigma_z", "Sigma Z [cm]", labelWidth=300, tooltip="Sigma Z [cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "emittance_x", "Emittance X [rad.cm]", labelWidth=300, tooltip="Emittance X [rad.cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "emittance_z", "Emittance Z [rad.cm]", labelWidth=300, tooltip="Emittance Z [rad.cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "energy", "Energy [GeV]", tooltip="Energy [GeV]", labelWidth=300, valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "distance_from_waist_x", "Distance from Waist X [cm]", labelWidth=300, tooltip="Distance from Waist X [cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "distance_from_waist_z", "Distance from Waist Z [cm]", labelWidth=300, tooltip="Distance from Waist Z [cm]", valueType=float, orientation="horizontal")

        left_box_3 = ShadowGui.widgetBox(self.controlArea, "Bending Magnet Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_3, self, "magnetic_radius", "Magnetic Radius [m]", labelWidth=300, callback=self.calculateMagneticField, tooltip="Magnetic Radius [m]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "magnetic_field", "Magnetic Field [T]", labelWidth=300, callback=self.calculateMagneticRadius, tooltip="Magnetic Field [T]", valueType=float, orientation="horizontal")

        ShadowGui.lineEdit(left_box_3, self, "horizontal_half_divergence_from", "Horizontal half-divergence [rads] From [+]", labelWidth=300, tooltip="Horizontal half-divergence [rads] From [+]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "horizontal_half_divergence_to", "Horizontal half-divergence [rads] To [-]", labelWidth=300, tooltip="Horizontal half-divergence [rads] To [-]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "max_vertical_half_divergence_from", "Max vertical half-divergence [rads] From [+]", labelWidth=300, tooltip="Max vertical half-divergence [rads] From [+]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "max_vertical_half_divergence_to", "Max vertical half-divergence [rads] To [-]", labelWidth=300, tooltip="Max vertical half-divergence [rads] To [-]", valueType=float, orientation="horizontal")
        gui.comboBox(left_box_3, self, "calculation_mode_combo", label="Calculation Mode", items=["Precomputed", "Exact"], labelWidth=300, orientation="horizontal")

        gui.separator(self.controlArea, height=150)

        button_box = ShadowGui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Reset Fields", callback=self.callResetSettings)
        font = QFont(button.font())
        font.setItalic(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Red'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Run Shadow/trace", callback=self.runShadowSource)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            self.resetSettings()

    def calculateMagneticField(self):
        self.magnetic_radius=abs(self.magnetic_radius)
        if self.magnetic_radius > 0:
           self.magnetic_field=3.334728*self.energy/self.magnetic_radius


    def calculateMagneticRadius(self):
        if self.magnetic_field > 0:
           self.magnetic_radius=3.334728*self.energy/self.magnetic_field

    def runShadowSource(self):
        try:
            self.error()
            self.progressBarInit()

            self.number_of_rays = ShadowGui.checkPositiveNumber(self.number_of_rays, "Number of rays")
            self.seed = ShadowGui.checkPositiveNumber(self.seed, "Seed")
            self.e_min = ShadowGui.checkPositiveNumber(self.e_min, "Minimum energy")
            self.e_max = ShadowGui.checkPositiveNumber(self.e_max, "Maximum energy")
            self.sigma_x = ShadowGui.checkPositiveNumber(self.sigma_x, "Sigma x")
            self.sigma_z = ShadowGui.checkPositiveNumber(self.sigma_z, "Sigma z")
            self.emittance_x = ShadowGui.checkPositiveNumber(self.emittance_x, "Emittance x")
            self.emittance_z = ShadowGui.checkPositiveNumber(self.emittance_z, "Emittance z")
            self.energy = ShadowGui.checkPositiveNumber(self.energy, "Energy")
            self.magnetic_radius = ShadowGui.checkPositiveNumber(self.magnetic_radius, "Magnetic radius")
            self.horizontal_half_divergence_from = ShadowGui.checkPositiveNumber(self.horizontal_half_divergence_from, "Horizontal half-divergence from [+]")
            self.horizontal_half_divergence_to = ShadowGui.checkPositiveNumber(self.horizontal_half_divergence_to, "Horizontal half-divergence to [-]")
            self.max_vertical_half_divergence_from = ShadowGui.checkPositiveNumber(self.max_vertical_half_divergence_from, "Max vertical half-divergence from [+]")
            self.max_vertical_half_divergence_to = ShadowGui.checkPositiveNumber(self.max_vertical_half_divergence_to, "Max vertical half-divergence to [-]")

            shadow_src = Orange.shadow.ShadowSource.create_bm_src()

            shadow_src.src.NPOINT=self.number_of_rays
            shadow_src.src.ISTAR1=self.seed
            shadow_src.src.PH1=self.e_min
            shadow_src.src.PH2=self.e_max
            shadow_src.src.F_OPD=self.store_optical_paths
            shadow_src.src.F_SR_TYPE=self.sample_distribution_combo
            shadow_src.src.F_POL=1+self.generate_polarization_combo

            shadow_src.src.SIGMAX=self.sigma_x
            shadow_src.src.SIGMAZ=self.sigma_z
            shadow_src.src.EPSI_X=self.emittance_x
            shadow_src.src.EPSI_Z=self.emittance_z
            shadow_src.src.BENER=self.energy
            shadow_src.src.EPSI_DX=self.distance_from_waist_x
            shadow_src.src.EPSI_DZ=self.distance_from_waist_z

            shadow_src.src.R_MAGNET=self.magnetic_radius
            shadow_src.src.R_ALADDIN=self.magnetic_radius*100
            shadow_src.src.HDIV1=self.horizontal_half_divergence_from
            shadow_src.src.HDIV2=self.horizontal_half_divergence_to
            shadow_src.src.VDIV1=self.max_vertical_half_divergence_from
            shadow_src.src.VDIV2=self.max_vertical_half_divergence_to

            shadow_src.src.FDISTR=4+2*self.calculation_mode_combo

            self.progressBarSet(10)

            self.information(0, "Running SHADOW")
            qApp.processEvents()

            sys.stdout = EmittingStream(textWritten=self.writeStdOut)
            grabber = TTYGrabber()
            grabber.start()

            self.progressBarSet(50)

            beam_out = Orange.shadow.ShadowBeam.traceFromSource(shadow_src)

            grabber.stop()

            for row in grabber.ttyData:
               self.writeStdOut(row)

            self.information(0, "Plotting Results")
            qApp.processEvents()

            self.progressBarSet(80)
            self.plot_results(beam_out)

            self.information()
            qApp.processEvents()

            self.send("Beam", beam_out)
        except Exception as exception:
            self.error(0, exception.args[0])
            QtGui.QMessageBox.critical(self, "QMessageBox.critical()",
                exception.args[0],
                QtGui.QMessageBox.Ok)

        self.progressBarFinished()

    def sendNewBeam(self, trigger):
        if trigger and trigger.new_beam == True:
            self.runShadowSource()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = BendingMagnet()
    ow.show()
    a.exec_()
    ow.saveSettings()
