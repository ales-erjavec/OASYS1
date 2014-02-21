import os, sys
import Orange
import Orange.shadow
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from PyQt4.QtGui import QApplication, qApp, QScrollArea

from Orange.widgets.shadow_gui import ow_generic_element
from Orange.shadow.shadow_objects import EmittingStream, TTYGrabber
from Orange.shadow.shadow_util import ShadowGui

class GeometricalSource(ow_generic_element.GenericElement):

    name = "Geometrical Source"
    description = "Shadow Source: Geometrical Source"
    icon = "icons/geometrical.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "Sources"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"Beam",
                "type":Orange.shadow.ShadowBeam,
                "doc":"Shadow Beam",
                "id":"beam"}]


    want_main_area=1

    # TODO ELEMENTO DA FARE COMPLETAMENTE
    # TODO INSERIRE LIVELLI DI ASTRAZIONE COME PER OE

    def __init__(self):
        super().__init__()

        button = gui.button(self.controlArea, self, "Run Shadow/source", callback=self.runShadowSource)
        button.setFixedHeight(45)

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

        shadow_src = Orange.shadow.ShadowSource.create_src()

#        shadow_src.src.NPOINT=self.number_of_rays
#        shadow_src.src.ISTAR1=self.seed
#        shadow_src.src.PH1=self.e_min
#        shadow_src.src.PH2=self.e_max
#        shadow_src.src.F_OPD=self.optical_paths_combo
#        shadow_src.src.F_SR_TYPE=self.sample_distribution_combo
#        shadow_src.src.F_POL=1+self.generate_polarization_combo

#        shadow_src.src.SIGMAX=self.sigma_x
#        shadow_src.src.SIGMAZ=self.sigma_z
#        shadow_src.src.EPSI_X=self.emittance_x
#        shadow_src.src.EPSI_Z=self.emittance_z
#        shadow_src.src.BENER=self.energy
#        shadow_src.src.EPSI_DX=self.distance_from_waist_x
#        shadow_src.src.EPSI_DZ=self.distance_from_waist_z

#        shadow_src.src.R_MAGNET=self.magnetic_radius
#        shadow_src.src.R_ALADDIN=self.magnetic_radius*100
#        shadow_src.src.HDIV1=self.horizontal_half_divergence_from
#        shadow_src.src.HDIV2=self.horizontal_half_divergence_to
#        shadow_src.src.VDIV1=self.max_vertical_half_divergence_from
#        shadow_src.src.VDIV2=self.max_vertical_half_divergence_to

#        shadow_src.src.FDISTR=4+2*self.calculation_mode_combo

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
    ow = GeometricalSource()
    ow.show()
    a.exec_()
    ow.saveSettings()
