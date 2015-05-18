'''
Created 23 March 2015

@author: Morten Chabert Eskesen
'''

import os, json

from architecture import Architecture, Component, Connection, ComponentLibrary, LibraryComponent
from application import Application, Operation, Flow
from faultmodel import FaultModel

class Parser(object):
	def __init__(self, file):
		self.file = file

	def parse(self):
		raise NotImplementedError

	def load_data(self, file):
		with open(file) as data_file:
			try:
				data = json.load(data_file)
			except ValueError as err:
				raise InvalidJSONFile('JSON error:' + str(err))
		return data


class ArchitectureParser(Parser):

	def __init__(self, file):
		super().__init__(file)

		self.architecture = Architecture()
		self.components = {}
		self.component_types = {}

		try:
			self.data = self.load_data(file)
		except FileNotFoundError as err:
			raise ArchitectureFileNotFoundError('Architecture file error: ' + str(err))

	def parse_architecture(self):
		self.architecture.id = self.data['architecture']
		self.architecture.size = self.data['width'], self.data['height']

	def parse_components(self):
		components = self.data['componentList']

		for each in components:
			componentid = each['name']
			componenttype = each['functions'][0].lower()
			#try:
			#	connections = each['connections']
			#except KeyError:
			#	connections = None

			c = Component(componentid, componenttype)
			self.add_component(c)

	def parse_connections(self):
		connections = self.data['connectionList']

		for each in connections:
			name = each['name']
			from_comp = each['sourceComponent']
			to_comp = each['sinkComponent'][0]['sinkName']

			from_c = self.components[from_comp]
			to_c = self.components[to_comp]
			self.add_connection(name, from_c, to_c)

	def parse(self):
		self.parse_architecture()
		self.parse_components()
		self.parse_connections()
		self.architecture.parsing_done()

	def add_connection(self, name, c1, c2):
		con = Connection(name,c1, c2)
		#self.architecture.connections.add(con)
		self.architecture.add_connection(con)

	def add_component(self, c):
		self.components[c.id] = c
		#self.architecture.components.add(c)
		self.architecture.add_component(c)

		try:
			self.component_types[c.type] += 1
		except KeyError:
			self.component_types[c.type] = 1

class NetlistParser(ArchitectureParser):
	def __init__(self, file):
		super().__init__(file)

	def parse(self):
		super().parse()


class ComponentLibraryParser(Parser):
	def __init__(self, file):
		super().__init__(file)

		self.componentlibrary = None

		try:
			self.data = self.load_data(file)
		except FileNotFoundError as err:
			raise ComponentLibraryFileNotFoundError('Component library file error: ' + str(err))

		self.parse()

	def get_component_library(self):
		if self.component_library:
			return self.component_library
		else:
			self.parse()
			return self.component_library

	def parse(self):
		self.component_library = ComponentLibrary()
		self.parse_componentlibrary()

	def parse_componentlibrary(self):
		componentlib = self.data['components']

		for each in componentlib:
			componenttype = each['type']
			componentsize = each['width'], each['height']
			componentvalves = each['valves']
			componnentvalveList = each['valveList']

			try:
				routingallowed = each['route']
			except KeyError:
				routingallowed = False

			try:
				faulttolerance = each['faulttolerance']
			except KeyError:
				faulttolerance = None


			libc = LibraryComponent(componenttype, componentsize, componentvalves, componnentvalveList, routingallowed, faulttolerance)
			self.component_library.add_component(libc)
			#self.component_library.librarycomponents.add(libc)

