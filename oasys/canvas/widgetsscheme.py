"""
OASYS Widgets Scheme
====================

A Scheme for OASYS Orange Widgets Scheme.

.. autoclass:: OASYSWidgetsScheme
   :bases:

.. autoclass:: OASYSWidgetsSignalManager
   :bases:

"""
import os
import sys
import logging

import sip

from PyQt4.QtCore import QSettings
from PyQt4.QtCore import pyqtSignal as Signal, pyqtProperty as Property

from orangecanvas.scheme import Scheme, readwrite

from orangewidget.canvas.workflow import (
    WidgetsScheme, WidgetManager, WidgetsSignalManager
)

log = logging.getLogger(__name__)


class OASYSWidgetsScheme(WidgetsScheme):
    #: Signal emitted when the working directory changes.
    working_directory_changed = Signal(str)

    def __init__(self, parent=None, title=None, description=None,
                 working_directory=None):
        settings = QSettings()

        self.__working_directory = (
            working_directory or
            settings.value("output/default-working-directory",
                           os.path.expanduser("~/Oasys"), type=str))

        if not os.path.exists(self.__working_directory):
            os.makedirs(self.__working_directory, exist_ok=True)

        super().__init__(parent, title=title, description=description)

        # Replace the signal manager from.
        self.signal_manager.setParent(None)
        self.signal_manager.deleteLater()
        sip.delete(self.signal_manager)
        sip.delete(self.widget_manager)

        self.set_loop_flags(Scheme.AllowLoops)
        self.signal_manager = OASYSSignalManager(self)
        self.widget_manager = OASYSWidgetManager()
        self.widget_manager.set_scheme(self)

    def set_working_directory(self, working_directory):
        """
        Set the scheme working_directory.
        """
        if self.__working_directory != working_directory:
            self.__working_directory = working_directory
            self.working_directory_changed.emit(working_directory)

    def working_directory(self):
        """
        The working_directory of the scheme.
        """
        return self.__working_directory

    working_directory = Property(str,
                                 fget=working_directory,
                                 fset=set_working_directory)

    def save_to(self, stream, pretty=True, pickle_fallback=False):
        """
        Reimplemented from Scheme.save_to.
        """
        if isinstance(stream, str):
            stream = open(stream, "wb")

        self.sync_node_properties()

        tree = readwrite.scheme_to_etree(self, pickle_fallback=pickle_fallback)
        root = tree.getroot()
        root.set("working_directory", self.working_directory or "")

        if pretty:
            readwrite.indent(tree.getroot(), 0)

        if sys.version_info < (2, 7):
            # in Python 2.6 the write does not have xml_declaration parameter.
            tree.write(stream, encoding="utf-8")
        else:
            tree.write(stream, encoding="utf-8", xml_declaration=True)


class OASYSWidgetManager(WidgetManager):
    def set_scheme(self, scheme):
        super().set_scheme(scheme)
        scheme.working_directory_changed.connect(self.__wd_changed)

    def create_widget_instance(self, node):
        """
        Reimplemented from WidgetManager.create_widget_instance
        """
        widget = super().create_widget_instance(node)
        if hasattr(widget, "setWorkingDirectory"):
            widget.setWorkingDirectory(self.scheme().working_directory)
        return widget

    def __wd_changed(self, workdir):
        for node in self.scheme().nodes:
            w = self.widget_for_node(node)
            if hasattr(w, "setWorkingDirectory"):
                w.setWorkingDirectory(workdir)


class OASYSSignalManager(WidgetsSignalManager):
    def pending_nodes(self):
        """
        Reimplemented from SignalManager.pending_nodes.

        Enforce some custom ordering semantics in workflow cycles.
        """

        pending = super().pending_nodes()

        pending_new = [node for node in pending
                       if not getattr(self.scheme().widget_for_node(node),
                                      "process_last", False)]

        if pending_new:
            pending = pending_new

        return pending
