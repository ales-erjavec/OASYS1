__author__ = 'labx'

from PyQt4.QtCore import Qt
from Orange.widgets import gui

import numpy, math
import Shadow.ShadowLibExtensions as sd
import sys
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib import figure as matfig
    import pylab
except ImportError:
    print(sys.exc_info()[1])
    pass

import Shadow.ShadowTools as ST
import Shadow.ShadowToolsPrivate as stp
from Shadow.ShadowToolsPrivate import Histo1_Ticket as Histo1_Ticket
from Shadow.ShadowToolsPrivate import plotxy_Ticket as plotxy_Ticket
import os

class ShadowGui():

    @classmethod
    def lineEdit(cls, widget, master, value, label=None, labelWidth=None,
             orientation='vertical', box=None, callback=None,
             valueType=str, validator=None, controlWidth=None,
             callbackOnType=False, focusInCallback=None,
             enterPlaceholder=False, **misc):

        lEdit = gui.lineEdit(widget, master, value, label, labelWidth, orientation, box, callback, valueType, validator, controlWidth, callbackOnType, focusInCallback, enterPlaceholder, **misc)

        if value:
            if (isinstance(value, str)):
                lEdit.setAlignment(Qt.AlignRight)

        return lEdit

    @classmethod
    def widgetBox(cls, widget, box=None, orientation='vertical', margin=None, spacing=4, height=None, width=None, **misc):

        box = gui.widgetBox(widget, box, orientation, margin, spacing, **misc)
        box.layout().setAlignment(Qt.AlignTop)

        if not height is None:
            box.setFixedHeight(height)
        if not width is None:
            box.setFixedWidth(width)

        return box

    @classmethod
    def tabWidget(cls, widget, height=None, width=None):
        tabWidget = gui.tabWidget(widget)

        if not height is None:
            tabWidget.setFixedHeight(height)
        if not width is None:
            tabWidget.setFixedWidth(width)

        return tabWidget

    @classmethod
    def createTabPage(cls, tabWidget, name, widgetToAdd=None, canScroll=False, height=None, width=None):

        tab = gui.createTabPage(tabWidget, name, widgetToAdd, canScroll)
        tab.layout().setAlignment(Qt.AlignTop)

        if not height is None:
            tab.setFixedHeight(height)
        if not width is None:
            tab.setFixedWidth(width)

        return tab

