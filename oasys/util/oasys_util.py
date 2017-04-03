import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtWebKit import QWebView

class TTYGrabber:
    def __init__(self,  tmpFileName = 'out.tmp.dat'):
        self.tmpFileName = tmpFileName
        self.ttyData = []
        self.outfile = False
        self.save = False

    def start(self):
        self.outfile = os.open(self.tmpFileName, os.O_RDWR|os.O_CREAT)
        self.save = os.dup(1)
        os.dup2(self.outfile, 1)
        return

    def stop(self):
        if not self.save:
            return
        os.dup2(self.save, 1)
        tmpFile = open(self.tmpFileName, "r")
        self.ttyData = tmpFile.readlines()
        tmpFile.close()
        os.close(self.outfile)
        os.remove(self.tmpFileName)

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

class ShowHtmlDialog(QtGui.QDialog):

    def __init__(self, title, hrml_text, width=650, height=400, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle(title)
        layout = QtGui.QVBoxLayout(self)

        web_view = QWebView(self)
        web_view.setHtml(hrml_text)

        text_area = QtGui.QScrollArea(self)
        text_area.setWidget(web_view)
        text_area.setWidgetResizable(True)
        text_area.setFixedHeight(height)
        text_area.setFixedWidth(width)

        bbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)

        bbox.accepted.connect(self.accept)
        layout.addWidget(text_area)
        layout.addWidget(bbox)

    @classmethod
    def show_html(cls, title, html_text, width=650, height=400, parent=None):
        dialog = ShowHtmlDialog(title, html_text, width, height, parent)
        dialog.show()


class ShowTextDialog(QtGui.QDialog):

    def __init__(self, title, text, width=650, height=400, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(True)
        self.setWindowTitle(title)
        layout = QtGui.QVBoxLayout(self)

        text_edit = QtGui.QTextEdit("", self)
        text_edit.append(text)
        text_edit.setReadOnly(True)

        text_area = QtGui.QScrollArea(self)
        text_area.setWidget(text_edit)
        text_area.setWidgetResizable(True)
        text_area.setFixedHeight(height)
        text_area.setFixedWidth(width)

        bbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)

        bbox.accepted.connect(self.accept)
        layout.addWidget(text_area)
        layout.addWidget(bbox)

    @classmethod
    def show_text(cls, title, text, width=650, height=400, parent=None):
        dialog = ShowTextDialog(title, text, width, height, parent)
        dialog.show()

