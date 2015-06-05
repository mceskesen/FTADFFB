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

class ArchitectureModifier(object):

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
		self.last_component_removed_added_connections = None
		self.last_component_removed_connections = None
		self.last_move_removed_ftcomp = None, None
		self.last_move = None
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
	def make_random_component_fault_tolerant(self):
		types = self.architecture.component_library.get_types_with_a_fault_tolerant_version()
		#randomtype = random.choice(types)
		allcomps = list(self.architecture.components) + list(self.architecture.components_removed)
		comptypes = list(filter(lambda c: not c.is_fault_tolerant() and c.type in types, allcomps))
		#while(randomtype not in self.architecture.types_to_components):
		#	randomtype = random.choice(comptypes)
		if comptypes:
			component = random.choice(comptypes)
		else:
			component = None
		#randomcomponents = self.architecture.types_to_components[randomtype]
		#any(type(f).__name__ == 'ChannelFault' for f in switch.faults):
		#randomcomponents = list(filter(lambda c: c.is_fault_tolerant() == False, self.architecture.types_to_components[randomtype])) 
		#component = random.choice(randomcomponents)
		if component is not None:
			ftcomp = self.architecture.component_library.get_faulttolerance_version_of_component(component)
			num = randint(1, 1000)
			try:
				while num in self.component_type_to_numbers[ftcomp.get_type()]:
					num = randint(1, 1000)

				self.component_type_to_numbers[ftcomp.get_type()].append(num)
			except KeyError:
				self.component_type_to_numbers[ftcomp.get_type()] = list()
				self.component_type_to_numbers[ftcomp.get_type()].append(num)
			#try:
			#	l = self.architecture.types_to_components[ftcomp.get_type()]
			#	num = len(l) + 1
			#except KeyError:
			#	num = 1
			componenttype = ftcomp.type
			componentid = str(ftcomp.type)+ '-' + str(num)
			new_component = Component(componentid, componenttype)
			print('Replacing: '+str(component) + ' with '+str(new_component))
			self.architecture.replace_component_with_other_component(component, new_component)
			self.ftcomponents_replaced[new_component] = component
			#if not component in self.architecture.original_components:
			#	components_added.append(new_component)
			#	components_added.remove(component)
			if component in self.components_added:
				self.components_added.append(new_component)
				self.components_added.remove(component)
			self.last_ftcomponent_replaced = new_component
			self.possible_moves.add(self.non_ftcomponent_move)
			self.last_move = self.ftcomponent_move
			#print(self.last_ftcomponent_replaced)
			#print(self.ftcomponents_replaced)
			if len(comptypes) == 1:
				self.possible_moves.discard(self.ftcomponent_move)
			return True
		else:
			return False

	def make_random_component_non_fault_tolerant(self):
		if self.ftcomponents_replaced:
			ftcomp = random.sample(self.ftcomponents_replaced.keys(), 1)
			org_component = self.ftcomponents_replaced[ftcomp[0]]
			#self.architecture.replace_component_with_other_component(ftcomp, new_component)
			print('Unreplacing: '+str(ftcomp[0]) + ' with '+str(org_component))
			self.architecture.unreplace_component(org_component, ftcomp[0])
			self.ftcomponents_replaced.pop(ftcomp[0])
			if ftcomp[0] in self.components_added:
				self.components_added.append(org_component)
				self.components_added.remove(ftcomp[0])
			self.ftcomponents_unreplaced[org_component] = ftcomp[0]
			self.last_nonftcomponent_replaced = org_component
			self.last_move = self.non_ftcomponent_move
			self.possible_moves.add(self.ftcomponent_move)
			if not self.ftcomponents_replaced:
				self.possible_moves.discard(self.non_ftcomponent_move)
			return True
		else:
			return False

	def add_connection_between_two_random_components(self):
		for each in self.architecture.components:
			s = str(each) + ': in connections: ' + str(each.total_in_connections())
			print(s)
			s = str(each) + ': out connections: ' + str(each.total_out_connections())
			print(s)
		pos_out_comps = list(filter(lambda c: c.total_out_connections() < self.max_out_connections_for_components[c.get_type()], self.architecture.components))
		pos_in_comps = list(filter(lambda c: c.total_in_connections() < self.max_in_connections_for_components[c.get_type()], self.architecture.components)) 
		print('Possible out comps: '+str(pos_out_comps))
		print('Possible in comps: '+str(pos_in_comps))
		if pos_out_comps and pos_in_comps:
			to_c = random.choice(pos_in_comps)
			from_c = random.choice(pos_out_comps)
			while from_c == to_c:
				from_c = random.choice(pos_out_comps)
				to_c = random.choice(pos_in_comps)
			s = str(from_c) + ': out connections: ' + str(from_c.total_out_connections())
			s2 = str(to_c) + ': in connections: ' + str(to_c.total_in_connections())
			#print('From component: '+s)
			#print('To component: '+s2)
			name = 'con-{}-{}'.format(from_c.id, to_c.id)
			con = Connection(name, from_c, to_c)
			print('Adding connection between: ' + str(from_c)+ ' and ' + str(to_c))
			self.architecture.add_connection(con)
			self.connections_added.append(con)
			self.last_connection_added = con
			self.possible_moves.add(self.remove_connection_move)
			self.last_move = self.add_connection_move
			if len(pos_out_comps) == 1 or len(pos_in_comps) == 1:
				self.possible_moves.discard(self.add_connection_move)
			return True
		else:
			return False

	def insert_component_to_make_random_component_redundant(self):
		#pos_comps = list(filter(lambda c: not c.is_fault_tolerant() and c.type[:5] != 'switch' and c.type[:5] != 'input' and c.type[:6] != 'ouput', self.architecture.components))
		allcomps = list(self.architecture.components) + list(self.architecture.components_removed)
		pos_comps = list(filter(lambda c: c.type[:6] != 'switch' and c.type[:5] != 'input' and c.type[:6] != 'output', allcomps))
		#pos_comps = list(filter(lambda c: c.type[:5] != 'switch' or c.type[:5] != 'input' or c.type[:6] != 'ouput', list(self.architecture.components) + list(self.architecture.components_removed)))
		if pos_comps:
			component = random.choice(pos_comps)
			num = randint(1, 1000)
			try:
				while num in self.component_type_to_numbers[component.get_type()]:
					num = randint(1, 1000)

				self.component_type_to_numbers[component.get_type()].append(num)
			except KeyError:
				self.component_type_to_numbers[component.get_type()] = list()
				self.component_type_to_numbers[component.get_type()].append(num)

			#l = self.architecture.types_to_components[component.get_type()]
			#num = len(l) + 1
			componenttype = component.type
			componentid = 'added ' + str(component.type) + '-' + str(num)
			new_component = Component(componentid, componenttype)
			print('Adding component: '+ str(new_component) + ' to make '+str(component) + ' redundant')

			switches = self.architecture.find_two_available_switches()
			if switches[0] == None and switches[1] == None:
				#Add new switches and all their connections
				cons = self.architecture.find_connections_between_two_switches(2)
				if cons[0] != None and cons[1] != None:
					l = self.architecture.types_to_components['switch']
					num = len(l) + 1
					switch1id = 'switch-' + str(num)
					new_switch1 = Component(switch1id, 'switch')
					num += 1
					switch2id = 'switch-' + str(num)
					new_switch2 = Component(switch2id, 'switch')
					self.architecture.add_component(new_switch1)
					self.architecture.add_component(new_switch2)

					#self.last_component_added_modified_connections = cons[0], cons[1]
					self.component_added_modified_connections[new_component] = cons[0], cons[1]

					self.architecture.modify_connection_to_have_comp_in_middle(cons[0], new_switch1)
					self.architecture.modify_connection_to_have_comp_in_middle(cons[1], new_switch2)

					self.architecture.add_component(new_component)
					con1name = 'con-{}-{}'.format(new_switch1.id, new_component.id)
					con1 = Connection(con1name, new_switch1, new_component)

					con2name = 'con-{}-{}'.format(new_component.id, new_switch2)
					con2 = Connection(con2name, new_component, new_switch2)
					self.architecture.add_connection(con1)
					self.architecture.add_connection(con2)
					self.component_added_switch_added[new_component] = new_switch1, new_switch2
					#self.last_component_switch_added = new_switch1, new_switch2
					#self.last_component_connections_added = con1, con2

			elif switches[1] == None:
				#Only one switch available
				con = self.architecture.find_connections_between_two_switches(1)
				if con != None:
					#add a new switch and have it as middle point between the two component of this connection
					l = self.architecture.types_to_components['switch']
					num = len(l) + 1
					switchid = 'switch-' + str(num)
					new_switch = Component(switchid, 'switch')
					self.architecture.add_component(new_switch)
					#self.last_component_added_modified_connections = con, None
					self.component_added_modified_connections[new_component] = con, None
					self.architecture.modify_connection_to_have_comp_in_middle(con, new_switch)

					self.architecture.add_component(new_component)
					con1name = 'con-{}-{}'.format(switches[0].id, new_component.id)
					con1 = Connection(con1name, switches[0], new_component)

					con2name = 'con-{}-{}'.format(new_component.id, new_switch)
					con2 = Connection(con2name, new_component, new_switch)
					self.architecture.add_connection(con1)
					self.architecture.add_connection(con2)
					#self.last_component_switch_added = new_switch, None
					self.component_added_switch_added[new_component] = new_switch, None
					#self.last_component_connections_added = con1, con2
			else:
				#Two switches available
				self.architecture.add_component(new_component)
				con1name = 'con-{}-{}'.format(switches[0].id, new_component.id)
				con1 = Connection(con1name, switches[0], new_component)
				con2name = 'con-{}-{}'.format(new_component.id, switches[1])
				con2 = Connection(con2name, new_component, switches[1])
				self.architecture.add_connection(con1)
				self.architecture.add_connection(con2)

				self.component_added_switch_added[new_component] = None, None
				self.component_added_modified_connections[new_component] = None, None
				#self.last_component_switch_added = None, None
				#self.last_component_added_modified_connections = None, None
				#self.last_component_connections_added = con1, con2
			self.components_added.append(new_component)
			self.last_component_added = new_component
			self.possible_moves.add(self.remove_component_move)
			self.last_move = self.add_component_move
			print('New component in_connections: ' + str(new_component.in_connections))
			print('New component out_connections: '+str(new_component.out_connections))
			if not new_component.is_fault_tolerant():
				self.possible_moves.add(self.ftcomponent_move)
			return True
		else:
			return False

	def remove_random_connection(self):
		if self.connections_added:
			con = random.choice(self.connections_added)
			self.connections_added.remove(con)
			print('Removing connection: '+str(con))
			self.architecture.remove_added_connection(con)
			self.last_connection_removed = con
			if not self.connections_added:
				self.possible_moves.discard(self.remove_connection_move)
			self.last_move = self.remove_connection_move
			self.possible_moves.add(self.add_connection_move)
			return True
		else:
			return False

	def remove_random_component(self):
		if self.components_added:
			comp = random.choice(self.components_added)
			print('Trying to remove: '+str(comp))
			self.components_added.remove(comp)
			#self.last_component_removed_connections = list(comp.out_connections.values()) + list(comp.in_connections.values())
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

				print(switch0_con)
				if len(switch0_c) == 0:
					print('Removing comp:' + str(switches[0]))
					self.architecture.remove_added_component(switches[0])
					print('Adding con:' + str(connections[0]))
					if connections[0].components[0] in self.architecture.components and connections[0].components[1] in self.architecture.components:
						print('Adding con:' + str(connections[0]))
						self.architecture.add_connection(connections[0])
				else:
					print('Adding: '+str(switches[0])+' to added components')
					self.components_added.append(switches[0])
					self.switch_to_modified_connection[switches[0]] = connections[0]

				print(switch1_con)
				print(switch1_c)
				if len(switch1_c) == 0:
					print('Removing comp:' + str(switches[1]))
					self.architecture.remove_added_component(switches[1])
					if connections[1].components[1] in self.architecture.components and connections[1].components[1] in self.architecture.components:
						print('Adding con:' + str(connections[1]))
						self.architecture.add_connection(connections[1])
				else:
					print('Adding: '+str(switches[1])+' to added components')
					self.components_added.append(switches[1])
					self.switch_to_modified_connection[switches[1]] = connections[1]

			elif switches[0] != None:
				switch0_con = set(switches[0].out_connections.values()) | set(switches[0].in_connections.values())
				switch0_c = set(filter(lambda c: c.get_other_component(switches[0]) != connections[0].components[0] and c.get_other_component(switches[0]) != connections[0].components[1] and c.get_other_component(switches[0]) != comp, switch0_con))
				print(switch0_con)
				if len(switch0_c) == 0:
					print('Removing comp:' + str(switches[0]))
					self.architecture.remove_added_component(switches[0])
					if connections[0].components[0] in self.architecture.components and connections[0].components[1] in self.architecture.components:
						print('Adding con:' + str(connections[0]))
						self.architecture.add_connection(connections[0])
				else:
					print('Adding: '+str(switches[0])+' to added components')
					self.components_added.append(switches[0])
					self.switch_to_modified_connection[switches[0]] = connections[0]
			else:
				pass

			print('Removing component: '+ str(comp))
			self.architecture.remove_added_component(comp)
			self.last_component_removed = comp
			if comp in self.switch_to_modified_connection:
				print('Readding modified connection: '+str(switch_to_modified_connection[comp]))
				self.architecture.add_connection(self.switch_to_modified_connection[comp])

			if len(self.last_component_removed_added_connections) > 0:
				for each in self.last_component_removed_added_connections:
					print(each)
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
		else:
			return False
	'''
	'''
	def add_fault_scenario_to_architecture(self, faultscenario):
		for f in faultscenario.faults:
			self.architecture.add_fault(f)

	def restore_architecture_from_fault_scenario(self):
		self.architecture.restore()
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
		self.last_component_removed_added_connections = None
		self.last_component_removed_connections = None
		self.last_move_removed_ftcomp = None, None
		self.last_move = None
		self.switch_to_modified_connection = {}

		self.component_type_to_numbers = {}


		self.ftcomponents_replaced = {}
		self.ftcomponents_unreplaced = {}

	def add_fault_scenario_to_architecture(self, faultscenario, architecture):
		for f in faultscenario.faults:
			architecture.add_fault(f)

	def restore_architecture_from_fault_scenario(self, architecture):
		architecture.restore()

	def undo_last_move(self):
		if self.last_move == self.non_ftcomponent_move:
			org_comp = self.last_nonftcomponent_replaced
			ftcomp = self.ftcomponents_unreplaced[org_comp]
			self.architecture.replace_component_with_other_component(org_comp, ftcomp)
			self.ftcomponents_unreplaced.pop(org_comp)
			if org_comp in self.components_added:
				self.components_added.append(ftcomp)
				self.components_added.remove(org_comp)
			self.ftcomponents_replaced[ftcomp] = org_comp
			self.possible_moves.add(self.ftcomponent_move)
			self.last_move = None

		elif self.last_move == self.ftcomponent_move:
			ftcomp = self.last_ftcomponent_replaced
			print(ftcomp)
			print(self.ftcomponents_replaced)
			org_component = self.ftcomponents_replaced[ftcomp]
			self.architecture.unreplace_component(org_component, ftcomp)
			self.ftcomponents_replaced.pop(ftcomp)
			if ftcomp in self.components_added:
				self.components_added.append(org_component)
				self.components_added.remove(ftcomp)
			self.possible_moves.add(self.non_ftcomponent_move)
			self.last_move = None

		elif self.last_move == self.remove_component_move:
			comp = self.last_component_removed
			print('Undoing removal of '+str(comp))
			self.architecture.add_component(comp)
			#cons = self.last_component_connections_added
			#self.architecture.add_connection(cons[0])
			#self.architecture.add_connection(cons[1])
			if comp in self.switch_to_modified_connection:
				print('Removing modified connection: '+str(self.switch_to_modified_connection[comp]))
				self.architecture.removed_added_connection(self.switch_to_modified_connection[comp])

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
					print(str(switches[1])+' already added')
				else:
					print('Readding comp:' + str(switches[1]))
					self.architecture.add_component(switches[1])
				if switches[0] in self.components_added:
					self.components_added.remove(switches[0])
					print(str(switches[0])+' already added')
				else:
					print('Readding comp:' + str(switches[0]))
					self.architecture.add_component(switches[0])
			elif switches[0] != None:
				if switches[0] in self.components_added:
					self.components_added.remove(switches[0])
					print(str(switches[0])+' already added')
				else:
					print('Readding comp:' + str(switches[0]))
					self.architecture.add_component(switches[0])


			if self.last_component_removed_added_connections != None:
				for each in self.last_component_removed_added_connections:
					self.connections_added.append(each)
			for each in self.last_component_removed_connections:
				print('Readding connection: '+str(each))
				self.architecture.add_connection(each)
			self.components_added.append(comp)

			if self.last_move_removed_ftcomp[0] != None and self.last_move_removed_ftcomp[1] != None:
				#print('Reading in ftcomponents_replaced: '+str(self.last_move_removed_ftcomp[0]) + ' = '+str(self.last_move_removed_ftcomp[1]))
				self.ftcomponents_replaced[self.last_move_removed_ftcomp[0]] = self.last_move_removed_ftcomp[1]
				self.last_move_removed_ftcomp = None, None

			self.possible_moves.add(self.add_component_move)
			self.last_connection_removed_connections = None
			self.last_component_removed_added_connections = None
			self.last_move = None

		elif self.last_move == self.add_component_move:
			comp = self.last_component_added
			self.components_added.remove(comp)
			self.architecture.remove_added_component(comp)

			if comp in self.component_added_switch_added:
				switches = self.component_added_switch_added[comp]
			else:
				switches = None, None
			if comp in self.component_added_modified_connections:
				connections = self.component_added_modified_connections[comp]
			else:
				connections = None, None
			#switches = self.component_added_switch_added[comp]
			#switches = self.last_component_switch_added
			if switches[1] != None:
				print('Removing comps:' + str(switches[0]) + ' ' + str(switches[1]))
				self.architecture.remove_added_component(switches[1])
				self.architecture.remove_added_component(switches[0])
			elif switches[0] != None:
				print('Removing comp:' + str(switches[0]))
				self.architecture.remove_added_component(switches[0])
			#self.last_component_switch_added = None, None
			self.component_added_switch_added.pop(comp)
			
			#connections = self.last_component_added_modified_connections
			#connections = self.component_added_modified_connections[comp]
			if connections[1] != None:
				#print('Adding cons:' + str(connections[0]) + ' ' + str(connections[1]))
				self.architecture.add_connection(connections[0])
				self.architecture.add_connection(connections[1])
			elif connections[0] != None:
				print('Adding con:' + str(connections[0]))
				self.architecture.add_connection(connections[0])
			#self.last_component_added_modified_connections = None, None
			self.component_added_modified_connections.pop(comp)
			self.possible_moves.add(self.remove_component_move)
			self.last_move = None

		elif self.last_move == self.remove_connection_move:
			con = self.last_connection_removed
			self.architecture.add_connection(con)
			self.connections_added.append(con)
			self.possible_moves.add(self.add_connection_move)
			self.last_move = None

		elif self.last_move == self.add_connection_move:
			con = self.last_connection_added
			self.connections_added.remove(con)
			self.architecture.remove_added_connection(con)
			self.possible_moves.add(self.remove_connection_move)
			self.last_move = None

		else:
			pass

	def evaluate_architecture(self, architecture):
		schedulable_sum = 0
		fault_tolerant_sum = 0
		for fs in self.faultscenarios:
			#print('Adding fault scenario to architecture:')
			#print(fs)
			self.add_fault_scenario_to_architecture(fs, architecture)
			#d = self.is_architecture_non_fault_tolerant()
			#k = True if d == 0 else False
			#print('Architecture is connected with this fault scenario: '+str(k))
			fault_tolerant_sum += self.is_architecture_non_fault_tolerant(architecture)
			schedulable_sum += self.application_finish_time(architecture)
			self.restore_architecture_from_fault_scenario()

		#schedulable_sum = (schedulable_sum * self.schedulable_weight) / 100
		schedulable_sum = schedulable_sum * self.schedulable_weight
		#fault_tolerant_sum = (fault_tolerant_sum * self.fault_tolerant_weight) / 100
		fault_tolerant_sum = fault_tolerant_sum * self.fault_tolerant_weight
		architecture_cost = architecture.number_of_valves() + architecture.number_of_connections()

		return fault_tolerant_sum + schedulable_sum + architecture_cost

	def is_architecture_non_fault_tolerant(self, architecture):
		return 0 if architecture.is_connected() else 1

	def application_finish_time(self, architecture):
		s = ListScheduler(self.application, architecture, self.average_connection_time)
		applicationtime = 0
		try:
			s.schedule_application()
			applicationtime = self.application.sink.finish_time
		except NoScheduleFoundError:
			applicationtime = self.application_deadline * 2
		#print('With this fault scenario the application time is: '+str(applicationtime))
		returnvalue = max(0, applicationtime - self.application_deadline)
		self.application.unschedule()
		architecture.unschedule()
		return returnvalue
	'''
	def evaluate_architecture(self):
		schedulable_sum = 0
		fault_tolerant_sum = 0
		for fs in self.faultscenarios:
			#print('Adding fault scenario to architecture:')
			#print(fs)
			self.add_fault_scenario_to_architecture(fs)
			#d = self.is_architecture_non_fault_tolerant()
			#k = True if d == 0 else False
			#print('Architecture is connected with this fault scenario: '+str(k))
			fault_tolerant_sum += self.is_architecture_non_fault_tolerant()
			schedulable_sum += self.application_finish_time()
			self.restore_architecture_from_fault_scenario()

		#schedulable_sum = (schedulable_sum * self.schedulable_weight) / 100
		schedulable_sum = schedulable_sum * self.schedulable_weight
		#fault_tolerant_sum = (fault_tolerant_sum * self.fault_tolerant_weight) / 100
		fault_tolerant_sum = fault_tolerant_sum * self.fault_tolerant_weight
		architecture_cost = self.architecture.number_of_valves() + self.architecture.number_of_connections()

		return fault_tolerant_sum + schedulable_sum + architecture_cost

	def is_architecture_non_fault_tolerant(self):
		return 0 if self.architecture.is_connected() else 1

	def application_finish_time(self):
		s = ListScheduler(self.application, self.architecture, self.average_connection_time)
		applicationtime = 0
		try:
			s.schedule_application()
			applicationtime = self.application.sink.finish_time
		except NoScheduleFoundError:
			applicationtime = self.application_deadline * 2
		#print('With this fault scenario the application time is: '+str(applicationtime))
		returnvalue = max(0, applicationtime - self.application_deadline)
		self.application.unschedule()
		self.architecture.unschedule()
		return returnvalue
	'''
	def make_random_component_fault_tolerant(self):
		types = self.architecture.component_library.get_types_with_a_fault_tolerant_version()
		#randomtype = random.choice(types)
		allcomps = list(self.architecture.components) + list(self.architecture.components_removed)
		comptypes = list(filter(lambda c: not c.is_fault_tolerant() and c.type in types, allcomps))
		#while(randomtype not in self.architecture.types_to_components):
		#	randomtype = random.choice(comptypes)
		if comptypes:
			component = random.choice(comptypes)
		else:
			component = None
		#randomcomponents = self.architecture.types_to_components[randomtype]
		#any(type(f).__name__ == 'ChannelFault' for f in switch.faults):
		#randomcomponents = list(filter(lambda c: c.is_fault_tolerant() == False, self.architecture.types_to_components[randomtype])) 
		#component = random.choice(randomcomponents)
		if component is not None:
			self.make_component_fault_tolerant(component)
			if len(comptypes) == 1:
				self.possible_moves.discard(self.ftcomponent_move)
			return True
		else:
			return False

	def make_component_fault_tolerant(self, component):
		ftcomp = self.architecture.component_library.get_faulttolerance_version_of_component(component)
		num = randint(1, 1000)
		try:
			while num in self.component_type_to_numbers[ftcomp.get_type()]:
				num = randint(1, 1000)

			self.component_type_to_numbers[ftcomp.get_type()].append(num)
		except KeyError:
			self.component_type_to_numbers[ftcomp.get_type()] = list()
			self.component_type_to_numbers[ftcomp.get_type()].append(num)
		#try:
		#	l = self.architecture.types_to_components[ftcomp.get_type()]
		#	num = len(l) + 1
		#except KeyError:
		#	num = 1
		componenttype = ftcomp.type
		componentid = str(ftcomp.type)+ '-' + str(num)
		new_component = Component(componentid, componenttype)
		print('Replacing: '+str(component) + ' with '+str(new_component))
		self.architecture.replace_component_with_other_component(component, new_component)
		self.ftcomponents_replaced[new_component] = component
		#if not component in self.architecture.original_components:
		#	components_added.append(new_component)
		#	components_added.remove(component)
		if component in self.components_added:
			self.components_added.append(new_component)
			self.components_added.remove(component)
		self.last_ftcomponent_replaced = new_component
		self.possible_moves.add(self.non_ftcomponent_move)
		self.last_move = self.ftcomponent_move
		#print(self.last_ftcomponent_replaced)
		#print(self.ftcomponents_replaced)

	def make_random_component_non_fault_tolerant(self):
		if self.ftcomponents_replaced:
			ftcomp = random.sample(self.ftcomponents_replaced.keys(), 1)
			org_component = self.ftcomponents_replaced[ftcomp[0]]
			self.make_component_non_fault_tolerant(org_component, ftcomp[0])
			return True
		else:
			return False

	def make_component_non_fault_tolerant(self, org_component, ftcomp):
		print('Unreplacing: '+str(ftcomp) + ' with '+str(org_component))
		self.architecture.unreplace_component(org_component, ftcomp)
		self.ftcomponents_replaced.pop(ftcomp)
		if ftcomp in self.components_added:
			self.components_added.append(org_component)
			self.components_added.remove(ftcomp)
		self.ftcomponents_unreplaced[org_component] = ftcomp
		self.last_nonftcomponent_replaced = org_component
		self.last_move = self.non_ftcomponent_move
		self.possible_moves.add(self.ftcomponent_move)
		if not self.ftcomponents_replaced:
			self.possible_moves.discard(self.non_ftcomponent_move)

	def add_connection_between_two_random_components(self):
		for each in self.architecture.components:
			s = str(each) + ': in connections: ' + str(each.total_in_connections())
			print(s)
			s = str(each) + ': out connections: ' + str(each.total_out_connections())
			print(s)
		pos_out_comps = list(filter(lambda c: c.total_out_connections() < self.max_out_connections_for_components[c.get_type()], self.architecture.components))
		pos_in_comps = list(filter(lambda c: c.total_in_connections() < self.max_in_connections_for_components[c.get_type()], self.architecture.components)) 
		print('Possible out comps: '+str(pos_out_comps))
		print('Possible in comps: '+str(pos_in_comps))
		if pos_out_comps and pos_in_comps:
			to_c = random.choice(pos_in_comps)
			from_c = random.choice(pos_out_comps)
			while from_c == to_c:
				from_c = random.choice(pos_out_comps)
				to_c = random.choice(pos_in_comps)
			self.add_connection_between_two_components(from_c, to_c)
			if len(pos_out_comps) == 1 or len(pos_in_comps) == 1:
				self.possible_moves.discard(self.add_connection_move)
			return True
		else:
			return False


	def add_connection_between_two_components(self, from_c, to_c):
		name = 'con-{}-{}'.format(from_c.id, to_c.id)
		con = Connection(name, from_c, to_c)
		print('Adding connection between: ' + str(from_c)+ ' and ' + str(to_c))
		self.architecture.add_connection(con)
		self.connections_added.append(con)
		self.last_connection_added = con
		self.possible_moves.add(self.remove_connection_move)
		self.last_move = self.add_connection_move

	def insert_component_to_make_random_component_redundant(self):
		#pos_comps = list(filter(lambda c: not c.is_fault_tolerant() and c.type[:5] != 'switch' and c.type[:5] != 'input' and c.type[:6] != 'ouput', self.architecture.components))
		allcomps = list(self.architecture.components) + list(self.architecture.components_removed)
		pos_comps = list(filter(lambda c: c.type[:6] != 'switch' and c.type[:5] != 'input' and c.type[:6] != 'output', allcomps))
		#pos_comps = list(filter(lambda c: c.type[:5] != 'switch' or c.type[:5] != 'input' or c.type[:6] != 'ouput', list(self.architecture.components) + list(self.architecture.components_removed)))
		if pos_comps:
			component = random.choice(pos_comps)
			num = randint(1, 1000)
			try:
				while num in self.component_type_to_numbers[component.get_type()]:
					num = randint(1, 1000)

				self.component_type_to_numbers[component.get_type()].append(num)
			except KeyError:
				self.component_type_to_numbers[component.get_type()] = list()
				self.component_type_to_numbers[component.get_type()].append(num)

			#l = self.architecture.types_to_components[component.get_type()]
			#num = len(l) + 1
			componenttype = component.type
			componentid = 'added ' + str(component.type) + '-' + str(num)
			new_component = Component(componentid, componenttype)
			print('Adding component: '+ str(new_component) + ' to make '+str(component) + ' redundant')
			self.insert_redundant_component(new_component)
			return True
		else:
			return False


	def insert_redundant_component(self, new_component):
		switches = self.architecture.find_two_available_switches()
		if switches[0] == None and switches[1] == None:
			#Add new switches and all their connections
			cons = self.architecture.find_connections_between_two_switches(2)
			if cons[0] != None and cons[1] != None:
				l = self.architecture.types_to_components['switch']
				num = len(l) + 1
				switch1id = 'switch-' + str(num)
				new_switch1 = Component(switch1id, 'switch')
				num += 1
				switch2id = 'switch-' + str(num)
				new_switch2 = Component(switch2id, 'switch')
				self.architecture.add_component(new_switch1)
				self.architecture.add_component(new_switch2)

				#self.last_component_added_modified_connections = cons[0], cons[1]
				self.component_added_modified_connections[new_component] = cons[0], cons[1]

				self.architecture.modify_connection_to_have_comp_in_middle(cons[0], new_switch1)
				self.architecture.modify_connection_to_have_comp_in_middle(cons[1], new_switch2)

				self.architecture.add_component(new_component)
				con1name = 'con-{}-{}'.format(new_switch1.id, new_component.id)
				con1 = Connection(con1name, new_switch1, new_component)

				con2name = 'con-{}-{}'.format(new_component.id, new_switch2)
				con2 = Connection(con2name, new_component, new_switch2)
				self.architecture.add_connection(con1)
				self.architecture.add_connection(con2)
				self.component_added_switch_added[new_component] = new_switch1, new_switch2
				#self.last_component_switch_added = new_switch1, new_switch2
				#self.last_component_connections_added = con1, con2

		elif switches[1] == None:
			#Only one switch available
			con = self.architecture.find_connections_between_two_switches(1)
			if con != None:
				#add a new switch and have it as middle point between the two component of this connection
				l = self.architecture.types_to_components['switch']
				num = len(l) + 1
				switchid = 'switch-' + str(num)
				new_switch = Component(switchid, 'switch')
				self.architecture.add_component(new_switch)
				#self.last_component_added_modified_connections = con, None
				self.component_added_modified_connections[new_component] = con, None
				self.architecture.modify_connection_to_have_comp_in_middle(con, new_switch)

				self.architecture.add_component(new_component)
				con1name = 'con-{}-{}'.format(switches[0].id, new_component.id)
				con1 = Connection(con1name, switches[0], new_component)

				con2name = 'con-{}-{}'.format(new_component.id, new_switch)
				con2 = Connection(con2name, new_component, new_switch)
				self.architecture.add_connection(con1)
				self.architecture.add_connection(con2)
				#self.last_component_switch_added = new_switch, None
				self.component_added_switch_added[new_component] = new_switch, None
				#self.last_component_connections_added = con1, con2
		else:
			#Two switches available
			self.architecture.add_component(new_component)
			con1name = 'con-{}-{}'.format(switches[0].id, new_component.id)
			con1 = Connection(con1name, switches[0], new_component)
			con2name = 'con-{}-{}'.format(new_component.id, switches[1])
			con2 = Connection(con2name, new_component, switches[1])
			self.architecture.add_connection(con1)
			self.architecture.add_connection(con2)

			self.component_added_switch_added[new_component] = None, None
			self.component_added_modified_connections[new_component] = None, None
			#self.last_component_switch_added = None, None
			#self.last_component_added_modified_connections = None, None
			#self.last_component_connections_added = con1, con2
		self.components_added.append(new_component)
		self.last_component_added = new_component
		self.possible_moves.add(self.remove_component_move)
		self.last_move = self.add_component_move
		print('New component in_connections: ' + str(new_component.in_connections))
		print('New component out_connections: '+str(new_component.out_connections))
		if not new_component.is_fault_tolerant():
			self.possible_moves.add(self.ftcomponent_move)

	def remove_random_connection(self):
		if self.connections_added:
			con = random.choice(self.connections_added)
			self.remove_connection(con)
			return True
		else:
			return False

	def remove_connection(self, con):
		self.connections_added.remove(con)
		print('Removing connection: '+str(con))
		self.architecture.remove_added_connection(con)
		self.last_connection_removed = con
		if not self.connections_added:
			self.possible_moves.discard(self.remove_connection_move)
		self.last_move = self.remove_connection_move
		self.possible_moves.add(self.add_connection_move)

	def remove_random_component(self):
		if self.components_added:
			comp = random.choice(self.components_added)
			self.remove_component(comp)
			return True
		else:
			return False

	def remove_component(self, comp):
		print('Trying to remove: '+str(comp))
		self.components_added.remove(comp)
		#self.last_component_removed_connections = list(comp.out_connections.values()) + list(comp.in_connections.values())
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

			print(switch0_con)
			if len(switch0_c) == 0:
				print('Removing comp:' + str(switches[0]))
				self.architecture.remove_added_component(switches[0])
				print('Adding con:' + str(connections[0]))
				if connections[0].components[0] in self.architecture.components and connections[0].components[1] in self.architecture.components:
					print('Adding con:' + str(connections[0]))
					self.architecture.add_connection(connections[0])
			else:
				print('Adding: '+str(switches[0])+' to added components')
				self.components_added.append(switches[0])
				self.switch_to_modified_connection[switches[0]] = connections[0]

			print(switch1_con)
			print(switch1_c)
			if len(switch1_c) == 0:
				print('Removing comp:' + str(switches[1]))
				self.architecture.remove_added_component(switches[1])
				if connections[1].components[1] in self.architecture.components and connections[1].components[1] in self.architecture.components:
					print('Adding con:' + str(connections[1]))
					self.architecture.add_connection(connections[1])
			else:
				print('Adding: '+str(switches[1])+' to added components')
				self.components_added.append(switches[1])
				self.switch_to_modified_connection[switches[1]] = connections[1]

		elif switches[0] != None:
			switch0_con = set(switches[0].out_connections.values()) | set(switches[0].in_connections.values())
			switch0_c = set(filter(lambda c: c.get_other_component(switches[0]) != connections[0].components[0] and c.get_other_component(switches[0]) != connections[0].components[1] and c.get_other_component(switches[0]) != comp, switch0_con))
			print(switch0_con)
			if len(switch0_c) == 0:
				print('Removing comp:' + str(switches[0]))
				self.architecture.remove_added_component(switches[0])
				if connections[0].components[0] in self.architecture.components and connections[0].components[1] in self.architecture.components:
					print('Adding con:' + str(connections[0]))
					self.architecture.add_connection(connections[0])
			else:
				print('Adding: '+str(switches[0])+' to added components')
				self.components_added.append(switches[0])
				self.switch_to_modified_connection[switches[0]] = connections[0]
		else:
			pass

		print('Removing component: '+ str(comp))
		self.architecture.remove_added_component(comp)
		self.last_component_removed = comp
		if comp in self.switch_to_modified_connection:
			print('Readding modified connection: '+str(switch_to_modified_connection[comp]))
			self.architecture.add_connection(self.switch_to_modified_connection[comp])

		if len(self.last_component_removed_added_connections) > 0:
			for each in self.last_component_removed_added_connections:
				print(each)
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

