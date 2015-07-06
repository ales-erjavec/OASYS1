import os

from PyQt4.QtGui import QMenu, QAction, QDialog, QMessageBox

from OrangeCanvas.application import canvasmain

from .widgetsscheme import NoWorkingDirectoryException


class OASYSMainWindow(canvasmain.CanvasMainWindow):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.menu_registry = None

    def open_scheme(self):
        """
        Open an new OASYS scheme.
        """
        try:
            super().open_scheme()
        except NoWorkingDirectoryException:
            return QDialog.Rejected

    def load_scheme(self, filename):
        dirname = os.path.dirname(filename)

        self.last_scheme_dir = dirname

        new_scheme = self.new_scheme_from(filename)
        if new_scheme is not None:
            self.set_new_scheme(new_scheme)

            scheme_doc_widget = self.current_document()
            scheme_doc_widget.setPath(filename)

            self.add_recent_scheme(new_scheme.title, filename)
            status = QDialog.Accepted
        else:  # MODIFIED BY LUCA REBUFFI 14-10-2014
            msgBox = QMessageBox()
            msgBox.setText("Working directory not set by user:\n\nproject load aborted")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec_()
            status = QDialog.Rejected
        return status


    def new_scheme_from(self, filename):
        return super().new_scheme_from(self, filename)

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
