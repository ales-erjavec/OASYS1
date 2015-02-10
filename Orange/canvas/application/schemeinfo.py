"""
Scheme Info editor widget.

"""

import os

from PyQt4.QtGui import (
    QWidget, QDialog, QLabel, QTextEdit, QCheckBox, QLineEdit, QFormLayout, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialogButtonBox, QSizePolicy, QFileDialog
)

from PyQt4.QtCore import Qt, QSettings

from ..gui.lineedit import LineEdit
from ..gui.utils import StyledWidget_paintEvent, StyledWidget

class SchemeInfoEdit(QWidget):
    """Scheme info editor widget.
    """
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.scheme = None
        self.__setupUi()

    def __setupUi(self):
        layout = QFormLayout()
        layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.name_edit = LineEdit(self)
        self.name_edit.setPlaceholderText(self.tr("untitled"))
        self.name_edit.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Fixed)

        self.working_dir_edit = QWidget(self)
        self.working_dir_edit.setLayout(QHBoxLayout())
        self.working_dir_edit.layout().setContentsMargins(0, 0, 0, 0)

        settings = QSettings()
        self.working_dir_line = QLineEdit(self)
        self.working_dir_line.setReadOnly(True)

        cur_wd = settings.value("output/default-working-directory",
                                "", type=str) or \
            os.path.expanduser("~/OASYS")

        self.working_dir_line.setText(cur_wd)
        pb = QPushButton("Change ...")
        pb.clicked.connect(self.change_working_directory)

        self.working_dir_edit.layout().addWidget(self.working_dir_line)
        self.working_dir_edit.layout().addWidget(pb)

        self.desc_edit = QTextEdit(self)
        self.desc_edit.setTabChangesFocus(True)

        layout.addRow(self.tr("Name"), self.name_edit)
        layout.addRow(self.tr("Working directory"), self.working_dir_edit)
        layout.addRow(self.tr("Description"), self.desc_edit)

        self.__schemeIsUntitled = True

        self.setLayout(layout)

    def setScheme(self, scheme):
        """Set the scheme to display/edit

        """
        self.scheme = scheme
        if not scheme.title:
            self.name_edit.setText(self.tr("untitled"))
            self.name_edit.selectAll()
            self.__schemeIsUntitled = True
        else:
            self.name_edit.setText(scheme.title)
            self.__schemeIsUntitled = False
        self.desc_edit.setPlainText(scheme.description or "")
        self.working_dir_line.setText(scheme.working_directory)

    def commit(self):
        """Commit the current contents of the editor widgets
        back to the scheme.

        """
        if self.__schemeIsUntitled and \
            self.name_edit.text() == self.tr("untitled"):
            # 'untitled' text was not changed
            name = ""
        else:
            name = str(self.name_edit.text()).strip()

        working_directory = self.working_dir_line.text()

        description = str(self.desc_edit.toPlainText()).strip()
        self.scheme.title = name
        self.scheme.description = description
        self.scheme.working_directory = working_directory

        os.chdir(working_directory)

        if not os.path.exists(working_directory + "/Output"):
            os.mkdir(working_directory + "/Output")

        if not os.path.exists(working_directory + "/Files"):
            os.mkdir(working_directory + "/Files")


    def paintEvent(self, event):
        return StyledWidget_paintEvent(self, event)

    def title(self):
        return str(self.name_edit.text()).strip()

    def description(self):
        return str(self.desc_edit.toPlainText()).strip()

    def working_directory(self):
        return self.working_dir_line.text()

    def change_working_directory(self):
        cur_wd = self.working_dir_line.text()
        new_wd = QFileDialog.getExistingDirectory(
            self, "Set working directory", cur_wd
        )
        if new_wd:
            self.working_dir_line.setText(new_wd)


class SchemeInfoDialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.scheme = None
        self.__autoCommit = True

        self.__setupUi()

    def __setupUi(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.editor = SchemeInfoEdit(self)
        self.editor.layout().setContentsMargins(20, 20, 20, 20)
        self.editor.layout().setSpacing(15)
        self.editor.setSizePolicy(QSizePolicy.MinimumExpanding,
                                  QSizePolicy.MinimumExpanding)

        heading = self.tr("Workflow Info")
        heading = "<h3>{0}</h3>".format(heading)
        self.heading = QLabel(heading, self, objectName="heading")

        # Insert heading
        self.editor.layout().insertRow(0, self.heading)

        self.buttonbox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
            )

        # Insert button box
        self.editor.layout().addRow(self.buttonbox)

        widget = StyledWidget(self, objectName="auto-show-container")
        check_layout = QHBoxLayout()
        check_layout.setContentsMargins(20, 10, 20, 10)

        self.__showAtNewSchemeCheck = \
            QCheckBox(self.tr("Show when I make a New Workflow."),
                      self,
                      objectName="auto-show-check",
                      checked=False,
                      )

        check_layout.addWidget(self.__showAtNewSchemeCheck)

        check_layout.addWidget(
               QLabel(self.tr("You can also edit Workflow Info later "
                              "(File -> Workflow Info)."),
                      self,
                      objectName="auto-show-info"),
               alignment=Qt.AlignRight)
        widget.setLayout(check_layout)
        widget.setSizePolicy(QSizePolicy.MinimumExpanding,
                             QSizePolicy.Fixed)

        if self.__autoCommit:
            self.buttonbox.accepted.connect(self.editor.commit)

        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

        layout.addWidget(self.editor, stretch=10)
        layout.addWidget(widget)

        self.setLayout(layout)

    def setShowAtNewScheme(self, checked):
        """
        Set the 'Show at new scheme' check state.
        """
        self.__showAtNewSchemeCheck.setChecked(checked)

    def showAtNewScheme(self):
        """
        Return the check state of the 'Show at new scheme' check box.
        """
        return self.__showAtNewSchemeCheck.isChecked()

    def setAutoCommit(self, auto):
        if self.__autoCommit != auto:
            self.__autoCommit = auto
            if auto:
                self.buttonbox.accepted.connect(self.editor.commit)
            else:
                self.buttonbox.accepted.disconnect(self.editor.commit)

    def setScheme(self, scheme):
        """Set the scheme to display/edit.
        """
        self.scheme = scheme
        self.editor.setScheme(scheme)
