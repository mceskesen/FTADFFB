
import json

'''
#from scheduling import ListScheduler
from parsing import ApplicationParser, NetlistParser

ap = ApplicationParser('applications/synthetic1_seq.json')
ap.application.preprocess()
print(ap.application)
ap.application.calculate_bottom_levels()

for each in ap.application.operations:
    s = str(each) + ' ' + 'bottom_level = ' + str(each.bottom_level)
    #print(s)
ap.application.order_by_reverse_bottom_levels()

for each in sorted(ap.application.operations):
    s = str(each) + ' ' + 'bottom_level = ' + str(each.bottom_level)
    print(s)

'''
from parsing import NetlistParser, ComponentLibraryParser, ApplicationParser, FaultModelParser, ConfigParser
from faultmodel import RandomFaultScenarioGenerator
from scheduling import ListScheduler
from architecture_modifier import ArchitectureModifier, SimulatedAnnealing
import random
import math

clp = ComponentLibraryParser('components/library.json')

np = NetlistParser('netlists/arch-mes-example.json')
config = ConfigParser('config/arch-mes-config.conf')
ap = ApplicationParser('applications/mes_seq_example.json')
np.architecture.component_library = clp.get_component_library()
np.parse()
fmp = FaultModelParser('faultmodels/faultmodel-arch-mes.json')
rfsg = RandomFaultScenarioGenerator(fmp.faultmodel, config.data['faultscenarios'])
rfsg.generate_fault_scenarios()
#print('Random scenarios generated')
#am = ArchitectureModifier(np.architecture, ap.application, rfsg.faultscenarios, config.data)
sa = SimulatedAnnealing(np.architecture, ap.application, rfsg.faultscenarios, config.data)
print(sa.cost)

#c = 6570230.0 - 311096.0
#print(c)
#i = c / 0.9458
#print(i)
#d = math.exp(i)
#print(d)
#print(c)
#i = c / 9900.448802097482
#print(i)
print(sa.architecture)


#print('Random component is inserted: '+ str(b))
#print(am.ftcomponents_replaced)
#print(am.components_added)

#for each in am.ftcomponents_replaced.keys():
#    print('Replacer:')
#    print(each)
#    print(each.out_connections)
#    print(each.in_connections)
#    print('Is replacing:')
#    print(am.ftcomponents_replaced[each])
#    print(am.ftcomponents_replaced[each].out_connections)
#    print(am.ftcomponents_replaced[each].in_connections)

#print(am.architecture)
#cost = am.evaluate_architecture()
#print(cost)

#b = am.remove_random_component()
#print('The architecture is returned to normal: '+str(b))
#print(am.architecture)
#am.evaluate_architecture_with_two_faultscenarios()
#cost = am.evaluate_architecture()
#print(cost)


#def __init__(self, architecture, application, faultscenarios, config):

#np.architecture.generate_switch_valve_connections()
#print(np.architecture)
#from_c = np.architecture.component_by_name['Switch3']
#print(np.architecture.component_library.get_valvelist_for_component(from_c))


#print(from_c.out_connections)
#print('Sorted')
#print(sorted(from_c.out_connections))
#print(from_c.in_connections)
#print('Sorted')
#print(sorted(from_c.in_connections))

#complib = np.architecture.component_library.librarycomponents

#test = list(filter(lambda c: c.valves == 3 and c.type[:6] == 'switch', complib))



#b = np.architecture.is_connected()

#print('Number of valves: ' + str(np.architecture.number_of_valves()))
#print('Number of connections: ' + str(np.architecture.number_of_connections()))
#print('Without faults the architecture is connected: '+str(b))
#print('Number of valves: ' + str(np.architecture.number_of_valves()))
#print('Number of connections: ' + str(np.architecture.number_of_connections()))

#b = np.architecture.is_connected()
#print('With fault: ' + str(cf))
#print('The architecture is now connected: '+str(b))

#print(np.architecture.is_connected())

#print(fmp.faultmodel)

#cf = fmp.faults['Blocked-channel-Switch1-Mixer1']

#np.architecture.add_fault(cf)

#rfsg = RandomFaultScenarioGenerator(fmp.faultmodel, 100)

#rfsg.generate_fault_scenarios()

#print(len(rfsg.faultscenarios))
#for each in rfsg.faultscenarios:
#    print(each)


#cf = fmp.faults['Open-valve-Filter1-output']

#print(vf)
#vf2 = fmp.faults['Open-valve-Switch4-to-Switch5']
#print(vf2)

#print(np.architecture)

#r = np.architecture.find_route(from_c, to_c)
#print(r)
#np.architecture.add_fault(vf)
#np.architecture.add_fault(vf2)

#cf = fmp.faults['Blocked-channel-Mixer1']
#np.architecture.add_fault(cf)
#from_c = np.architecture.component_by_name['ftmixer2']
#to_c = np.architecture.component_by_name['Switch4']

