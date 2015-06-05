'''
Created on 26 March 2015

Travel time is an average time given by the designer

@author: Morten Chabert Eskesen
'''

from queue import PriorityQueue
from application import Application, Operation, Flow
from architecture import Architecture, Component, Connection

class Scheduler(object):

	def __init__(self, application, architecture, averagetime):
		self.schedule = list()

		self.application = application
		self.architecture = architecture
		self.averagetime = averagetime
		self.architecture.average_connection_time = averagetime

		self.storage_component = self.architecture.storage


		self.operation_to_components = {'mix': 'mixer',
                                        'heat': 'heater',
                                        'detect': 'detector',
                                        'filter': 'filter',
                                        'separate': 'separator',
                                        'input': 'input',
                                        'output': 'output',
                                        'sink': 'output',
                                        'source': 'input',
                                        'flow': 'flow'}

	def schedule(self):
		raise NotImplementedError

	def get_components_for_operation(self, o):
		return self.architecture.get_components_of_type(self.operation_to_components[o.type])

	def get_ready_operations(self, operation):
		readyops = set()
		for each in application:
				if all(d in scheduled_operations for d in self.application.dependencies[o.id]):
						readyops.add(each)

		return sorted(readyops)


class ListScheduler(Scheduler):

	def __init__(self, application, architecture, averagetime):
		super().__init__(application, architecture, averagetime)

		if self.storage_component:
			application.storage_allowed = True
			Flow.storage_operation.component = self.storage_component

		Flow.architecture = architecture

	def schedule_application(self):
		self.schedule_inputs()
		self.schedule_operations()

	def schedule_operation_on_component(self, operation, component, start_time):
		operation.schedule(component,start_time)
		component.schedule(operation)

	def schedule_inputs(self):
		for o in self.application.inputs:
			try:
				c = self.architecture.component_by_name[self.application.input_binds[o]]
				self.schedule_operation_on_component(o, c, 0)
			except KeyError:
				pass

	def schedule_operations(self):
		self.application.calculate_bottom_levels()
		self.application.order_by_reverse_bottom_levels()

		readyops = PriorityQueue()
		readyops.put(self.application.source)

		while(not readyops.empty()):
			o = readyops.get()
			if not o.scheduled:
				self.bind_and_schedule(o)
			for each in o.successors_ready():
				readyops.put(each)

	def bind_and_schedule(self, o):
		t_min = float('inf')
		best_component = None
		possible_components = self.get_components_for_operation(o)

		for component in possible_components:
			t = o.ready_time_on_component(component)
			if t_min > t:
				t_min = t
				best_component = component

		if not best_component:
			raise NoScheduleFoundError
		self.schedule_operation_on_component(o, best_component,t_min)


class NoScheduleFoundError(Exception):
	pass