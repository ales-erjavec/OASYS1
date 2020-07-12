import os
import io
import platform
import pickle
import tempfile
import logging
import six
import concurrent.futures
from xml.etree import ElementTree
from contextlib import contextmanager
from datetime import datetime, timedelta
import pkg_resources

from PyQt5.QtWidgets import (
    QWidget, QMenu, QAction, QDialog, QMessageBox, QFileDialog,
    QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QLabel,
    QFormLayout, QComboBox, QGridLayout, QApplication
)
from PyQt5.QtGui import (
    QKeySequence, QIcon
)
from PyQt5.QtCore import Qt, QSettings, QEvent, QStandardPaths
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtCore import pyqtSignal as pyqtSignal

from orangecanvas.scheme import readwrite
from orangecanvas.application import (
    canvasmain, welcomedialog, schemeinfo, settings #, addons
)
from orangecanvas.gui.utils import (
    message_critical, message_warning, message_question, message_information
)
from orangecanvas import config

from oasys.widgets.gui import OptionDialog
import oasys.application.addons as addons

from . import widgetsscheme
from .conf import oasysconf


class OASYSUserSettings(settings.UserSettingsDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # find an hide the "Show welcome screen" check box
        showwelcome = self.findChild(QCheckBox, name="show-welcome-screen")
        if showwelcome is not None:
            showwelcome.hide()

        generaltab = self.widget(0)
        outputtab = self.widget(1)
        appstab = self.widget(2)

        box = QWidget(self, objectName="working-directory-container")
        layout = QVBoxLayout()
        self.default_wd_label = QLabel(
            QSettings().value("output/default-working-directory",
                              "", type=str))
        pb = QPushButton("Change ...")
        pb.clicked.connect(self.change_working_directory)

        layout.addWidget(self.default_wd_label)
        layout.addWidget(pb)
        box.setLayout(layout)

        box1 = QWidget(self, objectName="change-container")

        layout1 = QVBoxLayout()
        layout1.setContentsMargins(0, 0, 0, 0)
        self.combo_change_title = QComboBox()
        self.combo_change_title.addItems([self.tr("No"),  self.tr("Yes")])
        self.combo_change_title.setCurrentIndex(QSettings().value("oasys/change_title_on_new_duplicate", 0, int))
        self.combo_change_title.currentIndexChanged.connect(self.change_title)

        layout1.addWidget(self.combo_change_title)
        box1.setLayout(layout1)

        box2 = QWidget(self, objectName="units-container")

        layout2 = QVBoxLayout()
        layout2.setContentsMargins(0, 0, 0, 0)
        self.combo_units = QComboBox()
        self.combo_units.addItems([self.tr("m"),self.tr("cm"), self.tr("mm")])
        self.combo_units.setCurrentIndex(QSettings().value("output/default-units", 1, int))
        self.combo_units.currentIndexChanged.connect(self.change_units)

        layout2.addWidget(self.combo_units)
        box2.setLayout(layout2)


        box3 = QWidget(self, objectName="automatic-save-container")

        layout3 = QVBoxLayout()
        layout3.setContentsMargins(0, 0, 0, 0)
        self.combo_automatic_save = QComboBox()
        self.combo_automatic_save.addItems([self.tr("Never"),
                                  self.tr("5 min"),
                                  self.tr("10 min"),
                                  self.tr("30 min"),
                                  self.tr("60 min")])

        self.combo_automatic_save.setCurrentIndex(QSettings().value("output/automatic-save-minutes", 0, int))
        self.combo_automatic_save.currentIndexChanged.connect(self.change_automatic_save)

        layout3.addWidget(self.combo_automatic_save)
        box3.setLayout(layout3)


        box8 = QWidget(self, objectName="show-effective-source-size-container")

        layout8 = QVBoxLayout()
        layout8.setContentsMargins(0, 0, 0, 0)

        self.combo_show_effective_source_size = QComboBox()
        self.combo_show_effective_source_size.addItems([self.tr("No"), self.tr("Yes")])

        self.combo_show_effective_source_size.setCurrentIndex(QSettings().value("output/show-effective-source-size", 0, int))
        self.combo_show_effective_source_size.currentIndexChanged.connect(self.change_show_effective_source_size)

        layout8.addWidget(self.combo_show_effective_source_size)
        box8.setLayout(layout8)

        box4 = QWidget(self, objectName="send-footprint-container")

        layout4 = QVBoxLayout()
        layout4.setContentsMargins(0, 0, 0, 0)

        self.combo_send_footprint = QComboBox()
        self.combo_send_footprint.addItems([self.tr("No"), self.tr("Yes")])

        self.combo_send_footprint.setCurrentIndex(QSettings().value("output/send-footprint", 0, int))
        self.combo_send_footprint.currentIndexChanged.connect(self.change_send_footprint)

        layout4.addWidget(self.combo_send_footprint)
        box4.setLayout(layout4)

        box5 = QWidget(self, objectName="shadow-default-colormap-container")

        layout5 = QVBoxLayout()
        layout5.setContentsMargins(0, 0, 0, 0)

        self.combo_default_cm_shadow = QComboBox()
        self.combo_default_cm_shadow.addItems([self.tr("gray"), self.tr("reversed gray"), self.tr("temperature")])

        self.combo_default_cm_shadow.setCurrentText(QSettings().value("output/shadow-default-colormap", "temperature", str))
        self.combo_default_cm_shadow.currentIndexChanged.connect(self.change_default_cm_shadow)

        layout5.addWidget(self.combo_default_cm_shadow)
        box5.setLayout(layout5)

        box6 = QWidget(self, objectName="srw-default-colormap-container")

        layout6 = QVBoxLayout()
        layout6.setContentsMargins(0, 0, 0, 0)

        self.combo_default_cm_srw = QComboBox()
        self.combo_default_cm_srw.addItems([self.tr("gray"), self.tr("reversed gray"), self.tr("temperature")])

        self.combo_default_cm_srw.setCurrentText(QSettings().value("output/srw-default-colormap", "gray", str))
        self.combo_default_cm_srw.currentIndexChanged.connect(self.change_default_cm_srw)

        layout6.addWidget(self.combo_default_cm_srw)
        box6.setLayout(layout6)

        box7 = QWidget(self, objectName="srw-default-propagation-mode-container")

        layout7 = QVBoxLayout()
        layout7.setContentsMargins(0, 0, 0, 0)

        self.combo_default_pm_srw = QComboBox()
        self.combo_default_pm_srw.addItems([self.tr("Element by Element (Wofry)"), self.tr("Element by Element (Native)"), self.tr("Whole Beamline (Native)")])

        self.combo_default_pm_srw.setCurrentIndex(QSettings().value("output/srw-default-propagation-mode", 1, int))
        self.combo_default_pm_srw.currentIndexChanged.connect(self.change_default_pm_srw)

        layout7.addWidget(self.combo_default_pm_srw)
        box7.setLayout(layout7)


        box10 = QWidget(self, objectName="wonder-default-gsasii-mode-container")

        layout10 = QVBoxLayout()
        layout10.setContentsMargins(0, 0, 0, 0)

        self.combo_default_gsasii_wonder = QComboBox()
        self.combo_default_gsasii_wonder.addItems([self.tr("Online"), self.tr("External")])

        self.combo_default_gsasii_wonder.setCurrentIndex(QSettings().value("output/wonder-default-gsasii-mode", 0, int))
        self.combo_default_gsasii_wonder.currentIndexChanged.connect(self.change_default_gsasii_wonder)

        layout10.addWidget(self.combo_default_gsasii_wonder)
        box10.setLayout(layout10)

        box11 = QWidget(self, objectName="wonder-default-automatic-container")

        layout11 = QVBoxLayout()
        layout11.setContentsMargins(0, 0, 0, 0)

        self.combo_default_automatic_wonder = QComboBox()
        self.combo_default_automatic_wonder.addItems([self.tr("Runtime Only"), self.tr("OASYS Setting")])

        self.combo_default_automatic_wonder.setCurrentIndex(QSettings().value("output/wonder-default-automatic", 1, int))
        self.combo_default_automatic_wonder.currentIndexChanged.connect(self.change_default_automatic_wonder)

        layout11.addWidget(self.combo_default_automatic_wonder)
        box11.setLayout(layout11)

        generaltab.layout().insertRow(
            0, self.tr("Add Numeral on New/Duplicate"), box1)

        generaltab.layout().insertRow(
            0, self.tr("Default Units"), box2)

        generaltab.layout().insertRow(
            0, self.tr("Automatically save every"), box3)

        appstab.layout().insertRow(
            0, self.tr("Wonder: GSAS-II mode"), box10)

        appstab.layout().insertRow(
            0, self.tr("Wonder: Automatic Fit"), box11)

        appstab.layout().insertRow(
            0, self.tr("SRW: Default Propagation Mode"), box7)

        appstab.layout().insertRow(
            0, self.tr("SRW: Default Colormap"), box6)

        appstab.layout().insertRow(
            0, self.tr("ShadowOui: Default Colormap"), box5)

        appstab.layout().insertRow(
            0, self.tr("ShadowOui: Send footprint beam"), box4)

        appstab.layout().insertRow(
            0, self.tr("ShadowOui: Show Effective Source Size"), box8)

        outputtab.layout().insertRow(
            0, self.tr("Default working directory"), box)

    def change_automatic_save(self):
        QSettings().setValue("output/automatic-save-minutes", self.combo_automatic_save.currentIndex())
        
    def change_title(self):
        QSettings().setValue("oasys/change_title_on_new_duplicate", self.combo_change_title.currentIndex())

    def change_units(self):
        QSettings().setValue("output/default-units", self.combo_units.currentIndex())

    def change_show_effective_source_size(self):
        QSettings().setValue("output/show-effective-source-size", self.combo_show_effective_source_size.currentIndex())

    def change_send_footprint(self):
        QSettings().setValue("output/send-footprint", self.combo_send_footprint.currentIndex())

    def change_default_cm_shadow(self):
        QSettings().setValue("output/shadow-default-colormap", self.combo_default_cm_shadow.currentText())

    def change_default_cm_srw(self):
        QSettings().setValue("output/srw-default-colormap", self.combo_default_cm_srw.currentText())

    def change_default_pm_srw(self):
        QSettings().setValue("output/srw-default-propagation-mode", self.combo_default_pm_srw.currentIndex())

    def change_default_gsasii_wonder(self):
        QSettings().setValue("output/wonder-default-gsasii-mode", self.combo_default_gsasii_wonder.currentIndex())

    def change_default_automatic_wonder(self):
        QSettings().setValue("output/wonder-default-automatic", self.combo_default_automatic_wonder.currentIndex())

    def change_working_directory(self):
        cur_wd = QSettings().value("output/default-working-directory",
                                   os.path.expanduser("~/Oasys"), type=str)
        new_wd = QFileDialog.getExistingDirectory(
            self, "Set working directory", cur_wd
        )
        if new_wd:
            QSettings().setValue("output/default-working-directory", new_wd)
            self.default_wd_label.setText(new_wd)

class OASYSSchemeInfoDialog(schemeinfo.SchemeInfoDialog):
    def __init__(self, parent=None, existing_scheme=False, **kwargs):
        super().__init__(parent, **kwargs)

        # Insert a 'Working Directory' row in the editor form.
        layout = self.editor.layout()

        self.working_dir_edit = QWidget(self)
        self.working_dir_edit.setLayout(QHBoxLayout())
        self.working_dir_edit.layout().setContentsMargins(0, 0, 0, 0)

        settings = QSettings()

        self.working_dir_line = QLineEdit(self)
        self.working_dir_line.setReadOnly(True)

        cur_wd = (settings.value("output/default-working-directory",
                                 "", type=str) or
                  os.path.expanduser("~/Oasys"))

        self.working_dir_line.setText(cur_wd)
        pb = QPushButton("Change ...")
        pb.clicked.connect(self.__change_working_directory)

        self.working_dir_edit.layout().addWidget(self.working_dir_line)
        self.working_dir_edit.layout().addWidget(pb)

        layout.insertRow(2, self.tr("Working directory"), self.working_dir_edit)

        self.units_edit = QWidget(self)
        self.units_edit.setLayout(QGridLayout())
        self.units_edit.layout().setContentsMargins(0, 0, 0, 0)


        self.combo_units = QComboBox()
        self.combo_units.addItems([self.tr("m"),
                                   self.tr("cm"),
                                   self.tr("mm")])

        self.combo_units.setEnabled(not existing_scheme)

        label = QLabel("")

        richText = "<html><head><meta name=\"qrichtext\" content=\"1\" /></head>" + \
                       "<body style=\" white-space: pre-wrap; " + \
                       "font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">" + \
                       "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; " +\
                       "margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\">Units in use in the Scheme   </p>" "</body></html>"

        label.setText(richText)

        self.units_edit.layout().addWidget(label, 0, 0)
        self.units_edit.layout().addWidget(self.combo_units, 0, 1, Qt.AlignRight)

        layout.insertRow( 2, self.tr("Units"), self.units_edit)

        # Fix the widget tab order.
        item = layout.itemAt(1, QFormLayout.FieldRole)
        if item.widget() is not None:
            QWidget.setTabOrder(item.widget(), self.combo_units)
            QWidget.setTabOrder(self.combo_units, self.working_dir_line)
            QWidget.setTabOrder(self.working_dir_line, pb)

    def setScheme(self, scheme):
        super().setScheme(scheme)
        self.working_dir_line.setText(scheme.working_directory)
        self.combo_units.setCurrentIndex(scheme.workspace_units)

    def __change_working_directory(self):
        cur_wd = self.working_dir_line.text()
        new_wd = QFileDialog.getExistingDirectory(self, self.tr("Set working directory"), cur_wd)
        if new_wd: self.working_dir_line.setText(new_wd)

    def title(self):
        return self.editor.title()

    def description(self):
        return self.editor.description()

    def workingDirectory(self):
        return self.working_dir_line.text()

    def workspaceUnits(self):
        return self.combo_units.currentIndex()


def addons_cache_dir():
    cachedir = os.path.join(config.cache_dir(), "addons-cache")
    os.makedirs(cachedir, exist_ok=True)
    return cachedir


def addons_cache_path():
    cachedir = addons_cache_dir()
    cachename = "items-cache.pickle"
    return os.path.join(cachedir, cachename)


def _mktemp(dir, prefix, suffix=None, delete=False):
    return tempfile.NamedTemporaryFile(
        prefix=prefix, suffix=suffix, dir=dir, delete=False)


@contextmanager
def atomicupdate(filepath):
    dirname, basename = os.path.split(filepath)

    if not basename:
        raise ValueError("must name a file")

    basename, ext = os.path.splitext(basename)

    f = _mktemp(dirname, prefix=basename + "-", suffix=ext, delete=False)
    tempfilename = f.name

    try:
        stat = os.stat(filepath)
    except FileNotFoundError:
        os.chmod(tempfilename, 0o644)
    else:
        # Copy user, group and access flags
        if platform.system() != 'Windows':
            os.chown(tempfilename, stat.st_uid, stat.st_gid)
        os.chmod(tempfilename, stat.st_mode)

    try:
        yield f
    except BaseException:
        f.close()
        os.remove(tempfilename)
        raise
    else:
        f.close()

    try:
        os.replace(tempfilename, filepath)
    except OSError:
        os.remove(tempfilename)
        raise


def store_pypi_packages(items):
    with atomicupdate(addons_cache_path()) as f:
        pickle.dump(items, f)


def load_pypi_packages():
    try:
        with open(addons_cache_path(), "rb") as f:
            try:
                items = pickle.load(f)
            except Exception:
                items = []
    except OSError:
        items = []
    return items

def resource_path(path):
    return pkg_resources.resource_filename(__name__, path)

from oasys.util.external_command import CommandFailed, run_command

class OASYSMainWindow(canvasmain.CanvasMainWindow):

    automatic_save = pyqtSignal()

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.is_main = True
        self.menu_registry = None

        settings = QSettings()
        updateperiod = settings.value(
            "oasys/addon-update-check-period", defaultValue=1, type=int)
        try:
            timestamp = os.stat(addons_cache_path()).st_mtime
        except OSError:
            timestamp = 0

        lastdelta = datetime.now() - datetime.fromtimestamp(timestamp)
        self._log = logging.getLogger(__name__)
        self._log.info("Time from last update %s (%s)", lastdelta, timestamp)
        check = updateperiod >= 0 and \
                abs(lastdelta) > timedelta(days=updateperiod)

        self.__executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.__pypi_addons_f = None
        self.__pypi_addons = None
        self.__updatable = 0

        if check:
            f = self.__executor.submit(addons.list_available_versions)
            f.add_done_callback(
                addons.method_queued(self.__set_pypi_addons_f, (object,)))
            self.__pypi_addons_f = f
        else:
            try:
                items = load_pypi_packages()
            except Exception:
                pass
            else:
                self.__set_pypi_addons(items)

        self.automatic_save.connect(self.automatic_save_scheme)

        # PUT OLD CODE HERE IN CASE OF ROLLBACK

        if platform.system() == "Darwin":
            self.new_instance_action = \
                QAction(self.tr("New OASYS instance"), self,
                        objectName="new-oasys-instance",
                        toolTip=self.tr("Run a new OASYS instance"),
                        triggered=self.new_instance,
                        icon=canvasmain.canvas_icons("Open.svg")
                        )

            file_menu = self.menuBar().children()[-1]

            file_menu.addSeparator()
            file_menu.addAction(self.new_instance_action)

    def set_secondary(self):
        self.is_main = False

    @Slot(object)
    def __set_pypi_addons_f(self, f):
        if f.exception():
            err = f.exception()
            self._log.error("Error querying PyPi",
                            exc_info=(type(err), err, None))
        else:
            self.__set_pypi_addons(f.result())
            store_pypi_packages(self.__pypi_addons)

    def __set_pypi_addons(self, items):
            self.__pypi_addons = items
            self._log.debug("Got pypi packages: %r", self.__pypi_addons)
            items = addons.installable_items(
                self.__pypi_addons,
                [ep.dist for ep in oasysconf.addon_entry_points()])

            self.__updatable = sum(addons.is_updatable(item) for item in items)

    def new_instance(self):
        run_command(["python", "-m", "oasys.canvas"], raise_on_fail=False, wait_for_output=False)

    def automatic_save_scheme(self):
        """Save the current scheme. If the scheme does not have an associated
        path then prompt the user to select a scheme file. Return
        QDialog.Accepted if the scheme was successfully saved and
        QDialog.Rejected if the user canceled the file selection.

        """
        document = self.current_document()
        curr_scheme = document.scheme()
        path = document.path()

        temporary_file_name = "automatic_save_" + str(id(self)) + ".ows~"

        if path and self.check_can_save(document, path + "~"):
            if self.save_scheme_to(curr_scheme, path + "~"):
                if os.path.exists(temporary_file_name):
                    os.remove(temporary_file_name)

                return QDialog.Accepted
            else:
                return QDialog.Rejected
        else:
            return self.save_scheme_to(curr_scheme, temporary_file_name)

    def new_scheme(self):
        """
        Reimplemented from `CanvasMainWindow.new_scheme`.

        Create a new empty workflow scheme.

        Return QDialog.Rejected if the user canceled the operation and
        QDialog.Accepted otherwise.
        """
        document = self.current_document()
        if document.isModifiedStrict():
            # Ask for save changes
            if self.ask_save_changes() == QDialog.Rejected:
                return QDialog.Rejected

        new_scheme = widgetsscheme.OASYSWidgetsScheme(parent=self)

        status = self.show_scheme_properties_for(new_scheme, self.tr("New Workflow"))

        if status == QDialog.Rejected: return QDialog.Rejected
        elif not os.path.isdir(new_scheme.working_directory):
            message_information(
                "Workflow Working Directory does not exist\n\n"
                "project creation aborted",
                parent=self)

            return QDialog.Rejected

        self.set_new_scheme(new_scheme)
        self._log.info("Changing current work dir to '%s'",
                       new_scheme.working_directory)
        os.chdir(new_scheme.working_directory)
        return QDialog.Accepted

    def new_scheme_from(self, filename):
        """
        Reimplemented from `CanvasMainWindow.new_scheme_from`.
        Create and return a new :class:`WidgetsScheme` from `filename`.
        Return `None` if an error occurs or the user aborts the process.
        """
        log = logging.getLogger(__name__)

        default_workdir = QSettings().value("output/default-working-directory", os.path.expanduser("~/Oasys"), type=str)
        default_units   = QSettings().value("output/default-units", 1, type=int)

        try:
            contents = io.BytesIO(open(filename, "rb").read())
            doc  = ElementTree.parse(contents)
            root = doc.getroot()
            workdir   = root.get("working_directory")
            workunits = root.get("workspace_units")
            title     = root.get("title", "untitled")
            # First parse the contents into intermediate representation
            # to catch format errors early (will be re-parsed later).
            try:
                readwrite.parse_ows_etree_v_2_0(doc)
            except Exception:
                message_critical(
                     self.tr("Could not load an Orange Workflow file"),
                     title=self.tr("Error"),
                     informative_text=self.tr("An unexpected error occurred "
                                              "while loading '%s'.") % filename,
                     exc_info=True,
                     parent=self)
                return None

            if not workdir or not os.path.isdir(workdir): workdir = default_workdir
            if workunits is None: workunits = default_units
        except Exception:
            return None

        # change working directory of units on open

        new_scheme = widgetsscheme.OASYSWidgetsScheme(parent=self)

        if not title is None: new_scheme.title = title
        new_scheme.working_directory = workdir
        new_scheme.workspace_units   = int(workunits)

        status = self.show_scheme_properties_for(new_scheme, self.tr("Properties of " + new_scheme.title))

        if status == QDialog.Rejected or \
                (new_scheme.working_directory is None or new_scheme.workspace_units is None):
            log.info("Confirmation/Modification of workflow properties aborted by user")
            message_information(
                "Confirmation/Modification of workflow properties canceled by user\n\n"
                "project load aborted",
                parent=self)

            return None
        else:
            message = None
            if workdir      != new_scheme.working_directory: message = "Workflow working directory"
            if int(workunits) != new_scheme.workspace_units: message = "Workflow units" if message is None else (message + " and units")

            if not message is None:
                message += " changed by user"
                log.info(message)
                message_information(message, parent=self)

            if not os.path.isdir(new_scheme.working_directory): os.mkdir(new_scheme.working_directory)

            errors = []
            contents.seek(0)
            try:
                readwrite.scheme_load(new_scheme, contents, error_handler=errors.append)
            except Exception:
                message_critical(
                     self.tr("Could not load an Orange Workflow file"),
                     title=self.tr("Error"),
                     informative_text=self.tr("An unexpected error occurred "
                                              "while loading '%s'.") % filename,
                     exc_info=True,
                     parent=self)
                return None

            if errors:
                message_critical(
                    self.tr("Errors occurred while loading the workflow."),
                    title=self.tr("Problem"),
                    informative_text=self.tr(
                         "There were problems loading some "
                         "of the widgets/links in the "
                         "workflow."
                    ),
                    details="\n".join(map(repr, errors)),
                    parent=self
                )

                return None

            # now start the actual load with a valid working directory
            log.info("Changing current work dir to '%s'", new_scheme.working_directory)
            os.chdir(new_scheme.working_directory)

            return new_scheme

    def set_new_scheme(self, new_scheme):
        from oasys.util.oasys_util import ShowTextDialog

        dlg = ShowTextDialog("Loading Workflow...", "\nLoading Workflow " + new_scheme.title + " ...\n", label=True, button=False)
        dlg.show()

        super().set_new_scheme(new_scheme)

        dlg.hide()
        dlg.deleteLater()

    def getWorkspaceUnitsLabel(self, units):
        if units == 0:   return "m"
        elif units == 1: return "cm"
        elif units == 2: return "mm"
        else:            return None

    def welcome_dialog(self):
        """
        Show a modal welcome dialog for OASYS.

        Reimplemented from `CanvasMainWindow`.
        """

        dialog = welcomedialog.WelcomeDialog(self)
        dialog.setWindowTitle(self.tr("Welcome to OASYS"))

        def new_scheme():
            if self.new_scheme() == QDialog.Accepted:
                dialog.accept()

        def open_scheme():
            if self.open_scheme() == QDialog.Accepted:
                dialog.accept()

        def open_recent():
            if self.recent_scheme() == QDialog.Accepted:
                dialog.accept()

        def get_started():
            import webbrowser
            webbrowser.open("https://github.com/oasys-kit/oasys_school")

        def documentation():
            import webbrowser
            webbrowser.open("https://www.aps.anl.gov/Science/Scientific-Software/OASYS")


        new_action = \
            QAction(self.tr("New"), dialog,
                    toolTip=self.tr("Open a new workflow."),
                    triggered=new_scheme,
                    shortcut=QKeySequence.New,
                    icon=canvasmain.canvas_icons("New.svg")
                    )

        open_action = \
            QAction(self.tr("Open"), dialog,
                    objectName="welcome-action-open",
                    toolTip=self.tr("Open a workflow."),
                    triggered=open_scheme,
                    shortcut=QKeySequence.Open,
                    icon=canvasmain.canvas_icons("Open.svg")
                    )

        recent_action = \
            QAction(self.tr("Recent"), dialog,
                    objectName="welcome-recent-action",
                    toolTip=self.tr("Browse and open a recent workflow."),
                    triggered=open_recent,
                    shortcut=QKeySequence(Qt.ControlModifier | \
                                          (Qt.ShiftModifier | Qt.Key_R)),
                    icon=canvasmain.canvas_icons("Recent.svg")
                    )

        get_started_action = \
            QAction(self.tr("OASYS School"), self,
                    objectName="get-started-action",
                    toolTip=self.tr("OASYS School"),
                    triggered=get_started,
                    icon=canvasmain.canvas_icons("Get Started.svg")
                    )

        documentation_action = \
            QAction(self.tr("Web Site"), self,
                    objectName="documentation-action",
                    toolTip=self.tr("View reference website."),
                    triggered=documentation,
                    icon=canvasmain.canvas_icons("Documentation.svg")
                    )

        icon = resource_path("icons/Install.svg")

        addons_action = \
            QAction(self.tr("Add-ons"), dialog,
                    objectName="welcome-addons-action",
                    toolTip=self.tr("Install add-ons"),
                    triggered=self.open_addons,
                    icon=QIcon(icon),
                    )

        if self.__updatable:
            addons_action.setText("Update Now")
            addons_action.setToolTip("Update or install new add-ons")
            addons_action.setIcon(QIcon(resource_path("icons/Update.svg")))

            mbox = QMessageBox(
                dialog,
                icon=QMessageBox.Information,
                text="{} add-on{} {} a newer version.\n"
                     "Would you like to update now?"
                     .format("One" if self.__updatable == 1 else self.__updatable,
                             "s" if self.__updatable > 1 else "",
                             "has" if self.__updatable == 1 else "have"),
                standardButtons=QMessageBox.Ok | QMessageBox.No,
            )
            mbox.setWindowFlags(Qt.Sheet | Qt.MSWindowsFixedSizeDialogHint)
            mbox.setModal(True)
            dialog.show()
            mbox.show()
            mbox.finished.connect(
                lambda r:
                    self.open_addons() if r == QMessageBox.Ok else None
            )

        #bottom_row = [self.get_started_action, self.tutorials_action,
        #              self.documentation_action, addons_action]

        bottom_row = [get_started_action, documentation_action, addons_action]

        self.new_action.triggered.connect(dialog.accept)
        top_row = [new_action, open_action, recent_action]

        dialog.addRow(top_row, background="light-grass")
        dialog.addRow(bottom_row, background="light-orange")

        # Find and hide the welcome dialogs bottom bar. It contains the
        # Show at startup" check box and we ALWAYS want the Welcome Dialog
        # to show.
        bottombar = dialog.findChild(QWidget, name='bottom-bar')
        if bottombar is not None:
            bottombar.hide()

        status = dialog.exec_()

        dialog.deleteLater()

        return status

    def scheme_properties_dialog(self, existing_scheme=False):
        """Return an empty `SchemeInfo` dialog instance.
        """
        dialog = OASYSSchemeInfoDialog(self, existing_scheme)

        dialog.setWindowTitle(self.tr("Workflow Info"))
        dialog.setFixedSize(725, 450)
        return dialog

    def show_scheme_properties(self):
        """Show current scheme properties.
        """
        current_doc = self.current_document()
        scheme = current_doc.scheme()
        dialog = self.scheme_properties_dialog(existing_scheme=True)
        dialog.setAutoCommit(False)
        dialog.setScheme(scheme)
        status = dialog.exec_()

        if status == QDialog.Accepted:
            stack = current_doc.undoStack()
            scheme = current_doc.scheme()
            stack.beginMacro(self.tr("Change Info"))
            current_doc.setTitle(dialog.title())
            current_doc.setDescription(dialog.description())
            scheme.working_directory = dialog.workingDirectory()
            scheme.workspace_units = dialog.workspaceUnits()
            os.chdir(scheme.working_directory)

            stack.endMacro()

        return status

    def show_scheme_properties_for(self, scheme, window_title=None):
        """
        Reimplemented from `CanvasMainWindow.show_properties_for`

        Show scheme properties for `scheme` with `window_title (if None
        a default 'Scheme Info' title will be used.
        """
        dialog = self.scheme_properties_dialog(existing_scheme=False)
        if window_title is not None: dialog.setWindowTitle(window_title)
        dialog.setScheme(scheme)

        status = dialog.exec_()

        if status == QDialog.Accepted:
            scheme.working_directory = dialog.workingDirectory()
            scheme.workspace_units = dialog.workspaceUnits()
            os.chdir(scheme.working_directory)

        dialog.deleteLater()

        return status


    def open_canvas_settings(self):
        dlg = OASYSUserSettings(self)
        dlg.setWindowTitle(self.tr("Preferences"))
        if dlg.exec_() == 0:
            self._CanvasMainWindow__update_from_settings()

    def set_menu_registry(self, menu_registry):
        self.menu_registry = menu_registry

        for menu_instance in self.menu_registry.menus():
            try:
                menu_instance.setCanvasMainWindow(self)

                custom_menu = QMenu(menu_instance.name, self)
                sub_menus = menu_instance.getSubMenuNamesList()

                is_open_container = False
                container_menu = None
                action_index = 0

                for index in range(0, len(sub_menus)):
                    if is_open_container:
                        if menu_instance.isSeparator(sub_menus[index]):
                            if container_menu is None: raise Exception("Container Menu has not been defined")

                            container_menu.addSeparator()
                        elif menu_instance.isOpenContainer(sub_menus[index]):
                            raise Exception("Container has already been opened: Open Container Operation is inconsistent")
                        elif menu_instance.isCloseContainer(sub_menus[index]):
                            is_open_container = False
                            container_menu = None
                        else:
                            if container_menu is None:
                                container_menu = QMenu(sub_menus[index], self)

                                custom_menu.addMenu(container_menu)
                            else:
                                action_index = action_index + 1
                                custom_action = \
                                    QAction(sub_menus[index], self,
                                            objectName=sub_menus[index].lower() + "-action",
                                            toolTip=self.tr(sub_menus[index]),
                                            )
                                custom_action.triggered.connect(getattr(menu_instance, 'executeAction_' + str(action_index)))
                                container_menu.addAction(custom_action)
                    else:
                        if menu_instance.isSeparator(sub_menus[index]):
                            custom_menu.addSeparator()
                        elif menu_instance.isOpenContainer(sub_menus[index]):
                            is_open_container = True
                        elif menu_instance.isCloseContainer(sub_menus[index]):
                            raise Exception("Container has not been opened: Close Container Operation is inconsistent")
                        else:
                            action_index = action_index + 1
                            custom_action = \
                                QAction(sub_menus[index], self,
                                        objectName=sub_menus[index].lower() + "-action",
                                        toolTip=self.tr(sub_menus[index]),
                                        )
                            custom_action.triggered.connect(getattr(menu_instance, 'executeAction_' + str(action_index)))
                            custom_menu.addAction(custom_action)

                self.menuBar().addMenu(custom_menu)


            except Exception as exception:
                print("Error in creating Customized Menu: " + str(menu_instance))
                print(str(exception.args[0]))
                continue

    def open_addons(self):
        from oasys.application.addons import AddonManagerDialog, have_install_permissions
        if not have_install_permissions():
            QMessageBox(QMessageBox.Warning,
                        "Add-ons: insufficient permissions",
                        "Insufficient permissions to install add-ons. Try starting Orange "
                        "as a system administrator or install Orange in user folders.",
                        parent=self).exec_()
        dlg = AddonManagerDialog(self, windowTitle=self.tr("Add-ons"))
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        return dlg.exec_()

    def closeSecondaryEvent(self, event):
        """Close the main window.
        """
        document = self.current_document()
        if document.isModifiedStrict():
            if self.ask_save_changes() == QDialog.Rejected:
                # Reject the event
                event.ignore()
                return

        old_scheme = document.scheme()

        # Set an empty scheme to clear the document
        document.setScheme(config.workflow_constructor(parent=self))

        QApplication.sendEvent(old_scheme, QEvent(QEvent.Close))

        old_scheme.deleteLater()

        config.save_config()

        geometry = self.saveGeometry()
        state = self.saveState(version=self.SETTINGS_VERSION)
        settings = QSettings()
        settings.beginGroup("mainwindow")
        settings.setValue("geometry", geometry)
        settings.setValue("state", state)
        settings.setValue("canvasdock/expanded",
                          self.dock_widget.expanded())
        settings.setValue("scheme-margins-enabled",
                          self.scheme_margins_enabled)

        settings.setValue("last-scheme-dir", self.last_scheme_dir)
        settings.setValue("widgettoolbox/state",
                          self.widgets_tool_box.saveState())

        settings.setValue("quick-help/visible",
                          self.canvas_tool_dock.quickHelpVisible())

        settings.endGroup()

        event.accept()

    def closeEvent(self, event):
        if self.is_main:
            super().closeEvent(event)
            if event.isAccepted():
                if self.__pypi_addons_f is not None:
                    self.__pypi_addons_f.cancel()
                self.__executor.shutdown(wait=True)
        else:
            self.closeSecondaryEvent(event)
            if event.isAccepted():
                if self.__pypi_addons_f is not None:
                    self.__pypi_addons_f.cancel()


    ###############################################
    # REMOVED
    ###############################################

    '''
        in __init__:
        
        self.new_action_on_new_window = \
            QAction(self.tr("New on a New Window"), self,
                    objectName="action-new-new-window",
                    toolTip=self.tr("Open a new workflow on a new window."),
                    triggered=self.new_scheme_on_new_window,
                    icon=canvasmain.canvas_icons("New.svg")
                    )

        self.open_action_on_new_window = \
            QAction(self.tr("Open on a New Window"), self,
                    objectName="action-open-new-window",
                    toolTip=self.tr("Open a workflow on a new window."),
                    triggered=self.open_scheme_on_new_window,
                    icon=canvasmain.canvas_icons("Open.svg")
                    )

        file_menu = self.menuBar().children()[-1]

        file_menu.insertAction(file_menu.actions()[2], self.open_action_on_new_window)
        file_menu.insertAction(file_menu.actions()[1], self.new_action_on_new_window)
    '''

    '''
    
    in new_scheme_from:
    
    # ensure we have a valid working directory either default or
    # stored.
    if not workdir or not os.path.isdir(workdir):
        new_workdir = QFileDialog.getExistingDirectory(
            self, "Set working directory for project '%s'" % (title or "untitled"),
            default_workdir)
        if new_workdir:
            workdir = new_workdir
        else:
            log.info("Replacement of not existing Working Directory "
                     "'%s' aborted by user", workdir)
            message_information(
                "Working directory not set by user:\n\n"
                "project load aborted",
                parent=self)
            return None
    else:
        ret = message_question(
            "Working directory set to:\n\n" + workdir,
            "Working Directory",
            informative_text="Do you want to change it?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
            parent=self)

        if ret == QMessageBox.Yes:
            new_wd = QFileDialog.getExistingDirectory(
                self, "Set working directory for project '%s'" % (title or "untitled"),
                default_workdir)
            if new_wd:
                workdir = new_wd
                if not os.path.isdir(workdir):
                    os.mkdir(workdir)
            else:
                log.info("Replacement of not existing Working Directory "
                         "'%s' aborted by user.", workdir)
                message_information(
                    "Working directory not set by user:\n\n"
                    "project load aborted",
                    parent=self)
                return None

    # now start the actual load with a valid working directory
    log.info("Changing current work dir to '%s'", workdir)
    os.chdir(workdir)

    # ensure we have a valid working directory either default or
    # stored.
    if workunits is None:
        new_units = OptionDialog.get_option(self,
                                            "Set user's units for project '%s'" % (title or "untitled"),
                                            "Set user's units",
                                            ["m", "cm", "mm"], default_units)
        if not new_units is None:
            workunits = new_units
        else:
            log.info("Replacement of not existing User's Units "
                     "'%s' aborted by user", "")
            message_information(
                "Project units not set by user:\n\n"
                "project load aborted",
                parent=self)
            return None
    else:
        workunits = int(workunits)
        ret = message_question(
            "User's units set to: " + self.getWorkspaceUnitsLabel(workunits),
            "User's Units",
            informative_text="Do you want to change it?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No,
            parent=self)

        if ret == QMessageBox.Yes:
            new_units = OptionDialog.get_option(self,
                                                "Set user's units for project '%s'" % (title or "untitled"),
                                                "Set user's units",
                                                ["m", "cm", "mm"], workunits)
            if not new_units is None:
                workunits = new_units

                message_information(
                    "Project new units set by user: " + self.getWorkspaceUnitsLabel(workunits) + \
                    "\n\nWarning: values relating to the previous units are not converted",
                    parent=self)
            else:
                log.info("Replacement of existing User's Units "
                         "'%s' aborted by user", "")
                message_information(
                    "Project units not set by user:\n\n"
                    "project load aborted",
                    parent=self)
                return None
    '''

    '''
    def new_scheme_on_new_window(self):
        """New scheme. Return QDialog.Rejected if the user canceled
        the operation and QDialog.Accepted otherwise.

        """
        window = self.instantiate_window()

        document = window.current_document()
        if document.isModifiedStrict():
            # Ask for save changes
            if window.ask_save_changes() == QDialog.Rejected:
                return QDialog.Rejected

        new_scheme = config.workflow_constructor(parent=self)

        settings = QSettings()
        show = settings.value("schemeinfo/show-at-new-scheme", True,
                              type=bool)

        if show:
            status = window.show_scheme_properties_for(new_scheme, self.tr("New Workflow"))

            if status == QDialog.Rejected:
                return QDialog.Rejected

        window.set_new_scheme(new_scheme)

        return QDialog.Accepted

    def open_scheme_on_new_window(self):
        """Open a new scheme. Return QDialog.Rejected if the user canceled
        the operation and QDialog.Accepted otherwise.

        """
        document = self.current_document()
        if document.isModifiedStrict():
            if self.ask_save_changes() == QDialog.Rejected:
                return QDialog.Rejected

        if self.last_scheme_dir is None:
            # Get user 'Documents' folder
            start_dir = QStandardPaths.standardLocations(
                            QStandardPaths.DocumentsLocation)[0]
        else:
            start_dir = self.last_scheme_dir

        # TODO: Use a dialog instance and use 'addSidebarUrls' to
        # set one or more extra sidebar locations where Schemes are stored.
        # Also use setHistory
        filename = QFileDialog.getOpenFileName(
            self, self.tr("Open Orange Workflow File"),
            start_dir, self.tr("Orange Workflow (*.ows)"),
        )[0]

        if filename:
            return self.load_scheme_on_window(filename, self.instantiate_window())
        else:
            return QDialog.Rejected

    def instantiate_window(self):
        window = OASYSMainWindow()
        window.set_secondary()
        window.setStyleSheet(self.styleSheet())
        window.setWindowIcon(self.windowIcon())
        window.set_widget_registry(self.widget_registry)
        window.set_menu_registry(self.menu_registry)
        window.show()
        window.setGeometry(self.geometry().left() + 10,
                           self.geometry().top() + 10,
                           self.geometry().width(),
                           self.geometry().height())

        return window

    def load_scheme_on_window(self, filename, window):
        """Load a scheme from a file (`filename`) into the current
        document updates the recent scheme list and the loaded scheme path
        property.

        """
        filename = six.text_type(filename)
        dirname = os.path.dirname(filename)

        window.last_scheme_dir = dirname

        new_scheme = window.new_scheme_from(filename)
        if new_scheme is not None:
            window.set_new_scheme(new_scheme)

            scheme_doc_widget = window.current_document()
            scheme_doc_widget.setPath(filename)

            window.add_recent_scheme(new_scheme.title, filename)
            return QDialog.Accepted
        else:
            return QDialog.Rejected

    def new_scheme_from(self, filename):
        """
        Reimplemented from `CanvasMainWindow.new_scheme_from`.

        Create and return a new :class:`WidgetsScheme` from `filename`.

        Return `None` if an error occurs or the user aborts the process.
        """
        log = logging.getLogger(__name__)
        default_workdir = QSettings().value(
            "output/default-working-directory",
            os.path.expanduser("~/Oasys"), type=str)
        default_units = QSettings().value(
            "output/default-units", 1, type=int)

        try:
            contents = io.BytesIO(open(filename, "rb").read())
            doc = ElementTree.parse(contents)
            root = doc.getroot()
            workdir = root.get("working_directory")
            workunits = root.get("workspace_units")
            title = root.get("title", "untitled")
            # First parse the contents into intermediate representation
            # to catch format errors early (will be re-parsed later).
            try:
                readwrite.parse_ows_etree_v_2_0(doc)
            except Exception:
                message_critical(
                     self.tr("Could not load an Orange Workflow file"),
                     title=self.tr("Error"),
                     informative_text=self.tr("An unexpected error occurred "
                                              "while loading '%s'.") % filename,
                     exc_info=True,
                     parent=self)
                return None
            readwrite.parse_ows_etree_v_2_0(doc)
        except Exception:
            return None

        # ensure we have a valid working directory either default or
        # stored.
        if not workdir or not os.path.isdir(workdir):
            new_workdir = QFileDialog.getExistingDirectory(
                self, "Set working directory for project '%s'" % (title or "untitled"),
                default_workdir)
            if new_workdir:
                workdir = new_workdir
            else:
                log.info("Replacement of not existing Working Directory "
                         "'%s' aborted by user", workdir)
                message_information(
                    "Working directory not set by user:\n\n"
                    "project load aborted",
                    parent=self)
                return None
        else:
            ret = message_question(
                "Working directory set to:\n\n" + workdir,
                "Working Directory",
                informative_text="Do you want to change it?",
                buttons=QMessageBox.Yes | QMessageBox.No,
                default_button=QMessageBox.No,
                parent=self)

            if ret == QMessageBox.Yes:
                new_wd = QFileDialog.getExistingDirectory(
                    self, "Set working directory for project '%s'" % (title or "untitled"),
                    default_workdir)
                if new_wd:
                    workdir = new_wd
                    if not os.path.isdir(workdir):
                        os.mkdir(workdir)
                else:
                    log.info("Replacement of not existing Working Directory "
                             "'%s' aborted by user.", workdir)
                    message_information(
                        "Working directory not set by user:\n\n"
                        "project load aborted",
                        parent=self)
                    return None

        # now start the actual load with a valid working directory
        log.info("Changing current work dir to '%s'", workdir)
        os.chdir(workdir)

        # ensure we have a valid working directory either default or
        # stored.
        if workunits is None:
            new_units = OptionDialog.get_option(self,
                                                "Set user's units for project '%s'" % (title or "untitled"),
                                                "Set user's units",
                                                ["m", "cm", "mm"], default_units)
            if not new_units is None:
                workunits = new_units
            else:
                log.info("Replacement of not existing User's Units "
                         "'%s' aborted by user", "")
                message_information(
                    "Project units not set by user:\n\n"
                    "project load aborted",
                    parent=self)
                return None
        else:
            workunits = int(workunits)
            ret = message_question(
                "User's units set to: " + self.getWorkspaceUnitsLabel(workunits),
                "User's Units",
                informative_text="Do you want to change it?",
                buttons=QMessageBox.Yes | QMessageBox.No,
                default_button=QMessageBox.No,
                parent=self)

            if ret == QMessageBox.Yes:
                new_units = OptionDialog.get_option(self,
                                                    "Set user's units for project '%s'" % (title or "untitled"),
                                                    "Set user's units",
                                                    ["m", "cm", "mm"], workunits)
                if not new_units is None:
                    workunits = new_units

                    message_information(
                        "Project new units set by user: " + self.getWorkspaceUnitsLabel(workunits) + \
                        "\n\nWarning: values relating to the previous units are not converted",
                        parent=self)
                else:
                    log.info("Replacement of existing User's Units "
                             "'%s' aborted by user", "")
                    message_information(
                        "Project units not set by user:\n\n"
                        "project load aborted",
                        parent=self)
                    return None

        new_scheme = widgetsscheme.OASYSWidgetsScheme(parent=self)
        new_scheme.working_directory = workdir
        new_scheme.workspace_units = workunits
        errors = []
        contents.seek(0)
        try:
            readwrite.scheme_load(
                new_scheme, contents, error_handler=errors.append)
        except Exception:
            message_critical(
                 self.tr("Could not load an Orange Workflow file"),
                 title=self.tr("Error"),
                 informative_text=self.tr("An unexpected error occurred "
                                          "while loading '%s'.") % filename,
                 exc_info=True,
                 parent=self)
            return None

        if errors:
            message_warning(
                self.tr("Errors occurred while loading the workflow."),
                title=self.tr("Problem"),
                informative_text=self.tr(
                     "There were problems loading some "
                     "of the widgets/links in the "
                     "workflow."
                ),
                details="\n".join(map(repr, errors)),
                parent=self
            )
        return new_scheme
'''
