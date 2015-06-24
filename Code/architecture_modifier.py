'''
Created 28 April 2015

@author: Morten Chabert Eskesen
'''

from parsing import NetlistParser
from scheduling import ListScheduler, NoScheduleFoundError
from application import Application
from architecture import Architecture, Component, Connection
from random import randint
import random
import math

'''
The architecture modifier class
Is a superclass
Contains:
All the moves
The architecture evaluation 
'''
class ArchitectureModifier(object):
	'''
	Initializes everything needed for the moves and evaluation
	'''
	def __init__(self, architecture, application, faultscenarios, config):
		self.architecture = architecture
		self.faultscenarios = faultscenarios
		self.application = application
		self.config = config
		self.application_deadline = config['deadline']
		self.average_connection_time = config['average_connection_time']
		self.architecture.average_connection_time = self.average_connection_time
		self.ftcomponent_move = 'ftcomponent'
		self.non_ftcomponent_move = 'non ftcomponent'

		self.add_connection_move = 'add connection'
		self.remove_connection_move = 'remove connection'

		self.add_component_move = 'add component'
		self.remove_component_move = 'remove component'
		self.components_added = list()
		self.connections_added = list()
		self.possible_moves = set()
		self.possible_moves.add(self.ftcomponent_move)
		self.possible_moves.add(self.add_connection_move)
		self.possible_moves.add(self.add_component_move)

		self.last_ftcomponent_replaced = None
		self.last_nonftcomponent_replaced = None
		self.last_component_added = None
		self.component_added_switch_added = {}
		self.component_added_modified_connections = {}
		self.last_connection_added = None
		self.last_connection_removed = None
		self.last_component_removed = None
		self.made_redundant = list()
		self.redundant_to = {}
		self.last_component_removed_added_connections = None
		self.last_component_removed_connections = None
		self.last_move_removed_ftcomp = None, None
		self.last_move = None
		self.last_switch_modify_change = None
		self.switch_to_modified_connection = {}

		self.component_type_to_numbers = {}


		self.ftcomponents_replaced = {}
		self.ftcomponents_unreplaced = {}

		self.fault_tolerant_weight = 10000
		self.schedulable_weight = 5000

		self.max_in_connections_for_components = {	'mixer': 2,
													'input': 0,
													'output': 1, 
													'filter': 2,
													'switch': 4,
													'detector': 2,
													'seperator': 2,
													'storage': 2,
													'heater': 2}

		self.max_out_connections_for_components = {	'mixer': 2,
													'input': 1,
													'output': 0,
													'filter': 2,
													'switch': 4,
													'detector': 2,
													'seperator': 2,
													'storage': 2,
													'heater': 2}

	'''
	Reset all the tracking methods
	'''
	def reset(self):
		self.components_added = list()
		#self.ftcomponents_added = list()
		self.connections_added = list()
		#self.moves = list()
		self.possible_moves = set()
		self.possible_moves.add(self.ftcomponent_move)
		self.possible_moves.add(self.add_connection_move)
		self.possible_moves.add(self.add_component_move)

		#self.moves.append('non ftcomponent')
		#self.moves.append('ftcomponent')
		#self.moves.append('remove component')
		#self.moves.append('add component')
		#self.moves.append('remove connection')
		#self.moves.append('add connection')

		self.last_ftcomponent_replaced = None
		self.last_nonftcomponent_replaced = None
		self.last_component_added = None
		#self.last_component_connections_added = None, None
		self.component_added_switch_added = {}
		self.component_added_modified_connections = {}
		#self.last_component_switch_added = None, None
		#self.last_component_added_modified_connections = None, None
		self.last_connection_added = None
		self.last_connection_removed = None
		self.last_component_removed = None
		self.made_redundant = list()
		self.redundant_to = {}
		self.last_component_removed_added_connections = None
		self.last_component_removed_connections = None
		self.last_move_removed_ftcomp = None, None
		self.last_move = None
		self.switch_to_modified_connection = {}

		self.last_switch_modify_change = None
		self.component_type_to_numbers = {}


		self.ftcomponents_replaced = {}
		self.ftcomponents_unreplaced = {}

	
	'''
	Add all faults in a fault scenario to the architecture
	'''
	def add_fault_scenario_to_architecture(self, faultscenario, architecture):
		for f in faultscenario.faults:
			architecture.add_fault(f)

	'''
	Restore the architecture from a fault scenario
	'''
	def restore_architecture_from_fault_scenario(self, architecture):
		architecture.restore()

	'''
	Undo the last move made
	'''
	def undo_last_move(self, architecture):
		if self.last_move == self.non_ftcomponent_move:
			#Convert the component back to its fault tolerant type
			component = self.last_nonftcomponent_replaced
			ftcomp = architecture.component_library.get_faulttolerance_version_of_component(component)
			component.type = ftcomp.type
			self.possible_moves.add(self.ftcomponent_move)
			self.last_move = None

		elif self.last_move == self.ftcomponent_move:
			#Convert the component back to its non fault tolerant type
			ftcomp = self.last_ftcomponent_replaced
			comp = architecture.component_library.get_non_faulttolerance_version_of_component(ftcomp)
			ftcomp.type = comp.type
			self.possible_moves.add(self.non_ftcomponent_move)
			self.last_move = None

		elif self.last_move == self.remove_component_move:
			#Addthe last component removed
			comp = self.last_component_removed
			architecture.add_component(comp)
			if comp in self.redundant_to:
				red_c = self.redundant_to[comp]
				self.made_redundant.append(red_c)

			if comp in self.switch_to_modified_connection:
				architecture.remove_added_connection(self.switch_to_modified_connection[comp])

			if comp in self.component_added_switch_added:
				switches = self.component_added_switch_added[comp]
			else:
				switches = None, None
			if comp in self.component_added_modified_connections:
				connections = self.component_added_modified_connections[comp]
			else:
				connections = None, None

			if switches[1] != None:
				if switches[1] in self.components_added:
					self.components_added.remove(switches[1])
				else:
					architecture.add_component(switches[1])
				if switches[0] in self.components_added:
					self.components_added.remove(switches[0])
				else:
					architecture.add_component(switches[0])
			elif switches[0] != None:
				if switches[0] in self.components_added:
					self.components_added.remove(switches[0])
				else:
					architecture.add_component(switches[0])


			if self.last_component_removed_added_connections != None:
				for each in self.last_component_removed_added_connections:
					self.connections_added.append(each)
			for each in self.last_component_removed_connections:
				architecture.add_connection(each)
			self.components_added.append(comp)

			if self.last_move_removed_ftcomp[0] != None and self.last_move_removed_ftcomp[1] != None:
				self.ftcomponents_replaced[self.last_move_removed_ftcomp[0]] = self.last_move_removed_ftcomp[1]
				self.last_move_removed_ftcomp = None, None

			self.possible_moves.add(self.add_component_move)
			self.last_connection_removed_connections = None
			self.last_component_removed_added_connections = None
			self.last_move = None

		elif self.last_move == self.add_component_move:
			#Remove the last component added
			comp = self.last_component_added
			self.components_added.remove(comp)
			if comp in self.redundant_to:
				red_c = self.redundant_to[comp]
				self.made_redundant.remove(red_c)
			architecture.remove_added_component(comp)

			if comp in self.component_added_switch_added:
				switches = self.component_added_switch_added[comp]
			else:
				switches = None, None
			if comp in self.component_added_modified_connections:
				connections = self.component_added_modified_connections[comp]
			else:
				connections = None, None

			if switches[1] != None:
				architecture.remove_added_component(switches[1])
				architecture.remove_added_component(switches[0])
			elif switches[0] != None:
				architecture.remove_added_component(switches[0])

			self.component_added_switch_added.pop(comp)
			
			if connections[1] != None:
				architecture.add_connection(connections[0])
				architecture.add_connection(connections[1])
			elif connections[0] != None:
				architecture.add_connection(connections[0])

			self.component_added_modified_connections.pop(comp)
			self.possible_moves.add(self.remove_component_move)
			self.last_move = None

		elif self.last_move == self.remove_connection_move:
			#Add the last connection removed
			con = self.last_connection_removed
			architecture.add_connection(con)
			self.connections_added.append(con)
			self.possible_moves.add(self.add_connection_move)
			self.last_move = None

		elif self.last_move == self.add_connection_move:
			#Remove the last connection added
			con = self.last_connection_added
			self.connections_added.remove(con)
			architecture.remove_added_connection(con)
			self.possible_moves.add(self.remove_connection_move)
			self.last_move = None

		else:
			#Should not be possible
			pass

	
	'''
	Run all the fault scenarios on the architecture and check connectivity and schedulability
	Record the successes and non successes
	'''
	def run_all_faultscenarios_on_architecture(self, architecture, faultscenarios):
		tolerated_fs = 0
		not_tolerated_fs = 0
		schedulable_sum = 0
		fault_tolerant_sum = 0
		for fs in faultscenarios:
			self.add_fault_scenario_to_architecture(fs, architecture)

			non_ft = self.is_architecture_non_fault_tolerant(architecture)
			app_time = self.application_finish_time(architecture)

			if non_ft > 0 or app_time > 0:
				#Record untolerated fault scenario
				not_tolerated_fs += 1
			else:
				#Record tolerated fault scenario
				tolerated_fs += 1

			self.restore_architecture_from_fault_scenario(architecture)
			self.application.unschedule()
			architecture.unschedule()

		return tolerated_fs, not_tolerated_fs

	'''
	Evaluate the architecture
	'''
	def evaluate_architecture(self, architecture):
		schedulable_sum = 0
		fault_tolerant_sum = 0
		for fs in self.faultscenarios:
			self.add_fault_scenario_to_architecture(fs, architecture)
			fault_tolerant_sum += self.is_architecture_non_fault_tolerant(architecture)
			schedulable_sum += self.application_finish_time(architecture)
			self.restore_architecture_from_fault_scenario(architecture)
			self.application.unschedule()
			architecture.unschedule()

		schedulable_sum = schedulable_sum * self.schedulable_weight
		fault_tolerant_sum = fault_tolerant_sum * self.fault_tolerant_weight
		architecture_cost = architecture.number_of_valves() + architecture.number_of_connections()

		return fault_tolerant_sum + schedulable_sum + architecture_cost

	
	'''
	Is the architecture not connected?
	Returns 0 if the architecture is connected and 1 if it is
	'''
	def is_architecture_non_fault_tolerant(self, architecture):
		return 0 if architecture.is_connected() else 1

	
	'''
	What is the finish time of the application?
	0 => the application can finish within its deadline
	> 0 => the application cannot be scheduled or finishes after its deadline
	'''
	def application_finish_time(self, architecture):
		s = ListScheduler(self.application, architecture, self.average_connection_time)
		applicationtime = 0
		try:
			s.schedule_application()
			applicationtime = self.application.sink.finish_time
		except NoScheduleFoundError:
			applicationtime = self.application_deadline * 2
		returnvalue = max(0, applicationtime - self.application_deadline)
		return returnvalue

	
	'''
	Convert random component to its fault tolerant version
	'''
	def make_random_component_fault_tolerant(self, architecture):
		types = architecture.component_library.get_types_with_a_fault_tolerant_version()

		allcomps = list(architecture.components) + list(architecture.components_removed)
		comptypes = list(filter(lambda c: not c.is_fault_tolerant() and c.type in types, allcomps))

		if comptypes:
			component = random.choice(comptypes)
		else:
			component = None

		if component is not None:
			self.make_component_fault_tolerant(component, architecture)
			if len(comptypes) == 1:
				self.possible_moves.discard(self.ftcomponent_move)
			return True
		else:
			return False

	'''
	Convert the component to its fault tolerant version
	'''
	def make_component_fault_tolerant(self, component, architecture):
		ftcomp = architecture.component_library.get_faulttolerance_version_of_component(component)
		
		component.type = ftcomp.type
		self.last_ftcomponent_replaced = component
		self.possible_moves.add(self.non_ftcomponent_move)
		self.last_move = self.ftcomponent_move

	
	'''
	Convert random component to its regular version
	'''
	def make_random_component_non_fault_tolerant(self, architecture):
		ftcomps = list(filter(lambda c: c.is_fault_tolerant(), architecture.components))
		if ftcomps:
			comp = random.choice(ftcomps)
			self.make_component_non_fault_tolerant(comp, architecture)
			if len(ftcomps) == 1:
				self.possible_moves.discard(self.non_ftcomponent_move)
			return True
		else:
			return False

	'''
	Convert the component to its regular version
	'''
	def make_component_non_fault_tolerant(self, component, architecture):
		comp = architecture.component_library.get_non_faulttolerance_version_of_component(component)
		component.type = comp.type
		
		self.last_nonftcomponent_replaced = component
		self.last_move = self.non_ftcomponent_move
		self.possible_moves.add(self.ftcomponent_move)

	'''
	Add connection between two random components
	'''
	def add_connection_between_two_random_components(self, architecture):
		pos_out_comps = list(filter(lambda c: c.total_out_connections() < self.max_out_connections_for_components[c.get_type()], architecture.components))
		pos_in_comps = list(filter(lambda c: c.total_in_connections() < self.max_in_connections_for_components[c.get_type()], architecture.components)) 

		if pos_out_comps and pos_in_comps:
			to_c = random.choice(pos_in_comps)
			from_c = random.choice(pos_out_comps)
			while from_c == to_c:
				if len(pos_in_comps) == 1 and len(pos_out_comps) == 1:
					return False
				from_c = random.choice(pos_out_comps)
				to_c = random.choice(pos_in_comps)
			self.add_connection_between_two_components(from_c, to_c, architecture)
			if len(pos_out_comps) == 1 or len(pos_in_comps) == 1:
				self.possible_moves.discard(self.add_connection_move)
			return True
		else:
			return False

	'''
	Add connection between the two specified components
	'''
	def add_connection_between_two_components(self, from_c, to_c, architecture):
		name = 'add-con-{}-{}'.format(from_c.id, to_c.id)
		con = Connection(name, from_c, to_c)
		
		architecture.add_connection(con)
		self.connections_added.append(con)
		self.last_connection_added = con
		self.possible_moves.add(self.remove_connection_move)
		self.last_move = self.add_connection_move

	'''
	Add component to make a random component redundant
	'''
	def insert_component_to_make_random_component_redundant(self, architecture):
		allcomps = list(architecture.components) + list(architecture.components_removed)
		pos_comps = list(filter(lambda c: c not in self.made_redundant and c not in self.components_added and c.type[:6] != 'switch' and c.type[:5] != 'input' and c.type[:6] != 'output', allcomps))
		
		if pos_comps:
			component = random.choice(pos_comps)
			num = randint(1, 100000)
			try:
				while num in self.component_type_to_numbers[component.get_type()]:
					num = randint(1, 100000)

				self.component_type_to_numbers[component.get_type()].append(num)
			except KeyError:
				self.component_type_to_numbers[component.get_type()] = list()
				self.component_type_to_numbers[component.get_type()].append(num)

			self.made_redundant.append(component)
			componenttype = component.type
			componentid = 'added ' + str(component.type) + '-' + str(num)
			new_component = Component(componentid, componenttype)
			self.redundant_to[new_component] = component
			self.insert_redundant_component(new_component, architecture)
			return True
		else:
			return False

	'''
	Add redundant component
	'''
	def insert_redundant_component(self, new_component, architecture):
		switches = architecture.find_two_available_switches()
		if switches[0] == None and switches[1] == None:
			#Add new switches and all their connections
			cons = architecture.find_connections_between_two_switches(2)
			if cons[0] != None and cons[1] != None:
				num1 = randint(1, 100000)
				try:
					while num1 in self.component_type_to_numbers['switch']:
						num1 = randint(1, 100000)
					self.component_type_to_numbers['switch'].append(num1)
				except KeyError:
					self.component_type_to_numbers['switch'] = list()
					self.component_type_to_numbers['switch'].append(num1)
				num2 = randint(1, 100000)
				try:
					while num2 in self.component_type_to_numbers['switch']:
						num2 = randint(1, 100000)
					self.component_type_to_numbers['switch'].append(num2)
				except KeyError:
					self.component_type_to_numbers['switch'] = list()
					self.component_type_to_numbers['switch'].append(num2)
				
				switch1id = 'switch-' + str(num1)
				new_switch1 = Component(switch1id, 'switch')
				
				switch2id = 'switch-' + str(num2)
				new_switch2 = Component(switch2id, 'switch')
				architecture.add_component(new_switch1)
				architecture.add_component(new_switch2)

				self.component_added_modified_connections[new_component] = cons[0], cons[1]

				architecture.modify_connection_to_have_comp_in_middle(cons[0], new_switch1)
				architecture.modify_connection_to_have_comp_in_middle(cons[1], new_switch2)

				architecture.add_component(new_component)
				con1name = 'con-{}-{}'.format(new_switch1.id, new_component.id)
				con1 = Connection(con1name, new_switch1, new_component)

				con2name = 'con-{}-{}'.format(new_component.id, new_switch2.id)
				con2 = Connection(con2name, new_component, new_switch2)
				architecture.add_connection(con1)
				architecture.add_connection(con2)
				self.component_added_switch_added[new_component] = new_switch1, new_switch2

		elif switches[1] == None:
			#Only one switch available
			con = architecture.find_connections_between_two_switches(1)
			if con != None:
				#Add a new switch and have it as middle point between the two component of this connection
				num1 = randint(1, 100000)
				try:
					while num1 in self.component_type_to_numbers['switch']:
						num1 = randint(1, 100000)
					self.component_type_to_numbers['switch'].append(num1)
				except KeyError:
					self.component_type_to_numbers['switch'] = list()
					self.component_type_to_numbers['switch'].append(num1)
				l = architecture.types_to_components['switch']
				
				switchid = 'switch-' + str(num1)
				new_switch = Component(switchid, 'switch')
				architecture.add_component(new_switch)
				
				self.component_added_modified_connections[new_component] = con, None
				architecture.modify_connection_to_have_comp_in_middle(con, new_switch)

				architecture.add_component(new_component)
				con1name = 'con-{}-{}'.format(switches[0].id, new_component.id)
				con1 = Connection(con1name, switches[0], new_component)

				con2name = 'con-{}-{}'.format(new_component.id, new_switch.id)
				con2 = Connection(con2name, new_component, new_switch)
				architecture.add_connection(con1)
				architecture.add_connection(con2)

				self.component_added_switch_added[new_component] = new_switch, None
		else:
			#Two switches available
			architecture.add_component(new_component)
			con1name = 'con-{}-{}'.format(switches[0].id, new_component.id)
			con1 = Connection(con1name, switches[0], new_component)
			con2name = 'con-{}-{}'.format(new_component.id, switches[1])
			con2 = Connection(con2name, new_component, switches[1])
			architecture.add_connection(con1)
			architecture.add_connection(con2)

			self.component_added_switch_added[new_component] = None, None
			self.component_added_modified_connections[new_component] = None, None

		self.components_added.append(new_component)
		self.last_component_added = new_component
		self.possible_moves.add(self.remove_component_move)
		self.last_move = self.add_component_move

		if not new_component.is_fault_tolerant():
			self.possible_moves.add(self.ftcomponent_move)

	'''
	Remove random redundant connection
	'''
	def remove_random_connection(self, architecture):
		if self.connections_added:
			con = random.choice(self.connections_added)
			self.remove_connection(con, architecture)
			return True
		else:
			return False

	
	'''
	Remove the connection
	'''
	def remove_connection(self, con, architecture):
		self.connections_added.remove(con)
		architecture.remove_added_connection(con)
		self.last_connection_removed = con
		if not self.connections_added:
			self.possible_moves.discard(self.remove_connection_move)
		self.last_move = self.remove_connection_move
		self.possible_moves.add(self.add_connection_move)

	
	'''
	Remove random redundant component
	'''
	def remove_random_component(self, architecture):
		if self.components_added:
			comp = random.choice(self.components_added)
			if self.remove_component(comp, architecture):
				return True
			else:
				return False
		else:
			return False

	'''
	Remove the component
	'''
	def remove_component(self, comp, architecture):
		self.components_added.remove(comp)
		if comp in self.redundant_to:
				red_c = self.redundant_to[comp]
				self.made_redundant.remove(red_c)
		
		self.last_component_removed_connections = set(comp.out_connections.values()) | set(comp.in_connections.values())
		self.last_component_removed_added_connections = set(filter(lambda c: c in self.connections_added, self.last_component_removed_connections))
		
		if comp in self.component_added_switch_added:
			switches = self.component_added_switch_added[comp]
		else:
			switches = None, None
		if comp in self.component_added_modified_connections:
			connections = self.component_added_modified_connections[comp]
		else:
			connections = None, None
		
		if switches[1] != None:
			switch1_con = set(switches[1].out_connections.values()) | set(switches[1].in_connections.values())
			switch0_con = set(switches[0].out_connections.values()) | set(switches[0].in_connections.values())
			switch0_c = set(filter(lambda c: c.get_other_component(switches[0]) != connections[0].components[0] and c.get_other_component(switches[0]) != connections[0].components[1] and c.get_other_component(switches[0]) != comp, switch0_con))
			switch1_c = set(filter(lambda c: c.get_other_component(switches[1]) != connections[1].components[0] and c.get_other_component(switches[1]) != connections[1].components[1] and c.get_other_component(switches[1]) != comp, switch1_con))

			if len(switch0_c) == 0:
				architecture.remove_added_component(switches[0])
				
				if connections[0].components[0] in architecture.components and connections[0].components[1] in architecture.components:
					architecture.add_connection(connections[0])
			else:
				self.components_added.append(switches[0])
				self.switch_to_modified_connection[switches[0]] = connections[0]

			if len(switch1_c) == 0:
				architecture.remove_added_component(switches[1])
				if connections[1].components[1] in architecture.components and connections[1].components[1] in architecture.components:
					architecture.add_connection(connections[1])
			else:
				self.components_added.append(switches[1])
				self.switch_to_modified_connection[switches[1]] = connections[1]

		elif switches[0] != None:
			switch0_con = set(switches[0].out_connections.values()) | set(switches[0].in_connections.values())
			switch0_c = set(filter(lambda c: c.get_other_component(switches[0]) != connections[0].components[0] and c.get_other_component(switches[0]) != connections[0].components[1] and c.get_other_component(switches[0]) != comp, switch0_con))
			if len(switch0_c) == 0:
				architecture.remove_added_component(switches[0])
				if connections[0].components[0] in architecture.components and connections[0].components[1] in architecture.components:
					architecture.add_connection(connections[0])
			else:
				self.components_added.append(switches[0])
				self.switch_to_modified_connection[switches[0]] = connections[0]
		else:
			pass

		if comp.get_type() == 'switch':
			cons = list(filter(lambda d: d.components[1] == comp or d.components[0] == comp, self.switch_to_modified_connection.values()))
			if any(c.get_other_component(comp) in architecture.components for c in cons):
				#This switch should not be removed
				return False

		architecture.remove_added_component(comp)
		self.last_component_removed = comp
		if comp in self.switch_to_modified_connection:
			architecture.add_connection(self.switch_to_modified_connection[comp])

		if len(self.last_component_removed_added_connections) > 0:
			for each in self.last_component_removed_added_connections:
				self.connections_added.remove(each)
		else:
			self.last_component_removed_added_connections = None
		if comp in self.ftcomponents_replaced.keys():
			comprep = self.ftcomponents_replaced[comp]
			self.ftcomponents_replaced.pop(comp)
			self.last_move_removed_ftcomp = comp, comprep
		else:
			self.last_move_removed_ftcomp = None, None
		if not self.components_added:
			self.possible_moves.discard(self.remove_component_move)
		self.last_move = self.remove_component_move
		self.possible_moves.add(self.add_component_move)
		return True

