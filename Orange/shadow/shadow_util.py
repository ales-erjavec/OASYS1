__author__ = 'labx'

from PyQt4.QtCore import Qt
from Orange.widgets import gui

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
