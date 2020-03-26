# -*- coding: utf-8 -*-


import os

from jsonschema import ValidationError

from app_factory.base import AppZero
from gluon import current


class Menu(AppZero):
    _definition_path = os.path.join(
        current.request.folder, "static", "json", "menu", "menu.json"
    )
    _schema_name = "menu.schema.json"
    _schema_path = os.path.join(
        current.request.folder, "static", "json_schema", "menu_schema"
    )

    def _construction_method(self, param):
        self._validate()
        self._menu_validate()

    def _menu_validate(self):
        from app_factory.factory import AppZeroFactory

        db = current.db

        for section in self.data:
            for item in section["items"]:
                if item["has_sub_item"]:
                    if not item.get("sub_items"):
                        raise ValidationError(
                            "this item is missing subitem(s): '{item}'".format(
                                item=item["text"]
                            )
                        )
                    for sub_item in item["sub_items"]:
                        AppZeroFactory(
                            layer="view",
                            component="page/{page}".format(page=sub_item["page"]),
                            db=db,
                        ).build()
                else:
                    AppZeroFactory(
                        layer="view",
                        component="page/{page}".format(page=item["page"]),
                        db=db,
                    ).build()
