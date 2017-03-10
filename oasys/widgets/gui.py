import os, sys

from PyQt4.QtCore import Qt, QCoreApplication
from PyQt4.QtGui import QWidget, QGridLayout, QFileDialog, QMessageBox, QLabel, QComboBox

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

    return tabWidget

def createTabPage(tabWidget, name, widgetToAdd=None, canScroll=False, height=None, width=None):

    tab = orange_gui.createTabPage(tabWidget, name, widgetToAdd, canScroll)
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

from silx.gui.plot.BackendMatplotlib import BackendMatplotlibQt
from silx.gui.plot import Plot
from silx.gui import qt

import collections
import logging
_logger = logging.getLogger(__name__)

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

class OasysPlot(Plot.Plot):

    def __init__(self, parent=None, backend=None):
        super(OasysPlot, self).__init__(parent, backend)

        if backend is None:
            self._backend = OasysBackendMatplotlibQt(self, parent)



class OasysPlotWidget(qt.QMainWindow, OasysPlot):
    """Qt Widget providing a 1D/2D plot.

    This widget is a QMainWindow.
    It provides Qt signals for the Plot and add supports for panning
    with arrow keys.

    :param parent: The parent of this widget or None.
    :param backend: The backend to use for the plot.
                    The default is to use matplotlib.
    :type backend: str or :class:`BackendBase.BackendBase`
    """

    sigPlotSignal = qt.Signal(object)
    """Signal for all events of the plot.

    The signal information is provided as a dict.
    See :class:`.Plot` for documentation of the content of the dict.
    """

    sigSetYAxisInverted = qt.Signal(bool)
    """Signal emitted when Y axis orientation has changed"""

    sigSetXAxisLogarithmic = qt.Signal(bool)
    """Signal emitted when X axis scale has changed"""

    sigSetYAxisLogarithmic = qt.Signal(bool)
    """Signal emitted when Y axis scale has changed"""

    sigSetXAxisAutoScale = qt.Signal(bool)
    """Signal emitted when X axis autoscale has changed"""

    sigSetYAxisAutoScale = qt.Signal(bool)
    """Signal emitted when Y axis autoscale has changed"""

    sigSetKeepDataAspectRatio = qt.Signal(bool)
    """Signal emitted when plot keep aspect ratio has changed"""

    sigSetGraphGrid = qt.Signal(str)
    """Signal emitted when plot grid has changed"""

    sigSetGraphCursor = qt.Signal(bool)
    """Signal emitted when plot crosshair cursor has changed"""

    sigSetPanWithArrowKeys = qt.Signal(bool)
    """Signal emitted when pan with arrow keys has changed"""

    sigContentChanged = qt.Signal(str, str, str)
    """Signal emitted when the content of the plot is changed.

    It provides 3 informations:

    - action: The change of the plot: 'add' or 'remove'
    - kind: The kind of primitive changed: 'curve', 'image', 'item' or 'marker'
    - legend: The legend of the primitive changed.
    """

    sigActiveCurveChanged = qt.Signal(object, object)
    """Signal emitted when the active curve has changed.

    It provides 2 informations:

    - previous: The legend of the previous active curve or None
    - legend: The legend of the new active curve or None if no curve is active
    """

    sigActiveImageChanged = qt.Signal(object, object)
    """Signal emitted when the active image has changed.

    It provides 2 informations:

    - previous: The legend of the previous active image or None
    - legend: The legend of the new active image or None if no image is active
    """

    sigInteractiveModeChanged = qt.Signal(object)
    """Signal emitted when the interactive mode has changed

    It provides the source as passed to :meth:`setInteractiveMode`.
    """

    def __init__(self, parent=None, backend=None,
                 legends=False, callback=None, **kw):

        if kw:
            _logger.warning(
                'deprecated: __init__ extra arguments: %s', str(kw))
        if legends:
            _logger.warning('deprecated: __init__ legend argument')
        if callback:
            _logger.warning('deprecated: __init__ callback argument')

        self._panWithArrowKeys = True

        qt.QMainWindow.__init__(self, parent)
        if parent is not None:
            # behave as a widget
            self.setWindowFlags(qt.Qt.Widget)
        else:
            self.setWindowTitle('PlotWidget')

        OasysPlot.__init__(self, parent, backend=backend)

        widget = self.getWidgetHandle()
        if widget is not None:
            self.setCentralWidget(widget)
        else:
            _logger.warning("Plot backend does not support widget")

        self.setFocusPolicy(qt.Qt.StrongFocus)
        self.setFocus(qt.Qt.OtherFocusReason)

    def notify(self, event, **kwargs):
        """Override :meth:`Plot.notify` to send Qt signals."""
        eventDict = kwargs.copy()
        eventDict['event'] = event
        self.sigPlotSignal.emit(eventDict)

        if event == 'setYAxisInverted':
            self.sigSetYAxisInverted.emit(kwargs['state'])
        elif event == 'setXAxisLogarithmic':
            self.sigSetXAxisLogarithmic.emit(kwargs['state'])
        elif event == 'setYAxisLogarithmic':
            self.sigSetYAxisLogarithmic.emit(kwargs['state'])
        elif event == 'setXAxisAutoScale':
            self.sigSetXAxisAutoScale.emit(kwargs['state'])
        elif event == 'setYAxisAutoScale':
            self.sigSetYAxisAutoScale.emit(kwargs['state'])
        elif event == 'setKeepDataAspectRatio':
            self.sigSetKeepDataAspectRatio.emit(kwargs['state'])
        elif event == 'setGraphGrid':
            self.sigSetGraphGrid.emit(kwargs['which'])
        elif event == 'setGraphCursor':
            self.sigSetGraphCursor.emit(kwargs['state'])
        elif event == 'contentChanged':
            self.sigContentChanged.emit(
                kwargs['action'], kwargs['kind'], kwargs['legend'])
        elif event == 'activeCurveChanged':
            self.sigActiveCurveChanged.emit(
                kwargs['previous'], kwargs['legend'])
        elif event == 'activeImageChanged':
            self.sigActiveImageChanged.emit(
                kwargs['previous'], kwargs['legend'])
        elif event == 'interactiveModeChanged':
            self.sigInteractiveModeChanged.emit(kwargs['source'])
        OasysPlot.notify(self, event, **kwargs)

    # Panning with arrow keys

    def isPanWithArrowKeys(self):
        """Returns whether or not panning the graph with arrow keys is enable.

        See :meth:`setPanWithArrowKeys`.
        """
        return self._panWithArrowKeys

    def setPanWithArrowKeys(self, pan=False):
        """Enable/Disable panning the graph with arrow keys.

        This grabs the keyboard.

        :param bool pan: True to enable panning, False to disable.
        """
        pan = bool(pan)
        panHasChanged = self._panWithArrowKeys != pan

        self._panWithArrowKeys = pan
        if not self._panWithArrowKeys:
            self.setFocusPolicy(qt.Qt.NoFocus)
        else:
            self.setFocusPolicy(qt.Qt.StrongFocus)
            self.setFocus(qt.Qt.OtherFocusReason)

        if panHasChanged:
            self.sigSetPanWithArrowKeys.emit(pan)

    # Dict to convert Qt arrow key code to direction str.
    _ARROWS_TO_PAN_DIRECTION = {
        qt.Qt.Key_Left: 'left',
        qt.Qt.Key_Right: 'right',
        qt.Qt.Key_Up: 'up',
        qt.Qt.Key_Down: 'down'
    }

    def keyPressEvent(self, event):
        """Key event handler handling panning on arrow keys.

        Overrides base class implementation.
        """
        key = event.key()
        if self._panWithArrowKeys and key in self._ARROWS_TO_PAN_DIRECTION:
            self.pan(self._ARROWS_TO_PAN_DIRECTION[key], factor=0.1)

            # Send a mouse move event to the plot widget to take into account
            # that even if mouse didn't move on the screen, it moved relative
            # to the plotted data.
            qapp = qt.QApplication.instance()
            event = qt.QMouseEvent(
                qt.QEvent.MouseMove,
                self.getWidgetHandle().mapFromGlobal(qt.QCursor.pos()),
                qt.Qt.NoButton,
                qapp.mouseButtons(),
                qapp.keyboardModifiers())
            qapp.sendEvent(self.getWidgetHandle(), event)

        else:
            # Only call base class implementation when key is not handled.
            # See QWidget.keyPressEvent for details.
            super(OasysPlotWidget, self).keyPressEvent(event)



