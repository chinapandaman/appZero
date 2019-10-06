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

        if self._layer == "model":
            return self.build_model()

    def build_model(self):
        if self._component == "dal":
            from app_factory.model.dal.table import Table

            return Table()
