# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Language selected and regional time """
from tools import jsonconfig

region_config = None

class RegionConfig(jsonconfig.JsonConfig):
	""" Language selected and regional time """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.lang        = b"english"
		self.offset_time  = 1
		self.dst         = True
		self.current_time = 0

	@staticmethod
	def get():
		""" Return region configuration """
		global region_config
		if region_config is None:
			region_config = RegionConfig()
			if region_config.load() is False:
				region_config.save()
		if region_config.is_changed():
			region_config.load()
		return region_config
