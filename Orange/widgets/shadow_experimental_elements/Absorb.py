"""Web absorption computation
   Copyright: 2009, Robert B. Von Dreele (Argonne National Laboratory)
"""
import os
import math
import re
import sys

import numpy as np

import Orange.widgets.shadow_experimental_elements.Element as Element

class Absorb():
    ''' '''
    Wave = 1.5405      #CuKa default
    Kev = 12.397639    #keV for 1A x-rays
    Wmin = 0.05        #wavelength range
    Wmax = 2.0
    Wres = 0.004094    #plot resolution step size as const delta-lam/lam - gives 1000 steps for Wmin to Wmax
    Eres = 1.5e-4      #typical energy resolution for synchrotron x-ray sources
    Energy = Kev/Wave
    #ifWave = False   # broken
    Volume = 0
    ifVol = False
    Zcell = 1
    Pack = 0.50
    Radius = 0.4
    
    def __init__(self, Radius, Wave=0, Energy=0, InputDensity=0, Packing=0.0):
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
        self.Radius = Radius

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

    def ComputeMu(self):
        #Gkmu = unichr(0x3bc)
        Gkmu = 'mu'
        #Pwr3 = unichr(0x0b3)
        Pwr3 = "<sup>3</sup>"
        self.Energy = self.Kev/self.Wave
        self.Energy = round(self.Energy,4)
        E = self.Energy
        DE = E*self.Eres                         #smear by defined source resolution
        Text = ''
        self.Volume = 0
        for Elem in self.Elems:
            self.Volume += 10.*Elem[2]
        muT = 0
        Mass = 0
        Fo = 0
        Fop = 0
        Text += "Wavelength = %.4f Angstrom<BR>\n" % (self.Wave)
        Text += "Energy     = %.4f KeV<BR>\n" % (self.Energy)
        Text += "Sample Radius = %.2f mm (diameter=%.2f mm)<BR>\n" % (self.Radius,
                                                                  2*self.Radius,)
        Text += "<PRE>\n"
        for Elem in self.Elems:
            Mass += self.Zcell*Elem[2]*Elem[5]['Mass']
            r1 = Element.FPcalc(Elem[4],E+DE)
            r2 = Element.FPcalc(Elem[4],E-DE)
            Els = Elem[0]
            Els = Els.ljust(2).lower().capitalize()
            mu = 0
            Fo += Elem[2]*Elem[1]
            if Elem[1] > 78 and self.Energy+DE > self.Kev/0.16:
                mu = self.Zcell*Elem[2]*(r1[2]+r2[2])/2.0
                Text += "%s\t%s%8.2f  %s%6s  %s%6.3f  %s%10.2f %s\n" %    (
                    'Element= '+str(Els),"N = ",Elem[2]," f'=",'not valid',
                    ' f"=',(r1[1]+r2[1])/2.0,' '+Gkmu+'=',mu,'barns')
            elif Elem[1] > 94 and self.Energy-DE < self.Kev/2.67:
                mu = 0
                Text += "%s\t%s%8.2f  %s%6s  %s%6s  %s%10s%s\n" %    (
                    'Element= '+str(Els),"N = ",Elem[2]," f'=",'not valid',
                    ' f"=','not valid',' '+Gkmu+'=','not valid')
            else:
                mu = self.Zcell*Elem[2]*(r1[2]+r2[2])/2.0
                Fop += Elem[2]*(Elem[1]+(r1[0]+r2[0])/2.0)
                Text += "%s\t%s%8.2f  %s%6.3f  %s%6.3f  %s%10.2f %s\n" %    (
                    'Element= '+str(Els),"N = ",Elem[2]," f'=",(r1[0]+r2[0])/2.0,
                    ' f"=',(r1[1]+r2[1])/2.0,' '+Gkmu+'=',mu,'barns')
            muT += mu
        
        Text += "</PRE>\n"
        if self.Volume:
            den = Mass/(0.602*self.Volume)                
            if self.InputDensity: 
                self.Pack = self.InputDensity/den
                label = 'Input'
            else:
                label = 'Packed'
            Text += '%s' % ('Est. density=')
            Text += '%6.3f %s%.3f %s<BR>\n' % (den,'g/cm'+Pwr3+
                                           ', %s density=' % label,
                                           self.Pack*den,'g/cm'+Pwr3)
            Text += "%s %s%10.2f %s" % ("Total",' '+Gkmu+'=',self.Pack*muT/self.Volume,'cm<sup>-1</sup>, ')
            Text += "%s%10.2f%s" % ('Total '+Gkmu+'R=',self.Radius*self.Pack*muT/(10.0*self.Volume),', ')
            Text += "%s%10.4f%s<BR>\n" % ('Transmission exp(-2'+Gkmu+'R)=', \
                100.0*math.exp(-2*self.Radius*self.Pack*muT/(10.0*self.Volume)),'%')
            Text += '%s%10.2f%s\n'%('X-ray small angle scattering contrast',(28.179*Fo/self.Volume)**2,'*10<sup>20/cm<sup>')
            if Fop:
                Text += '%s%10.2f%s\n'%('Anomalous X-ray small angle scattering contrast',(28.179*Fop/self.Volume)**2,'*10<sup>20/cm<sup>')
            print(Text)
        else: 
            print("error in Volume computation")
        self.CalcFPPS()

    def CalcFPPS(self):
        """generate f" curves for selected elements
           does constant delta-lambda/lambda steps over defined range
        """
        FPPS = []
        if self.Elems:
            #wx.BeginBusyCursor()
            Corr = self.Zcell*self.Radius*self.Pack/(10.0*self.Volume)
            try:
                muT = []
                for iE,Elem in enumerate(self.Elems):
                    Els = Elem[0]
                    Els = Els = Els.ljust(2).lower().capitalize()
                    Wmin = self.Wmin
                    Wmax = self.Wmax
                    Z = Elem[1]
                    lWmin = math.log(Wmin)
                    N = int(round(math.log(Wmax/Wmin)/self.Wres))    #number of constant delta-lam/lam steps
                    I = range(N+1)
                    Ws = []
                    for i in I: Ws.append(math.exp(i*self.Wres+lWmin))
                    mus = []
                    Es = []
                    for j,W in enumerate(Ws):
                        E = self.Kev/W
                        DE = E*self.Eres                         #smear by defined source resolution
                        res1 = Element.FPcalc(Elem[4],E+DE)
                        res2 = Element.FPcalc(Elem[4],E-DE)
                        muR = Corr*Elem[2]*(res1[2]+res2[2])/2.0
                        mus.append(muR)
                        if iE:
                            muT[j] += muR
                        else:
                            muT.append(muR)
                        Es.append(E)
                    if self.ifWave:
                        Fpps = (Els,Ws,mus)
                    else:
                        Fpps = (Els,Es,mus)
                    FPPS.append(Fpps)
                if self.ifWave:
                    Fpps = ('Total',Ws,muT)
                else:
                    Fpps = ('Total',Es,muT)
                FPPS.append(Fpps)
            finally:
                pass
#                wx.EndBusyCursor()
        self.FPPS = FPPS
