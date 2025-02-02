# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the wifi """
from server.httpserver        import HttpServer
from htmltemplate.htmlclasses import *
from webpage.mainpage         import main_frame, manage_default_button
import wifi
from tools                    import lang,strings,logger,support

def static_ip_html(config, disabled):
	""" Html to get static ip """
	patternIp = br"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
	return [
			Edit(text=lang.ip_address,  name=b"ip_address", pattern=patternIp, placeholder=lang.enter_ip_address, value=config.ip_address, disabled=disabled),
			Edit(text=lang.netmask,     name=b"netmask",   pattern=patternIp, placeholder=lang.enter_netmask,    value=config.netmask,   disabled=disabled),
			Edit(text=lang.gateway,     name=b"gateway",   pattern=patternIp, placeholder=lang.enter_gateway,    value=config.gateway,   disabled=disabled),
			Edit(text=lang.dns,         name=b"dns",       pattern=patternIp, placeholder=lang.enter_dns,        value=config.dns,       disabled=disabled)]

current_networks = []
current_config  = None
current_network = None

def select_network(increase=0, reparse=False):
	""" Select wifi network """
	global current_networks, current_network
	if reparse:
		current_networks = current_network.list_known()
	current = 0
	for network in current_networks:
		searched = strings.tobytes(strings.tofilename(current_network.ssid))
		if searched == network:
			break
		current += 1

	if current + increase < 0:
		current = -1
	elif current + increase >= len(current_networks):
		current = 0
	else:
		current += increase
	current_network = wifi.NetworkConfig()
	try:
		try:
			part_filename = current_networks[current]
		except:
			part_filename = b""
		current_network.load(part_filename = part_filename)
	except Exception as err:
		logger.syslog(err)
	return current_network

@HttpServer.add_route(b'/wifi', menu=lang.menu_network, item=lang.item_wifi)
async def wifi_config(request, response, args):
	""" Page to configure the wifi station """
	global current_networks, current_config, current_network

	patternDns = rb"^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$"

	if current_config is None:
		current_config = wifi.Station.config
		current_network = wifi.Station.network
		current_networks = current_network.list_known()

	config  = current_config
	network = current_network

	action  = request.params.get(b"action",b"none")
	forced  = request.params.get(b"forced",b"none")
	current = request.params.get(b"current",b"")
	dynamic = request.params.get(b"dynamic",b"1")

	disabled = False
	# If default page
	if action == b"none" and len(request.params) == 0:
		disabled = True
	# If the dynamic ip switch changed
	elif   action == b"none":
		if dynamic == b"1":
			forced = b"1"
		else:
			forced = b"0"
		action = b"change"
	# If the modify button clicked
	elif action == b"modify":
		pass
	# If the save button clicked
	elif action == b"save":
		network.update(request.params, show_error=False)
		network.save()
		network = select_network(0, True)
		config.update(request.params, show_error=False)
		config.default = network.ssid
		config.save()
		forced  = b"none"
		disabled = True
	elif action == b"previous":
		network = select_network(-1)
		forced = b"none"
	elif action == b"next":
		network = select_network(1)
		forced = b"none"
	elif action == b"forget":
		forced = b"none"
		network.forget()
		network = select_network(-1,True)
	elif action == b"default":
		config.default = strings.tostrings(network.ssid)
		config.save()
	if forced == b"none":
		dynamic = network.dynamic
	elif forced == b"1":
		dynamic = True
	else:
		dynamic = False

	ssids = []

	if action in [b"previous",b"next",b"change",b"forget",b"modify",b"default"]:
		submit = \
			Submit (text=lang.save  ,     name=b"action",  value=b"save"    ), Space(), \
			Submit (text=lang.lt ,        name=b"action",  value=b"previous"), Space(), \
			Submit (text=lang.gt ,        name=b"action",  value=b"next"    ), Space(), \
			Submit (text=lang.forget,     name=b"action",  value=b"forget"  ), Space(), \
			Submit (text=lang.set_default,name=b"action",  value=b"default" ), Space(), \
			Input  (                      name=b"forced",  value=forced     , type=b"hidden"), \
			Input  (                      name=b"current", value=current    , type=b"hidden")

		if wifi.Station.is_active() or wifi.AccessPoint().is_active():
			networks = wifi.Station.scan()
			for net in networks:
				ssids.append(Option(value=net[0]))
	else:
		submit = Submit(text=lang.modify, name=b"action", value=b"modify")

	page = main_frame(request, response, args, lang.wifi_configuration,
		Form([
			Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
			Edit(text=lang.hostname ,   name=b"hostname",  placeholder=lang.hostname_not_available, pattern=patternDns, value=config.hostname, disabled=disabled) if support.hostname() else None,
			Switch(text=lang.fallback_to_the, name=b"fallback", checked=config.fallback, disabled=disabled),
			Card(
				[
					CardHeader(text= lang.wifi if strings.tostrings(network.ssid) != strings.tostrings(config.default) else lang.wifi_default),
					CardBody([
						ComboBox(ssids, text=lang.ssid, placeholder=lang.enter_ssid,  name=b"ssid", value=network.ssid, disabled=disabled),
						Edit(text=lang.password,    name=b"wifi_password", placeholder=lang.enter_password,      type=b"password",value=network.wifi_password, disabled=disabled),
					])
				]),
			Card(
				[
					CardHeader([\
						Switch(text=lang.dynamic_ip, spacer=b"mb-0", checked=dynamic, name=b"dynamic", event=b'onchange="this.form.submit()"', disabled=disabled)]),
					None if dynamic else CardBody([\
						static_ip_html(network, disabled)])
				]),
			submit
		]))
	await response.send_page(page)

@HttpServer.add_route(b'/accesspoint', menu=lang.menu_network, item=lang.item_access_point)
async def access_point(request, response, args):
	""" Page to configure the access point """
	config = wifi.AccessPointConfig()
	disabled, action, submit = manage_default_button(request, config)
	if action == b"save":
		if wifi.AccessPoint.is_active():
			wifi.AccessPoint.config = config
	authmodes = []
	for key, value in wifi.AUTHMODE.items():
		if value==config.authmode:
			authmodes.append(Option(text=value, selected=b"selected", value=value))
		else:
			authmodes.append(Option(text=value, value=value))
	# pylint: disable=missing-parentheses-for-call-in-test
	# pylint: disable=using-constant-test
	page = main_frame(request, response, args, lang.access_point_configuration if access_point else b"Wifi configuration",
		Form([
			Switch(text=lang.activated, name=b"activated", checked=config.activated, disabled=disabled),
			Card(
				[
					CardHeader(text=lang.wifi),
					CardBody([
						Edit(text=lang.ssid, placeholder=lang.enter_ssid, name=b"ssid", value=config.ssid, disabled=disabled),
						Edit(text=lang.password,    name=b"wifi_password",type=b"password", placeholder=lang.enter_password,      value=config.wifi_password, disabled=disabled),
						Label(text=lang.authentication_mode),
						Select(authmodes,name=b"authmode", disabled=disabled),
					]),
				]),
			Card(
				[
					CardHeader(text=lang.static_ip),
					CardBody(static_ip_html(config, disabled))
				]) if support.static_ip_accesspoint() else None ,
			submit
		]))
	await response.send_page(page)
