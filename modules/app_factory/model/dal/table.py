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
