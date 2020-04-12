# -*- coding: utf-8 -*-


import os

from app_factory.factory import AppZeroFactory


@auth.requires_login()
def index():
    api_list = []

    badge_mapping = {
        "GET": "primary",
        "POST": "info",
        "PUT": "warning",
        "DELETE": "danger",
    }

    example_mapping = {
        "GET": "/api/template/<id>?api_name={api_name}",
        "POST": "/api/template?api_name={api_name}",
        "PUT": "/api/template/<id>?api_name={api_name}",
        "DELETE": "/api/template/<id>?api_name={api_name}",
    }

    request_mapping = {}
    response_mapping = {}
    model_data = AppZeroFactory(layer="model", component="dal", db=db).build().data

    for each in os.listdir(os.path.join(request.folder, "static", "json", "api")):
        if each.endswith(".json"):
            api_name = each.split(".json")[0]
            api_data = (
                AppZeroFactory(layer="api", component=api_name, db=db).build().data
            )
            api_list.append(api_data)
            for table in model_data:
                if table["table_name"] == api_data["table_name"]:
                    data_body = {
                        x["field_name"]: "<{}>".format(x["field_type"])
                        for x in table["table_fields"]
                        if x["field_name"] in api_data["GET"]["selectors"]
                    }

                    request_mapping[api_name] = {}
                    request_mapping[api_name]["GET"] = {
                        "Argument (Optional)": "<id>",
                        "Searchable Parameters": api_data["GET"]["queryable_fields"],
                    }
                    request_mapping[api_name]["POST"] = {
                        "Body": data_body,
                    }
                    request_mapping[api_name]["PUT"] = {
                        "Argument": "<id>",
                        "Body": data_body,
                    }
                    request_mapping[api_name]["DELETE"] = {
                        "Argument": "<id>",
                    }

                    response_mapping[api_name] = {}
                    response_mapping[api_name]["GET"] = data_body
                    response_mapping[api_name]["POST"] = "<id>"
                    response_mapping[api_name]["PUT"] = "<id>"
                    response_mapping[api_name]["DELETE"] = "<id>"
                    continue

    return dict(
        api_list=api_list,
        badge_mapping=badge_mapping,
        example_mapping=example_mapping,
        request_mapping=request_mapping,
        response_mapping=response_mapping,
    )
