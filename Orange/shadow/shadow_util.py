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

    lEdit = gui.lineEdit(widget, master, value, label, labelWidth, orientation, box, callback, valueType, validator, controlWidth, callbackOnType, focusInCallback, enterPlaceholder)

    if value:
        if (isinstance(value, str)):
            lEdit.setAlignment(Qt.AlignRight)

    return lEdit
