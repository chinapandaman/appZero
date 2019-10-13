import os

from gluon import current, HTTP

from app_factory.base import AppZero


class API(AppZero):
    def _construction_method(self, param):
        self._locate_api_definition(param)
        self._validate()
        self._api_validate()

    def _locate_api_definition(self, param):
        self._definition_path = os.path.join(
            current.request.folder,
            "static",
            "json",
            "api",
            "{name}.json".format(name=param),
        )
        self._schema_name = "api.schema.json"
        self._schema_path = os.path.join(
            current.request.folder, "static", "json_schema", "api_schema"
        )

    def _api_validate(self):
        for each in self.data["supported_methods"]:
            if each not in self.data:
                raise Exception(
                    "missing method definition: {method}".format(method=each)
                )

    def get(self, table_id=None, additional_query=None):
        if "GET" not in self.data["supported_methods"]:
            raise HTTP(404)

        query = self._db[self.data["GET"]["table_name"]].id > 0

        if table_id:
            query &= self._db[self.data["GET"]["table_name"]].id == table_id

        if self.data["GET"].get("queryable_fields") and additional_query:
            for k, v in additional_query.items():
                if k in self.data["GET"]["queryable_fields"]:
                    query &= self._db[self.data["GET"]["table_name"]][k] == v
                else:
                    raise HTTP(400, "{field} is not a searchable field".format(field=k))

        result = self._db(query).select(
            *[
                self._db[self.data["GET"]["table_name"]][each]
                for each in self.data["GET"].get("selectors", [])
            ]
        )

        return result.first() if table_id else result
