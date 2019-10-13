import json

from utils.json_schema import validate_json_obj


class AppZero(object):
    data = {}

    _definition_path = ""
    _schema_name = ""
    _schema_path = ""

    def __init__(self, db, param=None):
        self._db = db
        self._construction_method(param)

    def _construction_method(self, param):
        self._validate()

    def _validate(self):
        with open(self._definition_path, "rb+") as f:
            obj = json.load(f)

            validate_json_obj(
                schema_path=self._schema_path, schema_name=self._schema_name, obj=obj
            )

            self.data = obj
