'''
Created 24 March 2015

@author: Morten Chabert Eskesen
'''

from queue import Queue
import random

class Architecture(object):
	
	def __init__(self):

		self.id = None
		self.components = set()
		self.size = 0, 0
		self.connections = set()
		self.types_to_components = {}
		self.component_by_name = {}
		self.connection_by_name = {}
		self.original_components = set()
		self.original_connections = set()

		self.connections_removed = set()
		self.components_removed = set()
		self.components_replaced = {}
		self.replaced_by = {}
		self.connections_added = set()
		self.components_replaced_in_connections = {}
		self.components_replaced_out_connections = {}

		self.faults = set()
		#self.component_connections = {}
		#self.componentlibrary = set()
		self.storage = None
		self.average_connection_time = None
		self.component_library = None
		self.discovered_by = {}
		self.component_out_connections = {}
		self.component_in_connections = {}
		self.component_extra_valves = {}

	def remove_component(self, component):
		for incon in component.in_connections.values():
			other = incon.get_other_component(component)
			other.remove_out_connection(component)
			#self.connections_removed.add(incon)
			#self.connections.discard(incon)

		for outcon in component.out_connections.values():
			other = outcon.get_other_component(component)
			other.remove_in_connection(component)
			#self.connections_removed.add(outcon)
			#self.connections.discard(outcon)

		component.faulty = True
		self.components_removed.add(component)
		self.components.discard(component)

	def remove_added_component(self, component):
		for incon in component.in_connections.values():
			other = incon.get_other_component(component)
			other.remove_added_out_connection(component, incon)
			#other.total_out_connections -= 1
			#if other.get_type() == 'switch':
			#	other.total_in_connections -= 1
			#self.connections_removed.add(incon)
			self.connections.discard(incon)

		for outcon in component.out_connections.values():
			other = outcon.get_other_component(component)
			other.remove_added_in_connection(component, outcon)
			#other.total_in_connections -= 1
			#if other.get_type() == 'switch' and other.total_in_connections < other.total_out_connections:
			#	other.total_out_connections = other.total_in_connections
			#self.connections_removed.add(outcon)
			#if other.get_type() == 'switch':
			#	other.total_out_connections -= 1
			self.connections.discard(outcon)

		self.components.discard(component)
		self.types_to_components[component.get_type()].remove(component)

	def remove_replacement_component(self, component):
		for incon in component.in_connections.values():
			other = incon.get_other_component(component)
			other.remove_added_out_connection(component, incon)
			#other.total_out_connections -= 1
			#self.connections_removed.add(incon)
			self.connections.discard(incon)

		for outcon in component.out_connections.values():
			other = outcon.get_other_component(component)
			other.remove_added_in_connection(component, outcon)
			#other.total_in_connections -= 1
			#if other.get_type() == 'switch' and other.total_in_connections < other.total_out_connections:
			#	other.total_out_connections = other.total_in_connections
			#self.connections_removed.add(outcon)
			self.connections.discard(outcon)

		self.components.discard(component)
		self.types_to_components[component.get_type()].remove(component)

	def remove_component_and_connections(self, component):
		for incon in component.in_connections.values():
			other = incon.get_other_component(component)
			other.remove_added_out_connection(component)
			self.connections_removed.add(incon)
			self.connections.discard(incon)

		for outcon in component.out_connections.values():
			other = outcon.get_other_component(component)
			other.remove_added_in_connection(component)
			self.connections_removed.add(outcon)
			self.connections.discard(outcon)

		self.types_to_components[component.get_type()].remove(component)
		#component.faulty = True
		#self.components_removed.add(component)
		#self.components.discard(component)

	def unremove_component_and_connections(self, component):
		for incon in component.in_connections.values():
			other = incon.get_other_component(component)
			other.add_out_connection(component)
			#self.connections_removed.add(incon)
			#self.connections.discard(incon)
			self.connections_removed.discard(incon)
			self.connections.add(incon)

		for outcon in component.out_connections.values():
			other = outcon.get_other_component(component)
			other.add_in_connection(component)
			#self.connections_removed.add(outcon)
			#self.connections.discard(outcon)
			self.connections_removed.discard(outcon)
			self.connections.add(outcon)

	def replaced_component(self, component):
		#self.components_replaced_in_connections[component] = list()
		#self.components_replaced_out_connections[component] = list()
		#for incon in component.in_connections.values():
		#	other = incon.get_other_component(component)
		#	other.remove_out_connection(component)
		#	self.components_replaced_in_connections[component].append(incon)
		#	self.connections.discard(incon)

		for each in component.total_connections:
			self.connections.discard(each)

		#for outcon in component.out_connections.values():
		#	other = outcon.get_other_component(component)
		#	other.remove_in_connection(component)
		#	self.components_replaced_in_connections[component].append(outcon)
		#	self.connections.discard(outcon)

		self.types_to_components[component.get_type()].remove(component)

	def unreplaced_component(self, component):
		#for incon in component.in_connections.values():
		#	other = incon.get_other_component(component)
		#	other.remove_added_out_connection(component)
		#	self.connections_replaced.remove(incon)
		#	self.connections.add(incon)

		#for outcon in component.out_connections.values():
		#	other = outcon.get_other_component(component)
		#	other.remove_added_in_connection(component)
		#	self.connections_replaced.remove(outcon)
		#	self.connections.add(outcon)

		self.types_to_components[component.get_type()].append(component)

	def remove_added_connection(self, connection):
		from_c = connection.components[0]
		to_c = connection.components[1]
		#from_c.total_out_connections -= 1

		#if(from_c.get_type() == 'switch'):
		#	from_c.total_in_connections -= 1

		#to_c.total_in_connections -= 1
		#if(to_c.get_type() == 'switch'):
		#	to_c.total_out_connections -= 1

		from_c.remove_added_in_connection(to_c, connection)
		from_c.remove_added_out_connection(to_c, connection)

		to_c.remove_added_in_connection(from_c, connection)
		to_c.remove_added_out_connection(from_c, connection)
		self.connections.discard(connection)

	def remove_connection(self, connection):
		from_c = connection.components[0]
		to_c = connection.components[1]

		from_c.remove_in_connection(to_c)
		from_c.remove_out_connection(to_c)

		to_c.remove_in_connection(from_c)
		to_c.remove_out_connection(from_c)
		self.remove_connection_from_arch(connection)

	def parsing_done(self):
		self.original_components = self.components.copy()
		self.original_connections = self.connections.copy()

	def remove_connection_from_arch(self, connection):
		if connection != None:
			self.connections_removed.add(connection)
			self.connections.discard(connection)

	def find_connections_between_two_switches(self, num):
		switches_in_architecture = list(filter(lambda s: s.type[:6] == 'switch', self.components))
		if num == 0 or num > 2:
			pass
		elif num == 1:
			#find one connection
			con = None
			for each in self.connections:
				if each.components[0].type[:6] == 'switch' and each.components[1].type[:6] == 'switch':
					con = each
					break
			return con
		else:
			con1 = None
			con2 = None
			for each in self.connections:
				if each.components[0].type[:6] == 'switch' and each.components[1].type[:6] == 'switch' and con1 == None:
					con1 = each
					continue
				if each.components[0].type[:6] == 'switch' and each.components[1].type[:6] == 'switch' and con2 == None:
					con2 = each
					break
			return con1, con2

	def add_extra_valve_for_component(self, component, fault):
		try:
			self.component_extra_valves[component].append(fault.control)
		except KeyError:
			self.component_extra_valves[component] = list()
			self.component_extra_valves[component].append(fault.control)
		self.extra_valve_added_for_component(component, fault)

	def extra_valve_added_for_component(self, component, fault):
		component.remove_fault(fault)
		if not component.faulty:
			self.components.add(component)
			self.components_removed.discard(component)
			for incon in component.in_connections.values():
				other = incon.get_other_component(component)
				other.add_out_connection(component, incon)
				self.connections.add(incon)
				self.connections_removed.discard(incon)

			for outcon in component.out_connections.values():
				other = outcon.get_other_component(component)
				other.add_in_connection(component, outcon)
				self.connections.add(outcon)
				self.connections_removed.discard(outcon)

	def modify_connection_to_have_comp_in_middle(self, connection, component):
		#This is only used by connections between switches and a component that is a switch
		print('Modifying connection: '+str(connection))
		from_c = connection.components[0]
		to_c = connection.components[1]
		#from_c.remove_in_connection(from_c)
		from_c.remove_added_in_connection(to_c)
		#from_c.remove_out_connection(to_c)
		from_c.remove_added_out_connection(to_c)
		#to_c.remove_in_connection(from_c)
		to_c.remove_added_in_connection(from_c)
		#to_c.remove_out_connection(from_c)
		to_c.remove_added_out_connection(from_c)
		self.connections.discard(connection)
		con1name = 'con-{}-{}'.format(from_c.id, component.id)
		con1 = Connection(con1name, from_c, component)
		con2name = 'con-{}-{}'.format(component.id, to_c.id)
		con2 = Connection(con2name, component, to_c)
		self.connections.add(con1)
		self.connection_by_name[con1.name] = con1
		self.connections.add(con2)
		self.connection_by_name[con2.name] = con2
		from_c.add_in_connection(component, con1)
		from_c.add_out_connection(component, con1)
		to_c.add_in_connection(component, con2)
		to_c.add_out_connection(component, con2)
		component.add_in_connection(from_c, con1)
		component.add_out_connection(from_c, con1)
		component.add_in_connection(to_c, con2)
		component.add_out_connection(to_c, con2)
		#component.total_out_connections += 2
		#component.total_in_connections += 2

	def find_two_available_switches(self):
		switches_in_architecture = list(filter(lambda s: s.type[:6] == 'switch', self.components))
		switch1 = None
		switch2 = None
		for each in switches_in_architecture:
			if each.total_out_connections() < 4 and switch1 == None:
				switch1 = each
				continue
			if each.total_out_connections() < 4 and switch2 == None:
				switch2 = each
				break
		return switch1, switch2

	def generate_switch_valve_connections(self):
		switches_in_architecture = list(filter(lambda s: s.type[:6] == 'switch', self.components))

		for switch in switches_in_architecture:
			outconlen = len(switch.out_connections)
			inconlen = len(switch.in_connections)
			connections = max(outconlen, inconlen)
			switches = list(filter(lambda s: s.valves == connections and s.type[:6] == 'switch', self.component_library.librarycomponents))
			comp = random.choice(switches)
			valvelist = list()
			valvelist.extend(comp.valvelist)

			if outconlen > inconlen:
				outcons = switch.out_connections.values()
				for oc in outcons:
					valvename = random.choice(valvelist)
					switch.valve_to_connections[valvename] = oc
					valvelist.remove(valvename)
			else:
				incons = switch.in_connections.values()
				for ic in incons:
					valvename = random.choice(valvelist)
					switch.valve_to_connections[valvename] = ic
					valvelist.remove(valvename)

	def unreplace_component(self, org_component, rep_component):
		#self.components_replaced.discard(org_component)
		#self.remove_component_and_connections(rep_component)
		if self.components_replaced[org_component] == 'removed':
			self.components_removed.add(org_component)
		if self.components_replaced[org_component] == 'added':
			self.components.add(org_component)
			#self.unremove_component_and_connections(org_component)

		self.components_replaced.pop(org_component)
		self.replaced_by.pop(org_component)
		#self.remove_added_component(rep_component)
		self.remove_replacement_component(rep_component)

		for each in rep_component.total_connections:
			other = each.get_other_component(rep_component)
			name = each.name
			other.remove_added_in_connection(rep_component, each)
			other.remove_added_out_connection(rep_component, each)
			
			if rep_component == each.components[0]:
				con = Connection(name, org_component, other)
			else:
				con = Connection(name, other, org_component)
			
			if self.component_library.route_through_component(con.components[0]) and self.component_library.route_through_component(con.components[1]):
				#con.components[0].out_connections[con.components[1]] = con
				con.components[0].add_out_connection(con.components[1], con)
				#con.components[1].in_connections[con.components[0]] = con
				con.components[1].add_in_connection(con.components[0], con)

				#con.components[1].out_connections[con.components[0]] = con
				con.components[1].add_out_connection(con.components[0], con)
				#con.components[0].in_connections[con.components[1]] = con
				con.components[0].add_in_connection(con.components[1], con)
			else:
				con.components[1].add_in_connection(con.components[0], con)
				con.components[0].add_out_connection(con.components[1], con)

			self.connections.add(con)
			self.connection_by_name[con.name] = con

		#for incon in self.components_replaced_in_connections[org_component]:
		#	other = incon.get_other_component(org_component)
		#	other.add_out_connection(org_component, incon)
		#	self.connections.add(incon)
		#	self.connection_by_name[incon.name] = incon

		#for outcon in self.components_replaced_out_connections[org_component]:
		#	other = outcon.get_other_component(org_component)
		#	other.add_in_connection(org_component, outcon)
		#	self.connections.add(outcon)
		#	self.connection_by_name[outcon.name] = outcon

		#org_component.total_in_connections = rep_component.total_in_connections
		#org_component.total_out_connections = rep_component.total_out_connections
		#org_component.added_out_connections = rep_component.added_out_connections
		#org_component.added_in_connections = rep_component.added_out_connections
		#org_component.removed_in_connections = rep_component.removed_in_connections
		#org_component.removed_out_connections = rep_component.removed_out_connections
		org_component.faults = list()
		org_component.faults.extend(rep_component.faults)
		#self.components_replaced_in_connections.pop(org_component)
		#self.components_replaced_out_connections.pop(org_component)
		self.types_to_components[org_component.get_type()].append(org_component)
		#cons_to_remove = list(rep_component.out_connections.values()) + list(rep_component.in_connections.values())
		cons_to_remove = rep_component.total_connections
		for each in cons_to_remove:
			print('Removing connection: '+str(each))
			self.connections.discard(each)
		#self.types_to_components[rep_component.get_type()].remove(rep_component)

	def replace_component_with_other_component(self, component, other_component):
		#remove connections from other components
		self.add_component(other_component)

		for each in component.total_connections:
			other = each.get_other_component(component)
			name = each.name
			other.remove_added_in_connection(component, each)
			other.remove_added_out_connection(component, each)
			if component == each.components[0]:
				con = Connection(name, other_component, other)
			else:
				con = Connection(name, other, other_component)

			if self.component_library.route_through_component(con.components[0]) and self.component_library.route_through_component(con.components[1]):
				#con.components[0].out_connections[con.components[1]] = con
				con.components[0].add_out_connection(con.components[1], con)
				#con.components[1].in_connections[con.components[0]] = con
				con.components[1].add_in_connection(con.components[0], con)

				#con.components[1].out_connections[con.components[0]] = con
				con.components[1].add_out_connection(con.components[0], con)
				#con.components[0].in_connections[con.components[1]] = con
				con.components[0].add_in_connection(con.components[1], con)
			else:
				con.components[1].add_in_connection(con.components[0], con)
				con.components[0].add_out_connection(con.components[1], con)

			self.connections.add(con)
			self.connection_by_name[con.name] = con

		#for incon in component.in_connections.values():
		#	other = incon.get_other_component(component)
			#name = 'con-{}-{}'.format(other.id, other_component.id)
		#	name = incon.name
		#	con = Connection(name, other, other_component)
		#	other.add_out_connection(other_component, con)
		#	other_component.add_in_connection(other, con)
		#	self.connections.add(con)
		#	self.connection_by_name[con.name] = con

		#for outcon in component.out_connections.values():
		#	other = outcon.get_other_component(component)
			#name = 'con-{}-{}'.format(other_component.id, other.id)
		#	name = outcon.name
		#	con = Connection(name, other_component, other)
		#	other.add_in_connection(other_component, con)
		#	other_component.add_out_connection(other, con)
		#	self.connections.add(con)
		#	self.connection_by_name[con.name] = con

		#other_component.total_in_connections = component.total_in_connections
		#other_component.total_out_connections = component.total_out_connections
		#other_component.added_out_connections = component.added_out_connections
		#other_component.added_in_connections = component.added_out_connections
		#other_component.removed_in_connections = component.removed_in_connections
		#other_component.removed_out_connections = component.removed_out_connections
		other_component.faults = list()
		other_component.faults.extend(component.faults)
		#self.types_to_components[other_component.get_type()].append(other_component)
		#self.types_to_components[component.get_type()].remove(component)
		#self.components_replaced.add(component)
		if component in self.components_removed:
			self.components_removed.discard(component)
			self.replaced_by[component] = other_component
			self.components_replaced[component] = 'removed'
		if component in self.components:
			#self.remove_component_and_connections(component)
			self.replaced_component(component)
			self.replaced_by[component] = other_component
			#self.components.discard(component)
			self.components.remove(component)
			#print(self.components)
			self.components_replaced[component] = 'added'

	def affect_storage_with_channel_fault(self, storage, channelfault):
		if len(storage.faults) == 3:
			self.remove_component(storage)
			storage.faults.append(channelfault)
		#elif storage.faults >= 4:
		#	storage.faults.append(channelfault)
		else:
			storage.faults.append(channelfault)

	def affect_component_with_open_valve_fault(self, component, valvefault):
		if component.get_type() == 'storage':
			self.affect_storage_with_open_valve_fault(component, valvefault)
		elif component.get_type() == 'filter':
			self.affect_filter_with_open_valve_fault(component, valvefault)
		elif component.get_type() == 'heater':
			self.affect_heater_with_open_valve_fault(component, valvefault)
		elif component.get_type() == 'detector':
			self.affect_heater_with_open_valve_fault(component, valvefault)
		else:
			pass

	def affect_storage_with_open_valve_fault(self, storage, valvefault):
		if len(storage.faults) == 3:
			self.remove_component(storage)
			storage.faults.append(valvefault)
		#elif storage.faults >= 4:
		#	storage.faults.append(valvefault)
		else:
			storage.faults.append(valvefault)

	def affect_filter_with_open_valve_fault(self, filterc, valvefault):
		if filterc.is_fault_tolerant():
			filterc.faults.append(valvefault)
		elif filterc.faulty:
			filterc.faults.append(valvefault)
		else:
			self.remove_component(filterc)

	def affect_detector_with_open_valve_fault(self, detector, valvefault):
		if detector.is_fault_tolerant():
			detector.faults.append(valvefault)
		elif detector.faulty:
			dectector.faults.append(valvefault)
		else:
			self.remove_component(detector)

	def affect_heater_with_open_valve_fault(self, heater, valvefault):
		if heater.is_fault_tolerant():
			heater.faults.append(valvefault)
		elif heater.faulty:
			heater.faults.append(valvefault)
		else:
			self.remove_component(detector)

	def affect_switch_with_open_valve_fault(self, switch, valvefault):
		if not switch.faults:
			#No faults already - hard part
			#We can only route to the valvefault.control connection if input is from other connections
			#We can route wherever when the input is from the valvefault.control connection

			#REMOVE THE CONNECTIONS FROM THE OTHER COMPONENTS
			switch.faults.append(valvefault)
			#con = switch.valve_to_connections[valvefault.control]
			con = self.connection_by_name[valvefault.affected]
			if con in switch.removed_out_connections:
				self.remove_component(switch) #the connection is blocked and cannot be used therefore the switch should be removed
		else:
			if any(type(f).__name__ == 'ChannelFault' for f in switch.faults):
				#Already removed - do nothing but add the fault
				switch.faults.append(valvefault)
			elif len(switch.faults) >= 2:
				switch.faults.append(valvefault)
				self.remove_component(switch)
			else:
				otherfault = switch.faults[0]
				if not otherfault == valvefault:
					othercon = self.connection_by_name[otherfault.affected]
					#othercon = switch.valve_to_connections[otherfault.control] 
					con = self.connection_by_name[valvefault.affected]
					#con = switch.valve_to_connections[valvefault.control]
					if con in switch.removed_out_connections or othercon in switch.removed_out_connections:
						self.remove_component(switch) #one of the connections is faulty and removed from the architecture
					else:
						othercon_othercomponent = othercon.get_other_component(switch)
						con_othercomponent = con.get_other_component(switch)

						remove_out = set()
						remove_in = set()

						for outcom in switch.out_connections.keys():
							if outcom != othercon_othercomponent and outcom != con_othercomponent:
								remove_out.add(outcom)
								#self.remove_connection_from_arch(switch.out_connections[outcom])

						for incom in switch.in_connections.keys():
							if incom != othercon_othercomponent and incom != con_othercomponent:
								remove_in.add(incom)
								#self.remove_connection_from_arch(switch.out_connections[incom])
						
						for each in remove_out:
							c = each.remove_in_connection(switch)
							c2 = each.remove_out_connection(switch)
							c3 = switch.remove_out_connection(each)
							self.remove_connection_from_arch(c)
							self.remove_connection_from_arch(c2)
							self.remove_connection_from_arch(c3)

						for each in remove_in:
							c = each.remove_in_connection(switch)
							c2 = each.remove_out_connection(switch)
							c3 = switch.remove_in_connection(each)
							self.remove_connection_from_arch(c)
							self.remove_connection_from_arch(c2)
							self.remove_connection_from_arch(c3)
					switch.faults.append(valvefault)

	def add_fault(self, fault):
		#Generate the effects of the fault
		#Store the effects of the fault to be able to restore the architecture
		#We are able to route through a mixer even though a channel is broken, because it has two channels
		#But the mixer can not function
		#Storage component? - we can still route
		self.faults.add(fault)
		if type(fault).__name__ == 'ChannelFault' and fault.type == 'block':
			if fault.objecttype == 'component':
				component = self.component_by_name[fault.objectname]
				if component in self.replaced_by:
					component = self.replaced_by[component]
				if component.get_type() == 'mixer':
					if component.faulty:
						component.faults.append(fault)
						self.remove_component(component)
					else:
						component.faults.append(fault)
						component.faulty = True
				if component.get_type() == 'storage':
					self.affect_storage_with_blocked_channel_fault(component, fault)
				else:
					if self.component_library.get_faulttolerance_for_component(component) == 'channel':
						if any(type(f).__name__ == 'ChannelFault' for f in component.faults):
							self.remove_component(component)
						component.faults.append(fault)
					else:
						component.faults.append(fault)
						self.remove_component(component)
			if fault.objecttype == 'connection':
				self.remove_connection(self.connection_by_name[fault.objectname])
		if type(fault).__name__ == 'ValveFault' and fault.type == 'open':
			if fault.objecttype == 'component':
				component = self.component_by_name[fault.objectname]
				if component.get_type() == 'mixer':
					compf = self.component_library.get_faulttolerance_for_component(component)
					if self.component_library.get_faulttolerance_for_component(component) == fault.affected:
						components.faults.append(fault)
					elif component.faulty:
						component.faults.append(fault)
						self.remove_component(component)
					else:
						component.faults.append(fault)
						component.faulty = True
				elif component.get_type() == 'switch':
					self.affect_switch_with_open_valve_fault(component, fault)
				else:
					valvelist = self.component_library.get_valvelist_for_component(component)
					if len(valvelist) <= 2:
						component.faults.append(fault)
						self.remove_component(component)
					else:
						self.affect_component_with_open_valve_fault(component, fault)
					#compf = self.component_library.get_faulttolerance_for_component(component)
					#fc = fault.control[:4]
					#if compf == fc:
					#	component.faults.append(fault)
					#else:
					#	component.faults.append(fault)
					#	self.remove_component(component)

	def restore(self):
		#Restore / reset the architecture to normal after being affected by faults
		for each in self.components_removed:
			if each not in self.components_replaced:
				self.components.add(each)
		for each in self.connections_removed:
			self.connections.add(each)

		for each in self.components:
			each.restore()
		self.connections_removed = set()
		self.components_removed = set()
		self.faults = set()

	def add_component(self, c):
		self.components.add(c)
		self.component_by_name[c.id] = c
		if c.get_type() == 'storage':
			if self.storage == None:
				self.storage = c
		try:
			self.types_to_components[c.get_type()].append(c)
		except KeyError:
			self.types_to_components[c.get_type()] = list()
			self.types_to_components[c.get_type()].append(c)
		#if c.connections is not None:
		#	self.component_connections[c] = c.connections

	def number_of_valves(self):
		allcomponents = list(self.components) + list(self.components_removed)
		total_valves = 0
		for each in allcomponents:
			if each.get_type() == 'switch':
				valves = each.total_out_connections()
			elif each.get_type() == 'input' or each.get_type() == 'output':
				valves = len(self.component_library.get_valvelist_for_component(each))
			else:
				valves = len(self.component_library.get_valvelist_for_component(each))
				valves = valves - 2
				valves += each.total_in_connections()
				valves += each.total_out_connections()
			total_valves += valves
		return total_valves

	def number_of_connections(self):
		return len(self.connections_removed) + len(self.connections)

	def add_connection(self, con):
		self.connections.add(con)
		self.connection_by_name[con.name] = con
		#con.components[0].total_out_connections += 1

		#if(con.components[0].get_type() == 'switch'):
		#	con.components[0].total_in_connections += 1

		#con.components[1].total_in_connections += 1
		#if(con.components[1].get_type() == 'switch'):
		#	con.components[1].total_out_connections += 1

		if self.component_library.route_through_component(con.components[0]) and self.component_library.route_through_component(con.components[1]):
			self.add_bidirectional_connection(con)
		else:
			#con.components[0].out_connections[con.components[1]] = con
			con.components[0].add_out_connection(con.components[1], con)

			#con.components[1].in_connections[con.components[0]] = con
			con.components[1].add_in_connection(con.components[0], con)

	def add_bidirectional_connection(self, con):
		#con.components[0].out_connections[con.components[1]] = con
		con.components[0].add_out_connection(con.components[1], con)
		#con.components[1].in_connections[con.components[0]] = con
		con.components[1].add_in_connection(con.components[0], con)

		#con.components[1].out_connections[con.components[0]] = con
		con.components[1].add_out_connection(con.components[0], con)
		#con.components[0].in_connections[con.components[1]] = con
		con.components[0].add_in_connection(con.components[1], con)

	def unschedule(self):
		for comp in self.components:
			comp.unschedule()
		for con in self.connections:
			con.unschedule()

	def generate_out_connections_for_component_coming_from(self, component, from_c):
		#component_out_connections = {}
		if component.type != 'switch':
			self.component_out_connections[component] = component.out_connections.values()
			#component_out_connections[component] = component.out_connections.values()
			#return component_out_connections
		elif len(component.faults) > 1 or not component.faults:
			self.component_out_connections[component] = component.out_connections.values()
			#component_out_connections[component] = component.out_connections.values()
			#return component_out_connections
		else:
			out_connections = set()
			#faultconname = component.faults[0].control
			#faultconname = self.find_connection_for_switch_by_valvename(component, component.faults[0])
			con = self.connection_by_name[component.faults[0].affected]
			#con = component.valve_to_connections[component.faults[0].control]
			if con.get_other_component(component) == from_c:
				self.component_out_connections[component] = component.out_connections.values()
				#component_out_connections[component] = component.out_connections.values()
				#return component_out_connections
			else:
				out_connections.add(con)
				self.component_out_connections[component] = out_connections
				#component_out_connections[component] = out_connections
				#return component_out_connections

	def get_components_of_type(self, ctype):
		components = list()
		for each in self.types_to_components[ctype]:
			#if not each.out_connections or not each.in_connections or each.faulty:
			#	pass
			if ctype != 'output':
				if each.faulty or each in self.components_removed or each in self.components_replaced or len(each.out_connections) == 0:
					pass
				else:
					components.append(each)
			else:
				if each.faulty or each in self.components_removed or each in self.components_replaced or len(each.in_connections) == 0:
					pass
				else:
					components.append(each)
		return components

	def find_route(self, from_c, to_c):
		print('Finding route from: '+str(from_c)+' to '+str(to_c))
		self.breadth_first_search(from_c, to_c)
		#print('Finding route from: '+str(from_c)+' to '+str(to_c))
		return self.backtrack_breadth_first_search(from_c, to_c)

	def is_connected(self):
		visited = set()
		inputs = list(filter(lambda c: c.type[:5] == 'input', self.components))
		allcomponents = list(self.components) + list(self.components_removed)
		minus_inputs = len(inputs) - 1
		start = random.choice(inputs)
		#start = self.component_by_name['In2']

		q = Queue()
		q.put(start)
		visited.add(start)
		self.generate_out_connections_for_component_coming_from(start, None)

		while(not q.empty()):
			v = q.get()

			v_out = list(v.removed_out_connections.values()) + list(v.out_connections.values())

			print('Current component: '+str(v))
			print('Out connections: '+str(v_out))
			#for each in v.out_connections.values():
			for each in v_out:
				if each in self.connections_removed:
					continue
				w = each.get_other_component(v)
				self.generate_out_connections_for_component_coming_from(w, v)
				if w not in visited and each in self.component_out_connections[v]:
					#self.discovered_by[w] = v
					if self.component_library.route_through_component(w):
						q.put(w)
					visited.add(w)

		#self.discovered_by = {}
		self.component_out_connections = {}
		return len(visited) == (len(allcomponents) - minus_inputs)


	def test_is_connected(self):
		allcomponents = set(self.components) | set(self.components_removed)
		pos_comps = set(filter(lambda c: c.type[:5] != 'input' and c.type[:6] != 'output', allcomponents))
		if any(len(c.in_connections.values()) == 0 for c in pos_comps):
			return False
		else:
			return True
		#for c in allcomponents:
		#	if any(type(f).__name__ == 'ChannelFault' for f in switch.faults):
		#	if not any(c.in_connections.values() for c in self.connections)
		#unreachable_comps = set(filter(lambda comp: ,allcomponents))

	def find_route(self, from_c, to_c):
		print('Finding route from: '+str(from_c)+' to '+str(to_c))
		#self.breadth_first_search(from_c, to_c)
		disc = self.reverse_route_finding(from_c, to_c)
		#print('Finding route from: '+str(from_c)+' to '+str(to_c))
		#print('discovered_by')
		#print(disc)
		return self.backtrack_reverse(from_c, to_c, disc)

	def generate_in_connections_for_component_going_to(self, component, to_c):
		if component.type != 'switch':
			#self.component_out_connections[component] = component.out_connections.values()
			self.component_in_connections[component] = set(component.in_connections.values())
			#return component_out_connections
		elif len(component.faults) > 1 or not component.faults:
			self.component_in_connections[component] = set(component.in_connections.values())
			#component_out_connections[component] = component.out_connections.values()
			#return component_out_connections
		else:
			in_connections = set()
			#faultconname = component.faults[0].control
			#faultconname = self.find_connection_for_switch_by_valvename(component, component.faults[0])
			con = self.connection_by_name[component.faults[0].affected]
			#con = component.valve_to_connections[component.faults[0].control]
			if con.get_other_component(component) == to_c:
				self.component_in_connections[component] = set(component.in_connections.values())
				#component_out_connections[component] = component.out_connections.values()
				#return component_out_connections
			else:
				in_connections.add(con)
				self.component_in_connections[component] = in_connections
				#component_out_connections[component] = out_connections
				#return component_out_connections


	def reverse_route_finding(self, start, end):
		visited = set()
		discovered_by = {}
		discovered_by[end] = None
		
		self.generate_in_connections_for_component_going_to(end, None)
		q = Queue()
		q.put(end)
		visited.add(end)

		while(not q.empty()):
			v = q.get()

			for each in v.in_connections.values():
				w = each.get_other_component(v)

				self.generate_in_connections_for_component_going_to(w, v)

				if w not in visited and each in self.component_in_connections[v]:
					#if type(w).__name__ == 'Component' and w != end and w != start:
					#	pass
					#else:
					#if type(w).__name__ == 'Component' and w != end and w != start and w.occupied_by:
					#	print(str(w) + ' has been passed')
					#	pass
					#else:
					discovered_by[w] = v
					if self.component_library.route_through_component(w):
						q.put(w)
					visited.add(w)

		return discovered_by

	def backtrack_reverse(self, from_component, to_component, discovered_by):
		connections = []
		previous = from_component
		
		try:
			current = discovered_by[from_component]
			backtracked = True
		except KeyError:
			current = None
			backtracked = False

		print('Backtracked: '+str(backtracked))


		while(current != None and previous != to_component):
			connection = current.in_connections[previous]
			#connections.insert(0, connection)
			connections.append(connection)
			previous = current
			current = discovered_by[current]

		if backtracked:
			routetime = len(connections) * self.average_connection_time
			r = Route(from_component, to_component, connections, routetime)
		else:
			r = None
		#self.discovered_by = {}
		self.component_in_connections = {}
		return r

	'''
	def find_route(self, from_c, to_c):
		print('Finding route from: '+str(from_c)+' to '+str(to_c))
		self.breadth_first_search(from_c, to_c)
		#print('Finding route from: '+str(from_c)+' to '+str(to_c))
		return self.backtrack_breadth_first_search(from_c, to_c)

	def breadth_first_search(self, start, end):
		visited = set()
		self.discovered_by[start] = None

		q = Queue()
		q.put(start)
		visited.add(start)
		self.generate_out_connections_for_component_coming_from(start, None)

		while(not q.empty()):
			v = q.get()
			#print('At component: '+str(v))

			#print('All out connections: '+str(v.out_connections.values()))
			for each in v.out_connections.values():
				#print(each)
				w = each.get_other_component(v)
				#print('Generating out connections for '+str(w)+ ' coming from '+str(v))
				self.generate_out_connections_for_component_coming_from(w, v)
				#print('Out connections for '+str(w)+': '+str(self.component_out_connections[v]))
				if w not in visited and each in self.component_out_connections[v]:
					if type(w).__name__ == 'Component' and w != end and w != start and w.occupied_by:
						pass
					else:
						#print(str(w)+' was discovered by '+str(v))
						self.discovered_by[w] = v
						if self.component_library.route_through_component(w):
							q.put(w)
						visited.add(w)


	def backtrack_breadth_first_search(self, from_component, to_component):
		connections = []
		previous = to_component
		
		try:
			current = self.discovered_by[to_component]
			backtracked = True
		except KeyError:
			current = None
			backtracked = False

		print('Backtracked: '+str(backtracked))


		while(current != None and previous != from_component):
			connection = current.out_connections[previous]
			connections.insert(0, connection)
			previous = current
			current = self.discovered_by[current]

		if backtracked:
			routetime = len(connections) * self.average_connection_time
			r = Route(from_component, to_component, connections, routetime)
		else:
			r = None
		self.discovered_by = {}
		self.component_out_connections = {}
		return r

	'''
	def __str__(self):

		components = list(self.components)
		components.sort()
		connections = list(self.connections)
		connections.sort()

		s = 'Architecture:\n'
		#s += 'Width: {}\n'.format(self.size[0])
		#s += 'Height: {}\n'.format(self.size[1])
		s += 'Components({})\n'.format(len(components))
		for each in components:
			s += ' ' + str(each) + '\n'
		s += 'Connections({})\n'.format(len(connections))
		for each in connections:
			s += ' ' + str(each) + '\n'
		return s



