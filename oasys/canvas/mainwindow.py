import os
import io
import logging
from xml.etree import ElementTree

from PyQt4.QtGui import (
    QWidget, QMenu, QAction, QKeySequence, QDialog, QMessageBox, QFileDialog,
    QHBoxLayout, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QLabel,
    QFormLayout
)
from PyQt4.QtCore import Qt, QSettings

from orangecanvas.scheme import readwrite
from orangecanvas.document import commands
from orangecanvas.application import (
    canvasmain, welcomedialog, schemeinfo, settings
)
from orangecanvas.gui.utils import (
    message_critical, message_warning, message_question, message_information
)

from . import widgetsscheme


class OASYSUserSettings(settings.UserSettingsDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # find an hide the "Show welcome screen" check box
        showwelcome = self.findChild(QCheckBox, name="show-welcome-screen")
        if showwelcome is not None:
            showwelcome.hide()

        outputtab = self.widget(1)

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
        outputtab.layout().insertRow(
            0, self.tr("Default working directory"), box)

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
    def __init__(self, parent=None, **kwargs):
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

        layout.insertRow(
            2, self.tr("Working directory"), self.working_dir_edit)

        # Fix the widget tab order.
        item = layout.itemAt(1, QFormLayout.FieldRole)
        if item.widget() is not None:
            QWidget.setTabOrder(item.widget(), self.working_dir_line)
            QWidget.setTabOrder(self.working_dir_line, pb)

    def setScheme(self, scheme):
        super().setScheme(scheme)
        self.working_dir_line.setText(scheme.working_directory)

    def __change_working_directory(self):
        cur_wd = self.working_dir_line.text()
        new_wd = QFileDialog.getExistingDirectory(
            self, self.tr("Set working directory"), cur_wd,
        )
        if new_wd:
            self.working_dir_line.setText(new_wd)

    def title(self):
        self.editor.title()

    def description(self):
        self.editor.description()

    def workingDirectory(self):
        return self.working_dir_line.text()


class OASYSMainWindow(canvasmain.CanvasMainWindow):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.menu_registry = None

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

        new_scheme = widgetsscheme.WidgetsScheme(parent=self)

        status = self.show_scheme_properties_for(
            new_scheme, self.tr("New Workflow")
        )

        if status == QDialog.Rejected:
            return QDialog.Rejected

        self.set_new_scheme(new_scheme)

        return QDialog.Accepted

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

        contents = io.BytesIO(open(filename, "rb").read())
        doc = ElementTree.parse(contents)
        root = doc.getroot()
        workdir = root.get("working_directory")
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

        # ensure we have a valid working directory either default or
        # stored.
        if not workdir or not os.path.isdir(workdir):
            new_workdir = QFileDialog.getExistingDirectory(
                self, "Set working directory for project '%s'" % title,
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
                    self, "Set working directory for project '%s'" % title,
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
        new_scheme = widgetsscheme.WidgetsScheme(parent=self)
        new_scheme.working_directory = workdir
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

        def tutorial():
            if self.tutorial_scheme() == QDialog.Accepted:
                dialog.accept()

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

        tutorials_action = \
            QAction(self.tr("Tutorial"), dialog,
                    objectName="welcome-tutorial-action",
                    toolTip=self.tr("Browse tutorial workflows."),
                    triggered=tutorial,
                    icon=canvasmain.canvas_icons("Tutorials.svg")
                    )

        bottom_row = [self.get_started_action, tutorials_action,
                      self.documentation_action]

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

    def scheme_properties_dialog(self):
        """Return an empty `SchemeInfo` dialog instance.
        """
        dialog = OASYSSchemeInfoDialog(self)

        dialog.setWindowTitle(self.tr("Workflow Info"))
        dialog.setFixedSize(725, 450)
        return dialog

    def show_scheme_properties(self):
        """Show current scheme properties.
        """
        current_doc = self.current_document()
        scheme = current_doc.scheme()
        dlg = self.scheme_properties_dialog()
        dlg.setAutoCommit(False)
        dlg.setScheme(scheme)
        status = dlg.exec_()

        if status == QDialog.Accepted:
            stack = current_doc.undoStack()
            scheme = current_doc.scheme()
            stack.beginMacro(self.tr("Change Info"))
            current_doc.setTitle(dlg.title())
            current_doc.setDescription(dlg.description())
            stack.push(
                commands.SetAttrCommand(
                    scheme, "working_directory", dlg.workingDirectory())
            )
            stack.endMacro()

        return status

    def show_scheme_properties_for(self, scheme, window_title=None):
        """
        Reimplemented from `CanvasMainWindow.show_properties_for`

        Show scheme properties for `scheme` with `window_title (if None
        a default 'Scheme Info' title will be used.
        """
        dialog = self.scheme_properties_dialog()
        if window_title is not None:
            dialog.setWindowTitle(window_title)
        dialog.setScheme(scheme)
        status = dialog.exec_()
        if status == QDialog.Accepted:
            scheme.working_directory = dialog.workingDirectory()
        dialog.deleteLater()
        return status

    def open_canvas_settings(self):
        dlg = OASYSUserSettings(self)
        dlg.setWindowTitle(self.tr("Preferences"))
        if dlg.exec_() == 0:
            # AAAAAAAAAAAAA!
            self._CanvasMainWindow__update_from_settings()

    def set_menu_registry(self, menu_registry):
        self.menu_registry = menu_registry

        for menu_instance in self.menu_registry.menus():
            try:
                menu_instance.setCanvasMainWindow(self)

                custom_menu = QMenu(menu_instance.name, self)

                sub_menus = menu_instance.getSubMenuNamesList()

                for index in range(0, len(sub_menus)):
                    custom_action = \
                        QAction(sub_menus[index], self,
                                objectName=sub_menus[index].lower() + "-action",
                                toolTip=self.tr(sub_menus[index]),
                                )

                    custom_action.triggered.connect(getattr(menu_instance, 'executeAction_' + str(index+1)))

                    custom_menu.addAction(custom_action)

                self.menuBar().addMenu(custom_menu)
            except Exception:
                print("Error in creating Customized Menu: " + str(menu_instance))
                continue
