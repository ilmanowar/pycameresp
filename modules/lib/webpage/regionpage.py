# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the date time and language """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import main_frame, manage_default_button
from tools             import lang, region

@HttpServer.add_route(b'/region', menu=lang.menu_account, item=lang.item_region)
async def region_page(request, response, args):
	""" Function define the web page to manage lang and time """
	config = region.RegionConfig.get()
	disabled, action, submit = manage_default_button(request, config)
	langages = []

	for langage in [b"english",b"french"]:
		if config.lang == langage:
			selected = b"selected"
		else:
			selected = b""
		langages.append(Option(text=langage, selected=selected, value=langage))

	if action == b"save":
		config.save()
		alert = AlertError(text=lang.taken_into_account)
	else:
		alert = None

	page = main_frame(request, response, args, lang.region_configuration,
		Form([
			Edit  (text=lang.utc_offset             , name=b"offset_time",pattern=b"-*[0-9]*[0-9]", placeholder=lang.offset_time_to,        value=b"%d"%config.offset_time,       disabled=disabled),
			Switch(text=lang.daylight_saving_time   , name=b"dst"       ,checked=config.dst,    disabled=disabled),
			Label(text=lang.language),
			Select(langages,name=b"lang", disabled=disabled), submit, alert
		]))
	await response.send_page(page)
