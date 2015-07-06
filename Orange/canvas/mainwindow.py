import os
import io
import logging
from xml.etree import ElementTree

from PyQt4.QtGui import QMenu, QAction, QMessageBox, QFileDialog
from PyQt4.QtCore import QSettings

from OrangeCanvas.scheme import readwrite
from OrangeCanvas.application import canvasmain
from OrangeCanvas.gui.utils import (
    message_critical, message_warning, message_question, message_information
)

from . import widgetsscheme


class OASYSMainWindow(canvasmain.CanvasMainWindow):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.menu_registry = None

    def new_scheme_from(self, filename):
        """
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
                message_information
                return None
        else:
            ret = message_question(
                "Working directory set to:\n\n" + workdir,
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
                        "project load aborted")
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
                details="\n".join(map(repr, errors))
            )
        return new_scheme

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