#print(np.architecture)
#print(str(from_c) + ' has out connections: ' + str(from_c.total_out_connections))
#print(from_c.out_connections)
#print(str(from_c) + ' has in connections: ' + str(from_c.total_in_connections))
#print(from_c.in_connections)

#print(str(to_c) + ' has out connections: ' + str(to_c.total_out_connections))
#print(to_c.out_connections)
#print(str(to_c) + ' has in connections: ' + str(to_c.total_in_connections))
#print(to_c.in_connections)
#from_c = np.architecture.component_by_name['Filter1']

#for each in fmp.faultmodel.faults:
#    np.architecture.add_fault(each)

#ga = GreedyAlgorithm(np.architecture)
#ga.tolerate_faults()

#print(np.architecture)
#print(np.architecture.component_extra_valves)

'''
print(str(from_c) + ' has out connections: ' + str(from_c.total_out_connections))
print(from_c.out_connections)
print('Added out connections:')
print(from_c.added_out_connections)
print(str(from_c) + ' has in connections: ' + str(from_c.total_in_connections))
print(from_c.in_connections)
print('Added in connections:')
print(from_c.added_in_connections)

print(str(to_c) + ' has out connections: ' + str(to_c.total_out_connections))
print(to_c.out_connections)
print('Added out connections:')
print(to_c.added_out_connections)
print(str(to_c) + ' has in connections: ' + str(to_c.total_in_connections))
print(to_c.in_connections)
print('Added in connections:')
print(to_c.added_in_connections)

np.architecture.remove_connection(np.architecture.connection_by_name['Switch4-Switch5'])

print(str(to_c) + ' has out connections: ' + str(to_c.total_out_connections))
print(to_c.out_connections)
print('Added out connections:')
print(to_c.added_out_connections)
print(str(to_c) + ' has in connections: ' + str(to_c.total_in_connections))
print(to_c.in_connections)
print('Added in connections:')
print(to_c.added_in_connections)
'''

#mix = np.architecture.component_by_name['Mixer1']
#heat = np.architecture.component_by_name['Heater1']
#filt = np.architecture.component_by_name['Filter1']
#mixft = np.architecture.component_library.get_specific_faulttolerance_version_of_component(mix, 'pump')
#print(mixft)
#heatft = np.architecture.component_library.get_specific_faulttolerance_version_of_component(heat, 'channel')
#print(heatft)
#filtft = np.architecture.component_library.get_specific_faulttolerance_version_of_component(filt, 'channel')
#print(filtft)

#mixft = np.architecture.component_library.get_specific_faulttolerance_version_of_component(mix, 'channel')
#print(mixft)
#heatft = np.architecture.component_library.get_specific_faulttolerance_version_of_component(heat, 'input')
#print(heatft)
#filtft = np.architecture.component_library.get_specific_faulttolerance_version_of_component(filt, 'output')
#print(filtft)



#from_c = np.architecture.component_by_name['Heater1']
#to_c = np.architecture.component_by_name['Mixer1']
#np.architecture.average_connection_time = 0.5

#print(to_c.faults)

#r = np.architecture.find_route(from_c, to_c)
#print(r)

'''
l = np.architecture.get_components_of_type('filter')
print(l)
l2 = np.architecture.get_components_of_type('mixer')
print(l2)
r = np.architecture.find_route(from_c, to_c)
print(r)
np.architecture.restore()

print(np.architecture)
l = np.architecture.get_components_of_type('filter')
print(l)
l2 = np.architecture.get_components_of_type('mixer')
print(l2)

r = np.architecture.find_route(from_c, to_c)
print(r)

#switch2 = np.architecture.component_by_name['Switch2']
#print(switch2)
#print(switch2.in_connections)
#print(switch2.out_connections)

#r = np.architecture.find_route(from_c, to_c)
#print(r)
'''

'''
from_c = np.architecture.component_by_name['Switch1']
to_c = np.architecture.component_by_name['Switch3']
np.architecture.average_connection_time = 0.5
np.architecture.add_fault(vf)

r = np.architecture.find_route(from_c, to_c)
print(r)

print(np.architecture)

print(from_c)
print(from_c.out_connections)
print(from_c.in_connections)
print(to_c)
print(to_c.in_connections)
print(to_c.out_connections)
'''

'''
clp = ComponentLibraryParser('components/library.json')

np = NetlistParser('netlists/arch-mes-example.json')
np.architecture.component_library = clp.get_component_library()
np.parse()

print(np.architecture)

#c = np.architecture.component_by_name['Mixer1']
#print('Out connections for Mixer1')
#for each in c.out_connections.values():
#    print(each)

ap = ApplicationParser('applications/wajid_seq_example.json')

print(ap.application)

s = ListScheduler(ap.application, np.architecture, 0.5)
s.schedule_application()

for each in ap.application.operations:
    s = str(each.id) +'\n'
    s += 'Start time: ' + str(each.start_time) + '\n'
    s += 'Time: ' + str(each.time) + '\n'
    s += 'Finish time: ' + str(each.finish_time) + '\n'
    s += str(each.component) + '\n'
    print(s)

'''
#np.architecture.average_connection_time = 1
#from_c = np.architecture.component_by_name['In2']
#to_c = np.architecture.component_by_name['Filter1']

