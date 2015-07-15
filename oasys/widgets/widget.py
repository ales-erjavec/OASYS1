from PyQt4.QtGui import QScrollArea

from Orange.widgets import widget, settings, gui


def layout_insert(layout, widget, before):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget() is before:
            break
    else:
        raise ValueError("{} is not in layout".format(widget))
    layout.insertWidget(i, widget, )


class _WhyWhyWhy(widget.WidgetMetaClass):
    def __new__(cls, name, bases, clsdict):
        clsdict = clsdict.copy()
        if "inputs" in clsdict:
            inputs = [widget.InputSignal(**spec)
                      if isinstance(spec, dict) else spec
                      for spec in clsdict["inputs"]]
            clsdict["inputs"] = inputs

        if "outputs" in clsdict:
            outputs = [widget.OutputSignal(**spec)
                       if isinstance(spec, dict) else spec
                       for spec in clsdict["outputs"]]
            clsdict["outputs"] = outputs

        return widget.WidgetMetaClass.__new__(cls, name, bases, clsdict)


class OWWidget(widget.OWWidget, metaclass=_WhyWhyWhy):

    def insertLayout(self):
        """
        Reimplemented from OWWidget.insertLayout.

        Pull the OWWidget created controlArea and mainArea widgets into
        QScrollArea's.

        """
        super().insertLayout()

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

blocking = widget.blocking

# Pull signal definition constants to oasys widget namespace.
Default = widget.Default
NonDefault = widget.NonDefault
Single = widget.Single
Multiple = widget.Multiple
Explicit = widget.Explicit
Dynamic = widget.Dynamic

InputSignal = widget.InputSignal
OutputSignal = widget.OutputSignal
