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
        "GET": "/api/template?api_name={api_name}",
        "POST": "/api/template?api_name={api_name}",
        "PUT": "/api/template/<id>?api_name={api_name}",
        "DELETE": "/api/template/<id>?api_name={api_name}",
    }

    for each in os.listdir(os.path.join(request.folder, "static", "json", "api")):
        if each.endswith(".json"):
            api_list.append(
                AppZeroFactory(layer="api", component=each.split(".json")[0], db=db)
                .build()
                .data
            )

    return dict(
        api_list=api_list, badge_mapping=badge_mapping, example_mapping=example_mapping
    )