#r = np.architecture.find_route(from_c, to_c)

#print(r)

'''
np = NetlistParser('netlists/arch10-1s.json')
np.architecture.component_library = clp.get_component_library()
np.parse()
np2 = NetlistParser('netlists/arch20-1s.json')
np2.architecture.component_library = clp.get_component_library()
np2.parse()

ap = ApplicationParser('applications/synthetic1-1_seq.json')
ap2 = ApplicationParser('applications/synthetic2-1_seq.json')

#s = ListScheduler(ap.application, np.architecture, 0.5)
#s.schedule_application()

s = ListScheduler(ap.application, np.architecture, 0.5)
s.schedule_application()

for each in ap.application.operations:
    s = str(each.id) +'\n'
    s += 'Start time: ' + str(each.start_time) + '\n'
    s += 'Time: ' + str(each.time) + '\n'
    s += 'Finish time: ' + str(each.finish_time) + '\n'
    s += str(each.component) + '\n'
    print(s)

print('Sink finish time')

print(ap.application.sink.finish_time)

ap.application.unschedule()
np.architecture.unschedule()

s2 = ListScheduler(ap2.application, np.architecture, 0.5)
s2.schedule_application()

for each in ap2.application.operations:
    s = str(each.id) +'\n'
    s += 'Start time: ' + str(each.start_time) + '\n'
    s += 'Time: ' + str(each.time) + '\n'
    s += 'Finish time: ' + str(each.finish_time) + '\n'
    s += str(each.component) + '\n'
    print(s)


print('Sink finish time')

print(ap2.application.sink.finish_time)
'''

'''
np.architecture.unschedule()
ap2.application.unschedule()

s2 = ListScheduler(ap.application, np2.architecture, 0.5)
s2.schedule_application()

for each in ap.application.operations:
    s = str(each.id) +'\n'
    s += 'Start time: ' + str(each.start_time) + '\n'
    s += 'Time: ' + str(each.time) + '\n'
    s += 'Finish time: ' + str(each.finish_time) + '\n'
    s += str(each.component) + '\n'
    print(s)
'''
#for each in ap.application.operations:
#    s = str(each.id) +'\n'
#    s += 'Start time: ' + str(each.start_time) + '\n'
#    s += 'Time: ' + str(each.time) + '\n'
#    s += 'Finish time: ' + str(each.finish_time) + '\n'
#    s += str(each.component) + '\n'
#    print(s)

'''
np2.architecture.unschedule()
ap.application.unschedule()

s2 = ListScheduler(ap2.application, np.architecture, 0.5)
s2.schedule_application()

for each in ap2.application.operations:
    s = str(each.id) +'\n'
    s += 'Start time: ' + str(each.start_time) + '\n'
    s += 'Time: ' + str(each.time) + '\n'
    s += 'Finish time: ' + str(each.finish_time) + '\n'
    s += str(each.component) + '\n'
    print(s)

print('Sink finish time')

print(ap2.application.sink.finish_time)

ap2.application.unschedule()
np.architecture.unschedule()

'''

#ap.application.calculate_bottom_levels()
#ap.application.order_by_reverse_bottom_levels()
#for each in sorted(ap.application.operations):
#    s = str(each) + ' ' + 'bottom_level = ' + str(each.bottom_level)
#    print(s)

#s = str(ap.application.source) + ' has component: ' + str(ap.application.source.component) + '\n'
#s = str(ap.application.source) + ' is scheduled: ' + str(ap.application.source.scheduled) + '\n'
#print(s)

#print('NU')
#for each in ap.application.operations:
#    s = str(each)+' is scheduled: ' + str(each.scheduled) + '\n'
#    s = str
#    print(s)

#for each in ap.application.flows:
#    print(each)
#    s = str(each.operations[0])+' is scheduled: ' + str(each.operations[0].scheduled) + '\n'
#    print(s)
#    s2 = str(each.operations[1])+' is scheduled: ' + str(each.operations[1].scheduled) + '\n'
#    print(s2)



'''
for each in sorted(ap.application.operations):
    s = str(each) + ' ' + 'bottom_level = ' + str(each.bottom_level)
    print(s)

ap.calculate_bottom_levels()
#print(np.architecture)

for each in sorted(ap.application.operations):
    s = str(each) + ' ' + 'bottom_level = ' + str(each.bottom_level)
    print(s)
'''

#from_c = np.architecture.component_by_name['Mixer4']
#to_c = np.architecture.component_by_name['Mixer9']

#r = np.architecture.find_route(from_c, to_c)

#print(r)

#print(np.architecture.component_connections)

'''
from parsing import ComponentLibraryParser

clp = ComponentLibraryParser('components/library.json')

for each in clp.componentlibrary:
    print(each.type)
    print(each.routing)
'''