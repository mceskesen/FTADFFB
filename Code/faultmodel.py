'''
Created 08 April 2015

@author: Morten Chabert Eskesen
'''

from random import randint
import random

class FaultModel(object):

	def __init__(self):
		self.id = None
		#self.faults = set()
		self.valvefaults = list()
		self.channelfaults = list()
		self.total_valvefaults = None
		self.total_channelfaults = None

	def add_valvefault(self, faultid, faulttype, objecttype, objectname, control, affected):
		vf = ValveFault(faultid, faulttype, objecttype, objectname, control, affected)
		#self.faults.add(vf)
		self.valvefaults.append(vf)
		return vf

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

class FaultScenario(object):

	def __init__(self, valvefaults, channelfaults):
		self.valvefaults = valvefaults
		self.channelfaults = channelfaults
		self.total_faults = valvefaults + channelfaults
		self.faults = set()

	def add_fault(self, fault):
		self.faults.add(fault)

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


class RandomFaultScenarioGenerator(object):

	def __init__(self, faultmodel, total_faultscenarios):
		self.faultmodel = faultmodel
		self.total_faultscenarios = total_faultscenarios
		self.faultscenarios = list()

	def fault_scenario_exists(self, faultscenario):
		return any(fs == faultscenario for fs in self.faultscenarios)

	def generate_fault_scenarios(self):
		i = 0
		while i < self.total_faultscenarios: 
			valvef = randint(0,self.faultmodel.total_valvefaults)
			channelf = randint(0, self.faultmodel.total_channelfaults)
			fs = FaultScenario(valvef, channelf)
			for j in range(0, valvef):
				vf = random.choice(self.faultmodel.valvefaults)
				while(fs.fault_exists(vf)):
					vf = random.choice(self.faultmodel.valvefaults)
				fs.add_fault(vf)
			for x in range(0, channelf):
				cf = random.choice(self.faultmodel.channelfaults)
				while(fs.fault_exists(cf)):
					cf = random.choice(self.faultmodel.channelfaults)
				fs.add_fault(cf)
			if not self.fault_scenario_exists(fs):
				self.faultscenarios.append(fs)
				i += 1


class Fault(object):

	def __init__(self, faultid, faulttype, objecttype, objectname):
		self.id = faultid
		self.type = faulttype
		self.objecttype = objecttype
		self.objectname = objectname

	def __hash__(self):
		return hash(self.id)


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