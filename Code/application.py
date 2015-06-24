'''
Created on 26 March 2015

@author: Morten Chabert Eskesen
'''

from data_structures import OrderedSet
from architecture import Architecture, Component, Connection, Route

class Application(object):

	def __init__(self):
		self.id = None
		self.operations = OrderedSet()
		self.flows = set()
		self.inputs = set()
		self.outputs = set()
		self.input_binds = None
		self.source = None
		self.sink = None
		self.storage_operation = Operation(self, 'St', 'storage', 0)
		Flow.storage_operation = self.storage_operation
		self.storage_allowed = None

		self.output_predecessors = set()

		self.calcuated_bottom_levels = False
		self.ordered_by_reverse_bottom_levels = False

	def operation_scheduled(self, o):
		if o in self.operations:
			o.scheduled = True

	def add_source(self):
		o = self.add_operation('So', 'source', 0)
		self.source = o
		for each in self.inputs:
			self.add_flow(self.source, each)

	def add_sink(self):
		o = self.add_operation('Si', 'sink',0)
		self.sink = o
		i = 1
		for each in self.output_predecessors:
			output = Operation(self, 'o{}'.format(i), 'output',0)
			output.order = -1
			self.operations.add(output)
			self.outputs.add(output)
			self.add_flow(each, output)
			self.add_flow(output, self.sink)
			i += 1
		self.sink.order = -2

	def preprocess(self):
		self.add_source()
		self.order_reverse_topologically()
		self.add_sink()
		self.set_source_and_sink()

	def set_source_and_sink(self):
		for o in self.operations:
			if not o.inputs:
				self.source = o
			if not o.outputs:
				self.sink = o

	def set_inputs(self, inputs, input_binds):
		self.inputs = inputs
		self.input_binds = input_binds
		for each in inputs:
			each.time = 0.0

	def order_reverse_topologically(self):
		visited = {}

		for each in self.operations:
			visited[each] = False

		self.order = 0
		self.output_predecessors = set()
		self.visit_reverse_topologically(self.source, visited)

	def visit_reverse_topologically(self, node, visited):
		if not visited[node]:
			if node.order == None:
				visited[node] = True
				if node.outputs:
					for each in node.outputs:
						self.visit_reverse_topologically(each.operations[1], visited)
				else:
					self.output_predecessors.add(node)
				node.order = self.order
				self.order += 1
				visited[node] = False

	def calculate_bottom_levels(self):
		if not self.calcuated_bottom_levels:
			for op in sorted(self.operations):
				max_ = 0
				for n in op.outputs:
					j = n.operations[1]
					max_candidate = j.bottom_level + j.time
					if max_candidate > max_:
						max_ = max_candidate
				op.bottom_level = max_ + op.time
		self.calcuated_bottom_levels = True

	def add_flow(self, o1, o2, amount = None):
		f = Flow(o1, o2, amount)
		o1.outputs.add(f)
		o2.inputs.add(f)
		self.flows.add(f)
		return f

	def order_by_reverse_bottom_levels(self):
		if not self.ordered_by_reverse_bottom_levels:
			for o in self.operations:
				o.order = -o.bottom_level
		self.ordered_by_reverse_bottom_levels = True

	def ready_operations(self):
		readyops = set()

		for each in self.operations:
			if each.scheduled is not True:
				try:
					if all(d.predecessor.scheduled is True for d in self.dependencies[each.id]):
						readyops.add(each)
				except KeyError:
					readyops.add(each)

		return readyops

	def unschedule(self):
		for o in self.operations:
			o.unschedule()
		for f in self.flows:
			f.unschedule()
		self.storage_operation.unschedule()

	def add_operation(self, operationid, operationtype, executiontime):
		o = Operation(self, operationid, operationtype, executiontime)
		self.operations.add(o)
		return o

	def __str__(self):
		operations = list(self.operations)

		s = 'Application: {}\n'.format(self.id)
		s += 'Operations({})\n'.format(len(operations))
		for each in operations:
			s += ' ' + str(each) + '\n'
		for each in self.flows:
			#for e in self.dependencies[each]:
			s += ' ' + str(each) + '\n'
		return s


