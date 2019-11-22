# -*- coding: utf-8 -*-


import os

from gluon import current

from app_factory.base import AppZero


class Table(AppZero):
    _definition_path = os.path.join(
        current.request.folder, "static", "json", "model", "dal", "table.json"
    )
    _schema_name = "table.schema.json"
    _schema_path = os.path.join(
        current.request.folder, "static", "json_schema", "model_schema", "dal_schema"
    )

    def _construction_method(self, param):
        self._validate()
        self._table_validate()

    def _table_validate(self):
        existed_table = []

        for table in self.data:
            if table["table_name"] in existed_table:
                raise Exception(
                    "duplicate table: '{table_name}'".format(
                        table_name=table["table_name"]
                    )
                )
            existed_table.append(table["table_name"])
            existed_field = []
            for field in table["table_fields"]:
                if field["field_name"] in existed_field:
                    raise Exception(
                        "duplicate field in '{table_name}': '{field_name}'".format(
                            table_name=table["table_name"],
                            field_name=field["field_name"],
                        )
                    )
                existed_field.append(field["field_name"])
                if field["field_type"] == "string" and "field_length" not in field:
                    raise Exception(
                        """
                            unspecified 'field_length' for string typed field in '{table_name}': '{field_name}'
                            """.format(
                            table_name=table["table_name"],
                            field_name=field["field_name"],
                        )
                    )
                if field["field_type"] not in ["string"] and "field_length" in field:
                    raise Exception(
                        "invalid property 'field_length' to type: '{field_type}'".format(
                            field_type=field["field_type"]
                        )
                    )
