
import os, copy, numpy
from PyQt4 import QtCore
import Shadow

class TTYGrabber:
    def __init__(self,  tmpFileName = 'out.tmp.dat'):
        self.tmpFileName = tmpFileName
        self.ttyData = []
        self.outfile = False
        self.save = False

    def start(self):
        self.outfile = os.open(self.tmpFileName, os.O_RDWR|os.O_CREAT)
        self.save = os.dup(1)
        os.dup2(self.outfile, 1)
        return

    def stop(self):
        if not self.save:
            return
        os.dup2(self.save, 1)
        tmpFile = open(self.tmpFileName, "r")
        self.ttyData = tmpFile.readlines()
        tmpFile.close()
        os.close(self.outfile)
        os.remove(self.tmpFileName)

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

class ShadowTriggerOut:
    def __new__(cls, new_beam=False):
        self = super().__new__(cls)

        self.new_beam = new_beam

        return self

class ShadowTriggerIn:
    def __new__(cls, new_beam=False, interrupt=False):
        self = super().__new__(cls)

        self.new_beam = new_beam
        self.interrupt = interrupt

        return self

class ShadowOEHistoryItem:

    def __new__(cls, shadow_oe=None):
        self = super().__new__(cls)

        self.shadow_oe = shadow_oe

        return self

    def duplicate(self):
        new_history_item = ShadowOEHistoryItem()

        new_history_item.shadow_oe = self.shadow_oe

        return new_history_item


class ShadowBeam:
    def __new__(cls, oe_number=0, beam=None, number_of_rays=0):
        self = super().__new__(cls)
        self.oe_number = oe_number
        if (beam is None):
            if number_of_rays > 0:
                self.beam = Shadow.Beam(number_of_rays)
            else:
                self.beam = Shadow.Beam()
        else:
            self.beam = beam

        self.history = []
        return self

    def setBeam(self, beam):
        self.beam = beam

    def duplicate(self, copy_rays=True, history=True):
        beam = Shadow.Beam()
        if copy_rays: beam.rays = copy.deepcopy(self.beam.rays)

        new_shadow_beam = ShadowBeam(self.oe_number, beam)

        if history:
            for historyItem in self.history:
                new_shadow_beam.history.append(historyItem)

        return new_shadow_beam

    @classmethod
    def mergeBeams(cls, beam_1, beam_2):
        if beam_1 and beam_2:
            rays_1 = None
            rays_2 = None

            if len(getattr(beam_1.beam, "rays", numpy.zeros(0))) > 0:
                rays_1 = copy.deepcopy(beam_1.beam.rays)
            if len(getattr(beam_2.beam, "rays", numpy.zeros(0))) > 0:
                rays_2 = copy.deepcopy(beam_2.beam.rays)

            merged_beam = beam_1.duplicate(copy_rays=False, history=True)

            if not rays_1 is None and not rays_2 is None:
                merged_beam.oe_number = beam_2.oe_number
                merged_beam.beam.rays = numpy.append(rays_1, rays_2, axis=0)
            elif not rays_1 is None:
                merged_beam.beam.rays = rays_1
                merged_beam.oe_number = beam_2.oe_number
            elif not rays_2 is None:
                merged_beam.beam.rays = rays_2
                merged_beam.oe_number = beam_2.oe_number

            return merged_beam

    @classmethod
    def traceFromSource(cls, shadow_src):
        self = cls.__new__(ShadowBeam, beam=Shadow.Beam())

        self.beam.write("begin.dat")
        self.beam.genSource(shadow_src.src)

        return self

    @classmethod
    def traceFromOE(cls, input_beam, shadow_oe):
        self = cls.initializeFromPreviousBeam(input_beam)

        history_shadow_oe = shadow_oe.duplicate()

        shadow_oe.oe.write("start.0" + str(self.oe_number))

        self.beam.traceOE(shadow_oe.oe, self.oe_number)

        shadow_oe.oe.write("end.0" + str(self.oe_number))

        if len(self.history) < self.oe_number:
            self.history.append(ShadowOEHistoryItem(history_shadow_oe))
        else:
            self.history[self.oe_number-1]=ShadowOEHistoryItem(history_shadow_oe)

        return self

    @classmethod
    def initializeFromPreviousBeam(cls, input_beam):
        self = input_beam.duplicate()
        self.oe_number = input_beam.oe_number + 1

        return self

    @classmethod
    def traceFromOENoHistory(cls, input_beam, shadow_oe):
        self = cls.initializeFromPreviousBeam(input_beam)

        self.beam.traceOE(shadow_oe.oe, self.oe_number)

        return self

    def getOEHistory(self, oe_number=None):
        if oe_number is None:
            return self.history
        else:
            return self.history[oe_number-1]

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

        self.src.OE_NUMBER =  0

        return self

    @classmethod
    def create_bm_src(cls):
        self = cls.create_src()

        self.src.FSOURCE_DEPTH=4
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

        self.src.F_WIGGLER = 0

        return self

