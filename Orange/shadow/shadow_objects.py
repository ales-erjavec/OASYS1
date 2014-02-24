
import os, copy
from PyQt4 import QtCore
import Shadow


class TTYGrabber:
    def __init__(self,  tmpFile = 'out.tmp.dat'):
        self.tmpFile = tmpFile
        self.ttyData = []
        self.outfile = False
        self.save = False

    def start(self):
        self.outfile = os.open(self.tmpFile, os.O_RDWR|os.O_CREAT)
        self.save = os.dup(1)
        os.dup2(self.outfile, 1)
        return

    def stop(self):
        if not self.save:
            return
        os.dup2(self.save, 1)
        self.ttyData = open(self.tmpFile, ).readlines()
        os.close(self.outfile)
        os.remove(self.tmpFile)

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

class ShadowOEHistoryItem:

    def __new__(cls, input_beam=None, shadow_oe=None, output_beam=None):
        self = super().__new__(cls)
        self.input_beam = input_beam
        self.shadow_oe = shadow_oe
        self.output_beam = output_beam
        return self

class ShadowBeam:

    def __new__(cls, oe_number=0, beam=None):
        self = super().__new__(cls)
        self.oe_number = oe_number
        self.beam = beam
        self.history = []
        return self

    def setBeam(self, beam):
        self.beam = beam

    @classmethod
    def traceFromSource(cls, shadow_src):
        self = cls.__new__(ShadowBeam, beam=Shadow.Beam())

        self.beam.genSource(shadow_src.src)
        self.beam.write("begin.dat")

        return self

    @classmethod
    def traceFromOE(cls, input_beam, shadow_oe):
        self = ShadowBeam.traceFromOENoHistory(input_beam=input_beam, shadow_oe=shadow_oe)

        if len(self.history) < self.oe_number:
            self.history.append(ShadowOEHistoryItem(input_beam, shadow_oe, self))
        else:
            self.history[self.oe_number-1]=ShadowOEHistoryItem(input_beam, shadow_oe, self)

        return self

    @classmethod
    def traceFromOENoHistory(cls, input_beam, shadow_oe):
        beam = copy.deepcopy(input_beam.beam)
        beam.rays = copy.deepcopy(input_beam.beam.rays)

        self = cls.__new__(ShadowBeam, input_beam.oe_number+1, beam)

        self.beam.traceOE(shadow_oe.oe, self.oe_number)

        return self

    def getOEHistory(self, oe_number=None):
        if oe_number is None:
            return self.history
        else:
            return self.history[oe_number-1]

    def getLastOE(self):
        dimension = len(self.history)

        if dimension > 0:
            return self.history[dimension-1]
        else:
            return None

class ShadowSource:
    def __new__(cls, src=None):
        self = super().__new__(cls)
        self.src = src
        return self

    def set_src(self, src):
        self.src = src

    @classmethod
    def create_src(cls):
        self = cls.__new__(ShadowSource, src=Shadow.Source())

        # parameters embedded

        self.src.FSOURCE_DEPTH= 4
        self.src.F_COLOR=3
        self.src.F_PHOT=0
        self.src.F_POLAR=1
        self.src.NCOL=0
        self.src.N_COLOR=0
        self.src.POL_DEG=0.0
        self.src.SIGDIX=0.0
        self.src.SIGDIZ=0.0
        self.src.SIGMAY=0.0
        self.src.WXSOU=0.0
        self.src.WYSOU=0.0
        self.src.WZSOU=0.0
        self.src.FILE_TRAJ=b"NONESPECIFIED"
        self.src.FILE_SOURCE=b"NONESPECIFIED"
        self.src.FILE_BOUND=b"NONESPECIFIED"
        self.src.OE_NUMBER =  0

        return self

    @classmethod
    def create_bm_src(cls):
        self = cls.create_src()

        self.src.F_WIGGLER = 0

        return self

class ShadowOpticalElement:
    def __new__(cls, oe=None):
        self = super().__new__(cls)
        self.oe = oe
        return self

    def set_oe(self, oe):
        self.oe = oe

    @classmethod
    def create_empty_oe(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        return self

    @classmethod
    def create_screen_slit(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=5
        self.oe.unsetCrystal()
        self.oe.F_REFRAC=2
        self.oe.F_SCREEN=1
        self.oe.N_SCREEN=1

        return self

    @classmethod
    def create_plane_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=5
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_spherical_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=1
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_toroidal_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=3
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_paraboloid_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=4
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_ellipsoid_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=2
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_hyperboloid_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=7
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_codling_slit_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=6
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self


    @classmethod
    def create_polynomial_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=9
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_conic_coefficients_mirror(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=10
        self.oe.unsetCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_plane_crystal(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=5
        self.oe.setCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_spherical_crystal(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=1
        self.oe.setCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_paraboloid_crystal(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=4
        self.oe.setCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_ellipsoid_crystal(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=2
        self.oe.setCrystal()
        self.oe.setReflector()

        return self

    @classmethod
    def create_hyperboloid_crystal(cls):
        self = cls.__new__(ShadowOpticalElement, oe=Shadow.OE())

        self.oe.FMIRR=7
        self.oe.setCrystal()
        self.oe.setReflector()

        return self