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
            return self._build_model()

        if self._layer == "api":
            from app_factory.api.base import API

            return API(self._db, param=self._component)

        if self._layer == "view":
            return self._build_view()

    def _build_model(self):
        if self._component == "dal":
            from app_factory.model.dal.table import Table

            return Table(self._db)

    def _build_view(self):
        if self._component.split("/")[0] == "section":
            from app_factory.view.section.section import Section

            return Section(db=self._db, param=self._component.split("/")[1])

        if self._component.split("/")[0] == "page":
            from app_factory.view.page.page import Page

            return Page(db=self._db, param=self._component.split("/")[1])