class SimulatedAnnealing(ArchitectureModifier):

	def __init__(self, architecture, application, faultscenarios, config):
		super().__init__(architecture, application, faultscenarios, config)
		self.temperature = 10000
		self.termination_temperature = 0.1
		self.steps_in_iteration = 1
		self.temperature_reduction_rate = 0.999
		self.cost = 0
		self.run()

	def reduce_temperature(self, temp):
		#return temp * self.temperature_reduction_rate
		return temp - 20

	def run(self):
		self.cost = self.evaluate_architecture(self.architecture)
		print('Inital cost: '+str(self.cost))
		while not self.terminated():
			self.iterations()
			t = str(self.temperature)
			c = str(self.cost)
			print('Temperature: '+t + ' - cost: '+c)
			self.temperature = self.reduce_temperature(self.temperature)

	def iterations(self):
		for _ in range(self.steps_in_iteration):
			success = self.perform_random_move()
			if not success:
				continue
			newcost = self.evaluate_architecture()
			if self.acceptance_probability(self.cost, newcost) > random.random():
				print('New arch accepted')
				self.cost = newcost
			else:
				print('New arch is not accepted')
				print('Undoing last move')
				self.undo_last_move()

	def acceptance_probability(self, oldcost, newcost):
		if newcost < oldcost:
			return 1.0
		else:
			delta = newcost - oldcost
			print('Calculating: ('+str(newcost)+' - '+str(oldcost) + ') / '+str(self.temperature))
		return math.exp(-delta / self.temperature)

	def terminated(self):
		if self.termination_temperature >= self.temperature:
			return True
		else:
			return False

	def perform_random_move(self):
		moves = random.sample(self.possible_moves, 1)
		ret = self.perform_move(moves[0])
		return ret

	def perform_move(self, move):
		if move == self.non_ftcomponent_move:
			ret = self.make_random_component_non_fault_tolerant()
			return ret

		if move == self.ftcomponent_move:
			ret = self.make_random_component_fault_tolerant()
			return ret

		if move == self.remove_component_move:
			ret = self.remove_random_component()
			return ret

		if move == self.add_component_move:
			ret = self.insert_component_to_make_random_component_redundant()
			return ret

		if move == self.remove_connection_move:
			ret = self.remove_random_connection()
			return ret

		if move == self.add_connection_move:
			ret = self.add_connection_between_two_random_components()
			return ret

