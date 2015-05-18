'''
Created 21 April 2015

@author: Morten Chabert Eskesen
'''

from architecture import Component, Connection
from faultmodel import ChannelFault, ValveFault

class GreedyAlgorithm(object):

	def __init__(self, architecture, ftcomponents=False):
		self.ftcomponents = ftcomponents
		self.architecture = architecture
		self.max_in_connections_for_components = {	'mixer': 2, 
													'filter': 2,
													'switch': 4,
													'detector': 2,
													'seperator': 2,
													'storage': 2}

		self.max_out_connections_for_components = {	'mixer': 2,
													'filter': 2,
													'switch': 4,
													'detector': 2,
													'seperator': 2,
													'storage': 2}

	def tolerate_faults(self):
		for f in self.architecture.faults:
			if type(f).__name__ == 'ChannelFault' and f.type == 'block':
				if f.objecttype == 'component':
					self.tolerate_channelfault_on_component(self.architecture.component_by_name[f.objectname], f)
				if f.objecttype == 'connection':
					self.tolerate_channelfault_on_connection(self.architecture.connection_by_name[f.objectname], f)
			if type(f).__name__ == 'ValveFault' and f.type == 'open':
				if f.objecttype == 'component':
					self.tolerate_valvefault_on_component(self.architecture.component_by_name[f.objectname], f)

	def tolerate_channelfault_on_component(self, component, fault):
		if self.ftcomponents:
			ftcomp = self.architecture.component_library.get_specific_faulttolerance_version_of_component(component, 'channel')
			if ftcomp != None:
				try:
					l = self.architecture.types_to_components[ftcomp.get_type()]
					num = len(l) + 1
				except KeyError:
					num = 1
				componenttype = ftcomp.type
				componentid = str(ftcomp.type)+ '-' + str(num)
				new_component = Component(componentid, componenttype)
				self.architecture.replace_component_with_other_component(component, new_component)
			else:
				self.tolerate_fault_by_adding_new_component(component, fault)
		else:
			self.tolerate_fault_by_adding_new_component(component, fault)

	def tolerate_fault_by_adding_new_component(self, component, fault):
		#Make component of same type and add connections to it
		l = self.architecture.types_to_components[component.get_type()]
		num = len(l) + 1
		componenttype = component.type
		componentid = str(component.type) + '-' + str(num)
		new_component = Component(componentid, componenttype)

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

				self.architecture.modify_connection_to_have_comp_in_middle(cons[0], new_switch1)
				self.architecture.modify_connection_to_have_comp_in_middle(cons[1], new_switch2)

				self.architecture.add_component(new_component)
				con1name = 'con-{}-{}'.format(new_switch1.id, new_component.id)
				con1 = Connection(con1name, new_switch1, new_component)

				con2name = 'con-{}-{}'.format(new_component.id, new_switch2)
				con2 = Connection(con2name, new_component, new_switch2)
				self.architecture.add_connection(con1)
				self.architecture.add_connection(con2)

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
				self.architecture.modify_connection_to_have_comp_in_middle(con, new_switch)

				self.architecture.add_component(new_component)
				con1name = 'con-{}-{}'.format(switches[0].id, new_component.id)
				con1 = Connection(con1name, switches[0], new_component)

				con2name = 'con-{}-{}'.format(new_component.id, new_switch)
				con2 = Connection(con2name, new_component, new_switch)
				self.architecture.add_connection(con1)
				self.architecture.add_connection(con2)
		else:
			#Two switches available
			self.architecture.add_component(new_component)
			con1name = 'con-{}-{}'.format(switches[0].id, new_component.id)
			con1 = Connection(con1name, switches[0], new_component)
			con2name = 'con-{}-{}'.format(new_component.id, switches[1])
			con2 = Connection(con2name, new_component, switches[1])
			self.architecture.add_connection(con1)
			self.architecture.add_connection(con2)

	def tolerate_channelfault_on_connection(self, connection, fault):
		from_c = connection.components[0]
		to_c = connection.components[1]
		#bi_con = False

		#if from_c in to_c.removed_out_connections and to_c in from_c.removed_in_connections:
		#	bi_con = True

		#if from_c in to_c.removed_out_connections and to_c in from_c.removed_in_connections:
		#	raise NotImplementedError
		#else:
			#from_c_cons = len(from_c.out_connections) + len(from_c.removed_out_connections)
			#to_c_cons = len(to_c.in_connections) + len(to_c.removed_in_connections)
			#For switches the total in connections and out connections need to be the same X
		if to_c.total_in_connections < self.max_in_connections_for_components[to_c.get_type()] and from_c.total_out_connections < self.max_out_connections_for_components[from_c.get_type()]:
			# ADD CONNECTION BETWEEN FROM_C AND TO_C
			print('Adding connection between the two components')
			name = 'con-{}-{}'.format(from_c.id, to_c.id)
			con = Connection(name, from_c, to_c)
			self.architecture.add_connection(con)
		elif to_c.total_in_connections < self.max_in_connections_for_components[to_c.get_type()] and from_c.total_out_connections == self.max_out_connections_for_components[from_c.get_type()]:
			# FIND NEAR SWITCH AND CONNECTION FROM THAT TO THE TO_C COMPONENT
			#print('FIND NEAR SWITCH AND ADD CONNECTION FROM THAT TO THE TO_C COMPONENT')
			comp = None
			for each in from_c.out_connections.keys():
				if each != to_c and each != from_c and each.get_type() == 'switch':
					comp = each
					break
			if comp == None:
				for each in to_c.out_connections.keys():
					if each != to_c and each != from_c and each.get_type() == 'switch':
						comp = each
						break

			if comp != None:
				name = 'con-{}{}'.format(comp.id, to_c.id)
				con = Connection(name, comp, to_c)
				self.architecture.add_connection(con)
		elif from_c.total_out_connections < self.max_out_connections_for_components[from_c.get_type()] and to_c.total_in_connections == self.max_in_connections_for_components[to_c.get_type()]:
			# NOTHING TO DO FOR THIS COMPONENT AS IT HAS THE ALLOWED AMOUNT OF IN CONNECTIONS
			# FIND NEAR SWITCH AND ADD CONNECTION FROM THAT TO THE 
			#print('FIND NEAR SWITCH AND ADD CONNECTION FROM THAT TO THE FROM_C COMPONENT')
			comp = None
			for each in to_c.in_connections.keys():
				if each != to_c and each != from_c and each.get_type() == 'switch':
					comp = each
					break
			if comp == None:
				for each in from_c.out_connections.keys():
					if each != to_c and each != from_c and each.get_type() == 'switch':
						comp = each
						break

			if comp != None:
				name = 'con-{}{}'.format(from_c, comp.id)
				con = Connection(name, from_c, comp)
				self.architecture.add_connection(con)
		else:
			print('Else statement - this should not happen')
			pass

	def tolerate_fault_by_adding_extra_valve(self, component, fault):
		self.architecture.add_extra_valve_for_component(component, fault)

	def tolerate_valvefault_on_component(self, component, fault):
		if self.ftcomponents:
			if component.type == 'mixer' and fault.control[:4] == 'pump':
				ftcomp = self.architecture.component_library.get_specific_faulttolerance_version_of_component(component, 'pump')
				if ftcomp != None:
					try:
						l = self.architecture.types_to_components[ftcomp.get_type()]
						num = len(l) + 1
					except KeyError:
						num = 1
					componenttype = ftcomp.type
					componentid = str(ftcomp.type) + str(num)
					new_component = Component(componentid, componenttype)
					self.architecture.replace_component_with_other_component(component, new_component)
				else:
					self.tolerate_fault_by_adding_new_component(component, fault)
			else:
				ftcomp = self.architecture.component_library.get_specific_faulttolerance_version_of_component(component, fault.control)
				if ftcomp != None:
					try:
						l = self.architecture.types_to_components[ftcomp.get_type()]
						num = len(l) + 1
					except KeyError:
						num = 1
					componenttype = ftcomp.type
					componentid = str(ftcomp.type) + str(num)
					new_component = Component(componentid, componenttype)
					self.architecture.replace_component_with_other_component(component, new_component)
				else:
					#self.tolerate_fault_by_adding_new_component(component, fault)
					self.tolerate_fault_by_adding_extra_valve(component, fault)
		else:
			#self.tolerate_fault_by_adding_new_component(component, fault)
			if component.type == 'mixer' and fault.control[:4] == 'pump':
				self.tolerate_fault_by_adding_new_component(component, fault)
			elif fault.control[:5] == 'input' or fault.control[:6] == 'output' or component.get_type() == 'switch':
				self.tolerate_fault_by_adding_extra_valve(component, fault)
			else:
				self.tolerate_fault_by_adding_new_component(component, fault)

