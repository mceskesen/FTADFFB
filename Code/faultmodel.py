'''
Created 08 April 2015

The fault model

@author: Morten Chabert Eskesen
'''

from random import randint
import itertools
import random

'''
The fault model class
'''
class FaultModel(object):

	def __init__(self):
		self.id = None
		#self.faults = set()
		self.valvefaults = list()
		self.channelfaults = list()
		self.total_valvefaults = None
		self.total_channelfaults = None

	'''
	Create valvefault and add it to the fault model
	'''
	def add_valvefault(self, faultid, faulttype, objecttype, objectname, control, affected):
		vf = ValveFault(faultid, faulttype, objecttype, objectname, control, affected)
		#self.faults.add(vf)
		self.valvefaults.append(vf)
		return vf

	'''
	Create channelfault and add it to the fault model
	'''
	def add_channelfault(self, faultid, faulttype, objecttype, objectname):
		cf = ChannelFault(faultid, faulttype, objecttype, objectname)
		#self.faults.add(cf)
		self.channelfaults.append(cf)
		return cf

	def __str__(self):
		s = 'Fault model: ' + self.id + '\n'
		s += 'ValveFaults({})\n'.format(len(self.valvefaults))
		for each in self.valvefaults:
			s += ' ' + str(each) + '\n'
		s += 'ChannelFaults({})\n'.format(len(self.channelfaults))
		for each in self.channelfaults:
			s += ' ' + str(each) + '\n'
		return s


'''
The Fault Scenario class
'''
class FaultScenario(object):

	def __init__(self, valvefaults, channelfaults):
		self.valvefaults = valvefaults
		self.channelfaults = channelfaults
		self.total_faults = valvefaults + channelfaults
		self.faults = set()

	'''
	Add a fault to this scenario
	'''
	def add_fault(self, fault):
		self.faults.add(fault)

	'''
	Does the fault exist in this fault scenario?
	'''
	def fault_exists(self, fault):
		return fault in self.faults

	def __eq__(self, other):
		eq = True
		if type(other).__name__ == type(self).__name__:
			eq = True
			if self.valvefaults == other.valvefaults and self.channelfaults == other.channelfaults:
				if len(self.faults) == len(other.faults):
					for each in self.faults:
						if not each in other.faults:
							eq = False
							break
				else:
					eq = False
			else:
				eq = False
		else:
			eq = False
		return eq

	def __str__(self):
		s = 'Fault scenario with channelfaults: ' + str(self.channelfaults) + ' and valvefaults: ' + str(self.valvefaults) + '\n'
		s += 'Faults({})\n'.format(len(self.faults))
		for each in self.faults:
			s += ' ' + str(each) + '\n'

		return s

'''
The random generation of fault scenarios class
'''
class RandomFaultScenarioGenerator(object):

	def __init__(self, faultmodel, total_faultscenarios):
		self.faultmodel = faultmodel
		self.total_faultscenarios = total_faultscenarios
		self.faultscenarios = list()

	'''
	Does the fault scenario already exist?
	'''
	def fault_scenario_exists(self, faultscenario):
		return any(fs == faultscenario for fs in self.faultscenarios)

	'''
	Generate all possible combinations of subsets from 0 to total_faults of set faults
	'''
	def generate_possible_combinations(self, faults, total_faults):
		j = 1
		possible_combinations = []
		f = total_faults + 1
		for j in range(j, f):
			r = list(itertools.permutations(faults,j))
			possible_combinations.append(r)
		
		empty_list = list()
		possible_combinations.append(empty_list)

		return possible_combinations
			
	'''
	Generate the fault scenarios until the number generated is total_faultscenarios
	'''
	def generate_fault_scenarios(self):
		i = 0
		valve_combs = self.generate_possible_combinations(self.faultmodel.valvefaults, self.faultmodel.total_valvefaults)
		channel_combs = self.generate_possible_combinations(self.faultmodel.channelfaults, self.faultmodel.total_channelfaults)

		while i < self.total_faultscenarios:
			valvefaults = random.choice(valve_combs)
			channelfaults = random.choice(channel_combs)
			#print(valvefaults)
			#print(channelfaults)
			if len(valvefaults) > 0:
				v = random.choice(valvefaults)
			else:
				v = list()
			if len(channelfaults) > 0:
				c = random.choice(channelfaults)
			else:
				c = list()
			#print('V: '+str(v))
			#print('C: '+str(c))
			fs = FaultScenario(len(v), len(c))
			for cf in c:
				fs.add_fault(cf)
			for vf in v:
				fs.add_fault(vf)

			if not self.fault_scenario_exists(fs):
				self.faultscenarios.append(fs)
				i += 1

'''
The super class fault
'''
class Fault(object):

	def __init__(self, faultid, faulttype, objecttype, objectname):
		self.id = faultid
		#Depending on the actual fault class (open/closed for valve and block/leak for channel)
		self.type = faulttype
		#Component or connection is denoted by objecttype
		self.objecttype = objecttype
		#The id of the component or connection
		self.objectname = objectname

	def __hash__(self):
		return hash(self.id)

'''
A subclass of fault - the channel fault class
'''
class ChannelFault(Fault):

	def __init__(self, faultid, faulttype, objecttype, objectname):
		super().__init__(faultid, faulttype, objecttype, objectname)

	def __repr__(self):
		return 'Channel fault: {}'.format(self.id)

	def __str__(self):
		return 'Channel fault: {}'.format(self.id)

	def __hash__(self):
		return hash(self.id)

	def __eq__(self, other):
		if type(other).__name__ == type(self).__name__:
			return self.id == other.id and self.objecttype == other.objecttype and self.objectname == other.objectname
		else:
			return False

'''
A subclass of fault - the valve fault class
'''
class ValveFault(Fault):

	def __init__(self, faultid, faulttype, objecttype, objectname, control, affected):
		super().__init__(faultid, faulttype, objecttype, objectname)

		self.control = control
		self.affected = affected
	
	def __repr__(self):
		return 'Valve fault: {}'.format(self.id)

	def __str__(self):
		return 'Valve fault: {}'.format(self.id)

	def __hash__(self):
		return hash(self.id)

	def __eq__(self, other):
		if type(other).__name__ == type(self).__name__:
			return self.id == other.id and self.objecttype == other.objecttype and self.objectname == other.objectname and self.affected == other.affected
		else:
			return False