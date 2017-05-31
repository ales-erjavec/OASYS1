import os, sys

from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtWidgets import QWidget, QGridLayout, QFileDialog, QMessageBox, QLabel, QComboBox, QTextEdit

from orangewidget import gui as orange_gui

current_module = sys.modules[__name__]
gui_point_size=12

# ----------------------------------
# Default fonts
def widgetLabel(widget, label="", labelWidth=None, **misc):
    lbl = QLabel(label, widget)
    if labelWidth:
        lbl.setFixedSize(labelWidth, lbl.sizeHint().height())
    orange_gui.miscellanea(lbl, None, widget, **misc)

    font = lbl.font()
    font.setPointSize(current_module.gui_point_size)
    lbl.setFont(font)

    return lbl

def set_font_size(point_size=12):
    current_module.gui_point_size = point_size

    qapp = QCoreApplication.instance()

    # change application font
    font = qapp.font()
    font.setPointSize(current_module.gui_point_size)
    qapp.setFont(font)

    # change orange gui label font
    orange_gui.widgetLabel = widgetLabel

def lineEdit(widget, master, value, label=None, labelWidth=None,
         orientation='vertical', box=None, callback=None,
         valueType=str, validator=None, controlWidth=None,
         callbackOnType=False, focusInCallback=None,
         enterPlaceholder=False, **misc):

    ledit = orange_gui.lineEdit(widget, master, value, label, labelWidth, orientation, box, callback, valueType, validator, controlWidth, callbackOnType, focusInCallback, enterPlaceholder, **misc)

    if value:
        if (valueType != str):
            ledit.setAlignment(Qt.AlignRight)

    ledit.setStyleSheet("background-color: white;")

    return ledit

def widgetBox(widget, box=None, orientation='vertical', margin=None, spacing=4, height=None, width=None, **misc):

    box = orange_gui.widgetBox(widget, box, orientation, margin, spacing, **misc)
    box.layout().setAlignment(Qt.AlignTop)

    if not height is None:
        box.setFixedHeight(height)
    if not width is None:
        box.setFixedWidth(width)

    return box

def tabWidget(widget, height=None, width=None):
    tabWidget = orange_gui.tabWidget(widget)

    if not height is None:
        tabWidget.setFixedHeight(height)
    if not width is None:
        tabWidget.setFixedWidth(width)

    tabWidget.setStyleSheet('QTabBar::tab::selected {background-color: #a6a6a6;}')

    return tabWidget

def createTabPage(tabWidget, name, widgetToAdd=None, canScroll=False, height=None, width=None, isImage=False):

    tab = orange_gui.createTabPage(tabWidget, name, widgetToAdd, canScroll)
    tab.layout().setAlignment(Qt.AlignTop)

    if not height is None:
        tab.setFixedHeight(height)
    if not width is None:
        tab.setFixedWidth(width)

    if isImage: tab.setStyleSheet("background-color: #FFFFFF;")

    return tab

def selectFileFromDialog(widget, previous_file_path="", message="Select File", start_directory=".", file_extension_filter="*.*"):
    file_path = QFileDialog.getOpenFileName(widget, message, start_directory, file_extension_filter)[0]

    if not file_path is None and not file_path.strip() == "":
        return file_path
    else:
        return previous_file_path

def textArea(height=None, width=None, readOnly=True):
        area = QTextEdit()
        area.setReadOnly(readOnly)
        area.setStyleSheet("background-color: white;")

        if not height is None: area.setFixedHeight(height)
        if not width is None: area.setFixedWidth(width)
    
        return area
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

class OptionDialog(QMessageBox):

    selection = 0

    def __init__(self, parent, message, title, options, default):
        super(OptionDialog, self).__init__(parent)

        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.setIcon(QMessageBox.Question)
        self.setText(message)
        self.setWindowTitle(title)

        self.selection = default

        box = QWidget()
        box.setLayout(QGridLayout())
        box.setFixedHeight(40)

        box_combo = QWidget()
        combo = QComboBox(box_combo)
        combo.setEditable(False)
        combo.box = box_combo
        for item in options:
            combo.addItem(str(item))
        combo.setCurrentIndex(default)
        combo.currentIndexChanged.connect(self.set_selection)

        box.layout().addWidget(QLabel("Select Option"), 0, 0, 1, 1)
        box.layout().addWidget(box_combo, 0, 1, 1, 1)

        self.layout().addWidget(box, 1, 1, 1, 2)

    def set_selection(self, index):
        self.selection = index

    @classmethod
    def get_option(cls, parent=None, message="Select Option", title="Select Option", option=["No", "Yes"], default=0):
        dlg = OptionDialog(parent, message, title, option, default)
        if dlg.exec_() == QMessageBox.Ok:
            return dlg.selection
        else:
            return None


#######################################################################
#######################################################################
#######################################################################
# FIXING BUG ON MATPLOTLIB 2.0.0
#######################################################################
#######################################################################
#######################################################################

from silx.gui.plot.backends.BackendMatplotlib import BackendMatplotlibQt
from silx.gui.plot.PlotWindow import PlotWindow

class OasysBackendMatplotlibQt(BackendMatplotlibQt):

    def __init__(self, plot, parent=None):
        super().__init__(plot, parent)

    def _onMouseMove(self, event):
        try:
            super(OasysBackendMatplotlibQt, self)._onMouseMove(event)
        except ValueError as exception:
            if "Data has no positive values, and therefore can not be log-scaled" in str(exception):
                pass
            else:
                raise exception


def plotWindow(parent=None, backend=None,
               resetzoom=True, autoScale=True, logScale=True, grid=True,
               curveStyle=True, colormap=True,
               aspectRatio=True, yInverted=True,
               copy=True, save=True, print_=True,
               control=False, position=False,
               roi=True, mask=True, fit=False):
    if backend is None:
        backend = OasysBackendMatplotlibQt

    return PlotWindow(parent=parent, backend=backend,
                      resetzoom=resetzoom, autoScale=autoScale, logScale=logScale, grid=grid,
                      curveStyle=curveStyle, colormap=colormap,
                      aspectRatio=aspectRatio, yInverted=yInverted,
                      copy=copy, save=save, print_=print_,
                      control=control, position=position,
                      roi=roi, mask=mask, fit=fit)