class Operation(object):

	def __init__(self, application, operationid, operationtype, executiontime):
		self.application = application
		self.id = operationid
		self.type = operationtype
		self.time = executiontime

		self.inputs = set()
		self.outputs = set()

		self.scheduled = False
		self.start_time = None
		self.finish_time = None
		self.component = None


		self.order = None
		self.bottom_level = 0

		self.input_flow_start_times = {}
		self.occupant_output_flow_start_times = {}

	def __repr__(self):
		return self.id

	def __lt__(self, other):
		if self.order == other.order:
			if len(self.outputs) == len(other.outputs):
				return self.id < other.id
			else:
				return len(self.outputs) > len(other.outputs)
		else:
			return self.order < other.order

	def __ge__(self, other):
		return self == other or other < self

	def __str__(self):
		return 'Operation {}: {}'.format(self.id, self.type)

	def __hash__(self):
		return hash(self.id)

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.id == other.id

	def unschedule(self):
		#Reset all schedule related stuff
		self.scheduled = False
		self.start_time = None
		self.finish_time = None
		self.component = None
		self.input_flow_start_times = {}
		self.occupant_output_flow_start_times = {}

	def schedule(self, component, start_time):
		self.component = component
		occupant = self.component.occupied_by

		if occupant:
			self.schedule_storage_flows()

		self.start_time = start_time
		self.finish_time = self.start_time + self.time
		self.schedule_input_flows()
		self.scheduled = True

	def schedule_storage_flows(self):
		try:
			for (f, start_time) in self.occupant_output_flow_start_times[self.component]:
				f.schedule_to_storage(start_time)
			self.occupant_output_flow_start_times = {}
		except KeyError:
			pass

	def schedule_input_flows(self):
		try:
			for (f, start_time) in self.input_flow_start_times[self.component]:
				f.schedule(start_time)
			self.input_flow_start_times = {}
		except KeyError:
			pass

	def ready(self):
		return all(f.predecessor.scheduled is True for f in self.inputs)

	def successors_ready(self):
		readyset = set()
		for f in self.outputs:
			if f.operations[1].ready():
				readyset.add(f.operations[1])
		return sorted(readyset)

	def ready_time_on_component(self, c):
		input_flow_start_times = []
		occupant_output_flow_start_times = []

		total_finish_time = 0
		inputflows = self.inputs

		occupant = c.occupied_by
		if occupant:
			if not self.application.storage_allowed:
				return float('inf')
			for outputflow in occupant.outputs:
				if not outputflow.operations[1] == self:
					start_time = max(outputflow.to_storage.predict_start_time(c), total_finish_time)
					occupant_output_flow_start_times.append((outputflow, start_time))
					total_finish_time = start_time + outputflow.to_storage.predict_time()

		sorted_input_flows = sorted(inputflows, key = lambda f: (f.predict_start_time(c), f.name))

		for f in sorted_input_flows:
			start_time = max(f.predict_start_time(c), total_finish_time)
			input_flow_start_times.append((f, start_time))
			total_finish_time = start_time + f.predict_time(c)

		self.input_flow_start_times[c] = input_flow_start_times
		self.occupant_output_flow_start_times[c] = occupant_output_flow_start_times

		return total_finish_time


