# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Periodic task, wifi management, get wan_ip, synchronize time """
import gc
import uasyncio
from server.server import ServerConfig, Server
import wifi
from tools import lang, awake, tasking, watchdog, info, system, support

async def periodic_task():
	""" Periodic task """
	periodic = Periodic()
	await tasking.task_monitoring(periodic.task)

class Periodic:
	""" Class to manage periodic task """
	def __init__(self):
		""" Constructor """
		self.server_config = ServerConfig()
		self.server_config.load()
		self.get_login_state = None
		self.last_success_notification = None
		self.current_time = 0
		watchdog.WatchDog.start(watchdog.SHORT_WATCH_DOG)

	async def check_login(self):
		""" Inform that login detected """
		# Login state not yet get
		if self.get_login_state is None:
			from server.user import User
			self.get_login_state = User.get_login_state

		# Get login state
		login =  self.get_login_state()

		# If login detected
		if login is not None:
			from server.notifier import Notifier
			if login:
				if self.last_success_notification is None:
					notif = True
					self.last_success_notification = self.current_time
				elif self.last_success_notification + 5*60 < self.current_time:
					self.last_success_notification = self.current_time
					notif = True
				else:
					notif = False
				if notif:
					Notifier.notify(lang.login_success_detected, display=False, enabled=self.server_config.notify)
			else:
				Notifier.notify(lang.login_failed_detected,  display=False, enabled=self.server_config.notify)

	async def task(self):
		""" Periodic task method """
		if support.battery():
			from tools import battery

		polling_id = 0

		watchdog.WatchDog.start(watchdog.SHORT_WATCH_DOG)
		while True:
			# Reload server config if changed
			if polling_id % 5 == 0:
				# Manage login user
				await self.check_login()

				if self.server_config.is_changed():
					self.server_config.load()

			# Manage server
			await Server.manage(polling_id)

			# Manage awake duration
			awake.Awake.manage()

			# Reset brownout counter if wifi connected
			if wifi.Wifi.is_wan_connected():
				if support.battery():
					battery.Battery.reset_brownout()

			# Periodic garbage to avoid memory fragmentation
			if polling_id % 7 == 0:
				gc.collect()
				try:
					# pylint:disable=no-member
					gc.threshold(gc.mem_free() // 5 + gc.mem_alloc())
				except:
					pass

			# Check if any problems have occurred and if a reboot is needed
			if polling_id % 3607 == 0:
				if info.get_issues_counter() > 15:
					system.reboot("Reboot required, %d problems detected"%info.get_issues_counter())

			# Reset watch dog
			watchdog.WatchDog.feed()
			await uasyncio.sleep(1)
			polling_id += 1
			self.current_time += 1
