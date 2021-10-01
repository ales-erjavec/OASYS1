import sys
import numpy

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel, QSizePolicy
from PyQt5.QtGui import QTextCursor,QFont, QPalette, QColor, QPixmap

from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from orangewidget import gui, widget
from orangewidget.settings import Setting

from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.widgets.gui import ConfirmDialog
from oasys.util.oasys_util import EmittingStream, Overlay

try:
    from mpl_toolkits.mplot3d import Axes3D  # necessario per caricare i plot 3D
except:
    pass

from srxraylib.metrology import profiles_simulation, dabam

class OWAbstractDabamHeightProfile(OWWidget):
    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 820

    IMAGE_WIDTH = 880
    IMAGE_HEIGHT = 770

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 738

    xx = None
    yy = None
    zz = None

    entry_number = Setting(1)

    shape=Setting(0)
    slope_error_from = Setting(0.0)
    slope_error_to = Setting(1.5)
    dimension_y_from = Setting(0.0)
    dimension_y_to = Setting(0.0)

    use_undetrended = Setting(0)

    step_x = Setting(0.0)
    dimension_x = Setting(0.0)

    kind_of_profile_x = Setting(3)

    power_law_exponent_beta_x = Setting(3.0)

    correlation_length_x = Setting(0.3)

    error_type_x = Setting(profiles_simulation.FIGURE_ERROR)

    rms_x = Setting(0.1)
    montecarlo_seed_x = Setting(8787)

    heigth_profile_1D_file_name_x= Setting("mirror_1D_x.dat")
    delimiter_x = Setting(0)
    conversion_factor_x_x = Setting(0.001)
    conversion_factor_x_y = Setting(1e-6)

    center_x = Setting(1)
    modify_x = Setting(0)
    new_length_x = Setting(0.0)
    filler_value_x = Setting(0.0)

    renormalize_x = Setting(0)

    center_y = Setting(1)
    modify_y = Setting(0)
    new_length_y = Setting(0.0)
    filler_value_y = Setting(0.0)

    renormalize_y = Setting(1)
    error_type_y = Setting(0)
    rms_y = Setting(0.9)

    dabam_profile_index = Setting(1)

    heigth_profile_file_name = Setting('mirror.hdf5')

    server_address =  Setting(dabam.default_server) # "http://ftp.esrf.eu/pub/scisoft/dabam/"

    tab=[]


    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Calculate Height Profile", self)
        self.runaction.triggered.connect(self.calculate_heigth_profile_ni)
        self.addAction(self.runaction)

        self.runaction = widget.OWAction("Generate Height Profile File", self)
        self.runaction.triggered.connect(self.generate_heigth_profile_file_ni)
        self.addAction(self.runaction)

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width() * 0.05),
                               round(geom.height() * 0.05),
                               round(min(geom.width() * 0.98, self.MAX_WIDTH)),
                               round(min(geom.height() * 0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        # DABAM INITIALIZATION
        self.server = dabam.dabam()
        self.server.set_input_silent(True)

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Calculate Height\nProfile", callback=self.calculate_heigth_profile)
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Generate Height\nProfile File", callback=self.generate_heigth_profile_file)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette)  # assign new palette
        button.setFixedHeight(45)
        button.setFixedWidth(150)

        button = gui.button(button_box, self, "Reset Fields", callback=self.call_reset_settings)
        font = QFont(button.font())
        font.setItalic(True)
        button.setFont(font)
        palette = QPalette(button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Red'))
        button.setPalette(palette)  # assign new palette
        button.setFixedHeight(45)

        gui.separator(self.controlArea)

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        tab_input = oasysgui.createTabPage(tabs_setting, "DABAM Search Setting")
        tab_gener = oasysgui.createTabPage(tabs_setting, "DABAM Generation Setting")
        tab_server = oasysgui.createTabPage(tabs_setting, "DABAM Server Setting")
        tab_out = oasysgui.createTabPage(tabs_setting, "Output")
        tab_usa = oasysgui.createTabPage(tabs_setting, "Use of the Widget")
        tab_usa.setStyleSheet("background-color: white;")

        tabs_dabam = oasysgui.tabWidget(tab_gener)
        tab_length = oasysgui.createTabPage(tabs_dabam, "DABAM Profile")
        tab_width = oasysgui.createTabPage(tabs_dabam, "Width")

        usage_box = oasysgui.widgetBox(tab_usa, "", addSpace=True, orientation="horizontal")

        label = QLabel("")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setPixmap(QPixmap(self.get_usage_path()))

        usage_box.layout().addWidget(label)

        manual_box = oasysgui.widgetBox(tab_input, "Manual Entry", addSpace=True, orientation="vertical")

        manual_box_1 = oasysgui.widgetBox(manual_box, "", addSpace=True, orientation="horizontal")
        oasysgui.lineEdit(manual_box_1, self, "entry_number", "Entry Number",
                           labelWidth=300, valueType=int, orientation="horizontal")
        button = gui.button(manual_box_1, self, "-1", callback=self.retrieve_profile_minus_one)
        button.setFixedWidth(35)
        button = gui.button(manual_box_1, self, "+1", callback=self.retrieve_profile_plus_one)
        button.setFixedWidth(35)

        gui.separator(manual_box)

        button_box = oasysgui.widgetBox(manual_box, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Retrieve Profile", callback=self.retrieve_profile)
        button.setFixedHeight(35)
        button = gui.button(button_box, self, "Send Profile", callback=self.send_profile)
        button.setFixedHeight(35)

        input_box = oasysgui.widgetBox(tab_input, "Search Parameters", addSpace=True, orientation="vertical")

        gui.comboBox(input_box, self, "shape", label="Mirror Shape", labelWidth=300,
                     items=["All", "Plane", "Cylindrical", "Elliptical", "Toroidal", "Spherical"],
                     sendSelectedValue=False, orientation="horizontal")

        gui.separator(input_box)
        
        input_box_1 = oasysgui.widgetBox(input_box, "", addSpace=True, orientation="horizontal")

        oasysgui.lineEdit(input_box_1, self, "slope_error_from", "Slope Error From (" + u"\u03BC" + "rad)",
                           labelWidth=150, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(input_box_1, self, "slope_error_to", "To (" + u"\u03BC" + "rad)",
                           labelWidth=60, valueType=float, orientation="horizontal")

        input_box_2 = oasysgui.widgetBox(input_box, "", addSpace=True, orientation="horizontal")

        self.le_dimension_y_from = oasysgui.lineEdit(input_box_2, self, "dimension_y_from", "Mirror Length From",
                           labelWidth=150, valueType=float, orientation="horizontal")
        self.le_dimension_y_to = oasysgui.lineEdit(input_box_2, self, "dimension_y_to", "To",
                           labelWidth=60, valueType=float, orientation="horizontal")

        table_box = oasysgui.widgetBox(tab_input, "Search Results", addSpace=True, orientation="vertical", height=350)

        self.overlay_search = Overlay(table_box, self.search_profiles)
        self.overlay_search.hide()

        button = gui.button(input_box, self, "Search", callback=self.overlay_search.show)
        button.setFixedHeight(35)
        button.setFixedWidth(self.CONTROL_AREA_WIDTH-35)

        gui.comboBox(table_box, self, "use_undetrended", label="Use Undetrended Profile", labelWidth=300,
                     items=["No", "Yes"], callback=self.table_item_clicked, sendSelectedValue=False, orientation="horizontal")

        gui.separator(table_box)

        self.scrollarea = QScrollArea()
        self.scrollarea.setMinimumWidth(self.CONTROL_AREA_WIDTH-35)

        table_box.layout().addWidget(self.scrollarea, alignment=Qt.AlignHCenter)

        self.table = QTableWidget(1, 5)
        self.table.setStyleSheet("background-color: #FBFBFB;")
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setVisible(False)

        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 70)
        self.table.setColumnWidth(3, 85)
        self.table.setColumnWidth(4, 80)

        self.table.resizeRowsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemClicked.connect(self.table_item_clicked)

        self.scrollarea.setWidget(self.table)
        self.scrollarea.setWidgetResizable(1)

        ##----------------------------------

        output_profile_box = oasysgui.widgetBox(tab_length, "Surface Generation Parameters", addSpace=True, orientation="vertical", height=320)

        gui.comboBox(output_profile_box, self, "center_y", label="Center Profile in the middle of O.E.", labelWidth=300,
                     items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")

        gui.separator(output_profile_box)

        gui.comboBox(output_profile_box, self, "modify_y", label="Modify Length?", labelWidth=150,
                     items=["No", "Rescale to new length", "Fit to new length (fill or cut)"], callback=self.set_ModifyY, sendSelectedValue=False, orientation="horizontal")

        self.modify_box_1 = oasysgui.widgetBox(output_profile_box, "", addSpace=False, orientation="vertical", height=60)

        self.modify_box_2 = oasysgui.widgetBox(output_profile_box, "", addSpace=False, orientation="vertical", height=60)
        self.le_new_length_1 = oasysgui.lineEdit(self.modify_box_2, self, "new_length_y", "New Length", labelWidth=300, valueType=float, orientation="horizontal")

        self.modify_box_3 = oasysgui.widgetBox(output_profile_box, "", addSpace=False, orientation="vertical", height=60)
        self.le_new_length_2 = oasysgui.lineEdit(self.modify_box_3, self, "new_length_y", "New Length", labelWidth=300, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.modify_box_3, self, "filler_value_y", "Filler Value (if new length > profile length) [nm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.set_ModifyY()

        gui.comboBox(output_profile_box, self, "renormalize_y", label="Renormalize Length Profile to different RMS", labelWidth=300,
                     items=["No", "Yes"], callback=self.set_RenormalizeY, sendSelectedValue=False, orientation="horizontal")

        self.output_profile_box_1 = oasysgui.widgetBox(output_profile_box, "", addSpace=False, orientation="vertical", height=60)
        self.output_profile_box_2 = oasysgui.widgetBox(output_profile_box, "", addSpace=False, orientation="vertical", height=60)

        gui.comboBox(self.output_profile_box_1, self, "error_type_y", label="Normalization to", labelWidth=270,
                     items=["Figure Error (nm)", "Slope Error (" + u"\u03BC" + "rad)"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.output_profile_box_1, self, "rms_y", "Rms Value",
                           labelWidth=300, valueType=float, orientation="horizontal")

        self.set_RenormalizeY()

        ##----------------------------------

        input_box_w = oasysgui.widgetBox(tab_width, "Calculation Parameters", addSpace=True, orientation="vertical")


        gui.comboBox(input_box_w, self, "kind_of_profile_x", label="Kind of Profile", labelWidth=260,
                     items=["Fractal", "Gaussian", "User File", "None"],
                     callback=self.set_KindOfProfileX, sendSelectedValue=False, orientation="horizontal")

        gui.separator(input_box_w)

        self.kind_of_profile_x_box_1 = oasysgui.widgetBox(input_box_w, "", addSpace=True, orientation="vertical", height=350)

        self.le_dimension_x = oasysgui.lineEdit(self.kind_of_profile_x_box_1, self, "dimension_x", "Dimensions",
                          labelWidth=260, valueType=float, orientation="horizontal")
        self.le_step_x = oasysgui.lineEdit(self.kind_of_profile_x_box_1, self, "step_x", "Step",
                          labelWidth=260, valueType=float, orientation="horizontal")

        self.kind_of_profile_x_box_1_0 = oasysgui.widgetBox(self.kind_of_profile_x_box_1, "", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.kind_of_profile_x_box_1_0, self, "montecarlo_seed_x", "Monte Carlo initial seed",
                          labelWidth=260, valueType=int, orientation="horizontal")

        self.kind_of_profile_x_box_1_1 = oasysgui.widgetBox(self.kind_of_profile_x_box_1, "", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.kind_of_profile_x_box_1_1, self, "power_law_exponent_beta_x", "Beta Value",
                           labelWidth=260, valueType=float, orientation="horizontal")

        self.kind_of_profile_x_box_1_2 = oasysgui.widgetBox(self.kind_of_profile_x_box_1, "", addSpace=True, orientation="vertical")

        self.le_correlation_length_x = oasysgui.lineEdit(self.kind_of_profile_x_box_1_2, self, "correlation_length_x", "Correlation Length",
                           labelWidth=260, valueType=float, orientation="horizontal")

        gui.separator(self.kind_of_profile_x_box_1)

        self.kind_of_profile_x_box_1_3 = oasysgui.widgetBox(self.kind_of_profile_x_box_1, "", addSpace=True, orientation="vertical")

        gui.comboBox(self.kind_of_profile_x_box_1_3, self, "error_type_x", label="Normalization to", labelWidth=270,
                     items=["Figure Error (nm)", "Slope Error (" + "\u03BC" + "rad)"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_x_box_1_3, self, "rms_x", "Rms Value",
                           labelWidth=260, valueType=float, orientation="horizontal")


        self.kind_of_profile_x_box_2 = oasysgui.widgetBox(input_box_w, "", addSpace=True, orientation="vertical", height=390)

        select_file_box_1 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=True, orientation="horizontal")

        self.le_heigth_profile_1D_file_name_x = oasysgui.lineEdit(select_file_box_1, self, "heigth_profile_1D_file_name_x", "1D Profile File Name",
                                                        labelWidth=120, valueType=str, orientation="horizontal")

        gui.button(select_file_box_1, self, "...", callback=self.selectFile1D_X)

        gui.comboBox(self.kind_of_profile_x_box_2 , self, "delimiter_x", label="Fields delimiter", labelWidth=260,
                     items=["Spaces", "Tabs"], sendSelectedValue=False, orientation="horizontal")

        self.le_conversion_factor_x_x = oasysgui.lineEdit(self.kind_of_profile_x_box_2, self, "conversion_factor_x_x", "Conversion from file to meters\n(Abscissa)",
                                                          labelWidth=260,
                                                          valueType=float, orientation="horizontal")

        self.le_conversion_factor_x_y = oasysgui.lineEdit(self.kind_of_profile_x_box_2, self, "conversion_factor_x_y", "Conversion from file to meters\n(Height Profile Values)",
                                                          labelWidth=260,
                                                          valueType=float, orientation="horizontal")

        gui.separator(self.kind_of_profile_x_box_2)

        gui.comboBox(self.kind_of_profile_x_box_2, self, "center_x", label="Center Profile in the middle of O.E.", labelWidth=300,
                     items=["No", "Yes"], sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(self.kind_of_profile_x_box_2, self, "modify_x", label="Modify Length?", labelWidth=200,
                     items=["No", "Rescale to new length", "Fit to new length (fill or cut)"], callback=self.set_ModifyX, sendSelectedValue=False, orientation="horizontal")

        self.modify_box_1_1 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=False, orientation="vertical", height=70)

        self.modify_box_1_2 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=False, orientation="vertical", height=70)
        self.le_new_length_x_1 = oasysgui.lineEdit(self.modify_box_1_2, self, "new_length_x", "New Length", labelWidth=300, valueType=float, orientation="horizontal")

        self.modify_box_1_3 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=False, orientation="vertical", height=70)
        self.le_new_length_x_2 = oasysgui.lineEdit(self.modify_box_1_3, self, "new_length_x", "New Length", labelWidth=300, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.modify_box_1_3, self, "filler_value_x", "Filler Value (if new length > profile length) [nm]", labelWidth=300, valueType=float, orientation="horizontal")

        self.set_ModifyX()

        gui.comboBox(self.kind_of_profile_x_box_2, self, "renormalize_x", label="Renormalize to different RMS", labelWidth=260,
                     items=["No", "Yes"], callback=self.set_KindOfProfileX, sendSelectedValue=False, orientation="horizontal")

        self.kind_of_profile_x_box_2_1 = oasysgui.widgetBox(self.kind_of_profile_x_box_2, "", addSpace=True, orientation="vertical")

        gui.comboBox(self.kind_of_profile_x_box_2_1, self, "error_type_x", label="Normalization to", labelWidth=270,
                     items=["Figure Error (nm)", "Slope Error (" + "\u03BC" + "rad)"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.kind_of_profile_x_box_2_1, self, "rms_x", "Rms Value",
                           labelWidth=260, valueType=float, orientation="horizontal")

        self.set_KindOfProfileX()

        ##----------------------------------

        output_box = oasysgui.widgetBox(tab_gener, "Outputs", addSpace=True, orientation="vertical")

        select_file_box = oasysgui.widgetBox(output_box, "", addSpace=True, orientation="horizontal")

        self.le_heigth_profile_file_name = oasysgui.lineEdit(select_file_box, self, "heigth_profile_file_name", "Output File Name",
                                                        labelWidth=120, valueType=str, orientation="horizontal")

        gui.button(select_file_box, self, "...", callback=self.selectFile)

        self.shadow_output = oasysgui.textArea(height=400)

        ##---------------------------------- server

        server_box = oasysgui.widgetBox(tab_server, "Server", addSpace=True, orientation="vertical")

        select_server_box = oasysgui.widgetBox(server_box, "", addSpace=True, orientation="vertical")

        self.le_server_address = oasysgui.lineEdit(select_server_box, self, "server_address",
                                                             "Server (URL or local repository): ",
                                                             labelWidth=220, valueType=str, orientation="vertical")

        gui.button(select_server_box, self, "local repository...", callback=self.selectServer)
        gui.button(select_server_box, self, "set default DABAM server", callback=self.selectServerDefault)

        self.server_box = oasysgui.textArea(height=400)

        ##----------------------------------
        out_box = oasysgui.widgetBox(tab_out, "System Output", addSpace=True, orientation="horizontal", height=680)
        out_box.layout().addWidget(self.shadow_output)

        gui.rubber(self.controlArea)

        self.initializeTabs()

        gui.rubber(self.mainArea)

        self.overlay_search.raise_()

    def resizeEvent(self, event):
        self.overlay_search.resize(self.CONTROL_AREA_WIDTH - 15, 290)
        event.accept()

    def get_usage_path(self):
        pass

    @classmethod
    def get_dabam_output(cls):
        return  {"name": "DABAM 1D Profile",
                "type": numpy.ndarray,
                "doc": "DABAM 1D Profile",
                "id": "DABAM 1D Profile"}

    def after_change_workspace_units(self):
        self.si_to_user_units = 1.0

        self.horHeaders = ["Entry", "Shape", "Length\n[m]", "Heights St.Dev.\n[nm]",  "Slopes St.Dev.\n[" + u"\u03BC" + "rad]"]
        self.table.setHorizontalHeaderLabels(self.horHeaders)
        self.plot_canvas[0].setGraphXLabel("Y [m]")
        self.plot_canvas[1].setGraphXLabel("Y [m]")
        self.axis.set_xlabel("X [m]")
        self.axis.set_ylabel("Y [m]")

        label = self.le_dimension_y_from.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_dimension_y_to.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_new_length_1.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_new_length_2.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")

        label = self.le_dimension_x.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_step_x.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_correlation_length_x.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")

        label = self.le_conversion_factor_x_x.parent().layout().itemAt(0).widget()
        label.setText("Conversion from file to meters\n(Abscissa)")
        label = self.le_conversion_factor_x_y.parent().layout().itemAt(0).widget()
        label.setText("Conversion from file to meters\n(Height Profile Values)")

        label = self.le_new_length_x_1.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")
        label = self.le_new_length_x_2.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [m]")

    def initializeTabs(self):
        self.tabs = oasysgui.tabWidget(self.mainArea)

        self.tab = [oasysgui.createTabPage(self.tabs, "Info"),
                    oasysgui.createTabPage(self.tabs, "Heights Profile"),
                    oasysgui.createTabPage(self.tabs, "Slopes Profile"),
                    oasysgui.createTabPage(self.tabs, "PSD Heights"),
                    oasysgui.createTabPage(self.tabs, "CSD Heights"),
                    oasysgui.createTabPage(self.tabs, "ACF"),
                    oasysgui.createTabPage(self.tabs, "Generated 2D Profile"),
        ]

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

        self.plot_canvas = [None, None, None, None, None, None]

        self.plot_canvas[0] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[0].setDefaultPlotLines(True)
        self.plot_canvas[0].setActiveCurveColor(color='blue')
        self.plot_canvas[0].setGraphYLabel("Z [nm]")
        self.plot_canvas[0].setGraphTitle("Heights Profile")
        self.plot_canvas[0].setInteractiveMode(mode='zoom')

        self.plot_canvas[1] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[1].setDefaultPlotLines(True)
        self.plot_canvas[1].setActiveCurveColor(color='blue')
        self.plot_canvas[1].setGraphYLabel("Zp [$\mu$rad]")
        self.plot_canvas[1].setGraphTitle("Slopes Profile")
        self.plot_canvas[1].setInteractiveMode(mode='zoom')

        self.plot_canvas[2] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[2].setDefaultPlotLines(True)
        self.plot_canvas[2].setActiveCurveColor(color='blue')
        self.plot_canvas[2].setGraphXLabel("f [m^-1]")
        self.plot_canvas[2].setGraphYLabel("PSD [m^3]")
        self.plot_canvas[2].setGraphTitle("Power Spectral Density of Heights Profile")
        self.plot_canvas[2].setInteractiveMode(mode='zoom')
        self.plot_canvas[2].setXAxisLogarithmic(True)
        self.plot_canvas[2].setYAxisLogarithmic(True)

        self.plot_canvas[3] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[3].setDefaultPlotLines(True)
        self.plot_canvas[3].setActiveCurveColor(color='blue')
        self.plot_canvas[3].setGraphXLabel("f [m^-1]")
        self.plot_canvas[3].setGraphYLabel("CSD [m^3]")
        self.plot_canvas[3].setGraphTitle("Cumulative Spectral Density of Heights Profile")
        self.plot_canvas[3].setInteractiveMode(mode='zoom')
        self.plot_canvas[3].setXAxisLogarithmic(True)

        self.plot_canvas[4] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[4].setDefaultPlotLines(True)
        self.plot_canvas[4].setActiveCurveColor(color='blue')
        self.plot_canvas[4].setGraphXLabel("Length [m]")
        self.plot_canvas[4].setGraphYLabel("ACF")
        self.plot_canvas[4].setGraphTitle("Autocovariance Function of Heights Profile")
        self.plot_canvas[4].setInteractiveMode(mode='zoom')

        self.figure = Figure(figsize=(10, 7))
        self.figure.patch.set_facecolor('white')

        self.axis = self.figure.add_subplot(111, projection='3d')
        self.axis.set_zlabel("Z [nm]")

        self.plot_canvas[5] = FigureCanvasQTAgg(self.figure)
        self.plot_canvas[5].setFixedWidth(self.IMAGE_WIDTH)
        self.plot_canvas[5].setFixedHeight(self.IMAGE_HEIGHT)

        self.profileInfo = oasysgui.textArea(height=self.IMAGE_HEIGHT-5, width=400)

        profile_box = oasysgui.widgetBox(self.tab[0], "", addSpace=True, orientation="horizontal", height = self.IMAGE_HEIGHT, width=410)
        profile_box.layout().addWidget(self.profileInfo)

        for index in range(0, 6):
            self.tab[index+1].layout().addWidget(self.plot_canvas[index])

        self.tabs.setCurrentIndex(1)

    def plot_dabam_graph(self, plot_canvas_index, curve_name, x_values, y_values, xtitle, ytitle, color='blue', replace=True):
        self.plot_canvas[plot_canvas_index].addCurve(x_values, y_values, curve_name, symbol='', color=color, replace=replace) #'+', '^', ','
        self.plot_canvas[plot_canvas_index].setGraphXLabel(xtitle)
        self.plot_canvas[plot_canvas_index].setGraphYLabel(ytitle)
        self.plot_canvas[plot_canvas_index].replot()

    def set_ModifyY(self):
        self.modify_box_1.setVisible(self.modify_y == 0)
        self.modify_box_2.setVisible(self.modify_y == 1)
        self.modify_box_3.setVisible(self.modify_y == 2)

    def set_RenormalizeY(self):
        self.output_profile_box_1.setVisible(self.renormalize_y==1)
        self.output_profile_box_2.setVisible(self.renormalize_y==0)

    def set_KindOfProfileX(self):
        self.kind_of_profile_x_box_1.setVisible(self.kind_of_profile_x<2 or self.kind_of_profile_x==3)

        self.kind_of_profile_x_box_1_0.setVisible(self.kind_of_profile_x<2)
        self.kind_of_profile_x_box_1_1.setVisible(self.kind_of_profile_x==0)
        self.kind_of_profile_x_box_1_2.setVisible(self.kind_of_profile_x==1)
        self.kind_of_profile_x_box_1_3.setVisible(self.kind_of_profile_x<2)

        self.kind_of_profile_x_box_2.setVisible(self.kind_of_profile_x==2)
        self.kind_of_profile_x_box_2_1.setVisible(self.kind_of_profile_x==2 and self.renormalize_x==1)

    def set_ModifyX(self):
        self.modify_box_1_1.setVisible(self.modify_x == 0)
        self.modify_box_1_2.setVisible(self.modify_x == 1)
        self.modify_box_1_3.setVisible(self.modify_x == 2)

    def table_item_clicked(self):
        if self.table.selectionModel().hasSelection():
            if not self.table.rowCount() == 0:
                if not self.table.item(0, 0) is None:
                    row = self.table.selectionModel().selectedRows()[0].row()
                    self.entry_number = int(self.table.item(row, 0).text())

                    self.retrieve_profile()

    def retrieve_profile(self):
        try:
            if self.entry_number is None or self.entry_number <= 0:
                raise Exception("Entry number should be a strictly positive integer number")

            self.server.set_server(self.server_address)
            self.server.load(self.entry_number)
            self.profileInfo.setText(self.server.info_profiles())
            self.plot_canvas[0].setGraphTitle(
                "Heights Profile. St.Dev.=%.3f nm" % (self.server.stdev_profile_heights() * 1e9))
            self.plot_canvas[1].setGraphTitle(
                "Slopes Profile. St.Dev.=%.3f $\mu$rad" % (self.server.stdev_profile_slopes() * 1e6))
            if self.use_undetrended == 0:
                self.plot_dabam_graph(0, "heights_profile", self.si_to_user_units * self.server.y,
                                      1e9 * self.server.zHeights, "Y [" + self.workspace_units_label + "]", "Z [nm]")
                self.plot_dabam_graph(1, "slopes_profile", self.si_to_user_units * self.server.y, 1e6 * self.server.zSlopes,
                                      "Y [" + self.workspace_units_label + "]", "Zp [$\mu$rad]")
            else:
                self.plot_dabam_graph(0, "heights_profile", self.si_to_user_units * self.server.y,
                                      1e9 * self.server.zHeightsUndetrended, "Y [" + self.workspace_units_label + "]",
                                      "Z [nm]")
                self.plot_dabam_graph(1, "slopes_profile", self.si_to_user_units * self.server.y,
                                      1e6 * self.server.zSlopesUndetrended, "Y [" + self.workspace_units_label + "]",
                                      "Zp [$\mu$rad]")
            y = self.server.f ** (self.server.powerlaw["hgt_pendent"]) * 10 ** self.server.powerlaw["hgt_shift"]
            i0 = self.server.powerlaw["index_from"]
            i1 = self.server.powerlaw["index_to"]
            beta = -self.server.powerlaw["hgt_pendent"]
            self.plot_canvas[2].setGraphTitle(
                "Power Spectral Density of Heights Profile (beta=%.2f,Df=%.2f)" % (beta, (5 - beta) / 2))
            self.plot_dabam_graph(2, "psd_heights_2", self.server.f, self.server.psdHeights, "f [m^-1]", "PSD [m^3]")
            self.plot_dabam_graph(2, "psd_heights_1", self.server.f, y, "f [m^-1]", "PSD [m^3]", color='green',
                                  replace=False)
            self.plot_dabam_graph(2, "psd_heights_3", self.server.f[i0:i1], y[i0:i1], "f [m^-1]", "PSD [m^3]", color='red',
                                  replace=False)
            self.plot_dabam_graph(3, "csd", self.server.f, self.server.csd_heights(), "f [m^-1]", "CSD [m^3]")
            c1, c2, c3 = dabam.autocorrelationfunction(self.server.y, self.server.zHeights)
            self.plot_canvas[4].setGraphTitle(
                "Autocovariance Function of Heights Profile.\nAutocorrelation Length (ACF=0.5)=%.3f m" % (c3))
            self.plot_dabam_graph(4, "acf", c1[0:-1], c2, "Length [m]", "Heights Autocovariance")
            # surface error removal
            if not self.zz is None and not self.yy is None and not self.xx is None:
                self.xx = None
                self.yy = None
                self.zz = None
                self.axis.set_title("")
                self.axis.clear()
                self.plot_canvas[5].draw()

            if (self.tabs.currentIndex()==6): self.tabs.setCurrentIndex(1)


        except Exception as exception:
            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

    def retrieve_profile_minus_one(self):
        self.entry_number -= 1
        self.retrieve_profile()

    def retrieve_profile_plus_one(self):
        self.entry_number += 1
        self.retrieve_profile()

    def send_profile(self):
        try:
            if self.server.y is None: raise Exception("No Profile Selected")

            dabam_y = self.server.y
            dabam_profile = numpy.zeros((len(dabam_y), 2))
            dabam_profile[:, 0] = dabam_y
            dabam_profile[:, 1] = self.server.zHeights

            self.send("DABAM 1D Profile", dabam_profile)
        except Exception as exception:
            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

    def search_profiles(self):
        try:
            self.table.itemClicked.disconnect(self.table_item_clicked)
            self.table.clear()

            row_count = self.table.rowCount()
            for n in range(0, row_count):
                self.table.removeRow(0)

            self.table.setHorizontalHeaderLabels(self.horHeaders)

            profiles = dabam.dabam_summary_dictionary(surface=self.get_dabam_shape(),
                                                      slp_err_from=self.slope_error_from*1e-6,
                                                      slp_err_to=self.slope_error_to*1e-6,
                                                      length_from=self.dimension_y_from / self.si_to_user_units,
                                                      length_to=self.dimension_y_to / self.si_to_user_units,
                                                      server=self.server_address)

            for index in range(0, len(profiles)):
                self.table.insertRow(0)

            for index in range(0, len(profiles)):
                table_item = QTableWidgetItem(str(profiles[index]["entry"]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(index, 0, table_item)
                table_item = QTableWidgetItem(str(profiles[index]["surface"]))
                table_item.setTextAlignment(Qt.AlignLeft)
                self.table.setItem(index, 1, table_item)
                table_item = QTableWidgetItem(str(numpy.round(profiles[index]["length"]*self.si_to_user_units, 3)))
                table_item.setTextAlignment(Qt.AlignRight)
                self.table.setItem(index, 2, table_item)
                table_item = QTableWidgetItem(str(numpy.round(profiles[index]["hgt_err"]*1e9, 3)))
                table_item.setTextAlignment(Qt.AlignRight)
                self.table.setItem(index, 3, table_item)
                table_item = QTableWidgetItem(str(numpy.round(profiles[index]["slp_err"]*1e6, 3)))
                table_item.setTextAlignment(Qt.AlignRight)
                self.table.setItem(index, 4, table_item)

            self.table.setHorizontalHeaderLabels(self.horHeaders)
            self.table.resizeRowsToContents()
            self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

            self.table.itemClicked.connect(self.table_item_clicked)

            self.overlay_search.hide()

        except Exception as exception:
            self.overlay_search.hide()

            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)

    def get_dabam_shape(self):
        if self.shape == 0: return None
        elif self.shape == 1: return "plane"
        elif self.shape == 2: return "cylindrical"
        elif self.shape == 3: return "elliptical"
        elif self.shape == 4: return "toroidal"
        elif self.shape == 5: return "spherical"

    def calculate_heigth_profile_ni(self):
        self.calculate_heigth_profile(not_interactive_mode=True)

    def calculate_heigth_profile(self, not_interactive_mode=False):
        try:
            if self.server.y is None: raise Exception("No Profile Selected")

            sys.stdout = EmittingStream(textWritten=self.writeStdOut)

            self.check_fields()

            combination = "E"

            if self.modify_y == 2:
                profile_1D_y_x_temp = self.si_to_user_units * self.server.y
                if self.use_undetrended == 0: profile_1D_y_y_temp = self.si_to_user_units * self.server.zHeights
                else: profile_1D_y_y_temp = self.si_to_user_units * self.server.zHeightsUndetrended

                first_coord = profile_1D_y_x_temp[0]
                second_coord  = profile_1D_y_x_temp[1]
                last_coord = profile_1D_y_x_temp[-1]
                step = numpy.abs(second_coord - first_coord)
                length = numpy.abs(last_coord - first_coord)
                n_points_old = len(profile_1D_y_x_temp)

                if self.new_length_y > length:
                    difference = self.new_length_y - length

                    n_added_points = int(difference/step)
                    if difference % step == 0:
                        n_added_points += 1
                    if n_added_points % 2 != 0:
                        n_added_points += 1


                    profile_1D_y_x = numpy.arange(n_added_points + n_points_old) * step
                    profile_1D_y_y = numpy.ones(n_added_points + n_points_old) * self.filler_value_y * 1e-9 * self.si_to_user_units
                    profile_1D_y_y[int(n_added_points/2) : n_points_old + int(n_added_points/2)] = profile_1D_y_y_temp
                elif self.new_length_y < length:
                    difference = length - self.new_length_y

                    n_removed_points = int(difference/step)
                    if difference % step == 0:
                        n_removed_points -= 1
                    if n_removed_points % 2 != 0:
                        n_removed_points -= 1

                    if n_removed_points >= 2:
                        profile_1D_y_x = profile_1D_y_x_temp[0 : (n_points_old - n_removed_points)]
                        profile_1D_y_y = profile_1D_y_y_temp[(int(n_removed_points/2) - 1) : (n_points_old - int(n_removed_points/2) - 1)]

                    else:
                        profile_1D_y_x = profile_1D_y_x_temp
                        profile_1D_y_y = profile_1D_y_y_temp
                else:
                    profile_1D_y_x = profile_1D_y_x_temp
                    profile_1D_y_y = profile_1D_y_y_temp

            else:
                if self.modify_y == 0:
                    profile_1D_y_x = self.si_to_user_units * self.server.y
                elif self.modify_y == 1:
                    scale_factor_y = self.new_length_y / (self.si_to_user_units * (max(self.server.y) - min(self.server.y)))
                    profile_1D_y_x = self.si_to_user_units * self.server.y * scale_factor_y

                if self.use_undetrended == 0: profile_1D_y_y = self.si_to_user_units * self.server.zHeights
                else: profile_1D_y_y = self.si_to_user_units * self.server.zHeightsUndetrended


            if self.center_y:
                first_coord = profile_1D_y_x[0]
                last_coord = profile_1D_y_x[-1]
                length = numpy.abs(last_coord - first_coord)

                profile_1D_y_x_temp = numpy.linspace(-length/2, length/2, len(profile_1D_y_x))

                profile_1D_y_x = profile_1D_y_x_temp

            if self.renormalize_y == 0:
                rms_y = None
            else:
                if self.error_type_y == profiles_simulation.FIGURE_ERROR:
                    rms_y = self.rms_y * 1e-9 * self.si_to_user_units  # from nm to m
                else:
                    rms_y = self.rms_y * 1e-6 # from urad to rad


            #### WIDTH
            if self.kind_of_profile_x == 3:
                combination += "F"

                xx, yy, zz = profiles_simulation.simulate_profile_2D(combination = combination,
                                                                     error_type_l = self.error_type_y,
                                                                     rms_l = rms_y,
                                                                     x_l = profile_1D_y_x,
                                                                     y_l = profile_1D_y_y,
                                                                     mirror_width = self.dimension_x,
                                                                     step_w = self.step_x,
                                                                     rms_w = 0.0)
            else:
                if self.kind_of_profile_x == 2:
                    combination += "E"

                    if self.delimiter_x == 1:
                        profile_1D_x_x, profile_1D_x_y = numpy.loadtxt(self.heigth_profile_1D_file_name_x, delimiter='\t', unpack=True)
                    else:
                        profile_1D_x_x, profile_1D_x_y = numpy.loadtxt(self.heigth_profile_1D_file_name_x, unpack=True)

                    profile_1D_x_x *= self.conversion_factor_x_x
                    profile_1D_x_y *= self.conversion_factor_x_y

                    first_coord = profile_1D_x_x[0]
                    second_coord  = profile_1D_x_x[1]
                    last_coord = profile_1D_x_x[-1]
                    step = numpy.abs(second_coord - first_coord)
                    length = numpy.abs(last_coord - first_coord)
                    n_points_old = len(profile_1D_x_x)

                    if self.modify_x == 2:
                        profile_1D_x_x_temp = profile_1D_x_x
                        profile_1D_x_y_temp = profile_1D_x_y

                        if self.new_length_x > length:
                            difference = self.new_length_x - length

                            n_added_points = int(difference/step)
                            if difference % step == 0:
                                n_added_points += 1
                            if n_added_points % 2 != 0:
                                n_added_points += 1


                            profile_1D_x_x = numpy.arange(n_added_points + n_points_old) * step
                            profile_1D_x_y = numpy.ones(n_added_points + n_points_old) * self.filler_value_x * 1e-9 * self.si_to_user_units
                            profile_1D_x_y[int(n_added_points/2) : n_points_old + int(n_added_points/2)] = profile_1D_x_y_temp
                        elif self.new_length_x < length:
                            difference = length - self.new_length_x

                            n_removed_points = int(difference/step)
                            if difference % step == 0:
                                n_removed_points -= 1
                            if n_removed_points % 2 != 0:
                                n_removed_points -= 1

                            if n_removed_points >= 2:
                                profile_1D_x_x = profile_1D_x_x_temp[0 : (n_points_old - n_removed_points)]
                                profile_1D_x_y = profile_1D_x_y_temp[(int(n_removed_points/2) - 1) : (n_points_old - int(n_removed_points/2) - 1)]

                            else:
                                profile_1D_x_x = profile_1D_x_x_temp
                                profile_1D_x_y = profile_1D_x_y_temp
                        else:
                            profile_1D_x_x = profile_1D_x_x_temp
                            profile_1D_x_y = profile_1D_x_y_temp

                    elif self.modify_x == 1:
                        scale_factor_x = self.new_length_x/length
                        profile_1D_x_x *= scale_factor_x

                    if self.center_x:
                        first_coord = profile_1D_x_x[0]
                        last_coord = profile_1D_x_x[-1]
                        length = numpy.abs(last_coord - first_coord)

                        profile_1D_x_x_temp = numpy.linspace(-length/2, length/2, len(profile_1D_x_x))
                        profile_1D_x_x = profile_1D_x_x_temp


                    if self.renormalize_x == 0:
                        rms_x = None
                    else:
                        if self.error_type_x == profiles_simulation.FIGURE_ERROR:
                            rms_x = self.rms_x * 1e-9 * self.si_to_user_units # from nm to m
                        else:
                            rms_x = self.rms_x * 1e-6 # from urad to rad

                else:
                    profile_1D_x_x = None
                    profile_1D_x_y = None

                    if self.kind_of_profile_x == 0: combination += "F"
                    else: combination += "G"

                    if self.error_type_x == profiles_simulation.FIGURE_ERROR:
                        rms_x = self.rms_x * 1e-9 * self.si_to_user_units # from nm to m
                    else:
                        rms_x = self.rms_x * 1e-6 # from urad to rad

                xx, yy, zz = profiles_simulation.simulate_profile_2D(combination = combination,
                                                                     error_type_l = self.error_type_y,
                                                                     rms_l = rms_y,
                                                                     x_l = profile_1D_y_x,
                                                                     y_l = profile_1D_y_y,
                                                                     mirror_width = self.dimension_x,
                                                                     step_w = self.step_x,
                                                                     random_seed_w = self.montecarlo_seed_x,
                                                                     error_type_w = self.error_type_x,
                                                                     rms_w = rms_x,
                                                                     power_law_exponent_beta_w = self.power_law_exponent_beta_x,
                                                                     correlation_length_w = self.correlation_length_x,
                                                                     x_w = profile_1D_x_x,
                                                                     y_w = profile_1D_x_y)

            self.xx = xx
            self.yy = yy
            self.zz = zz # in user units

            self.axis.clear()

            x_to_plot, y_to_plot = numpy.meshgrid(xx, yy)
            z_to_plot = zz * 1e9 / self.si_to_user_units #nm

            self.axis.plot_surface(x_to_plot, y_to_plot, z_to_plot,
                                   rstride=1, cstride=1, cmap=cm.autumn, linewidth=0.5, antialiased=True)


            sloperms = profiles_simulation.slopes(zz.T, xx, yy, return_only_rms=1)

            title = ' Slope error rms in X direction: %f $\mu$rad' % (sloperms[0]*1e6) + '\n' + \
                    ' Slope error rms in Y direction: %f $\mu$rad' % (sloperms[1]*1e6) + '\n' + \
                    ' Figure error rms in X direction: %f nm' % (round(zz[0, :].std()*1e9/self.si_to_user_units, 6)) + '\n' + \
                    ' Figure error rms in Y direction: %f nm' % (round(zz[:, 0].std()*1e9/self.si_to_user_units, 6))

            self.axis.set_xlabel("X [" + self.get_axis_um() + "]")
            self.axis.set_ylabel("Y [" + self.get_axis_um() + "]")
            self.axis.set_zlabel("Z [nm]")
            self.axis.set_title(title)
            self.axis.mouse_init()

            if not not_interactive_mode:
                self.tabs.setCurrentIndex(6)

                self.plot_canvas[5].draw()

                QMessageBox.information(self, "QMessageBox.information()",
                                        "Height Profile calculated: if the result is satisfactory,\nclick \'Generate Height Profile File\' to complete the operation ",
                                        QMessageBox.Ok)
        except Exception as exception:
            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

    def generate_heigth_profile_file_ni(self):
        self.generate_heigth_profile_file(not_interactive_mode=True)

    def generate_heigth_profile_file(self, not_interactive_mode=False):
        if not self.zz is None and not self.yy is None and not self.xx is None:
            try:
                congruence.checkDir(self.heigth_profile_file_name)

                sys.stdout = EmittingStream(textWritten=self.writeStdOut)

                congruence.checkFileName(self.heigth_profile_file_name)

                self.write_error_profile_file()

                if not not_interactive_mode:
                    QMessageBox.information(self, "QMessageBox.information()",
                                            "Height Profile file " + self.heigth_profile_file_name + " written on disk",
                                            QMessageBox.Ok)

                dimension_x = self.dimension_x

                if self.kind_of_profile_x == 2: #user defined
                    dimension_x = (self.xx[-1] - self.xx[0])

                if self.modify_y == 0:
                    dimension_y = self.si_to_user_units * (self.server.y[-1] - self.server.y[0])
                if self.modify_y == 1 or self.modify_y == 2:
                    dimension_y = self.new_length_y

                self.send_data(dimension_x, dimension_y)

            except Exception as exception:
                QMessageBox.critical(self, "Error",
                                     exception.args[0],
                                     QMessageBox.Ok)

    def write_error_profile_file(self):
        raise NotImplementedError("This method is abstract")

    def send_data(self, dimension_x, dimension_y):
        raise NotImplementedError("This method is abstract")


    def call_reset_settings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass

    def check_fields(self):
        congruence.checkLessOrEqualThan(self.step_x, self.dimension_x/2, "Step Width", "Width/2")

        if self.modify_y == 1 or self.modify_y == 2:
            self.new_length_y = congruence.checkStrictlyPositiveNumber(self.new_length_y, "New Length")

        if self.renormalize_y == 1:
            self.rms_y = congruence.checkPositiveNumber(self.rms_y, "Rms Y")

        congruence.checkDir(self.heigth_profile_file_name)

        if self.kind_of_profile_x == 3:
            self.dimension_x = congruence.checkStrictlyPositiveNumber(self.dimension_x, "Dimension X")
            self.step_x = congruence.checkStrictlyPositiveNumber(self.step_x, "Step X")
        elif self.kind_of_profile_x < 2:
            self.dimension_x = congruence.checkStrictlyPositiveNumber(self.dimension_x, "Dimension X")
            self.step_x = congruence.checkStrictlyPositiveNumber(self.step_x, "Step X")
            if self.kind_of_profile_x == 0: self.power_law_exponent_beta_x = congruence.checkPositiveNumber(self.power_law_exponent_beta_x, "Beta Value X")
            if self.kind_of_profile_x == 1: self.correlation_length_x = congruence.checkStrictlyPositiveNumber(self.correlation_length_x, "Correlation Length X")
            self.rms_x = congruence.checkPositiveNumber(self.rms_x, "Rms X")
            self.montecarlo_seed_x = congruence.checkPositiveNumber(self.montecarlo_seed_x, "Monte Carlo initial seed X")
        elif self.kind_of_profile_x == 2:
            congruence.checkFile(self.heigth_profile_1D_file_name_x)
            self.conversion_factor_x_x = congruence.checkStrictlyPositiveNumber(self.conversion_factor_x_x, "Conversion from file to meters (Abscissa)")
            self.conversion_factor_x_y = congruence.checkStrictlyPositiveNumber(self.conversion_factor_x_y, "Conversion from file to meters (Height Profile Values)")
            if self.modify_x > 0:
                self.new_length_x = congruence.checkStrictlyPositiveNumber(self.new_length_x, "New Length")
            if self.renormalize_x == 1:
                self.rms_x = congruence.checkPositiveNumber(self.rms_x, "Rms X")

    def writeStdOut(self, text):
        cursor = self.shadow_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.shadow_output.setTextCursor(cursor)
        self.shadow_output.ensureCursorVisible()

    def selectFile1D_X(self):
        self.le_heigth_profile_1D_file_name_x.setText(oasysgui.selectFileFromDialog(self, self.heigth_profile_1D_file_name_x, "Select 1D Height Profile File", file_extension_filter="Data Files (*.dat *.txt)"))

    def selectFile(self):
        self.le_heigth_profile_file_name.setText(oasysgui.selectFileFromDialog(self, self.heigth_profile_file_name, "Select Output File", file_extension_filter="Data Files (*.dat)"))

    def selectServerDefault(self):
        self.le_server_address.setText(self.server.get_default_server())

    def selectServer(self):
        # self.le_server_address.setText(oasysgui.selectFileFromDialog(self, self.server_address, "Select Local Directory"))

        directory_name = oasysgui.selectDirectoryFromDialog(self, self.server_address, "Select Local Directory")
        self.le_server_address.setText(directory_name)

    def get_axis_um(self):
        return "m"
