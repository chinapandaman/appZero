# -*- coding: utf-8 -*-


from app_factory.factory import AppZeroFactory


@auth.requires_login()
@request.restful()
def template():
    def GET(*args, **params):
        if not params.get("api_name"):
            raise HTTP(404)

        return response.json(
            AppZeroFactory(layer="api", component=params.pop("api_name"), db=db)
            .build()
            .get(
                table_id=args[0] if len(args) else None,
                additional_query=params if params else None,
            )
        )

    def POST(*args, **params):
        if not params.get("api_name"):
            raise HTTP(404)

        return response.json(
            AppZeroFactory(layer="api", component=params.pop("api_name"), db=db)
            .build()
            .post(data=params)
        )

    def PUT(*args, **params):
        if not params.get("api_name"):
            raise HTTP(404)

        if not len(args):
            raise HTTP(400)

        return response.json(
            AppZeroFactory(layer="api", component=params.pop("api_name"), db=db)
            .build()
            .put(table_id=args[0], data=params)
        )

    def DELETE(*args, **params):
        if not params.get("api_name"):
            raise HTTP(404)

        if not len(args):
            raise HTTP(400)

        return response.json(
            AppZeroFactory(layer="api", component=params.pop("api_name"), db=db)
            .build()
            .delete(table_id=args[0])
        )

    return locals()


@auth.requires_login()
@request.restful()
def sections():
    def GET(*args, **params):
        if not len(args):
            raise HTTP(400)

        return response.json(
            AppZeroFactory(
                layer="view",
                component="section/{component}".format(component=args[0]),
                db=db,
            )
            .build()
            .data
        )

    return locals()


@auth.requires_login()
@request.restful()
def pages():
    def GET(*args, **params):
        if not len(args):
            raise HTTP(400)

        return response.json(
            AppZeroFactory(
                layer="view",
                component="page/{component}".format(component=args[0]),
                db=db,
            )
            .build()
            .data
        )

    return locals()