class Flow(object):
	storage_operation = None
	architecture = None

	def __init__(self, from_o, to_o, amount = None):
		self.operations = [from_o, to_o]
		self.predecessor = from_o

		self.id = (from_o.id, to_o.id)
		self.name = '{},{}'.format(from_o.id, to_o.id)

		self.scheduled = False
		self.time = 0
		self.start_time = None
		self.finish_time = None
		self.route = None

		self.requires_storage = False
		if type(self).__name__ == 'Flow':
			self.to_storage = FlowToStorage(self, self.operations[0])
			self.from_storage = FlowFromStorage(self, self.operations[1])

	def __hash__(self):
		return hash(self.id)

	def __repr__(self):
		#return self.id
		return self.name

	def __str__(self):
		return self.name

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.id == other.id

	def unschedule(self):
		#Reset all schedule related stuff
		self.scheduled = False
		self.time = 0
		self.start_time = None
		self.finish_time = None
		self.route = None
		self.requires_storage = False
		if type(self).__name__ == 'Flow':
			self.to_storage = FlowToStorage(self, self.operations[0])
			self.from_storage = FlowFromStorage(self, self.operations[1])

	def schedule(self, start_time):
		if self.requires_storage:
			self.from_storage.schedule(start_time)
			self.start_time = self.to_storage.start_time
			self.time = self.from_storage.finish_time - self.to_storage.start_time
			self.finish_time = self.from_storage.finish_time

			self.scheduled = True
		else:
			self.route = self.find_route()
			self.start_time = start_time

			self.time = self.route.time

			self.finish_time = self.start_time + self.time
			self.set_connection_finish_times()

			self.scheduled = True
			self.release_component(self.operations[0])
		self.occupy_component(self.operations[1])

	def release_component(self, o):
		o.component.occupied_by = None
		o.component.finish_time = max(o.component.finish_time,self.finish_time)

	def occupy_component(self, o):
		if o.time > 0:
			o.component.occupied_by = o

	def schedule_to_storage(self, start_time):
		self.requires_storage = True
		self.to_storage.schedule(start_time)

	def predict_start_time(self, to_c):
		if self.requires_storage:
			return self.from_storage.predict_start_time(to_c)
		else:
			return max(self.operations[0].component.finish_time, self.predict_max_connection_finish_time(to_c), to_c.finish_time)

	def predict_time(self, to_c):
		if self.requires_storage:
			return self.from_storage.predict_time(to_c)
		else:
			r = self.predict_route(to_c)
			
			if not r:
				return float('inf')
			else:
				return r.time

	def predict_route(self, to_c):
		if self.operations[0].type == 'source' or self.operations[1].type == 'sink':
			return Route(None, None, [], 0)
		return Flow.architecture.find_route(self.operations[0].component, to_c)

	def predict_max_connection_finish_time(self, to_c):
		route = self.predict_route(to_c)

		if not route:
			return float('inf')

		maximum = 0
		for each in route.connections:
			if each.finish_time > maximum:
				maximum = each.finish_time
		return maximum

	def set_connection_finish_times(self):
		if self.route.connections != None:
			if len(self.route.connections) > 0:
				previous_con = self.route.connections[0]
		for each in self.route.connections:
			each.finish_time = previous_con.finish_time + Flow.architecture.average_connection_time
			previous_con = each

	def find_route(self):
		if self.operations[0].type == 'source' or self.operations[1].type == 'sink':
			return Route(None, None, [], 0)
		return Flow.architecture.find_route(self.operations[0].component,self.operations[1].component)

class FlowFromStorage(Flow):
	def __init__(self, parent, operation, amount = None):
		super().__init__(Flow.storage_operation, operation)
		self.parent_flow = parent

	def schedule(self, start_time):
		self.route = self.find_route()
		self.start_time = start_time
		self.time = self.route.time
		self.finish_time = self.start_time + self.time
		self.set_connection_finish_times()
		self.scheduled = True
		self.occupy_component(self.operations[1])

	def unschedule(self):
		super().unschedule()

	def predict_start_time(self, to_c):
		return max(self.parent_flow.to_storage.finish_time, self.predict_max_connection_finish_time(to_c), to_c.finish_time)


class FlowToStorage(Flow):
	def __init__(self, parent, operation, amount = None):
		super().__init__(operation, Flow.storage_operation)

		self.parent_flow = parent

	def schedule(self, start_time):
		self.route = self.find_route()
		self.start_time = start_time
		self.time = self.route.time
		self.finish_time = self.start_time + self.time
		self.set_connection_finish_times()
		self.scheduled = True
		self.release_component(self.operations[0])

	def unschedule(self):
		super().unschedule()

	def predict_start_time(self, to_c):
		return super().predict_start_time(Flow.architecture.storage)

	def predict_time(self):
		return super().predict_time(Flow.architecture.storage)
