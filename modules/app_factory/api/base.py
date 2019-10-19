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
        if not os.path.exists(self._definition_path):
            raise HTTP(404)
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

    def _method_validate(self, method):
        if method not in self.data["supported_methods"]:
            raise HTTP(405)

    def get(self, table_id=None, additional_query=None):
        self._method_validate("GET")

        query = (
            self._db[self.data["table_name"]].is_active == True
            if "is_active" in self._db[self.data["table_name"]].fields
            else self._db[self.data["table_name"]].id > 0
        )

        if table_id:
            query &= self._db[self.data["table_name"]].id == table_id

        if self.data["GET"].get("queryable_fields") and additional_query:
            for k, v in additional_query.items():
                if k in self.data["GET"]["queryable_fields"]:
                    query &= self._db[self.data["table_name"]][k] == v
                else:
                    raise HTTP(400, "{field} is not a searchable field".format(field=k))

        result = self._db(query).select(
            *[
                self._db[self.data["table_name"]][each]
                for each in self.data["GET"].get("selectors", [])
            ]
        )

        if table_id:
            if result:
                return result.first()
            raise HTTP(404)

        return result

    def post(self, data):
        self._method_validate("POST")

        if any(
            [each not in self.data["POST"]["allowed_fields"] for each in data.keys()]
        ):
            raise HTTP(400)

        if not self.data["POST"]["allow_duplicates"] and self._db[
            self.data["table_name"]
        ](**data):
            raise HTTP(400)

        return self._db[self.data["table_name"]].insert(**data)

    def put(self, table_id, data):
        self._method_validate("PUT")

        if any(
            [each not in self.data["PUT"]["allowed_fields"] for each in data.keys()]
        ):
            raise HTTP(400)

        self._db(
            (self._db[self.data["table_name"]].is_active == True)
            & (self._db[self.data["table_name"]].id == table_id)
        ).update(**data)

        return table_id

    def delete(self, table_id):
        self._method_validate("DELETE")

        record = self._db(
            (self._db[self.data["table_name"]].is_active == True)
            & (self._db[self.data["table_name"]].id == table_id)
        )

        record.delete() if self.data["DELETE"]["is_hard_removal"] else record.update(
            is_active=False
        )

        return table_id