class Ordered(object):
	order_id_counter = 0
	
	def __init__(self):
		self.order_id = __class__.order_id_counter
		__class__.order_id_counter = +1

	def __lt__(self, other):
		return self.order_id < other.order_id


class Component(Ordered):
	def __init__(self, componentid, componenttype):

		super().__init__()

		self.id = componentid
		self.type = componenttype
		self.in_connections = {}
		self.out_connections = {}
		#self.in_connections = set()
		#self.out_connections = set()

		self.added_in_connections = {}
		self.added_out_connections = {}

		self.total_connections = set()

		#self.total_in_connections = 0
		#self.total_out_connections = 0

		self.occupied_by = None
		self.operations = set()
		self.finish_time = 0
		self.valve_to_connections = {}

		self.faulty = False
		self.faults = list()
		self.removed_out_connections = {}
		self.removed_in_connections = {}

	def unschedule(self):
		self.occupied_by = None
		self.operations = set()
		self.finish_time = 0

	def add_out_connection(self, component, connection):
		self.total_connections.add(connection)
		if component in self.out_connections:
			self.added_out_connections[component] = connection
		else:
			self.out_connections[component] = connection

	def add_in_connection(self, component, connection):
		self.total_connections.add(connection)
		#con.components[1].in_connections[con.components[0]] = con
		if component in self.in_connections:
			self.added_in_connections[component] = connection
		else:
			self.in_connections[component] = connection

	def total_in_connections(self):
		if self.get_type() == 'switch':
			return len(self.total_connections)
			#if len(self.out_connections) < len(self.in_connections):
			#	return len(self.in_connections)
			#else:
			#	return len(self.out_connections)
		else:
			in_con = 0
			#print(self)
			#print(self.total_connections)
			#print(self.in_connections.values())
			for each in self.total_connections:
				if self == each.components[1]:
					in_con += 1
			#for each in self.in_connections.values():
			#	if self == each.components[1]:
			#		in_con += 1
			return in_con
			#return len(self.in_connections)

	def total_out_connections(self):
		if self.get_type() == 'switch':
			return len(self.total_connections)
			#if len(self.out_connections) < len(self.in_connections):
			#	return len(self.in_connections)
			#else:
			#	return len(self.out_connections)
		else:
			out_con = 0
			#print(self.out_connections.values())
			for each in self.total_connections:
				if self == each.components[0]:
					out_con += 1
			#for each in self.out_connections.values():
			#	if self == each.components[0]:
			#		out_con += 1
			return out_con
			#return len(self.out_connections)


	def remove_added_out_connection(self, component, connection):
		try:
			if component in self.added_out_connections:
				con_add = self.added_out_connections[component]
			else:
				con_add = None

			if component in self.out_connections:
				con_org = self.out_connections[component]
			else:
				con_org = None

			if con_add == connection:
				self.added_out_connections.pop(component)

			if con_org == connection:
				self.out_connections.pop(component)
			#con = self.out_connections.pop(component)
			#self.total_connections.discard(con)
			self.total_connections.discard(connection)
			#self.removed_out_connections[component] = con
			#if component in self.added_out_connections:
			#	con1 = self.out_connections[component]
				#if con1.get_other_component(component) != self:
				#	if con1.components[0] == component:
				#		con1.components[1] = self
				#	else:
				#		con1.components[0] = self
			#	self.total_connections.add(con1)
			#	self.out_connections[component] = con1
			#	self.added_out_connections.pop(component)
			return connection
		except KeyError:
			return None

	def remove_added_in_connection(self, component, connection):
		try:
			if component in self.added_in_connections:
				con_add = self.added_in_connections[component]
			else:
				con_add = None

			if component in self.in_connections:
				con_org = self.in_connections[component]
			else:
				con_org = None

			if con_add == connection:
				self.added_in_connections.pop(component)

			if con_org == connection:
				self.in_connections.pop(component)

			#con = self.in_connections.pop(component)
			#self.total_connections.discard(con)
			self.total_connections.discard(connection)
			#self.removed_in_connections[component] = con
			#if component in self.added_in_connections:
			#	con1 = self.added_in_connections[component]
				#if con1.get_other_component != self:
				#	if con1.components[0] == component:
				#		con1.components[1] = self
				#	else:
				#		con1.components[0] = self
			#	self.in_connections[component] = con1
			#	self.total_connections.add(con1)
			#	self.added_in_connections.pop(component)
			return connection
		except KeyError:
			return None

	def remove_out_connection(self, component):
		try:
			con = self.out_connections.pop(component)
			self.removed_out_connections[component] = con
			if component in self.added_out_connections:
				con1 = self.added_out_connections[component]
				#if con1.get_other_component(component) != self:
				#	if con1.components[0] == component:
				#		con1.components[1] = self
				#	else:
				#		con1.components[0] = self
				self.out_connections[component] = con1
				self.added_out_connections.pop(component)
			return con
		except KeyError:
			return None

	def remove_fault(self, fault):
		self.faults.remove(fault)
		if len(self.faults) == 0:
			self.restore()

	def remove_in_connection(self, component):
		try:
			con = self.in_connections.pop(component)
			self.removed_in_connections[component] = con
			if component in self.added_in_connections:
				con1 = self.added_in_connections[component]
				#if con1.get_other_component != self:
				#	if con1.components[0] == component:
				#		con1.components[1] = self
				#	else:
				#		con1.components[0] = self
				self.in_connections[component] = con1
				self.added_in_connections.pop(component)
			return con
		except KeyError:
			return None

	def restore(self):
		#Restore component from the faults
		for each in self.removed_in_connections.keys():
			con = self.removed_in_connections[each]
			if each in self.in_connections:
				self.added_in_connections[each] = self.in_connections[each]
			self.in_connections[each] = con
		for each in self.removed_out_connections.keys():
			con = self.removed_out_connections[each]
			if each in self.out_connections:
				self.added_out_connections[each] = self.out_connections[each]
			self.out_connections[each] = con
		self.faulty = False
		self.faults = list()
		self.removed_in_connections = {}
		self.removed_out_connections = {}

	def is_fault_tolerant(self):
		return self.type[:2] == 'ft'

	def is_fault_tolerant_version_of(self, other):
		typelength = len(self.type)
		return self.type[2:typelength] == other.type

	def __repr__(self):
		return self.id

	def get_type(self):
		if self.is_fault_tolerant():
			typelength = len(self.type)
			return self.type[2:typelength]
		else:
			return self.type

	def schedule(self, o):
		self.operations.add(o)
		self.finish_time = o.finish_time

	def __str__(self):
		return 'Component: {}'.format(self.id)

	def __hash__(self):
		return hash(self.id)

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.id == other.id


