__author__ = 'labx'
__menu__="just for discovery"

SEPARATOR = "OMENU_SEPARATOR"
OPEN_CONTAINER = "OPEN_CONTAINER"
CLOSE_CONTAINER = "CLOSE_CONTAINER"

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

    def openContainer(self):
        self.sub_menu_names.append(OPEN_CONTAINER)

    def closeContainer(self):
        self.sub_menu_names.append(CLOSE_CONTAINER)

    def addContainer(self, name):
        self.sub_menu_names.append(name)

    def isSeparator(self, name):
        return name == SEPARATOR

    def isOpenContainer(self, name):
        return name == OPEN_CONTAINER

    def isCloseContainer(self, name):
        return name == CLOSE_CONTAINER

    def getSubMenuNamesList(self):
        return self.sub_menu_names

