# -*- coding: utf-8 -*-


import os

from gluon import current, HTTP

from app_factory.base import AppZero


class Section(AppZero):
    def _locate_section_definition(self, param):
        self._definition_path = os.path.join(
            current.request.folder,
            "static",
            "json",
            "view",
            "section",
            "{name}.json".format(name=param),
        )
        if not os.path.exists(self._definition_path):
            raise HTTP(404)
        self._schema_name = "section.schema.json"
        self._schema_path = os.path.join(
            current.request.folder,
            "static",
            "json_schema",
            "view_schema",
            "section_schema",
        )

    def _construction_method(self, param):
        self._locate_section_definition(param)
        self._validate()