class ShadowPlot:

    @classmethod
    def plotxy_preview(cls, beam,cols1,cols2,nbins=25,nbins_h=None,level=5,xrange=None,yrange=None,nolost=0,title='PLOTXY',xtitle=None,ytitle=None,noplot=0,calfwhm=0,contour=0):
          if nbins_h==None: nbins_h=nbins+1
          try:
            stp.plotxy_CheckArg(beam,cols1,cols2,nbins,nbins_h,level,xrange,yrange,nolost,title,xtitle,ytitle,noplot,calfwhm,contour)
          except stp.ArgsError as e:
            raise e
          plt.ioff()
          col1,col2,col3,col4 = ST.getshcol(beam,(cols1,cols2,10,23,))

          nbins=nbins+1
          if xtitle==None: xtitle=(stp.getLabel(cols1-1))[0]
          if ytitle==None: ytitle=(stp.getLabel(cols2-1))[0]

          if nolost==0: t = numpy.where(col3!=-3299)
          if nolost==1: t = numpy.where(col3==1.0)
          if nolost==2: t = numpy.where(col3!=1.0)

          if xrange==None: xrange = stp.setGoodRange(col1[t])
          if yrange==None: yrange = stp.setGoodRange(col2[t])

          tx = numpy.where((col1>xrange[0])&(col1<xrange[1]))
          ty = numpy.where((col2>yrange[0])&(col2<yrange[1]))

          tf = set(list(t[0])) & set(list(tx[0])) & set(list(ty[0]))
          t = (numpy.array(sorted(list(tf))),)
          if len(t[0])==0:
            print ("no point selected")
            return None

          figure = pylab.plt.figure()

          axScatter = figure.add_axes([0.1,0.1,0.8,0.8])
          axScatter.set_xlabel(xtitle)
          axScatter.set_ylabel(ytitle)

          if contour==0:
            axScatter.scatter(col1[t],col2[t],s=0.5)
          if contour>0 and contour<7:
            if contour==1 or contour==3 or contour==5: w = numpy.ones( len(col1) )
            if contour==2 or contour==4 or contour==6: w = col4
            grid = numpy.zeros(nbins*nbins).reshape(nbins,nbins)
            for i in t[0]:
              indX = stp.findIndex(col1[i],nbins,xrange[0],xrange[1])
              indY = stp.findIndex(col2[i],nbins,yrange[0],yrange[1])
              try:
                grid[indX][indY] = grid[indX][indY] + w[i]
              except IndexError:
                pass
            X, Y = numpy.mgrid[xrange[0]:xrange[1]:nbins*1.0j,yrange[0]:yrange[1]:nbins*1.0j]
            L = numpy.linspace(numpy.amin(grid),numpy.amax(grid),level)
            if contour==1 or contour==2: axScatter.contour(X, Y, grid, colors='k', levels=L)
            if contour==3 or contour==4: axScatter.contour(X, Y, grid, levels=L)
            if contour==5 or contour==6: axScatter.pcolor(X, Y, grid)

          for tt in axScatter.get_xticklabels():
            tt.set_size('x-small')
          for tt in axScatter.get_yticklabels():
            tt.set_size('x-small')

          pylab.plt.draw()

          ticket = plotxy_Ticket()
          ticket.figure = figure
          ticket.xrange = xrange
          ticket.yrange = yrange
          ticket.xtitle = xtitle
          ticket.ytitle = ytitle
          ticket.title = title
          ticket.intensity = col4[t].sum()
          ticket.averagex = numpy.average( col1[t] )
          ticket.averagey = numpy.average( col2[t] )
          ticket.intensityinslit = 0
          return ticket

class ShadowMath:

    @classmethod
    def vectorial_product(cls, vector1, vector2):
        result = [0, 0, 0]

        result[0] = vector1[1]*vector2[2] - vector1[2]*vector2[1]
        result[1] = -(vector1[0]*vector2[2] - vector1[2]*vector2[0])
        result[2] = vector1[0]*vector2[1] - vector1[1]*vector2[0]

        return result

    @classmethod
    def scalar_product(cls, vector1, vector2):
        return vector1[0]*vector2[0] + vector1[1]*vector2[1] + vector1[2]*vector2[2]

    @classmethod
    def vector_modulus(cls, vector):
        return math.sqrt(cls.scalar_product(vector, vector))

    @classmethod
    def vector_multiply(cls, vector, constant):
        result = [0, 0, 0]

        result[0] = vector[0] * constant
        result[1] = vector[1] * constant
        result[2] = vector[2] * constant

        return result

    @classmethod
    def vector_divide(cls, vector, constant):
        result = [0, 0, 0]

        result[0] = vector[0] / constant
        result[1] = vector[1] / constant
        result[2] = vector[2] / constant

        return result

    @classmethod
    def vector_normalize(cls, vector):
        return cls.vector_divide(vector, cls.vector_modulus(vector))

    @classmethod
    def vector_sum(cls, vector1, vector2):
        result = [0, 0, 0]

        result[0] = vector1[0] + vector2[0]
        result[1] = vector1[1] + vector2[1]
        result[2] = vector1[2] + vector2[2]

        return result

    @classmethod
    def vector_difference(cls, vector1, vector2):
        result = [0, 0, 0]

        result[0] = vector1[0] - vector2[0]
        result[1] = vector1[1] - vector2[1]
        result[2] = vector1[2] - vector2[2]

        return result

    @classmethod
    def point_distance(cls, point1, point2):
        return cls.vector_modulus(cls.vector_difference(point1, point2))
