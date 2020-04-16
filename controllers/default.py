# -*- coding: utf-8 -*-


@auth.allows_jwt()
@auth.requires_login()
def index():
    return dict()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """

    form = auth()

    if request.args[0] == "register":
        form.custom.widget.first_name["_placeholder"] = "First Name"
        form.custom.widget.last_name["_placeholder"] = "Last Name"
        form.custom.widget.password_two["_placeholder"] = "Confirm Password"

    form.custom.widget.email["_placeholder"] = "Email"
    form.custom.widget.password["_placeholder"] = "Password"

    return dict(form=form)


@cache.action()
@auth.allows_jwt()
@auth.requires_login()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


@auth.allows_jwt()
@auth.requires_login()
def jwt_dump():
    response.cookies["_token"] = ""
    response.cookies["_token"]["expires"] = 0
    response.cookies["_token"]["path"] = "/"

    redirect(URL("default", "user/logout"))
