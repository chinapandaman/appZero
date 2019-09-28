class AppZeroFactory(object):
    _layer = ""
    _component = ""

    def __init__(self, layer, component):
        self._layer = layer
        self._component = component

    def build(self):
        if self._component == "menu":
            from app_factory.menu.menu import Menu

            return Menu()