from silx.utils.decorators import deprecated

from silx.gui.plot import PlotActions
from silx.gui.plot import PlotToolButtons
from silx.gui.plot.PlotTools import PositionInfo
from silx.gui.plot.LegendSelector import LegendsDockWidget
from silx.gui.plot.CurvesROIWidget import CurvesROIDockWidget
from silx.gui.plot.MaskToolsWidget import MaskToolsDockWidget
try:
    from silx.gui.console import IPythonDockWidget
except ImportError:
    IPythonDockWidget = None

class OasysPlotWindow(OasysPlotWidget):
    """Qt Widget providing a 1D/2D plot area and additional tools.

    This widgets inherits from :class:`.PlotWidget` and provides its plot API.

    Initialiser parameters:

    :param parent: The parent of this widget or None.
    :param backend: The backend to use for the plot.
                    The default is to use matplotlib.
    :type backend: str or :class:`BackendBase.BackendBase`
    :param bool resetzoom: Toggle visibility of reset zoom action.
    :param bool autoScale: Toggle visibility of axes autoscale actions.
    :param bool logScale: Toggle visibility of axes log scale actions.
    :param bool grid: Toggle visibility of grid mode action.
    :param bool curveStyle: Toggle visibility of curve style action.
    :param bool colormap: Toggle visibility of colormap action.
    :param bool aspectRatio: Toggle visibility of aspect ratio button.
    :param bool yInverted: Toggle visibility of Y axis direction button.
    :param bool copy: Toggle visibility of copy action.
    :param bool save: Toggle visibility of save action.
    :param bool print_: Toggle visibility of print action.
    :param bool control: True to display an Options button with a sub-menu
                         to show legends, toggle crosshair and pan with arrows.
                         (Default: False)
    :param position: True to display widget with (x, y) mouse position
                     (Default: False).
                     It also supports a list of (name, funct(x, y)->value)
                     to customize the displayed values.
                     See :class:`silx.gui.plot.PlotTools.PositionInfo`.
    :param bool roi: Toggle visibilty of ROI action.
    :param bool mask: Toggle visibilty of mask action.
    :param bool fit: Toggle visibilty of fit action.
    """

    def __init__(self, parent=None, backend=None,
                 resetzoom=True, autoScale=True, logScale=True, grid=True,
                 curveStyle=True, colormap=True,
                 aspectRatio=True, yInverted=True,
                 copy=True, save=True, print_=True,
                 control=False, position=False,
                 roi=True, mask=True, fit=False):
        super(OasysPlotWindow, self).__init__(parent=parent, backend=backend)
        if parent is None:
            self.setWindowTitle('PlotWindow')

        self._dockWidgets = []

        # lazy loaded dock widgets
        self._legendsDockWidget = None
        self._curvesROIDockWidget = None
        self._maskToolsDockWidget = None

        # Init actions
        self.group = qt.QActionGroup(self)
        self.group.setExclusive(False)

        self.resetZoomAction = self.group.addAction(PlotActions.ResetZoomAction(self))
        self.resetZoomAction.setVisible(resetzoom)
        self.addAction(self.resetZoomAction)

        self.zoomInAction = PlotActions.ZoomInAction(self)
        self.addAction(self.zoomInAction)

        self.zoomOutAction = PlotActions.ZoomOutAction(self)
        self.addAction(self.zoomOutAction)

        self.xAxisAutoScaleAction = self.group.addAction(
            PlotActions.XAxisAutoScaleAction(self))
        self.xAxisAutoScaleAction.setVisible(autoScale)
        self.addAction(self.xAxisAutoScaleAction)

        self.yAxisAutoScaleAction = self.group.addAction(
            PlotActions.YAxisAutoScaleAction(self))
        self.yAxisAutoScaleAction.setVisible(autoScale)
        self.addAction(self.yAxisAutoScaleAction)

        self.xAxisLogarithmicAction = self.group.addAction(
            PlotActions.XAxisLogarithmicAction(self))
        self.xAxisLogarithmicAction.setVisible(logScale)
        self.addAction(self.xAxisLogarithmicAction)

        self.yAxisLogarithmicAction = self.group.addAction(
            PlotActions.YAxisLogarithmicAction(self))
        self.yAxisLogarithmicAction.setVisible(logScale)
        self.addAction(self.yAxisLogarithmicAction)

        self.gridAction = self.group.addAction(
            PlotActions.GridAction(self, gridMode='both'))
        self.gridAction.setVisible(grid)
        self.addAction(self.gridAction)

        self.curveStyleAction = self.group.addAction(PlotActions.CurveStyleAction(self))
        self.curveStyleAction.setVisible(curveStyle)
        self.addAction(self.curveStyleAction)

        self.colormapAction = self.group.addAction(PlotActions.ColormapAction(self))
        self.colormapAction.setVisible(colormap)
        self.addAction(self.colormapAction)

        self.keepDataAspectRatioButton = PlotToolButtons.AspectToolButton(
            parent=self, plot=self)
        self.keepDataAspectRatioButton.setVisible(aspectRatio)

        self.yAxisInvertedButton = PlotToolButtons.YAxisOriginToolButton(
            parent=self, plot=self)
        self.yAxisInvertedButton.setVisible(yInverted)

        self.group.addAction(self.getRoiAction())
        self.getRoiAction().setVisible(roi)

        self.group.addAction(self.getMaskAction())
        self.getMaskAction().setVisible(mask)

        self._intensityHistoAction = self.group.addAction(
            PlotActions.PixelIntensitiesHistoAction(self))
        self._intensityHistoAction.setVisible(False)

        self._separator = qt.QAction('separator', self)
        self._separator.setSeparator(True)
        self.group.addAction(self._separator)

        self.copyAction = self.group.addAction(PlotActions.CopyAction(self))
        self.copyAction.setVisible(copy)
        self.addAction(self.copyAction)

        self.saveAction = self.group.addAction(PlotActions.SaveAction(self))
        self.saveAction.setVisible(save)
        self.addAction(self.saveAction)

        self.printAction = self.group.addAction(PlotActions.PrintAction(self))
        self.printAction.setVisible(print_)
        self.addAction(self.printAction)

        self.fitAction = self.group.addAction(PlotActions.FitAction(self))
        self.fitAction.setVisible(fit)
        self.addAction(self.fitAction)

        # lazy loaded actions needed by the controlButton menu
        self._consoleAction = None
        self._panWithArrowKeysAction = None
        self._crosshairAction = None

        if control or position:
            hbox = qt.QHBoxLayout()
            hbox.setContentsMargins(0, 0, 0, 0)

            if control:
                self.controlButton = qt.QToolButton()
                self.controlButton.setText("Options")
                self.controlButton.setToolButtonStyle(qt.Qt.ToolButtonTextBesideIcon)
                self.controlButton.setAutoRaise(True)
                self.controlButton.setPopupMode(qt.QToolButton.InstantPopup)
                menu = qt.QMenu(self)
                menu.aboutToShow.connect(self._customControlButtonMenu)
                self.controlButton.setMenu(menu)

                hbox.addWidget(self.controlButton)

            if position:  # Add PositionInfo widget to the bottom of the plot
                if isinstance(position, collections.Iterable):
                    # Use position as a set of converters
                    converters = position
                else:
                    converters = None
                self.positionWidget = PositionInfo(
                    plot=self, converters=converters)
                self.positionWidget.autoSnapToActiveCurve = True

                hbox.addWidget(self.positionWidget)

            hbox.addStretch(1)
            bottomBar = qt.QWidget()
            bottomBar.setLayout(hbox)

            layout = qt.QVBoxLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.getWidgetHandle())
            layout.addWidget(bottomBar)

            centralWidget = qt.QWidget()
            centralWidget.setLayout(layout)
            self.setCentralWidget(centralWidget)

        # Creating the toolbar also create actions for toolbuttons
        self._toolbar = self._createToolBar(title='Plot', parent=None)
        self.addToolBar(self._toolbar)

    def getSelectionMask(self):
        """Return the current mask handled by :attr:`maskToolsDockWidget`.

        :return: The array of the mask with dimension of the 'active' image.
                 If there is no active image, an empty array is returned.
        :rtype: 2D numpy.ndarray of uint8
        """
        return self.getMaskToolsDockWidget().getSelectionMask()

    def setSelectionMask(self, mask):
        """Set the mask handled by :attr:`maskToolsDockWidget`.

        If the provided mask has not the same dimension as the 'active'
        image, it will by cropped or padded.

        :param mask: The array to use for the mask.
        :type mask: numpy.ndarray of uint8 of dimension 2, C-contiguous.
                    Array of other types are converted.
        :return: True if success, False if failed
        """
        return bool(self.getMaskToolsDockWidget().setSelectionMask(mask))

    def _toggleConsoleVisibility(self, is_checked=False):
        """Create IPythonDockWidget if needed,
        show it or hide it."""
        # create widget if needed (first call)
        if not hasattr(self, '_consoleDockWidget'):
            available_vars = {"plt": self}
            banner = "The variable 'plt' is available. Use the 'whos' "
            banner += "and 'help(plt)' commands for more information.\n\n"
            self._consoleDockWidget = IPythonDockWidget(
                available_vars=available_vars,
                custom_banner=banner,
                parent=self)
            self._introduceNewDockWidget(self._consoleDockWidget)
            self._consoleDockWidget.visibilityChanged.connect(
                    self.getConsoleAction().setChecked)

        self._consoleDockWidget.setVisible(is_checked)

    def _createToolBar(self, title, parent):
        """Create a QToolBar from the QAction of the PlotWindow.

        :param str title: The title of the QMenu
        :param qt.QWidget parent: See :class:`QToolBar`
        """
        toolbar = qt.QToolBar(title, parent)

        # Order widgets with actions
        objects = self.group.actions()

        # Add push buttons to list
        index = objects.index(self.colormapAction)
        objects.insert(index + 1, self.keepDataAspectRatioButton)
        objects.insert(index + 2, self.yAxisInvertedButton)

        for obj in objects:
            if isinstance(obj, qt.QAction):
                toolbar.addAction(obj)
            else:
                # Add action for toolbutton in order to allow changing
                # visibility (see doc QToolBar.addWidget doc)
                if obj is self.keepDataAspectRatioButton:
                    self.keepDataAspectRatioAction = toolbar.addWidget(obj)
                elif obj is self.yAxisInvertedButton:
                    self.yAxisInvertedAction = toolbar.addWidget(obj)
                else:
                    raise RuntimeError()
        return toolbar

    def toolBar(self):
        """Return a QToolBar from the QAction of the PlotWindow.
        """
        return self._toolbar

    def menu(self, title='Plot', parent=None):
        """Return a QMenu from the QAction of the PlotWindow.

        :param str title: The title of the QMenu
        :param parent: See :class:`QMenu`
        """
        menu = qt.QMenu(title, parent)
        for action in self.group.actions():
            menu.addAction(action)
        return menu

    def _customControlButtonMenu(self):
        """Display Options button sub-menu."""
        controlMenu = self.controlButton.menu()
        controlMenu.clear()
        controlMenu.addAction(self.getLegendsDockWidget().toggleViewAction())
        controlMenu.addAction(self.getRoiAction())
        controlMenu.addAction(self.getMaskAction())
        controlMenu.addAction(self.getConsoleAction())

        controlMenu.addSeparator()
        controlMenu.addAction(self.getCrosshairAction())
        controlMenu.addAction(self.getPanWithArrowKeysAction())

    def _introduceNewDockWidget(self, dock_widget):
        """Maintain a list of dock widgets, in the order in which they are
        added. Tabify them as soon as there are more than one of them.

        :param dock_widget: Instance of :class:`QDockWidget` to be added.
        """
        if dock_widget not in self._dockWidgets:
            self._dockWidgets.append(dock_widget)
        if len(self._dockWidgets) == 1:
            # The first created dock widget must be added to a Widget area
            width = self.centralWidget().width()
            height = self.centralWidget().height()
            if width > (2.0 * height) and width > 1000:
                area = qt.Qt.RightDockWidgetArea
            else:
                area = qt.Qt.BottomDockWidgetArea
            self.addDockWidget(area, dock_widget)
        else:
            # Other dock widgets are added as tabs to the same widget area
            self.tabifyDockWidget(self._dockWidgets[0],
                                  dock_widget)

    # getters for dock widgets
    @property
    @deprecated
    def legendsDockWidget(self):
        return self.getLegendsDockWidget()

    def getLegendsDockWidget(self):
        """DockWidget with Legend panel"""
        if self._legendsDockWidget is None:
            self._legendsDockWidget = LegendsDockWidget(plot=self)
            self._legendsDockWidget.hide()
            self._introduceNewDockWidget(self._legendsDockWidget)
        return self._legendsDockWidget

    @property
    @deprecated
    def curvesROIDockWidget(self):
        return self.getCurvesRoiDockWidget()

    def getCurvesRoiDockWidget(self):
        """DockWidget with curves' ROI panel (lazy-loaded)."""
        if self._curvesROIDockWidget is None:
            self._curvesROIDockWidget = CurvesROIDockWidget(
                plot=self, name='Regions Of Interest')
            self._curvesROIDockWidget.hide()
            self._introduceNewDockWidget(self._curvesROIDockWidget)
        return self._curvesROIDockWidget

    @property
    @deprecated
    def maskToolsDockWidget(self):
        return self.getMaskToolsDockWidget()

    def getMaskToolsDockWidget(self):
        """DockWidget with image mask panel (lazy-loaded)."""
        if self._maskToolsDockWidget is None:
            self._maskToolsDockWidget = MaskToolsDockWidget(
                plot=self, name='Mask')
            self._maskToolsDockWidget.hide()
            self._introduceNewDockWidget(self._maskToolsDockWidget)
        return self._maskToolsDockWidget

    # getters for actions
    @property
    @deprecated
    def consoleAction(self):
        return self.getConsoleAction()

    def getConsoleAction(self):
        """QAction handling the IPython console activation.

        By default, it is connected to a method that initializes the
        console widget the first time the user clicks the "Console" menu
        button. The following clicks, after initialization is done,
        will toggle the visibility of the console widget.

        :rtype: QAction
        """
        if self._consoleAction is None:
            self._consoleAction = qt.QAction('Console', self)
            self._consoleAction.setCheckable(True)
            if IPythonDockWidget is not None:
                self._consoleAction.toggled.connect(self._toggleConsoleVisibility)
            else:
                self._consoleAction.setEnabled(False)
        return self._consoleAction

    @property
    @deprecated
    def crosshairAction(self):
        return self.getCrosshairAction()

    def getCrosshairAction(self):
        """Action toggling crosshair cursor mode.

        :rtype: PlotActions.PlotAction
        """
        if self._crosshairAction is None:
            self._crosshairAction = PlotActions.CrosshairAction(self, color='red')
        return self._crosshairAction

    @property
    @deprecated
    def maskAction(self):
        return self.getMaskAction()

    def getMaskAction(self):
        """QAction toggling image mask dock widget

        :rtype: QAction
        """
        return self.getMaskToolsDockWidget().toggleViewAction()

    @property
    @deprecated
    def panWithArrowKeysAction(self):
        return self.getPanWithArrowKeysAction()

    def getPanWithArrowKeysAction(self):
        """Action toggling pan with arrow keys.

        :rtype: PlotActions.PlotAction
        """
        if self._panWithArrowKeysAction is None:
            self._panWithArrowKeysAction = PlotActions.PanWithArrowKeysAction(self)
        return self._panWithArrowKeysAction

    @property
    @deprecated
    def roiAction(self):
        return self.getRoiAction()

    def getRoiAction(self):
        """QAction toggling curve ROI dock widget

        :rtype: QAction
        """
        return self.getCurvesRoiDockWidget().toggleViewAction()

    def getResetZoomAction(self):
        """Action resetting the zoom

        :rtype: PlotActions.PlotAction
        """
        return self.resetZoomAction

    def getZoomInAction(self):
        """Action to zoom in

        :rtype: PlotActions.PlotAction
        """
        return self.zoomInAction

    def getZoomOutAction(self):
        """Action to zoom out

        :rtype: PlotActions.PlotAction
        """
        return self.zoomOutAction

    def getXAxisAutoScaleAction(self):
        """Action to toggle the X axis autoscale on zoom reset

        :rtype: PlotActions.PlotAction
        """
        return self.xAxisAutoScaleAction

    def getYAxisAutoScaleAction(self):
        """Action to toggle the Y axis autoscale on zoom reset

        :rtype: PlotActions.PlotAction
        """
        return self.yAxisAutoScaleAction

    def getXAxisLogarithmicAction(self):
        """Action to toggle logarithmic X axis

        :rtype: PlotActions.PlotAction
        """
        return self.xAxisLogarithmicAction

    def getYAxisLogarithmicAction(self):
        """Action to toggle logarithmic Y axis

        :rtype: PlotActions.PlotAction
        """
        return self.yAxisLogarithmicAction

    def getGridAction(self):
        """Action to toggle the grid visibility in the plot

        :rtype: PlotActions.PlotAction
        """
        return self.gridAction

    def getCurveStyleAction(self):
        """Action to change curve line and markers styles

        :rtype: PlotActions.PlotAction
        """
        return self.curveStyleAction

    def getColormapAction(self):
        """Action open a colormap dialog to change active image
        and default colormap.

        :rtype: PlotActions.PlotAction
        """
        return self.colormapAction

    def getKeepDataAspectRatioButton(self):
        """Button to toggle aspect ratio preservation

        :rtype: PlotToolButtons.AspectToolButton
        """
        return self.keepDataAspectRatioButton

    def getKeepDataAspectRatioAction(self):
        """Action associated to keepDataAspectRatioButton.
        Use this to change the visibility of keepDataAspectRatioButton in the
        toolbar (See :meth:`QToolBar.addWidget` documentation).

        :rtype: PlotActions.PlotAction
        """
        return self.keepDataAspectRatioButton

    def getYAxisInvertedButton(self):
        """Button to switch the Y axis orientation

        :rtype: PlotToolButtons.YAxisOriginToolButton
        """
        return self.yAxisInvertedButton

    def getYAxisInvertedAction(self):
        """Action associated to yAxisInvertedButton.
        Use this to change the visibility yAxisInvertedButton in the toolbar.
        (See :meth:`QToolBar.addWidget` documentation).

        :rtype: PlotActions.PlotAction
        """
        return self.yAxisInvertedAction

    def getIntensityHistogramAction(self):
        """Action toggling the histogram intensity Plot widget

        :rtype: PlotActions.PlotAction
        """
        return self._intensityHistoAction

    def getCopyAction(self):
        """Action to copy plot snapshot to clipboard

        :rtype: PlotActions.PlotAction
        """
        return self.copyAction

    def getSaveAction(self):
        """Action to save plot

        :rtype: PlotActions.PlotAction
        """
        return self.saveAction

    def getPrintAction(self):
        """Action to print plot

        :rtype: PlotActions.PlotAction
        """
        return self.printAction

    def getFitAction(self):
        """Action to fit selected curve

        :rtype: PlotActions.PlotAction
        """
        return self.fitAction

