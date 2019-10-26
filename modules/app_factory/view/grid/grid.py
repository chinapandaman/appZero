import os

from gluon import current, HTTP

from app_factory.base import AppZero


class Grid(AppZero):
    def _locate_grid_definition(self, param):
        self._definition_path = os.path.join(
            current.request.folder,
            "static",
            "json",
            "view",
            "grid",
            "{name}.json".format(name=param),
        )
        if not os.path.exists(self._definition_path):
            raise HTTP(404)
        self._schema_name = "grid.schema.json"
        self._schema_path = os.path.join(
            current.request.folder,
            "static",
            "json_schema",
            "view_schema",
            "grid_schema",
        )

    def _construction_method(self, param):
        self._locate_grid_definition(param)
        self._validate()
