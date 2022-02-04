import numpy

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QFileDialog, QMessageBox, QLabel, QComboBox, QTextEdit

from orangewidget import gui as orange_gui

# ----------------------------------
# Default fonts
def widgetLabel(widget, label="", labelWidth=None, **misc):
    lbl = QLabel(label, widget)
    if labelWidth:
        lbl.setFixedSize(labelWidth, lbl.sizeHint().height())
    orange_gui.miscellanea(lbl, None, widget, **misc)

    return lbl

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

def selectSaveFileFromDialog(widget, message="Save File", default_file_name="", file_extension_filter="*.*"):
    file_path = QFileDialog.getSaveFileName(widget, message, default_file_name, file_extension_filter)[0]

    if not file_path is None and not file_path.strip() == "":
        return file_path
    else:
        return None

def selectDirectoryFromDialog(widget, previous_directory_path="", message="Select Directory", start_directory="."):
    directory_path = QFileDialog.getExistingDirectory(widget, message, start_directory)
    if not directory_path is None and not directory_path.strip() == "":
        return directory_path
    else:
        return previous_directory_path

def textArea(height=None, width=None, readOnly=True, noWrap=None):
        area = QTextEdit()
        area.setReadOnly(readOnly)
        area.setStyleSheet("background-color: white;")
        if noWrap is not None:
            area.setLineWrapMode(QTextEdit.NoWrap)

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

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import art3d

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class FigureCanvas3D(FigureCanvas):

    def __init__(self, fig, ax, show_legend=True):
        super().__init__(fig)
        self.ax = ax
        self.size_x, self.size_y = fig.get_size_inches() * fig.dpi
        self.x_c = int(self.size_x / 2)
        self.y_c = int(self.size_y / 2)

        self.last_pos_x = self.x_c
        self.last_pos_y = self.y_c

        self.__show_legend = show_legend
        self.__add_legend()

    def __add_legend(self):
        if self.__show_legend:
            self.ax.text2D(0.05, 0.95,
                           "Mouse Left Button -> Click and Hold: Rotate\n" +  #, Double Click: Recenter\n" + \
                           "Mouse Right Button -> Click and Hold: Zoom\n" +
                           "Mouse Left & Right Buttons or Central Button -> Click and Hold: Shift",
                           transform=self.ax.transAxes,
                           color='blue')

    def __recenter(self, posx, posy):
        pass #

    def __reset_view(self):
        pass

    def __pan(self, dx, dy):
        # convert dx dy -> dxx dyy dzz
        minx, maxx, miny, maxy, minz, maxz = self.ax.get_w_lims()
        elev, azim = numpy.deg2rad(self.ax.elev), numpy.deg2rad(self.ax.azim)
        dxe = (dy / self.size_y) * numpy.sin(elev)
        dye = - (dx / self.size_x)
        dze = - (dy / self.size_y) * numpy.cos(elev)
        dxx = (maxx - minx) * (dxe * numpy.cos(azim) - dye * numpy.sin(azim))
        dyy = (maxy - miny) * (dye * numpy.cos(azim) + dxe * numpy.sin(azim))
        dzz = (maxz - minz) * (dze)
        # pan
        self.ax.set_xlim3d(minx + dxx, maxx + dxx)
        self.ax.set_ylim3d(miny + dyy, maxy + dyy)
        self.ax.set_zlim3d(minz + dzz, maxz + dzz)
        self.ax.get_proj()

    def __zoom(self, dy):
        minx, maxx, miny, maxy, minz, maxz = self.ax.get_w_lims()
        df = 1 - ((self.size_y - dy) / self.size_y)
        dx = (maxx - minx) * df
        dy = (maxy - miny) * df
        dz = (maxz - minz) * df
        self.ax.set_xlim3d(minx - dx, maxx + dx)
        self.ax.set_ylim3d(miny - dy, maxy + dy)
        self.ax.set_zlim3d(minz - dz, maxz + dz)
        self.ax.get_proj()

    def __rotate(self, dx, dy):
        self.ax.view_init(azim=art3d._norm_angle(self.ax.azim - (dx / self.size_x) * 180),
                          elev=art3d._norm_angle(self.ax.elev - (dy / self.size_y) * 180))

    def mouseMoveEvent(self, event):
        pos_x = event.pos().x() - self.x_c
        pos_y = -(event.pos().y() - self.y_c)

        dx = pos_x - self.last_pos_x
        dy = pos_y - self.last_pos_y

        if dx == 0 and dy == 0: return

        if int(event.buttons()) == 1:        self.__rotate(dx, dy) # left button
        elif int(event.buttons())==2:        self.__zoom(dy) # right button
        elif int(event.buttons()) in [3, 4]: self.__pan(dx, dy) #central button/wheel or left and right together

        self.last_pos_x = pos_x
        self.last_pos_y = pos_y

        self.draw()

    def clear_axis(self):
        self.ax.clear()
        self.__add_legend()

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

    plot_window = PlotWindow(parent=parent, backend=backend,
                      resetzoom=resetzoom, autoScale=autoScale, logScale=logScale, grid=grid,
                      curveStyle=curveStyle, colormap=colormap,
                      aspectRatio=aspectRatio, yInverted=yInverted,
                      copy=copy, save=save, print_=print_,
                      control=control, position=position,
                      roi=roi, mask=mask, fit=fit)

    plot_window._backend.ax.ticklabel_format(axis='y', style='sci')

    return plot_window

from silx.gui.plot import ImageView, PlotToolButtons
import silx.gui.qt as qt
from silx.gui.plot.Profile import ProfileToolBar

def imageWiew(parent=None):
    image_view = ImageView(parent=parent)
    image_view._toolbar.setVisible(False)

    image_view.removeToolBar(image_view.profile)
    image_view.profile = ProfileToolBar(plot=image_view)
    image_view.addToolBar(image_view.profile)

    def _createToolBar(image_view, title, parent):
        image_view.keepDataAspectRatioButton = PlotToolButtons.AspectToolButton(parent=image_view, plot=image_view)
        image_view.keepDataAspectRatioButton.setVisible(True)

        image_view.yAxisInvertedButton = PlotToolButtons.YAxisOriginToolButton(parent=image_view, plot=image_view)
        image_view.yAxisInvertedButton.setVisible(True)

        toolbar = qt.QToolBar(title, parent)

        objects = image_view.group.actions()
        index = objects.index(image_view.colormapAction)
        objects.insert(index + 1, image_view.keepDataAspectRatioButton)
        objects.insert(index + 2, image_view.yAxisInvertedButton)

        for obj in objects:
            if isinstance(obj, qt.QAction):
                toolbar.addAction(obj)
            else:
                if obj is image_view.keepDataAspectRatioButton:
                    image_view.keepDataAspectRatioAction = toolbar.addWidget(obj)
                elif obj is image_view.yAxisInvertedButton:
                    image_view.yAxisInvertedAction = toolbar.addWidget(obj)
                else:
                    raise RuntimeError()

        return toolbar

    image_view._toolbar = _createToolBar(image_view, title='Plot', parent=image_view)
    image_view.insertToolBar(image_view._interactiveModeToolBar, image_view._toolbar)

    return image_view
