# -*- coding: utf-8 -*-


import os

from jsonschema import ValidationError

from app_factory.base import AppZero
from gluon import HTTP, current


class Page(AppZero):
    def _locate_page_definition(self, param):
        self._definition_path = os.path.join(
            current.request.folder,
            "static",
            "json",
            "view",
            "page",
            "{name}.json".format(name=param),
        )
        if not os.path.exists(self._definition_path):
            raise HTTP(404, "cannot locate page definition '{name}'".format(name=param))
        self._schema_name = "page.schema.json"
        self._schema_path = os.path.join(
            current.request.folder,
            "static",
            "json_schema",
            "view_schema",
            "page_schema",
        )

    def _construction_method(self, param):
        self._locate_page_definition(param)
        self._validate()
        self._page_validate()

    def _page_validate(self):
        for row in self.data["rows"]:
            total_ratio = 0
            for section in row:
                total_ratio += section["col_ratio"]
            if total_ratio > 12:
                raise ValidationError(
                    "sections exceed maximum resolution: {sections}".format(
                        sections=", ".join(
                            ["'{}'".format(each["section_name"]) for each in row]
                        )
                    )
                )
