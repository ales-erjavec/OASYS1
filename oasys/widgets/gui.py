import os, sys

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFileDialog, QMessageBox, QLineEdit, QLabel

from orangewidget import gui

# ----------------------------------
# Default fonts
def widgetLabel(widget, label="", labelWidth=None, **misc):
    lbl = QLabel(label, widget)
    if labelWidth:
        lbl.setFixedSize(labelWidth, lbl.sizeHint().height())
    gui.miscellanea(lbl, None, widget, **misc)

    font = lbl.font()
    #font.setPointSize(11)
    lbl.setFont(font)

    return lbl

gui.widgetLabel = widgetLabel

def lineEdit(widget, master, value, label=None, labelWidth=None,
         orientation='vertical', box=None, callback=None,
         valueType=str, validator=None, controlWidth=None,
         callbackOnType=False, focusInCallback=None,
         enterPlaceholder=False, **misc):

    ledit = gui.lineEdit(widget, master, value, label, labelWidth, orientation, box, callback, valueType, validator, controlWidth, callbackOnType, focusInCallback, enterPlaceholder, **misc)

    if value:
        if (valueType != str):
            ledit.setAlignment(Qt.AlignRight)

    return ledit

def widgetBox(widget, box=None, orientation='vertical', margin=None, spacing=4, height=None, width=None, **misc):

    box = gui.widgetBox(widget, box, orientation, margin, spacing, **misc)
    box.layout().setAlignment(Qt.AlignTop)

    if not height is None:
        box.setFixedHeight(height)
    if not width is None:
        box.setFixedWidth(width)

    return box

def tabWidget(widget, height=None, width=None):
    tabWidget = gui.tabWidget(widget)

    if not height is None:
        tabWidget.setFixedHeight(height)
    if not width is None:
        tabWidget.setFixedWidth(width)

    return tabWidget

def createTabPage(tabWidget, name, widgetToAdd=None, canScroll=False, height=None, width=None):

    tab = gui.createTabPage(tabWidget, name, widgetToAdd, canScroll)
    tab.layout().setAlignment(Qt.AlignTop)

    if not height is None:
        tab.setFixedHeight(height)
    if not width is None:
        tab.setFixedWidth(width)

    return tab

def selectFileFromDialog(widget, previous_file_path="", message="Select File", start_directory=".", file_extension_filter="*.*"):
    file_path = QFileDialog.getOpenFileName(widget, message, start_directory, file_extension_filter)

    if not file_path is None and not file_path.strip() == "":
        return file_path
    else:
        return previous_file_path

# ------------------------------------
# UTILITY CLASS
# ------------------------------------

class ConfirmDialog(QMessageBox):
    def __init__(self, parent, message, title):
        super(ConfirmDialog, self).__init__(parent)

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setIcon(QMessageBox.Question)
        self.setText(message)
        self.setWindowTitle(title)

    @classmethod
    def confirmed(cls, parent=None, message="Confirm Action?", title="Confirm Action"):
        return ConfirmDialog(parent, message, title).exec_() == QMessageBox.Ok
