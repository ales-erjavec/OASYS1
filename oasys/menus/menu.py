__author__ = 'labx'
__menu__="just for discovery"

SEPARATOR = "OMENU_SEPARATOR"

class OMenu():

    def __init__(self, name="NewMenu"):
        self.name = name
        self.canvas_main_window=None
        self.sub_menu_names = []

    def setCanvasMainWindow(self, canvas_main_window):
        self.canvas_main_window = canvas_main_window

    def addSubMenu(self, name):
        self.sub_menu_names.append(name)

    def addSeparator(self):
        self.sub_menu_names.append(SEPARATOR)

    def isSeparator(self, name):
        return name == SEPARATOR

    def getSubMenuNamesList(self):
        return self.sub_menu_names

