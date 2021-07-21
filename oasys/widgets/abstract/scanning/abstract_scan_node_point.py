#!/usr/bin/env python
# -*- coding: utf-8 -*-
# #########################################################################
# Copyright (c) 2020, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2020. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

from PyQt5.QtGui import QPalette, QFont, QColor
from PyQt5.QtWidgets import QMessageBox

from orangewidget import gui
from orangewidget.widget import OWAction
from orangewidget.settings import Setting

from oasys.widgets import widget
from oasys.widgets import gui as oasysgui
from oasys.widgets.gui import ConfirmDialog

from oasys.util.oasys_util import TriggerIn, TriggerOut


class AbstractScanLoopPoint(widget.OWWidget):
    inputs = [("Trigger", TriggerIn, "passTrigger")]

    outputs = [{"name": "Trigger",
                "type": TriggerOut,
                "doc": "Trigger",
                "id": "Trigger"}]
    want_main_area = 0

    number_of_new_objects = Setting(1)
    current_new_object = 0
    run_loop = True
    suspend_loop = False

    variable_name = Setting("<variable name>")
    variable_display_name = Setting("<variable display name>")
    variable_um = Setting("<u.m.>")

    current_variable_value = None

    #################################
    process_last = True

    #################################

    def __init__(self):
        self.runaction = OWAction("Start", self)
        self.runaction.triggered.connect(self.startLoop)
        self.addAction(self.runaction)

        self.runaction = OWAction("Stop", self)
        self.runaction.triggered.connect(self.stopLoop)
        self.addAction(self.runaction)

        self.runaction = OWAction("Suspend", self)
        self.runaction.triggered.connect(self.suspendLoop)
        self.addAction(self.runaction)

        self.runaction = OWAction("Restart", self)
        self.runaction.triggered.connect(self.restartLoop)
        self.addAction(self.runaction)

        self.setFixedWidth(400)
        self.setFixedHeight(500)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=True, orientation="horizontal")

        self.start_button = gui.button(button_box, self, "Start", callback=self.startLoop)
        self.start_button.setFixedHeight(35)

        stop_button = gui.button(button_box, self, "Stop", callback=self.stopLoop)
        stop_button.setFixedHeight(35)
        font = QFont(stop_button.font())
        font.setBold(True)
        stop_button.setFont(font)
        palette = QPalette(stop_button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('red'))
        stop_button.setPalette(palette)  # assign new palette

        self.stop_button = stop_button

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=True, orientation="horizontal")

        suspend_button = gui.button(button_box, self, "Suspend", callback=self.suspendLoop)
        suspend_button.setFixedHeight(35)
        font = QFont(suspend_button.font())
        font.setBold(True)
        suspend_button.setFont(font)
        palette = QPalette(suspend_button.palette())  # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('orange'))
        suspend_button.setPalette(palette)  # assign new palette

        self.re_start_button = gui.button(button_box, self, "Restart", callback=self.restartLoop)
        self.re_start_button.setFixedHeight(35)
        self.re_start_button.setEnabled(False)

        left_box_1 = oasysgui.widgetBox(self.controlArea, "Loop Management", addSpace=True, orientation="vertical", width=380, height=380)

        if self.has_variable_list():
            self.create_variable_list_box(left_box_1)
        else:
            self.create_default_variable_box(left_box_1)

        self.create_specific_loop_box(left_box_1)

        self.le_current_new_object = oasysgui.lineEdit(left_box_1, self, "current_new_object", "Current Loop Number", labelWidth=250, valueType=int, orientation="horizontal")
        self.le_current_new_object.setReadOnly(True)
        font = QFont(self.le_current_new_object.font())
        font.setBold(True)
        self.le_current_new_object.setFont(font)
        palette = QPalette(self.le_current_new_object.palette())  # make a copy of the palette
        palette.setColor(QPalette.Text, QColor('dark blue'))
        palette.setColor(QPalette.Base, QColor(243, 240, 160))
        self.le_current_new_object.setPalette(palette)

        self.le_current_new_object = oasysgui.lineEdit(left_box_1, self, "current_variable_value", "Current Variable Value", labelWidth=250, valueType=self.get_current_value_type(), orientation="horizontal")
        self.le_current_new_object.setReadOnly(True)
        font = QFont(self.le_current_new_object.font())
        font.setBold(True)
        self.le_current_new_object.setFont(font)
        palette = QPalette(self.le_current_new_object.palette())  # make a copy of the palette
        palette.setColor(QPalette.Text, QColor('dark blue'))
        palette.setColor(QPalette.Base, QColor(243, 240, 160))
        self.le_current_new_object.setPalette(palette)

        gui.rubber(self.controlArea)

    def startLoop(self):
        if self.has_variable_list(): self.set_VariableName()

        self.current_new_object = 1

        if self.initialize_start_loop():
            self.setStatusMessage("Running Loop Number " + str(self.current_new_object) + " of " + str(self.number_of_new_objects))
            self.send("Trigger", TriggerOut(new_object=True, additional_parameters={"variable_name": self.variable_name,
                                                                                    "variable_display_name": self.variable_display_name,
                                                                                    "variable_value": self.current_variable_value,
                                                                                    "variable_um": self.variable_um if self.has_variable_um() else ""}))

    def stopLoop(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Interruption of the Loop?"):
            self.run_loop = False
            self.current_variable_value = None
            self.setStatusMessage("Interrupted by user")

    def suspendLoop(self):
        try:
            if ConfirmDialog.confirmed(parent=self, message="Confirm Suspension of the Loop?"):
                self.run_loop = False
                self.suspend_loop = True
                self.stop_button.setEnabled(False)
                self.re_start_button.setEnabled(True)
                self.setStatusMessage("Suspended by user")
        except:
            pass

    def restartLoop(self):
        try:
            self.run_loop = True
            self.suspend_loop = False
            self.stop_button.setEnabled(True)
            self.re_start_button.setEnabled(False)
            self.passTrigger(TriggerIn(new_object=True))
        except:
            pass

    def passTrigger(self, trigger):
        if self.run_loop:
            if trigger:
                if trigger.interrupt:
                    self.current_new_object = 0
                    self.current_variable_value = None
                    self.start_button.setEnabled(True)
                    self.setStatusMessage("")
                    self.send("Trigger", TriggerOut(new_object=False))
                elif trigger.new_object:
                    if self.current_new_object == 0:
                        QMessageBox.critical(self, "Error", "Loop has to be started properly: press the button Start", QMessageBox.Ok)
                        return

                    if self.keep_looping():
                        self.setStatusMessage("Running Loop Number " + str(self.current_new_object) + " of " + str(self.number_of_new_objects))
                        self.start_button.setEnabled(False)
                        self.send("Trigger", TriggerOut(new_object=True, additional_parameters={"variable_name": self.variable_name,
                                                                                                "variable_display_name": self.variable_display_name,
                                                                                                "variable_value": self.current_variable_value,
                                                                                                "variable_um": self.variable_um if self.has_variable_um() else ""}))
                    else:
                        self.current_new_object = 0
                        self.current_variable_value = None
                        self.start_button.setEnabled(True)
                        self.setStatusMessage("")
                        self.send("Trigger", TriggerOut(new_object=False))
        else:
            if not self.suspend_loop:
                self.current_new_object = 0
                self.current_variable_value = None
                self.start_button.setEnabled(True)

            self.send("Trigger", TriggerOut(new_object=False))
            self.setStatusMessage("")
            self.run_loop = True
            self.suspend_loop = False

    def create_default_variable_box(self, box):
        oasysgui.lineEdit(box, self, "variable_name", "Variable Name", labelWidth=100, valueType=str, orientation="horizontal")
        oasysgui.lineEdit(box, self, "variable_display_name", "Variable Display Name", labelWidth=100, valueType=str, orientation="horizontal")
        if self.has_variable_um(): oasysgui.lineEdit(box, self, "variable_um", "Variable Units", labelWidth=250, valueType=str, orientation="horizontal")

    # ABSTRACT METHODS
    def get_current_value_type(self): raise NotImplementedError("This method is abstract")
    def has_variable_list(self): return False
    def has_variable_um(self): return True
    def create_variable_list_box(self, box): raise NotImplementedError("This method is abstract")
    def create_specific_loop_box(self, box): raise NotImplementedError("This method is abstract")
    def initialize_start_loop(self): raise NotImplementedError("This method is abstract")
    def keep_looping(self): raise NotImplementedError("This method is abstract")
    def set_VariableName(self): raise NotImplementedError("This method is abstract")
