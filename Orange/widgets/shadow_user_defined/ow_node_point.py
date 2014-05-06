import Orange
from Orange.widgets import widget
from Orange.shadow.shadow_objects import ShadowBeam


class NodePoint(widget.OWWidget):

    name = "Node Point"
    description = "User Defined: NodePoint"
    icon = "icons/point.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    priority = 1
    category = "User Defined"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Trigger", Orange.shadow.ShadowTrigger, "passTrigger")]

    outputs = [{"name":"Trigger",
                "type":Orange.shadow.ShadowTrigger,
                "doc":"Trigger",
                "id":"Trigger"}]

    def passTrigger(self, trigger):
        self.send("Trigger", trigger)