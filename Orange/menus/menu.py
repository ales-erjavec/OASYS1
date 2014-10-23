__author__ = 'labx'
__menu__="just for discovery"

from Orange.canvas.application.canvasmain import CanvasMainWindow

class OMenu():

    canvas_main_window=None
    name = None
    sub_menu_names = []

    def __init__(self, canvas_main_window, name="NewMenu"):
        self.canvas_main_window = canvas_main_window
        self.name = name

    def addSubMenu(self, name):
        self.sub_menu_names.append(name)

    def getSubMenuNamesList(self):
        return self.sub_menu_names

    def executeAction(self, sub_menu_index):
        pass

