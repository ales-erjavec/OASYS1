import numpy

from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMessageBox

from orangewidget import gui
from orangewidget.settings import Setting

from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from silx.gui import qt
import silx.gui.hdf5
from silx.gui.data.DataViewerFrame import DataViewerFrame
from silx.gui.data.DataViewer import DataViewer, DataViews
from silx.gui.hdf5._utils import H5Node
from silx.gui.plot.PlotWindow import Plot2D

from h5py import Dataset

class Hdf5TreeViewWidget(qt.QWidget):
    x_scale = 0
    y_scale = 1

    def __init__(self, file_names=None):
        qt.QWidget.__init__(self)

        self.__treeview = silx.gui.hdf5.Hdf5TreeView(self)
        self.__text = qt.QTextEdit(self)
        self.__dataViewer = DataViewerFrame(self)

        box = oasysgui.widgetBox(self, "", orientation="vertical")

        box.layout().addWidget(self.__dataViewer)
        self.box_scale = oasysgui.widgetBox(box, "", orientation="horizontal")

        self.cb_x_scale = gui.comboBox(self.box_scale, self, "x_scale", label="X Scale", items=[], labelWidth=240, sendSelectedValue=False, orientation="horizontal")
        self.cb_y_scale = gui.comboBox(self.box_scale, self, "y_scale", label="Y Scale", items=[], labelWidth=240, sendSelectedValue=False, orientation="horizontal")
        gui.button(self.box_scale, self, "Set Scale", callback=self.rescale)

        self.box_scale.setVisible(False)

        vSplitter = qt.QSplitter(qt.Qt.Vertical)
        vSplitter.addWidget(box)
        vSplitter.addWidget(self.__text)
        vSplitter.setSizes([10, 0])

        splitter = qt.QSplitter(self)
        splitter.addWidget(self.__treeview)
        splitter.addWidget(vSplitter)
        splitter.setStretchFactor(1, 1)

        layout = qt.QVBoxLayout()
        layout.addWidget(splitter)
        layout.setStretchFactor(splitter, 1)
        self.setLayout(layout)

        # append all files to the tree
        if not file_names is None:
            for file_name in file_names:
                self.__treeview.findHdf5TreeModel().appendFile(file_name)

        self.__treeview.activated.connect(self.displayData)

    def displayData(self):
        """Called to update the dataviewer with the selected data.
        """
        selected = list(self.__treeview.selectedH5Nodes())
        if len(selected) == 1:
            # Update the viewer for a single selection
            data = selected[0]
            self.__dataViewer.setData(data)

            if isinstance(data, H5Node) and len(data.maxshape)==2:
                current_group = data.h5py_object.parent

                self.datasets_1d_info = []
                def func(name, obj):
                    if isinstance(obj, Dataset) and obj.ndim==1:
                       self.datasets_1d_info.append([name, obj.value])

                current_group.visititems(func)

                self.cb_x_scale.clear()
                self.cb_y_scale.clear()

                for dataset in self.datasets_1d_info:
                    self.cb_x_scale.addItem(dataset[0])
                    self.cb_y_scale.addItem(dataset[0])

                #for key in group.keys():
                #    print(key)

                self.box_scale.setVisible(True)
            else:
                self.box_scale.setVisible(False)

    def rescale(self):
        current_view = self.__dataViewer.displayedView()
        if isinstance(current_view, DataViews._ImageView):
            dataset_x = self.cb_x_scale.itemText(self.x_scale)
            dataset_y = self.cb_y_scale.itemText(self.y_scale)

            min_x = 0.0
            max_x = 0.0
            min_y = 0.0
            max_y = 0.0
            nbins_x = 0.0
            nbins_y = 0.0

            for dataset in self.datasets_1d_info:
                if dataset[0] == dataset_x:
                    min_x = numpy.min(dataset[1])
                    max_x = numpy.max(dataset[1])
                    nbins_x = len(dataset[1])
                elif dataset[0] == dataset_y:
                    min_y = numpy.min(dataset[1])
                    max_y = numpy.max(dataset[1])
                    nbins_y = len(dataset[1])

            origin = (min_x, min_y)
            scale = (abs((max_x-min_x)/nbins_x), abs((max_y-min_y)/nbins_y))

            for view in current_view.availableViews():
                widget = view.getWidget()

                if isinstance(widget, Plot2D):
                    widget.getActiveImage().setOrigin(origin)
                    widget.getActiveImage().setScale(scale)
                    widget.setGraphXLimits(min_x, max_x)
                    widget.setGraphYLimits(min_y, max_y)

    def load_file(self, filename):
        self.__treeview.findHdf5TreeModel().insertFile(filename)

    def set_text(self, text):
        self.__text.setText(text)

    def __hdf5ComboChanged(self, index):
        function = self.__hdf5Combo.itemData(index)
        self.__createHdf5Button.setCallable(function)

    def __edfComboChanged(self, index):
        function = self.__edfCombo.itemData(index)
        self.__createEdfButton.setCallable(function)


class OWHDF5FileReader(OWWidget):
    name = "HDF5 File Reader"
    id = "hdf5_file_reader"
    description = "HDF5 File Reader"
    icon = "icons/plot_xy.png"
    author = "Luca Rebuffi"
    maintainer_email = "lrebuffi@anl.gov"
    priority = 3
    category = ""
    keywords = ["hdf5_file_reader"]

    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 645

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 618

    xx = None
    yy = None
    zz = None

    hdf5_file_name = Setting('file.hdf5')

    def __init__(self):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width() * 0.05),
                               round(geom.height() * 0.05),
                               round(min(geom.width() * 0.98, self.MAX_WIDTH)),
                               round(min(geom.height() * 0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Load HDF5 file", callback=self.load_file)
        button.setFixedHeight(45)

        input_box_l = oasysgui.widgetBox(self.controlArea, "Input", addSpace=True, orientation="horizontal", height=self.TABS_AREA_HEIGHT)

        self.le_hdf5_file_name = oasysgui.lineEdit(input_box_l, self, "hdf5_file_name", "HDF5 File Name",
                                                        labelWidth=120, valueType=str, orientation="horizontal")

        gui.button(input_box_l, self, "...", callback=self.selectPlotXYFile)

        self.tree_view = Hdf5TreeViewWidget()

        self.mainArea.layout().addWidget(self.tree_view)

        gui.rubber(self.mainArea)


    def load_file(self):
        try:
            hdf5_file_name = congruence.checkDir(self.hdf5_file_name)

            self.tree_view.load_file(hdf5_file_name)
            self.tree_view.set_text("Loaded File: " + hdf5_file_name)

        except Exception as exception:
            QMessageBox.critical(self, "Error", exception.args[0], QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

    def selectPlotXYFile(self):
        self.le_hdf5_file_name.setText(oasysgui.selectFileFromDialog(self, self.hdf5_file_name, "Select Input File", file_extension_filter="HDF5 Files (*.hdf5 *.h5 *.hdf)"))