'''
The implementation of Simulated Annealing
'''
class SimulatedAnnealing(ArchitectureModifier):
	'''
	Set all the initial values of simulated annealing
	'''
	def __init__(self, architecture, application, faultscenarios, config):
		super().__init__(architecture, application, faultscenarios, config)
		try:
			self.sa_data = config['simulated_annealing']
			self.temp_data = self.sa_data['temperature']

			self.temperature = self.temp_data['initial_value']
			self.temperature_reduction_rate = self.temp_data['reduction_rate']

			self.termination_temperature = self.sa_data['termination']
			self.steps_in_iteration = self.sa_data['iterations']
		except KeyError:
			self.temperature = 10000
			self.termination_temperature = 0.1
			self.steps_in_iteration = 1
			self.temperature_reduction_rate = 0.999

		self.initial_cost = 0
		self.cost = 0
		self.run()

	'''
	Reduce the temperature
	'''
	def reduce_temperature(self, temp):
		return temp * self.temperature_reduction_rate

	'''
	Run the algorithm
	'''
	def run(self):
		self.initial_cost = self.evaluate_architecture(self.architecture)
		self.cost = self.initial_cost
		print('Inital cost: '+str(self.cost))
		while not self.terminated():
			self.iterations()
			t = str(self.temperature)
			c = str(self.cost)
			print('Temperature: '+t + ' - cost: '+c)
			self.temperature = self.reduce_temperature(self.temperature)

	'''
	Perform the iterations in the while loop
	'''
	def iterations(self):
		for _ in range(self.steps_in_iteration):
			success = self.perform_random_move(self.architecture)
			if not success:
				continue
			newcost = self.evaluate_architecture(self.architecture)
			if self.acceptance_probability(self.cost, newcost) > random.random():
				print('New arch accepted')
				self.cost = newcost
			else:
				print('New arch is not accepted')
				self.undo_last_move(self.architecture)

	
	'''
	The probability of acceptance
	'''
	def acceptance_probability(self, oldcost, newcost):
		if newcost < oldcost:
			return 1.0
		else:
			delta = newcost - oldcost
			print('Calculating: ('+str(newcost)+' - '+str(oldcost) + ') / '+str(self.temperature))
		return math.exp(-delta / self.temperature)
	
	'''
	Should the algorithm be terminated?
	'''
	def terminated(self):
		if self.termination_temperature >= self.temperature:
			return True
		else:
			return False

	'''
	Choose and apply a random move
	'''
	def perform_random_move(self, architecture):
		moves = random.sample(self.possible_moves, 1)
		ret = self.perform_move(moves[0], architecture)
		return ret

	'''
	Apply the specified move
	'''
	def perform_move(self, move, architecture):
		if move == self.non_ftcomponent_move:
			ret = self.make_random_component_non_fault_tolerant(architecture)
			return ret

		if move == self.ftcomponent_move:
			ret = self.make_random_component_fault_tolerant(architecture)
			return ret

		if move == self.remove_component_move:
			ret = self.remove_random_component(architecture)
			return ret

		if move == self.add_component_move:
			ret = self.insert_component_to_make_random_component_redundant(architecture)
			return ret

		if move == self.remove_connection_move:
			ret = self.remove_random_connection(architecture)
			return ret

		if move == self.add_connection_move:
			ret = self.add_connection_between_two_random_components(architecture)
			return ret

