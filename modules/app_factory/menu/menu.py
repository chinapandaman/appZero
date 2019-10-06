import os

from gluon import current

from app_factory.base import AppZero


class Menu(AppZero):
    _definition_path = os.path.join(
        current.request.folder, "static", "json", "menu", "menu.json"
    )
    _schema_name = "menu.schema.json"
    _schema_path = os.path.join(
        current.request.folder, "static", "json_schema", "menu_schema"
    )
