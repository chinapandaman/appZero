class AppZeroFactory(object):
    _layer = ""
    _component = ""

    def __init__(self, layer, component, db):
        self._layer = layer
        self._component = component
        self._db = db

    def build(self):
        if self._component == "menu":
            from app_factory.menu.menu import Menu

            return Menu(self._db)

        if self._layer == "model":
            return self.build_model()

        if self._layer == "api":
            from app_factory.api.base import API

            return API(self._db, param=self._component)

    def build_model(self):
        if self._component == "dal":
            from app_factory.model.dal.table import Table

            return Table(self._db)