class Connection(Ordered):

	def __init__(self, name, c1, c2):
		
		super().__init__()

		self.components = [c1, c2]

		self.name = name
		self.id = (c1.id, c2.id)
		self.finish_time = 0

	def unschedule(self):
		self.finish_time = 0

	def get_other_component(self, component):
		if component == self.components[0]:
			return self.components[1]
		else:
			return self.components[0]

	def __hash__(self):
		#return hash(self.name + self.id)
		return hash(self.name + ' ' +self.components[0].id +' ' +self.components[1].id)

	def __repr__(self):
		#return self.name + self.id
		return self.name + ' ' +self.components[0].id +' ' +self.components[1].id

	def __str__(self):
		return 'Connection {}: {}'.format(self.name, self.id)

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.id == other.id and self.name == other.name

class ComponentLibrary(object):
	def __init__(self):
		self.librarycomponents = set()
		self.type_to_routing = {}
		self.type_to_faulttolerance = {}
		self.type_to_valvelist = {}
		self.component_types_with_fault_tolerant_versions = list()

	def add_component(self, libcomponent):
		self.librarycomponents.add(libcomponent)
		self.type_to_routing[libcomponent.type] = libcomponent.routing
		self.type_to_faulttolerance[libcomponent.type] = libcomponent.faulttolerant
		self.type_to_valvelist[libcomponent.type] = libcomponent.valvelist

	def get_types_with_a_fault_tolerant_version(self):
		if len(self.component_types_with_fault_tolerant_versions) == 0:
			for each in self.librarycomponents:
				if each.is_fault_tolerant():
					self.component_types_with_fault_tolerant_versions.append(each.get_type())
			return self.component_types_with_fault_tolerant_versions
		else:
			return self.component_types_with_fault_tolerant_versions

	def route_through_component(self, component):
		return self.type_to_routing[component.type]
		#comptype = component.type
		#for each in self.librarycomponents:
		#	if comptype == each.type:
		#		return each.routing

	def get_valvelist_for_component(self, component):
		return self.type_to_valvelist[component.type]

	def get_faulttolerance_for_component(self, component):
		return self.type_to_faulttolerance[component.type]

	def get_faulttolerance_version_of_component(self, component):
		c = None
		for each in self.librarycomponents:
			if each.is_fault_tolerant_version_of(component):
				c = each
				break
		if type(c).__name__  == 'NoneType':
			ret = None
		else:
			ret = c
		return ret

	def get_specific_faulttolerance_version_of_component(self, component, faulttolerance):
		c = None
		for each in self.librarycomponents:
			if each.is_fault_tolerant_version_of(component):
				if each.faulttolerant == faulttolerance:
					c = each
					#type(fault).__name__ == 'ChannelFault' 
					break
		if type(c).__name__  == 'NoneType':
			ret = None
		else:
			ret = c
		return ret

	def __str__(self):
		s = 'Component Library:\n'
		#s += 'Width: {}\n'.format(self.size[0])
		#s += 'Height: {}\n'.format(self.size[1])
		s += 'Components({})\n'.format(len(self.librarycomponents))
		for each in self.librarycomponents:
			s += ' ' + str(each) + '\n'

		return s


