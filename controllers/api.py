from app_factory.factory import AppZeroFactory


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

    return locals()
