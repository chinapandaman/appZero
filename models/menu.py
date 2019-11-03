# -*- coding: utf-8 -*-

from app_factory.factory import AppZeroFactory

response.menu = [(T("Home"), False, URL("default", "index"), [])]

response.side_bar = AppZeroFactory(layer="view", component="menu", db=db).build().data