class ShadowOpticalElement:
    def __new__(cls, oe=None):
        self = super().__new__(cls)
        self.oe = oe
        return self

    def set_oe(self, oe):
        self.oe = oe

    def duplicate(self):
        new_oe = ShadowOpticalElement.create_empty_oe()

        new_oe.oe.FMIRR = self.oe.FMIRR
        new_oe.oe.F_TORUS = self.oe.F_TORUS
        new_oe.oe.FCYL = self.oe.FCYL
        new_oe.oe.F_EXT = self.oe.F_EXT
        new_oe.oe.FSTAT = self.oe.FSTAT
        new_oe.oe.F_SCREEN = self.oe.F_SCREEN
        new_oe.oe.F_PLATE = self.oe.F_PLATE
        new_oe.oe.FSLIT = self.oe.FSLIT
        new_oe.oe.FWRITE = self.oe.FWRITE
        new_oe.oe.F_RIPPLE = self.oe.F_RIPPLE
        new_oe.oe.F_MOVE = self.oe.F_MOVE
        new_oe.oe.F_THICK = self.oe.F_THICK
        new_oe.oe.F_BRAGG_A = self.oe.F_BRAGG_A
        new_oe.oe.F_G_S = self.oe.F_G_S
        new_oe.oe.F_R_RAN = self.oe.F_R_RAN
        new_oe.oe.F_GRATING = self.oe.F_GRATING
        new_oe.oe.F_MOSAIC = self.oe.F_MOSAIC
        new_oe.oe.F_JOHANSSON = self.oe.F_JOHANSSON
        new_oe.oe.F_SIDE = self.oe.F_SIDE
        new_oe.oe.F_CENTRAL = self.oe.F_CENTRAL
        new_oe.oe.F_CONVEX = self.oe.F_CONVEX
        new_oe.oe.F_REFLEC = self.oe.F_REFLEC
        new_oe.oe.F_RUL_ABS = self.oe.F_RUL_ABS
        new_oe.oe.F_RULING = self.oe.F_RULING
        new_oe.oe.F_PW = self.oe.F_PW
        new_oe.oe.F_PW_C = self.oe.F_PW_C
        new_oe.oe.F_VIRTUAL = self.oe.F_VIRTUAL
        new_oe.oe.FSHAPE = self.oe.FSHAPE
        new_oe.oe.FHIT_C = self.oe.FHIT_C
        new_oe.oe.F_MONO = self.oe.F_MONO
        new_oe.oe.F_REFRAC = self.oe.F_REFRAC
        new_oe.oe.F_DEFAULT = self.oe.F_DEFAULT
        new_oe.oe.F_REFL = self.oe.F_REFL
        new_oe.oe.F_HUNT = self.oe.F_HUNT
        new_oe.oe.F_CRYSTAL = self.oe.F_CRYSTAL
        new_oe.oe.F_PHOT_CENT = self.oe.F_PHOT_CENT
        new_oe.oe.F_ROUGHNESS = self.oe.F_ROUGHNESS
        new_oe.oe.F_ANGLE = self.oe.F_ANGLE
        new_oe.oe.NPOINT = self.oe.NPOINT
        new_oe.oe.NCOL = self.oe.NCOL
        new_oe.oe.N_SCREEN = self.oe.N_SCREEN
        new_oe.oe.ISTAR1 = self.oe.ISTAR1
        new_oe.oe.CIL_ANG = self.oe.CIL_ANG
        new_oe.oe.ELL_THE = self.oe.ELL_THE
        new_oe.oe.N_PLATES = self.oe.N_PLATES
        new_oe.oe.IG_SEED = self.oe.IG_SEED
        new_oe.oe.MOSAIC_SEED = self.oe.MOSAIC_SEED
        new_oe.oe.ALPHA = self.oe.ALPHA
        new_oe.oe.SSOUR = self.oe.SSOUR
        new_oe.oe.THETA = self.oe.THETA
        new_oe.oe.SIMAG = self.oe.SIMAG
        new_oe.oe.RDSOUR = self.oe.RDSOUR
        new_oe.oe.RTHETA = self.oe.RTHETA
        new_oe.oe.OFF_SOUX = self.oe.OFF_SOUX
        new_oe.oe.OFF_SOUY = self.oe.OFF_SOUY
        new_oe.oe.OFF_SOUZ = self.oe.OFF_SOUZ
        new_oe.oe.ALPHA_S = self.oe.ALPHA_S
        new_oe.oe.RLEN1 = self.oe.RLEN1
        new_oe.oe.RLEN2 = self.oe.RLEN2
        new_oe.oe.RMIRR = self.oe.RMIRR
        new_oe.oe.AXMAJ = self.oe.AXMAJ
        new_oe.oe.AXMIN = self.oe.AXMIN
        new_oe.oe.CONE_A = self.oe.CONE_A
        new_oe.oe.R_MAJ = self.oe.R_MAJ
        new_oe.oe.R_MIN = self.oe.R_MIN
        new_oe.oe.RWIDX1 = self.oe.RWIDX1
        new_oe.oe.RWIDX2 = self.oe.RWIDX2
        new_oe.oe.PARAM = self.oe.PARAM
        new_oe.oe.HUNT_H = self.oe.HUNT_H
        new_oe.oe.HUNT_L = self.oe.HUNT_L
        new_oe.oe.BLAZE = self.oe.BLAZE
        new_oe.oe.RULING = self.oe.RULING
        new_oe.oe.ORDER = self.oe.ORDER
        new_oe.oe.PHOT_CENT = self.oe.PHOT_CENT
        new_oe.oe.X_ROT = self.oe.X_ROT
        new_oe.oe.D_SPACING = self.oe.D_SPACING
        new_oe.oe.A_BRAGG = self.oe.A_BRAGG
        new_oe.oe.SPREAD_MOS = self.oe.SPREAD_MOS
        new_oe.oe.THICKNESS = self.oe.THICKNESS
        new_oe.oe.R_JOHANSSON = self.oe.R_JOHANSSON
        new_oe.oe.Y_ROT = self.oe.Y_ROT
        new_oe.oe.Z_ROT = self.oe.Z_ROT
        new_oe.oe.OFFX = self.oe.OFFX
        new_oe.oe.OFFY = self.oe.OFFY
        new_oe.oe.OFFZ = self.oe.OFFZ
        new_oe.oe.SLLEN = self.oe.SLLEN
        new_oe.oe.SLWID = self.oe.SLWID
        new_oe.oe.SLTILT = self.oe.SLTILT
        new_oe.oe.COD_LEN = self.oe.COD_LEN
        new_oe.oe.COD_WID = self.oe.COD_WID
        new_oe.oe.X_SOUR = self.oe.X_SOUR
        new_oe.oe.Y_SOUR = self.oe.Y_SOUR
        new_oe.oe.Z_SOUR = self.oe.Z_SOUR
        new_oe.oe.X_SOUR_ROT = self.oe.X_SOUR_ROT
        new_oe.oe.Y_SOUR_ROT = self.oe.Y_SOUR_ROT
        new_oe.oe.Z_SOUR_ROT = self.oe.Z_SOUR_ROT
        new_oe.oe.R_LAMBDA = self.oe.R_LAMBDA
        new_oe.oe.THETA_I = self.oe.THETA_I
        new_oe.oe.ALPHA_I = self.oe.ALPHA_I
        new_oe.oe.T_INCIDENCE = self.oe.T_INCIDENCE
        new_oe.oe.T_SOURCE = self.oe.T_SOURCE
        new_oe.oe.T_IMAGE = self.oe.T_IMAGE
        new_oe.oe.T_REFLECTION = self.oe.T_REFLECTION
        new_oe.oe.FILE_SOURCE = self.oe.FILE_SOURCE
        new_oe.oe.FILE_RIP = self.oe.FILE_RIP
        new_oe.oe.FILE_REFL = self.oe.FILE_REFL
        new_oe.oe.FILE_MIR = self.oe.FILE_MIR
        new_oe.oe.FILE_ROUGH = self.oe.FILE_ROUGH
        new_oe.oe.FZP = self.oe.FZP
        new_oe.oe.HOLO_R1 = self.oe.HOLO_R1
        new_oe.oe.HOLO_R2 = self.oe.HOLO_R2
        new_oe.oe.HOLO_DEL = self.oe.HOLO_DEL
        new_oe.oe.HOLO_GAM = self.oe.HOLO_GAM
        new_oe.oe.HOLO_W = self.oe.HOLO_W
        new_oe.oe.HOLO_RT1 = self.oe.HOLO_RT1
        new_oe.oe.HOLO_RT2 = self.oe.HOLO_RT2
        new_oe.oe.AZIM_FAN = self.oe.AZIM_FAN
        new_oe.oe.DIST_FAN = self.oe.DIST_FAN
        new_oe.oe.COMA_FAC = self.oe.COMA_FAC
        new_oe.oe.ALFA = self.oe.ALFA
        new_oe.oe.GAMMA = self.oe.GAMMA
        new_oe.oe.R_IND_OBJ = self.oe.R_IND_OBJ
        new_oe.oe.R_IND_IMA = self.oe.R_IND_IMA
        new_oe.oe.R_ATTENUATION_OBJ = self.oe.R_ATTENUATION_OBJ
        new_oe.oe.R_ATTENUATION_IMA = self.oe.R_ATTENUATION_IMA
        new_oe.oe.F_R_IND = self.oe.F_R_IND
        new_oe.oe.FILE_R_IND_OBJ = self.oe.FILE_R_IND_OBJ
        new_oe.oe.FILE_R_IND_IMA = self.oe.FILE_R_IND_IMA
        new_oe.oe.RUL_A1 = self.oe.RUL_A1
        new_oe.oe.RUL_A2 = self.oe.RUL_A2
        new_oe.oe.RUL_A3 = self.oe.RUL_A3
        new_oe.oe.RUL_A4 = self.oe.RUL_A4
        new_oe.oe.F_POLSEL = self.oe.F_POLSEL
        new_oe.oe.F_FACET = self.oe.F_FACET
        new_oe.oe.F_FAC_ORIENT = self.oe.F_FAC_ORIENT
        new_oe.oe.F_FAC_LATT = self.oe.F_FAC_LATT
        new_oe.oe.RFAC_LENX = self.oe.RFAC_LENX
        new_oe.oe.RFAC_LENY = self.oe.RFAC_LENY
        new_oe.oe.RFAC_PHAX = self.oe.RFAC_PHAX
        new_oe.oe.RFAC_PHAY = self.oe.RFAC_PHAY
        new_oe.oe.RFAC_DELX1 = self.oe.RFAC_DELX1
        new_oe.oe.RFAC_DELX2 = self.oe.RFAC_DELX2
        new_oe.oe.RFAC_DELY1 = self.oe.RFAC_DELY1
        new_oe.oe.RFAC_DELY2 = self.oe.RFAC_DELY2
        new_oe.oe.FILE_FAC = self.oe.FILE_FAC
        new_oe.oe.F_SEGMENT = self.oe.F_SEGMENT
        new_oe.oe.ISEG_XNUM = self.oe.ISEG_XNUM
        new_oe.oe.ISEG_YNUM = self.oe.ISEG_YNUM
        new_oe.oe.FILE_SEGMENT = self.oe.FILE_SEGMENT
        new_oe.oe.FILE_SEGP = self.oe.FILE_SEGP
        new_oe.oe.SEG_LENX = self.oe.SEG_LENX
        new_oe.oe.SEG_LENY = self.oe.SEG_LENY
        new_oe.oe.F_KOMA = self.oe.F_KOMA
        new_oe.oe.FILE_KOMA = self.oe.FILE_KOMA
        new_oe.oe.F_EXIT_SHAPE = self.oe.F_EXIT_SHAPE
        new_oe.oe.F_INC_MNOR_ANG = self.oe.F_INC_MNOR_ANG
        new_oe.oe.ZKO_LENGTH = self.oe.ZKO_LENGTH
        new_oe.oe.RKOMA_CX = self.oe.RKOMA_CX
        new_oe.oe.RKOMA_CY = self.oe.RKOMA_CY
        new_oe.oe.F_KOMA_CA = self.oe.F_KOMA_CA
        new_oe.oe.FILE_KOMA_CA = self.oe.FILE_KOMA_CA
        new_oe.oe.F_KOMA_BOUNCE = self.oe.F_KOMA_BOUNCE
        new_oe.oe.X_RIP_AMP = self.oe.X_RIP_AMP
        new_oe.oe.X_RIP_WAV = self.oe.X_RIP_WAV
        new_oe.oe.X_PHASE = self.oe.X_PHASE
        new_oe.oe.Y_RIP_AMP = self.oe.Y_RIP_AMP
        new_oe.oe.Y_RIP_WAV = self.oe.Y_RIP_WAV
        new_oe.oe.Y_PHASE = self.oe.Y_PHASE
        new_oe.oe.N_RIP = self.oe.N_RIP
        new_oe.oe.ROUGH_X = self.oe.ROUGH_X
        new_oe.oe.ROUGH_Y = self.oe.ROUGH_Y
        new_oe.oe.OE_NUMBER = self.oe.OE_NUMBER
        new_oe.oe.IDUMMY = self.oe.IDUMMY
        new_oe.oe.DUMMY = self.oe.DUMMY

        new_oe.oe.CX_SLIT = copy.deepcopy(self.oe.CX_SLIT)
        new_oe.oe.CZ_SLIT = copy.deepcopy(self.oe.CZ_SLIT)
        new_oe.oe.D_PLATE = copy.deepcopy(self.oe.D_PLATE)
        new_oe.oe.FILE_ABS = copy.deepcopy(self.oe.FILE_ABS)
        new_oe.oe.FILE_SCR_EXT = copy.deepcopy(self.oe.FILE_SCR_EXT)
        new_oe.oe.I_ABS = copy.deepcopy(self.oe.I_ABS)
        new_oe.oe.I_SCREEN = copy.deepcopy(self.oe.I_SCREEN)
        new_oe.oe.I_SLIT = copy.deepcopy(self.oe.I_SLIT)
        new_oe.oe.I_STOP = copy.deepcopy(self.oe.I_STOP)
        new_oe.oe.K_SLIT = copy.deepcopy(self.oe.K_SLIT)
        new_oe.oe.RX_SLIT = copy.deepcopy(self.oe.RX_SLIT)
        new_oe.oe.RZ_SLIT = copy.deepcopy(self.oe.RZ_SLIT)
        new_oe.oe.SCR_NUMBER = copy.deepcopy(self.oe.SCR_NUMBER)
        new_oe.oe.SL_DIS = copy.deepcopy(self.oe.SL_DIS)
        new_oe.oe.THICK = copy.deepcopy(self.oe.THICK)
        new_oe.oe.CCC = copy.deepcopy(self.oe.CCC)

        return new_oe

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