# -*- coding: utf-8 -*-


import os

from jsonschema import ValidationError

from app_factory.base import AppZero
from gluon import HTTP, current


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
        self._section_validate()

    def _section_validate(self):
        from app_factory.factory import AppZeroFactory

        db = current.db

        api_data = (
            AppZeroFactory(layer="api", component=self.data["api_name"], db=current.db)
            .build()
            .data
        )

        for each in self.data["summary_fields"]:
            if each not in db[api_data["table_name"]]:
                raise ValidationError(
                    "invalid summary field: '{field}'".format(field=each)
                )

        for each in self.data["detail_fields"]:
            if each["name"] not in db[api_data["table_name"]]:
                raise ValidationError(
                    "invalid detail field: '{field}'".format(field=each["name"])
                )

        operation_to_method_mapping = {
            "create": "POST",
            "read": "GET",
            "update": "PUT",
            "delete": "DELETE",
        }

        for each in self.data["allowed_operation"]:
            if operation_to_method_mapping[each] not in api_data["supported_methods"]:
                raise ValidationError(
                    "unallowed operation: '{operation}'".format(operation=each)
                )
