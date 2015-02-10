__author__ = 'labx'
__menu__="just for discovery"

class OMenu():
    canvas_main_window=None
    name = None
    sub_menu_names = []

    def __init__(self, name="NewMenu"):
        self.name = name

    def setCanvasMainWindow(self, canvas_main_window):
        self.canvas_main_window = canvas_main_window

    def addSubMenu(self, name):
        self.sub_menu_names.append(name)

    def getSubMenuNamesList(self):
        return self.sub_menu_names

