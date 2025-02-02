# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=unused-import
# pylint:disable=consider-using-f-string
""" Example of task starter """
import uasyncio
from server.httpserver import HttpServer
import pycameresp

def html_page_loader():
	""" Load html pages when connecting to http server """
	import sample.sample

def startup(loop):
	""" This function is called automatically by the starter.
	It must receive the asynchronous loop object as a parameter. """
	# Addition of the html page loader, the call will be made during the first connection to the server
	HttpServer.add_page_loader(html_page_loader)

	# Register the user task, monitor all exceptions
	pycameresp.create_user_task(loop, sample_task)

async def sample_task():
	""" Example of asynchronous task """
	# This task is protected against exceptions, if an uncaught exception occurs, this task will be automatically restarted.
	# If there are too many unhandled exceptions, the device reboots.
	# A crash trace is kept in the syslog file
	count = 0

	while True:
		print("Sample HELLO WORLD task %d"%count)
		await uasyncio.sleep(10)
		count += 1
