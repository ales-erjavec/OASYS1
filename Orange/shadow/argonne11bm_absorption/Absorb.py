"""Web absorption computation
   Copyright: 2009, Robert B. Von Dreele (Argonne National Laboratory)
"""
import os
import math
import re
import sys

import numpy as np

import Orange.shadow.argonne11bm_absorption.Element as Element

class Absorb():
    ''' '''
    Wave = 1.5405      #CuKa default
    Kev = 12.397639    #keV for 1A x-rays
    Wmin = 0.05        #wavelength range
    Wmax = 2.0
    Wres = 0.004094    #plot resolution step size as const delta-lam/lam - gives 1000 steps for Wmin to Wmax
    Eres = 1.5e-4      #typical energy resolution for synchrotron x-ray sources
    Energy = Kev/Wave
    Volume = 0
    ifVol = False
    Zcell = 1
    Pack = 0.50
    Path = 0.4
    
    def __init__(self, Path, Wave=0, Energy=0, InputDensity=0, Packing=0.0):
        if Wave and Energy:
            raise Exception("Energy and wavelength cannot both be set")
        if Wave:
            self.ifWave = True
            self.Wave = Wave
            self.Energy = self.Kev/self.Wave
        elif Energy:
            self.ifWave = False
            self.Energy = Energy
            self.Wave = self.Kev/Energy 
        else:
            raise Exception("Either energy or wavelength must be set")
        if InputDensity and Packing:
            raise Exception("InputDensity and Packing cannot both be set")
        if InputDensity:
            self.InputDensity = InputDensity
            self.Pack = 0
        elif Packing:
            self.InputDensity = 0
            self.Pack = Packing
        else:
            raise Exception("Either InputDensity or Packing must be set")
        self.Path = Path

    def SetElems(self,ElementString):
        self.Elems = []
        # are there any invalid characters
        invalid = re.findall('[^A-Za-z0-9.\s]', ElementString)
        if len(invalid):
            s = ""
            for i in invalid: s+=i
            raise Exception('Invalid characters ("%s") in chemical formula' % s)
        for El,N in re.findall('\s*([A-Z][a-z]?)\s*([0-9]*\\.?[0-9]*)\s*',
                               ElementString):
            if not N:
                N = 1
            ElemSym = El.strip().upper()
            try:
                atomData = Element.GetAtomInfo(ElemSym)
            except UnboundLocalError:
                raise Exception('Element "%s" not found' % ElemSym)
            FormFactors = Element.GetFormFactorCoeff(ElemSym)
            for FormFac in FormFactors:
                FormSym = FormFac['Symbol'].strip()
                if FormSym == ElemSym:
                    Z = FormFac['Z']                #At. No.
                    #N =                           #no atoms / formula unit
                    Orbs = Element.GetXsectionCoeff(ElemSym)
                    Elem = [ElemSym,Z,float(N),FormFac,Orbs,atomData]
            self.Elems.append(Elem)
        if not self.Elems:
            raise Exception("No valid elements found in chemical formula")

    ########################################################
    #
    # METHOD ADDED FOR ONLINE COMPUTATION OF TRANSMITTANCE
    #
    ########################################################

    def ComputeTransmittance(self):
        return math.exp(-self.ComputeLinearAttenuationCoefficient()*self.Path)

    def ComputeLinearAttenuationCoefficient(self):
        coefficient = 0.0

        self.Energy = self.Kev/self.Wave
        self.Energy = round(self.Energy,4)
        E = self.Energy
        DE = E*self.Eres                         #smear by defined source resolution
        self.Volume = 0
        for Elem in self.Elems:
            self.Volume += 10.*Elem[2]
        muT = 0
        Mass = 0
        for Elem in self.Elems:
            Mass += self.Zcell*Elem[2]*Elem[5]['Mass']
            r1 = Element.FPcalc(Elem[4],E+DE)
            r2 = Element.FPcalc(Elem[4],E-DE)
            mu = 0
            if Elem[1] > 78 and self.Energy+DE > self.Kev/0.16:
                mu = self.Zcell*Elem[2]*(r1[2]+r2[2])/2.0
            elif Elem[1] > 94 and self.Energy-DE < self.Kev/2.67:
                mu = 0
            else:
                mu = self.Zcell*Elem[2]*(r1[2]+r2[2])/2.0
            muT += mu

        if self.Volume:
            if self.InputDensity:
                den = Mass/(0.602*self.Volume)
                self.Pack = self.InputDensity/den

            coefficient = self.Pack*muT/self.Volume
        else:
            raise Exception('error in Volume computation')

        return coefficient