class LibraryComponent(object):
	def __init__(self, componenttype, totalsize, totalvalves, valvelist, routingallowed=False, faulttolerance=None):
		self.type = componenttype
		self.valves = totalvalves
		self.size = totalsize

		self.valvelist = valvelist
		self.routing = routingallowed
		self.faulttolerant = faulttolerance

	def is_fault_tolerant(self):
		return self.type[:2] == 'ft'

	def is_fault_tolerant_version_of(self, other):
		typelength = len(self.type)
		return self.type[2:typelength] == other.type

	def get_type(self):
		if self.is_fault_tolerant():
			typelength = len(self.type)
			return self.type[2:typelength]
		else:
			return self.type

	def __hash__(self):
		return hash(self.type)

	def __repr__(self):
		return self.type

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.id == other.id

	def __str__(self):
		return 'Component: {} is fault tolerant: {}'.format(self.type,self.is_fault_tolerant())

class Route(object):
	def __init__(self, start, end, connections, time):
		self.start = start
		self.end = end
		self.time = time
		self.connections = connections

		self.name = 'Route from {} to {} using {} taking time {}'.format(self.start,self.end,self.connections,self.time)

	def __lt__(self, other):
		if self.start.id == other.start.id:
			return self.end.id < other.end.id
		else:
			return self.start.id < other.start.id

	def __str__(self):
		return self.name