class ApplicationParser(Parser):
	def __init__(self, file):
		super().__init__(file)

		self.application = Application()
		self.operations = {}
		self.operation_types = {}

		try:
			self.data = self.load_data(file)
		except FileNotFoundError as err:
			raise ApplicationFileNotFoundError('Application file error: ' + str(err))

		self.parse()
		self.application.preprocess()

	def add_operation(self, name, operationtype, exetime, dependencies=None):
		#self.operations[o.id] = o
		#if dependencies is not None:
		#	self.application.add_operation(o, dependencies)
		#else:
		#	self.application.add_operation(o)

		o = self.application.add_operation(name, operationtype, exetime)
		self.operations[o.id] = o
		try:
			self.operation_types[operationtype] += 1
		except KeyError:
			self.operation_types[operationtype] = 1

		return o

	def parse(self):
		self.parse_application()
		self.parse_operations()

	def parse_application(self):
		self.application.id = self.data['assay']

	def parse_operations(self):
		operations = self.data['operations']
		inputs = set()
		input_binds = {}

		for each in operations:
			operationid = each['name']
			exetime = each['executionTime']
			operationtype = each['operation'].lower()
			#o = Operation(operationid, operationtype, exetime)
			o = self.add_operation(operationid, operationtype, exetime)
			try:
				component = each['component']
				if operationtype == 'input':
					input_binds[o] = component
			except KeyError:
				component = None


			try:
				#dependencies = list()
				d = each['dependencies']
				for e in d:
					amount = e['amount']
					name = e['name']
					#dep = Dependency(o, self.operations[name], amount)
					self.application.add_flow(self.operations[name],o,amount)
			except KeyError: #if no dependencies it is an input
				inputs.add(o)
		
		self.application.set_inputs(inputs, input_binds)
		self.application.preprocess()

class FaultModelParser(Parser):
	def __init__(self, file):
		super().__init__(file)

		self.faultmodel = FaultModel()
		self.faults = {}
		self.no_of_valve_fault_types = {}
		self.no_of_channel_fault_types = {}

		try:
			self.data = self.load_data(file)
		except FileNotFoundError as err:
			raise FaultModelFileNotFoundError('Fault model file error: ' + str(err))

		self.parse()
	
	def parse(self):
		self.parse_faultmodel()
		self.parse_channelfaults()
		self.parse_valvefaults()

	def parse_faultmodel(self):
		self.faultmodel.id = self.data['faultmodel']
		self.faultmodel.total_channelfaults = self.data['channelfaults']
		self.faultmodel.total_valvefaults = self.data['valvefaults']

	def parse_channelfaults(self):
		channelfaults = self.data['channelfaultList']

		for each in channelfaults:
			faultid = each['name']
			faulttype = each['fault']
			objecttype = each['objectType']
			objectname = each['objectName']
			
			self.add_channelfault(faultid, faulttype, objecttype, objectname)


	def parse_valvefaults(self):
		valvefaults = self.data['valvefaultList']

		for each in valvefaults:
			faultid = each['name']
			faulttype = each['fault']
			objecttype = each['objectType']
			objectname = each['objectName']
			control = each['control']
			affected = each['affected']
			
			self.add_valvefault(faultid, faulttype, objecttype, objectname, control, affected)

	def add_valvefault(self, faultid, faulttype, objecttype, objectname, control, affected):
		vf = self.faultmodel.add_valvefault(faultid, faulttype, objecttype, objectname, control, affected)

		self.faults[vf.id] = vf
		try:
			self.no_of_valve_fault_types[faulttype] += 1
		except KeyError:
			self.no_of_valve_fault_types[faulttype] = 1

		return vf

	def add_channelfault(self, faultid, faulttype, objecttype, objectname):
		cf = self.faultmodel.add_channelfault(faultid, faulttype, objecttype, objectname)

		self.faults[cf.id] = cf
		try:
			self.no_of_channel_fault_types[faulttype] += 1
		except KeyError:
			self.no_of_channel_fault_types[faulttype] = 1

		return cf

class ConfigParser(Parser):
	def __init__(self, file):
		super().__init__(file)

		try:
			self.data = self.load_data(file)
		except FileNotFoundError as err:
			raise ConfigFileNotFoundError('Config file error: ' + str(err))

class ArchitectureFileNotFoundError(Exception):
	pass

class ApplicationFileNotFoundError(Exception):
	pass

class ComponentLibraryFileNotFoundError(Exception):
	pass

class FaultModelFileNotFoundError(Exception):
	pass

class ConfigFileNotFoundError(Exception):
	pass