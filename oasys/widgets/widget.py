import os

from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtCore import Qt

from orangewidget import widget

def layout_insert(layout, widget, before):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget() is before:
            break
    else:
        raise ValueError("{} is not in layout".format(widget))
    layout.insertWidget(i, widget, )

class OWWidget(widget.OWWidget):

    IS_DEVELOP = False if not "OASYSDEVELOP" in os.environ.keys() else str(os.environ.get('OASYSDEVELOP')) == "1"

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

    def insertLayout(self):
        """
        Reimplemented from OWWidget.insertLayout.

        Pull the OWWidget created controlArea and mainArea widgets into
        QScrollArea's.

        """
        super().insertLayout()

        self.setStyleSheet("background-color: #EBEBEB;")

        cls = type(self)

        if cls.want_basic_layout and cls.want_control_area:
            layout = self.leftWidgetPart.layout()
            area = QScrollArea()
            layout_insert(layout, area, before=self.controlArea)
            layout.takeAt(layout.indexOf(self.controlArea))
            area.setWidget(self.controlArea)
            area.setWidgetResizable(True)

        if cls.want_basic_layout and cls.want_main_area:
            layout = self.topWidgetPart.layout()
            area = QScrollArea()
            layout_insert(layout, area, before=self.mainArea)
            layout.takeAt(layout.indexOf(self.mainArea))
            area.setWidget(self.mainArea)
            area.setWidgetResizable(True)

    def setWorkingDirectory(self, directory):
        self.working_directory = directory

        self.after_change_working_directory()

    def setWorkspaceUnits(self, units):
        self.workspace_units = units

        if self.workspace_units == 0:
            self.workspace_units_label = "m"
            self.workspace_units_to_m = 1.0
            self.workspace_units_to_cm = 100.0
            self.workspace_units_to_mm = 1000.0

        elif self.workspace_units == 1:
            self.workspace_units_label = "cm"
            self.workspace_units_to_m = 0.01
            self.workspace_units_to_cm = 1.0
            self.workspace_units_to_mm = 10.0

        elif self.workspace_units == 2:
            self.workspace_units_label = "mm"
            self.workspace_units_to_m = 0.001
            self.workspace_units_to_cm = 0.1
            self.workspace_units_to_mm = 1.0

        self.after_change_workspace_units()

    def after_change_working_directory(self):
        pass

    def after_change_workspace_units(self):
        pass

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        for shower in getattr(self, "showers", []):
            if name in shower.expression:
                shower()

    def show_at(self, expression, what):
        class ShowerClass:
            def __init__(shower):
                shower.what = what
                shower.expression = expression

            def __call__(shower):
                x = self # to force self into the closure, because we need it in the expression
                to_show = eval(expression)
                if shower.what.isHidden() == to_show:
                    if to_show:
                        shower.what.show()
                    else:
                        shower.what.hide()

        shower = ShowerClass()
        if not hasattr(self, "showers"):
            self.showers = []
        self.showers.append(shower)

    def process_showers(self):
        for shower in getattr(self, "showers", []):
            shower()


# Pull signal definition constants to oasys widget namespace.
Default = widget.Default
NonDefault = widget.NonDefault
Single = widget.Single
Multiple = widget.Multiple
Explicit = widget.Explicit
Dynamic = widget.Dynamic

InputSignal = widget.InputSignal
OutputSignal = widget.OutputSignal

from orangewidget import gui
from orangewidget.settings import Setting

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect

class AutomaticWidget(OWWidget):

    is_automatic_execution = Setting(True)

    CONTROL_AREA_WIDTH = 405

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    def __init__(self, is_automatic=True):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.98, self.MAX_WIDTH)),
                               round(min(geom.height()*0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        if is_automatic:
            self.general_options_box = gui.widgetBox(self.controlArea, "General Options", addSpace=True, orientation="horizontal")

            gui.checkBox(self.general_options_box, self, 'is_automatic_execution', 'Automatic Execution')
        else:
            self.is_automatic_execution=False