'''
The implementation of GRASP
'''
class GreedilyRandomAdaptiveSearchProcedure(ArchitectureModifier):
	'''
	Set all the initial values of GRASP
	'''
	def __init__(self, architecture, application, faultscenarios, config, architecture_file, componentlibraryparser):
		super().__init__(architecture, application, faultscenarios, config)
		self.componentlibraryparser = componentlibraryparser
		self.architecture_file = architecture_file
		
		try:
			self.grasp_data = config['grasp']
			self.number_of_iterations = self.grasp_data['iterations']
			self.local_search_iterations = self.grasp_data['local_search_iterations']
			self.c = self.grasp_data['cl_size']
			self.increase_c = self.grasp_data['increase_cl_size']
			self.max_number_of_iterations_before_increasing_c = self.grasp_data['unsuccesful_iterations_before_increasing_cl']
		except KeyError:
			self.number_of_iterations = 50
			self.local_search_iterations = 50
			self.max_number_of_iterations_before_increasing_c = 5
			self.c = 2
			self.increase_c = 2

		self.number_of_unsuccesful_iterations = 0
		self.best_architecture = architecture
		self.initial_cost = self.evaluate_architecture(self.best_architecture)
		self.best_cost = self.initial_cost

		self.make_redundant = 'redundant component'
		self.make_ftcomponent = 'ftcomponent'
		self.make_ftcomponent_with_in_con = 'ftcomponent with in connection'
		self.make_ftcomponent_with_out_con = 'ftcomponent with out connection'
		self.make_ftcomponent_with_both_con = 'ftcomponent with both connections'
		self.design_transformations = set()
		self.create_design_transformations()
		self.component_transformation = {}
		self.components_ranked = False
		self.run()


	
	'''
	Create the design transformations of GRASP (the special 5 on the RCL)
	'''
	def create_design_transformations(self):
		self.design_transformations.add(self.make_redundant)
		self.design_transformations.add(self.make_ftcomponent)
		self.design_transformations.add(self.make_ftcomponent_with_in_con)
		self.design_transformations.add(self.make_ftcomponent_with_out_con)
		self.design_transformations.add(self.make_ftcomponent_with_both_con)

	'''
	Apply all the design transformations on RCL
	'''
	def apply_design_transformations(self, architecture):
		for c in self.component_transformation:
			self.apply_single_design_transformation(c, self.component_transformation[c], architecture)

	'''
	Apply a single design transformation
	'''
	def apply_single_design_transformation(self, component, transformation, architecture):
		if transformation == self.make_redundant:
			num = randint(1, 1000)
			try:
				while num in self.component_type_to_numbers[component.get_type()]:
					num = randint(1, 1000)

				self.component_type_to_numbers[component.get_type()].append(num)
			except KeyError:
				self.component_type_to_numbers[component.get_type()] = list()
				self.component_type_to_numbers[component.get_type()].append(num)


			self.made_redundant.append(component)
			componenttype = component.type
			componentid = 'added ' + str(component.type) + '-' + str(num)
			new_component = Component(componentid, componenttype)
			self.redundant_to[new_component] = component

			self.insert_redundant_component(new_component, architecture)

		elif transformation == self.make_ftcomponent:
			self.make_component_fault_tolerant(component, architecture)

		elif transformation == self.make_ftcomponent_with_out_con:
			self.make_component_fault_tolerant(component, architecture)
			ftcomp = self.last_ftcomponent_replaced
			pos_in_comps = set(filter(lambda c: c.total_in_connections() < self.max_in_connections_for_components[c.get_type()], architecture.components))
			if pos_in_comps:
				to_comp = random.sample(pos_in_comps, 1)
				to_c = to_comp[0]
				while to_c == ftcomp:
					to_comp = random.sample(pos_in_comps, 1)
					to_c = to_comp[0]

				self.add_connection_between_two_components(ftcomp, to_c, architecture)

		elif transformation == self.make_ftcomponent_with_in_con:
			self.make_component_fault_tolerant(component, architecture)
			ftcomp = self.last_ftcomponent_replaced
			pos_out_comps = set(filter(lambda c: c.total_out_connections() < self.max_out_connections_for_components[c.get_type()], architecture.components))
			if pos_out_comps:
				from_comp = random.sample(pos_out_comps, 1)
				from_c = from_comp[0]
				while from_c == ftcomp:
					from_comp = random.sample(pos_out_comps, 1)
					from_c = from_comp[0]

				self.add_connection_between_two_components(from_c, ftcomp, architecture)

		elif transformation == self.make_ftcomponent_with_both_con:
			self.make_component_fault_tolerant(component, architecture)
			#make in con and out con
			ftcomp = self.last_ftcomponent_replaced
			pos_out_comps = set(filter(lambda c: c.total_out_connections() < self.max_out_connections_for_components[c.get_type()], architecture.components))
			pos_in_comps = set(filter(lambda c: c.total_in_connections() < self.max_in_connections_for_components[c.get_type()], architecture.components))
			if pos_out_comps and pos_in_comps:
				from_comp = random.sample(pos_out_comps, 1)
				from_c = from_comp[0]
				while from_c == ftcomp:
					from_comp = random.sample(pos_out_comps, 1)
					from_c = from_comp[0]

				self.add_connection_between_two_components(from_c, ftcomp, architecture)

			if pos_in_comps:
				to_comp = random.sample(pos_in_comps, 1)
				to_c = to_comp[0]
				while to_c == ftcomp:
					to_comp = random.sample(pos_in_comps, 1)
					to_c = to_comp[0]

				self.add_connection_between_two_components(ftcomp, to_c, architecture)
		else:
			pass

	
	'''
	A middle man for choosing and apply the design transformations
	'''
	def choose_and_apply_design_transformations(self, rcl, architecture):
		for c in rcl:
			self.choose_random_design_transformation_for_component(c)

		self.apply_design_transformations(architecture)
		self.component_transformation = {}

	'''
	Randomly choose the design transformation for the RCL
	'''
	def choose_random_design_transformation_for_component(self, component):
		transformation = random.sample(self.design_transformations, 1)
		self.component_transformation[component] = transformation[0]

	'''
	Run the GRASP algorithm
	'''
	def run(self):
		i = 0
		while(i < self.number_of_iterations):
			self.reset()
			new_arch = self.load_original_architecture()
			cl = self.create_candidates(new_arch.components, self.c, new_arch)
			rcl = self.choose_candidates(cl)
			self.choose_and_apply_design_transformations(rcl, new_arch)
			previous_cost = self.evaluate_architecture(new_arch)
			new_arch_cost = self.local_search(new_arch, previous_cost)
			#new_arch_cost = self.evaluate_architecture(new_arch)
			print('Cost before: '+str(self.best_cost))
			print('New cost: '+str(new_arch_cost))
			if new_arch_cost < self.best_cost:
				print('Changing architecture')
				self.best_architecture = new_arch
				self.best_cost = new_arch_cost
				print('Cost of the newly changed architecture: '+str(self.best_cost))
				self.number_of_unsuccesful_iterations = 0
			else:
				self.number_of_unsuccesful_iterations += 1
			if self.number_of_unsuccesful_iterations >= self.max_number_of_iterations_before_increasing_c:
				self.c = self.c * self.increase_c
				self.number_of_unsuccesful_iterations = 0
			i += 1

	'''
	Load the original architecture (used in every iteration of the GRASP main loop)
	'''
	def load_original_architecture(self):
		np = NetlistParser(self.architecture_file)
		np.architecture.component_library = self.componentlibraryparser.get_component_library()
		np.parse()
		np.architecture.average_connection_time = self.average_connection_time
		return np.architecture

	'''
	Choose candidates from the CL (builds the RCL)
	'''
	def choose_candidates(self, candidatelist):
		num = randint(1, len(candidatelist))
		rcl = set(random.sample(candidatelist, num))
		return rcl

	'''
	Do local search on this architecture accepting only improving solutions
	'''
	def local_search(self, architecture, previous_cost):
		j = 0
		while j < self.local_search_iterations:
			success = self.perform_random_move(architecture)
			if not success:
				continue
			new_arch_cost = self.evaluate_architecture(architecture)
			print('New cost: ' + str(new_arch_cost))
			print('Old cost: ' + str(previous_cost))
			if new_arch_cost < previous_cost:
				print('New arch accepted')
				previous_cost = new_arch_cost
			else:
				print('New arch is not accepted')
				self.undo_last_move(architecture)
			j += 1
		print('Returning cost:' +str(previous_cost))
		return previous_cost

	'''
	Randomly choose a move and apply it (used in local search)
	'''
	def perform_random_move(self, architecture):
		moves = random.sample(self.possible_moves, 1)
		ret = self.perform_move(moves[0], architecture)
		return ret

	'''
	Apply the move
	'''
	def perform_move(self, move, architecture):
		if move == self.non_ftcomponent_move:
			ret = self.make_random_component_non_fault_tolerant(architecture)
			return ret

		if move == self.ftcomponent_move:
			ret = self.make_random_component_fault_tolerant(architecture)
			return ret

		if move == self.remove_component_move:
			ret = self.remove_random_component(architecture)
			return ret

		if move == self.add_component_move:
			ret = self.insert_component_to_make_random_component_redundant(architecture)
			return ret

		if move == self.remove_connection_move:
			ret = self.remove_random_connection(architecture)
			return ret

		if move == self.add_connection_move:
			ret = self.add_connection_between_two_random_components(architecture)
			return ret

	'''
	Rank the components according to how many fault scenarios affect the components
	'''
	def rank_components(self, components, architecture):
		comps = set(filter(lambda c: c.type[:6] != 'switch' and c.type[:5] != 'input' and c.type[:6] != 'output', components))
		for fs in self.faultscenarios:
			for c in comps:
				increased = False
				if any(f.objectname == c.id for f in fs.faults):
					c.grasp_ranking += 1
					increased = True

				if not increased:
					cons = set()
					cf = set(filter(lambda f: type(f).__name__ == 'ChannelFault' and f.objecttype == 'connection', fs.faults))
					for each in cf:
						cons.add(architecture.connection_by_name[each.objectname])

					if any(con.components[0] == c or con.components[1] == c for con in cons):
						c.grasp_ranking += 1

	'''
	Create the candidate list (CL)
	'''
	def create_candidates(self, components, amount, architecture):
		#return set of candidates (with number of components = amount)
		if not self.components_ranked:
			self.rank_components(components, architecture)
		#for each in architecture.components:
			#print(str(each) + ' grasp_ranking '+str(each.grasp_ranking))
		#list_c = list(components)
		list_c = list(filter(lambda c: c.type[:6] != 'switch' and c.type[:5] != 'input' and c.type[:6] != 'output', components))
		sorted_components = sorted(list_c, key = lambda c: c.grasp_ranking, reverse=True)
		candidates = set()
		for x in range(0,amount):
			if len(sorted_components) == 0:
				break
			candidates.add(sorted_components.pop(0))
		print(candidates)
		return candidates
