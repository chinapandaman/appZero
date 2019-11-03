# -*- coding: utf-8 -*-


import json
import os

from jsonschema import validate, RefResolver


def validate_json_obj(schema_path, schema_name, obj):
    with open(os.path.join(schema_path, schema_name), "rb+") as f:
        schema = json.load(f)

        reference_path = (
            "file://{0}/".format(schema_path)
            if os.name == "posix"
            else "file:///{0}/".format(schema_path)
        )
        resolver = RefResolver(reference_path, schema)

        validate(instance=obj, schema=schema, resolver=resolver)
