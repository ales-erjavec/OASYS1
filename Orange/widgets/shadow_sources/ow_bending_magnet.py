import os, sys
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication, qApp, QScrollArea

from Orange.widgets.shadow_gui import ow_generic_element
from Orange.shadow.shadow_objects import EmittingStream, TTYGrabber
from Orange.shadow.shadow_util import ShadowGui

class BendingMagnet(ow_generic_element.GenericElement):

    name = "Bending Magnet"
    description = "Shadow Source: Bending Magnet"
    icon = "icons/bending_magnet.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 2
    category = "Sources"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"Beam",
                "type":Orange.shadow.ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"}]

    number_of_rays=Setting(5000)
    seed=Setting(6775431)
    e_min=Setting(0)
    e_max=Setting(100000)
    optical_paths_combo=Setting(1) # REMOVED FROM GUI: 1 AS DEFAULT
    sample_distribution_combo=Setting(0) # REMOVED FROM GUI: 0 AS DEFAULT
    generate_polarization_combo=Setting(2)

    sigma_x=Setting(0)
    sigma_z=Setting(0)
    emittance_x=Setting(0)
    emittance_z=Setting(0)
    energy=Setting(0)
    distance_from_waist_x=Setting(0)
    distance_from_waist_z=Setting(0)

    magnetic_radius=Setting(0)
    magnetic_field=Setting(0)
    horizontal_half_divergence_from=Setting(0)
    horizontal_half_divergence_to=Setting(0)
    max_vertical_half_divergence_from=Setting(0)
    max_vertical_half_divergence_to=Setting(0)

    calculation_mode_combo=Setting(0)

    want_main_area=1

    def __init__(self):
        super().__init__()

        left_box_1 = gui.widgetBox(self.controlArea, "Monte Carlo and Energy Spectrum", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_1, self, "number_of_rays", "Number of Rays", tooltip="Number of Rays", valueType=int, orientation="horizontal")

        ShadowGui.lineEdit(left_box_1, self, "seed", "Seed", tooltip="Seed", valueType=int, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "e_min", "Minimum Energy (eV)", tooltip="Minimum Energy (eV)", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_1, self, "e_max", "Maximum Energy (eV)", tooltip="Maximum Energy (eV)", valueType=float, orientation="horizontal")
        #gui.comboBox(left_box_1, self, "optical_paths_combo", label="Store Optical Paths?", items=["No", "Yes"], orientation="horizontal")
        #gui.comboBox(left_box_1, self, "sample_distribution_combo", label="Sample Distribution", items=["Photon", "Power"], orientation="horizontal")
        gui.comboBox(left_box_1, self, "generate_polarization_combo", label="Generate Polarization", items=["Only Parallel", "Only Perpendicular", "Total"], orientation="horizontal")

        left_box_2 = gui.widgetBox(self.controlArea, "Machine Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_2, self, "sigma_x", "Sigma X [cm]", tooltip="Sigma X [cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "sigma_z", "Sigma Z [cm]", tooltip="Sigma Z [cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "emittance_x", "Emittance X [rad.cm]", tooltip="Emittance X [rad.cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "emittance_z", "Emittance Z [rad.cm]", tooltip="Emittance Z [rad.cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "energy", "Energy [GeV]", tooltip="Energy [GeV]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "distance_from_waist_x", "Distance from Waist X [cm]", tooltip="Distance from Waist X [cm]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_2, self, "distance_from_waist_z", "Distance from Waist Z [cm]", tooltip="Distance from Waist Z [cm]", valueType=float, orientation="horizontal")

        left_box_3 = gui.widgetBox(self.controlArea, "Bending Magnet Parameters", addSpace=True, orientation="vertical")

        ShadowGui.lineEdit(left_box_3, self, "magnetic_radius", "Magnetic Radius [m]", callback=self.calculateMagneticField, tooltip="Magnetic Radius [m]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "magnetic_field", "Magnetic Field [T]", callback=self.calculateMagneticRadius, tooltip="Magnetic Field [T]", valueType=float, orientation="horizontal")

        ShadowGui.lineEdit(left_box_3, self, "horizontal_half_divergence_from", "Horizontal half-divergence [rads] From [+]", tooltip="Horizontal half-divergence [rads] From [+]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "horizontal_half_divergence_to", "Horizontal half-divergence [rads] To [-]", tooltip="Horizontal half-divergence [rads] To [-]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "max_vertical_half_divergence_from", "Max vertical half-divergence [rads] From [+]", tooltip="Max vertical half-divergence [rads] From [+]", valueType=float, orientation="horizontal")
        ShadowGui.lineEdit(left_box_3, self, "max_vertical_half_divergence_to", "Max vertical half-divergence [rads] To [-]", tooltip="Max vertical half-divergence [rads] To [-]", valueType=float, orientation="horizontal")
        gui.comboBox(left_box_3, self, "calculation_mode_combo", label="Calculation Mode", items=["Precomputed", "Exact"], orientation="horizontal")

        left_box_4 = gui.widgetBox(self.controlArea, "", addSpace=True, orientation="vertical")
        left_box_4.setFixedHeight(120)

        gui.button(self.controlArea, self, "Run Shadow/source", callback=self.runShadowSource)

        gui.rubber(self.controlArea)

        gui.rubber(self.mainArea)

        #if (self.is_automatic_run):
        #    self.runShadowSource()

    def calculateMagneticField(self):
        self.magnetic_radius=abs(self.magnetic_radius)
        if self.magnetic_radius > 0:
           self.magnetic_field=3.334728*self.energy/self.magnetic_radius


    def calculateMagneticRadius(self):
        if self.magnetic_field > 0:
           self.magnetic_radius=3.334728*self.energy/self.magnetic_field

    def runShadowSource(self):

        self.progressBarInit()

        shadow_src = Orange.shadow.ShadowSource.create_bm_src()

        shadow_src.src.NPOINT=self.number_of_rays
        shadow_src.src.ISTAR1=self.seed
        shadow_src.src.PH1=self.e_min
        shadow_src.src.PH2=self.e_max
        shadow_src.src.F_OPD=self.optical_paths_combo
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

        self.progressBarFinished()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = BendingMagnet()
    ow.show()
    a.exec_()
    ow.saveSettings()