class GreedilyRandomAdaptiveSearchProcedure(ArchitectureModifier):

	def __init__(self, architecture, application, faultscenarios, config, architecture_file):
		super().__init__(architecture, application, faultscenarios, config)

		self.number_of_iterations = 500
		self.best_architecutre = architecture
		self.best_cost = self.evaluate_architecture(self.best_architecutre)
		self.max_number_of_iterations_before_increasing_c = 25
		self.number_of_unsuccesful_iterations = 0
		self.c = 1
		self.increase_c = 2
		self.make_redundant = 'redundant component'
		self.make_ftcomponent = 'ftcomponent'
		self.make_ftcomponent_with_in_con = 'ftcomponent with in connection'
		self.make_ftcomponent_with_out_con = 'ftcomponent with out connection'
		self.make_ftcomponent_with_both_con = 'ftcomponent with both connections'
		self.design_transformations = set()
		self.create_design_transformations()
		self.component_transformation = {}

	def create_design_transformations(self):
		self.design_transformations.add(self.make_redundant)
		self.design_transformations.add(self.make_ftcomponent)
		self.design_transformations.add(self.make_ftcomponent_with_in_con)
		self.design_transformations.add(self.make_ftcomponent_with_out_con)
		self.design_transformations.add(self.make_ftcomponent_with_both_con)

	def apply_design_transformations(self):
		for c in self.component_transformation:
			self.apply_single_design_transformation(c, self.component_transformation[c])

	def apply_single_design_transformation(self, component, transformation):
		if transformation == self.make_redundant:
			self.insert_redundant_component(component)

		elif transformation == self.make_ftcomponent:
			self.make_component_fault_tolerant(component)

		elif transformation == self.make_ftcomponent_with_in_con:
			self.make_component_fault_tolerant(component)
			#make in con
			pos_in_comps = set(filter(lambda c: c.total_in_connections() < self.max_in_connections_for_components[c.get_type()], self.architecture.components))
			if pos_in_comps:
				to_comp = random.sample(pos_in_comps, 1)
				to_c = to_comp[0]
				while to_c == component:
					to_comp = random.sample(pos_in_comps, 1)
					to_c = to_comp[0]

				self.add_connection_between_two_components(component, to_c)

		elif transformation == self.make_ftcomponent_with_out_con:
			self.make_component_fault_tolerant(component)
			#make out con
			pos_out_comps = set(filter(lambda c: c.total_out_connections() < self.max_out_connections_for_components[c.get_type()], self.architecture.components))
			if pos_out_comps:
				from_comp = random.sample(pos_out_comps, 1)
				from_c = from_comp[0]
				while from_c == to_c:
					from_comp = random.sample(pos_out_comps, 1)
					from_c = from_comp[0]

				self.add_connection_between_two_components(from_c, component)

		elif transformation == self.make_ftcomponent_with_both_con:
			self.make_component_fault_tolerant(component)
			#make in con and out con
			pos_out_comps = set(filter(lambda c: c.total_out_connections() < self.max_out_connections_for_components[c.get_type()], self.architecture.components))
			pos_in_comps = set(filter(lambda c: c.total_in_connections() < self.max_in_connections_for_components[c.get_type()], self.architecture.components))
			if pos_out_comps:
				from_comp = random.sample(pos_out_comps, 1)
				from_c = from_comp[0]
				while from_c == to_c:
					from_comp = random.sample(pos_out_comps, 1)
					from_c = from_comp[0]

				self.add_connection_between_two_components(from_c, component)

			if pos_in_comps:
				to_comp = random.sample(pos_in_comps, 1)
				to_c = to_comp[0]
				while to_c == component:
					to_comp = random.sample(pos_in_comps, 1)
					to_c = to_comp[0]

				self.add_connection_between_two_components(component, to_c)
		else:
			pass

	def choose_and_apply_design_transformations(self, rcl):
		for c in rcl:
			self.choose_random_design_transformation_for_component(c)

		self.apply_design_transformations()
		self.reset()
		self.component_transformation = {}

	def choose_random_design_transformation_for_component(self, component):
		transformation = random.sample(self.design_transformations, 1)
		self.component_transformation[component] = transformation[0]

	def run(self):
		i = 0
		while(i < self.number_of_iterations):
			new_arch = load_original_architecture()
			cl = create_candidates(new_arch.components, self.c)
			rcl = choose_candidates(cl)
			self.choose_and_apply_design_transformations(rcl)
			#do local search
			new_arch_cost = self.evaluate_architecture(new_arch)
			if new_arch_cost < self.best_cost:
				self.best_architecutre = new_arch
				self.best_cost = new_arch_cost
				self.number_of_unsuccesful_iterations = 0
			else:
				self.number_of_unsuccesful_iterations += 1
			if self.number_of_unsuccesful_iterations >= self.max_number_of_iterations_before_increasing_c:
				self.c = self.c * self.increase_c
				self.number_of_unsuccesful_iterations = 0
			i += 1

	def load_original_architecture(self):
		np = NetlistParser(self.architecture_file)
		np.architecture.component_library = clp.get_component_library()
		np.parse()
		return np.architecture

	def choose_candidates(self, candidatelist):
		num = randint(1, len(candidatelist))
		rcl = set(random.sample(candidatelist, num))
		return rcl

	def local_search(self, architecture):
		raise NotImplementedError

	def create_candidates(self, components, amount):
		#return set of candidates (with number of components = amount)
		raise NotImplementedError

	def rank_component(self, component):
		raise NotImplementedError




