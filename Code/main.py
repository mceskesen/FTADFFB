
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
from architecture_modifier import ArchitectureModifier, SimulatedAnnealing, GreedilyRandomAdaptiveSearchProcedure
from architecture import Component
from serializing import NetlistSerializer
import random
import math
import time

clp = ComponentLibraryParser('components/library.json')

arch_file = 'netlists/arch-mes-example.json'
arch_file2 = 'netlists/archPCR1s.json'
arch_file3 = 'netlists/archIVD1s.json'
np = NetlistParser(arch_file)
np2 = NetlistParser(arch_file2)
np3 = NetlistParser(arch_file3)
np.architecture.component_library = clp.get_component_library()
np.parse()
np2.architecture.component_library = clp.get_component_library()
np2.parse()
np3.architecture.component_library = clp.get_component_library()
np3.parse()

mes1 = np.architecture.number_of_valves() + np.architecture.number_of_connections()
pcr = np2.architecture.number_of_valves() + np2.architecture.number_of_connections()
ivd = np3.architecture.number_of_valves() + np3.architecture.number_of_connections()

print('MES: '+str(np.architecture.number_of_valves())+ ' + '+str(np.architecture.number_of_connections())+' = '+str(mes1))
print('PCR: '+str(np2.architecture.number_of_valves())+ ' + '+str(np2.architecture.number_of_connections())+' = '+str(pcr))
print('IVD: '+str(np3.architecture.number_of_valves())+ ' + '+str(np3.architecture.number_of_connections())+' = '+str(ivd))

#config = ConfigParser('config/arch-mes-config.conf')
config = ConfigParser('config/arch-mes-config.conf')
#config = ConfigParser('config/pcr-grasp-config.conf')
#config = ConfigParser('config/ivd-grasp-config.conf')
ap = ApplicationParser('applications/mes_seq_motivational-example.json')
#ap = ApplicationParser('applications/pcr_seq.json')
#ap = ApplicationParser('applications/ivd_seq.json')
np.architecture.component_library = clp.get_component_library()
np.parse()
fmp = FaultModelParser('faultmodels/faultmodel-motivational-example.json')
#fmp = FaultModelParser('faultmodels/faultmodel-pcr-example.json')
#fmp = FaultModelParser('faultmodels/faultmodel-ivd-example.json')
rfsg = RandomFaultScenarioGenerator(fmp.faultmodel, config.data['faultscenarios'])
rfsg.generate_fault_scenarios()
#rfsg.test_generate_fault_scenarios()
#print(np.architecture)
#start = time.clock()
#am = ArchitectureModifier(np.architecture, ap.application, rfsg.faultscenarios, config.data)
#print(am.architecture)
#am.application_finish_time(am.architecture)
#am.architecture.add_fault(fmp.faults['Blocked-channel-Filter1'])
#am.application_finish_time(am.architecture)
#am.architecture.restore()
#am.make_component_fault_tolerant(am.architecture.component_by_name['Filter1'], am.architecture)
#am.architecture.add_fault(fmp.faults['Blocked-channel-Filter1'])
#am.application_finish_time(am.architecture)
#check channel fault på filter på samme måde som før

'''
sa = SimulatedAnnealing(np.architecture, ap.application, rfsg.faultscenarios, config.data)
print(sa.architecture)
print(sa.cost)

print('Components')
for each in sa.architecture.components:
    print('NEW COMPONENT: '+str(each))
    print('In connections:')
    for incon in each.in_connections:
        t = incon in sa.architecture.components
        print(str(incon)+ ' in components: '+str(t))
    print('Out connections:')
    for outcon in each.out_connections:
        t = outcon in sa.architecture.components
        print(str(outcon)+ ' in components: '+str(t))

print('Connections')
for each in sa.architecture.connections:
    t = each.components[0] in sa.architecture.components
    d = each.components[1] in sa.architecture.components
    print(str(each) + ' both in components '+str(t)+ ' and '+str(d))
'''



#am.insert_component_to_make_random_component_redundant(am.architecture)
#print(am.architecture)
#am.insert_component_to_make_random_component_redundant(am.architecture)
#print(am.architecture)

#am.insert_component_to_make_random_component_redundant(am.architecture)
#print(am.architecture)
#for each in am.architecture.components:
#    print(str(each) + ' type: '+str(each.type))
#am.insert_component_to_make_random_component_redundant(am.architecture)
#print(am.architecture)
#print('Removing')
#am.remove_random_component(am.architecture)
#print(am.architecture)
#for each in am.architecture.components:
#    print(str(each) + ' type: '+str(each.type))
#cost = am.evaluate_architecture(am.architecture)
#tolerance = am.run_all_faultscenarios_on_architecture(am.architecture, rfsg.faultscenarios)
#tolerated = tolerance[0]
#not_tolerated = tolerance[1]
#ns_grasp1 = NetlistSerializer(am.architecture, cost, cost, len(am.faultscenarios), 0, 'grasp', tolerated, not_tolerated)
#ns_grasp1.export('testing-arch-output.json')
#cost = am.evaluate_architecture(am.architecture)
#end = time.clock()
#runtime = end - start
#archs = NetlistSerializer(am.architecture, cost, cost, len(am.faultscenarios), runtime, 'simulated_annealing')
#archs.export('test-arch-ivd.json')
#print('Is connected: '+str(am.architecture.is_connected()))
#am.application_finish_time(am.architecture)
#c = am.evaluate_architecture(am.architecture)
#print('Cost: '+str(c))

#sa = SimulatedAnnealing(np.architecture, ap.application, rfsg.faultscenarios, config.data)
#print(sa.architecture)
#print(sa.cost)
'''
for x in range(0, 20):
    am.make_random_component_fault_tolerant(am.architecture)
    am.evaluate_architecture(am.architecture)
    if x == 5 or x == 10 or x == 15:
        am.make_random_component_non_fault_tolerant(am.architecture)
        am.evaluate_architecture(am.architecture)
'''
'''
f = fmp.faults['Blocked-channel-Switch3-Switch4']
f2 = fmp.faults['Open-valve-Switch4-to-Switch3']
f3 = fmp.faults['Blocked-channel-Mixer1']
am = ArchitectureModifier(np.architecture, ap.application, rfsg.faultscenarios, config.data)
switch4 = am.architecture.component_by_name['Switch4']
switch3 = am.architecture.component_by_name['Switch3']
switch5 = am.architecture.component_by_name['Switch5']
filter1 = am.architecture.component_by_name['Filter1']
in1 = am.architecture.component_by_name['In1']

#c = am.evaluate_architecture()
#print('Cost of architecture: '+str(c))

print(switch3)
print(switch3.in_connections)
print(switch3.out_connections)
print(switch4)
print(switch4.in_connections)
print(switch4.out_connections)
print(switch5)
print(switch5.in_connections)
print(switch5.out_connections)

print('Is connected before faults: '+str(am.architecture.is_connected()))
r = am.architecture.find_route(in1, filter1)
print(r)
am.architecture.add_fault(f2)
am.architecture.add_fault(f)


print('Is connected after faults: '+str(am.architecture.is_connected()))
r = am.architecture.find_route(in1, filter1)
print(r)

print(switch3)
print(switch3.in_connections)
print(switch3.out_connections)
print(switch4)
print(switch4.in_connections)
print(switch4.out_connections)
print(switch5)
print(switch5.in_connections)
print(switch5.out_connections)
'''

#am.make_component_fault_tolerant(f)
#c = am.evaluate_architecture()
#print('Cost of architecture: '+str(c))

#print(np.architecture)
'''
print('Restoring')
am.architecture.restore()
print('Is connected after restoring: '+str(am.architecture.is_connected()))
r = am.architecture.find_route(in1, filter1)
print(r)

print(switch3)
print(switch3.in_connections)
print(switch3.out_connections)
print(switch4)
print(switch4.in_connections)
print(switch4.out_connections)
print(switch5)
print(switch5.in_connections)
print(switch5.out_connections)
'''

#sa = SimulatedAnnealing(np.architecture, ap.application, rfsg.faultscenarios, config.data)
#print(sa.architecture)
#print('Final cost: '+str(sa.cost))
#d = am.architecture.is_connected()
#print(d)
#am.architecture.add_fault(f2)
#d = am.architecture.is_connected()
#print(d)
#am.architecture.add_fault(f2)
#d = am.architecture.is_connected()
#print(d)
#am.architecture.restore()
#d = am.architecture.is_connected()
#print(d)
#c = am.is_architecture_non_fault_tolerant()
#print('Non fault tolerance: '+ str(c))
#ap = am.application_finish_time()
#print('App finish time: '+str(ap))
'''
filterop = ap.operations['O3']
f = fmp.faults['Open-valve-Switch4-to-Switch3']
#f2 = fmp.faults['Open-valve-Filter1-output']
in1 = am.architecture.component_by_name['In1']
switch3 = am.architecture.component_by_name['Switch3']
switch4 = am.architecture.component_by_name['Switch4']
switch5 = am.architecture.component_by_name['Switch5']
filter1 = am.architecture.component_by_name['Filter1']
storage = am.architecture.component_by_name['Storage-8']
s = ListScheduler(am.application, am.architecture, 0.5)
s.schedule_application()

#print(filterop)
#print(filterop.input_flow_start_times)
#print(filterop.occupant_output_flow_start_times)
#print(filterop.inputs)
for each in filterop.inputs:
    print(str(each) + 's route is:')
    print(each.route)
    print('Start-time for flow: '+str(each.start_time))
    print('Time for flow: '+str(each.time))
    print('Finish-time for flow: '+str(each.finish_time))
    print(str(each.to_storage) + 's route is:')
    print(each.to_storage.route)
    print(each.to_storage.start_time)
    print(each.to_storage.finish_time)
    print(str(each.from_storage) + 's route is:')
    print(each.from_storage.route)
    print(each.from_storage.start_time)
    print(each.from_storage.finish_time)
print(filterop.outputs)

am.application.unschedule()
am.architecture.unschedule()
am.architecture.add_fault(f)
s2 = ListScheduler(am.application, am.architecture, 0.5)
s2.schedule_application()
for each in filterop.inputs:
    print(str(each) + 's route is:')
    print(each.route)
    print('Start-time for flow: '+str(each.start_time))
    print('Time for flow: '+str(each.time))
    print('Finish-time for flow: '+str(each.finish_time))
    print(str(each.to_storage) + 's route is:')
    print(each.to_storage.route)
    print(each.to_storage.start_time)
    print(each.to_storage.finish_time)
    print(str(each.from_storage) + 's route is:')
    print(each.from_storage.route)
    print(each.from_storage.start_time)
    print(each.from_storage.finish_time)
print(filterop.outputs)
'''
#am.architecture.average_connection_time = 0.2
#c = am.application_finish_time()
#print(c)

#am.architecture.add_fault(f)
#am.architecture.average_connection_time = 0.2


'''
print('Going to switch4 from Filter1')
s = am.architecture.test_generate_in_connections_for_component_going_to(switch4, filter1)
print(s)
print('Going to switch4 from switch5')
s = am.architecture.test_generate_in_connections_for_component_going_to(switch4, switch5)
print(s)
print('Going to switch4 from switch3')
s = am.architecture.test_generate_in_connections_for_component_going_to(switch4, switch3)
print(s)

#d = am.architecture.test_is_connected()
#print('Is connected before first fault: '+str(d))
#c = am.application_finish_time()
#print(c)

am.architecture.add_fault(f)
print('Going to switch4 from Filter1')
s = am.architecture.test_generate_in_connections_for_component_going_to(switch4, filter1)
print(s)
print('Going to switch4 from switch5')
s = am.architecture.test_generate_in_connections_for_component_going_to(switch4, switch5)
print(s)
print('Going to switch4 from switch3')
s = am.architecture.test_generate_in_connections_for_component_going_to(switch4, switch3)
print(s)
'''
#am.architecture.find_route(am.architecture.component_by_name['Mixer1'], am.architecture.component_by_name['Filter1'])
#c = am.application_finish_time()
#print(c)
#d = am.architecture.test_is_connected()
#print('Is connected after fault: '+str(d))
#c = am.application_finish_time()
#print(c)


#print('Restoring')
#am.architecture.restore()
#d = am.architecture.test_is_connected()
#print('Is connected after restoring: '+str(d))
#c = am.application_finish_time()
#print(c)

#d = am.application_finish_time()
#print(d)

'''
mix1 = am.architecture.component_by_name['Mixer1']
switch1 = am.architecture.component_by_name['Switch1']
am.make_component_fault_tolerant(mix1)

print('Switch1 in connections: '+str(switch1.in_connections))
print('Switch1 added in connections: '+str(switch1.added_in_connections))
print('Switch1 total in connections: '+str(switch1.total_in_connections()))
print('Switch1 out connections: '+str(switch1.out_connections))
print('Switch1 added out connections: '+str(switch1.added_out_connections))
print('Switch1 total out connections: '+str(switch1.total_out_connections()))
print(switch1.total_connections)

print('REPLACED MIXER1 WITH FTMIXER - types to components')
print(am.architecture.types_to_components)
print('Set of mixers usable')
s = am.architecture.get_components_of_type('mixer')
print(s)
am.add_connection_between_two_random_components()
print(am.architecture)
#am.undo_last_move()
am.make_random_component_non_fault_tolerant()
print('Switch1 in connections: '+str(switch1.in_connections))
print('Switch1 added in connections: '+str(switch1.added_in_connections))
print('Switch1 total in connections: '+str(switch1.total_in_connections()))
print('Switch1 out connections: '+str(switch1.out_connections))
print('Switch1 added out connections: '+str(switch1.added_out_connections))
print('Switch1 total out connections: '+str(switch1.total_out_connections()))
print(switch1.total_connections)
print(am.architecture)
print('UNREPLACED MIXER1 WITH FTMIXER - types to components')
print(am.architecture.types_to_components)
print('Set of mixers usable')
s = am.architecture.get_components_of_type('mixer')
print(s)
am.add_connection_between_two_random_components()
'''

'''
switch1 = am.architecture.component_by_name['Switch1']
filter1 = am.architecture.component_by_name['Filter1']
heater1 = am.architecture.component_by_name['Heater1']

print(am.architecture)
c = am.evaluate_architecture()
print('Inital cost: '+str(c))
am.make_component_fault_tolerant(filter1)

c = am.evaluate_architecture()
print(am.architecture)
print('Cost: '+str(c))

am.make_component_fault_tolerant(heater1)

c = am.evaluate_architecture()
print(am.architecture)
print('Cost: '+str(c))

componenttype = mix1.type
componentid = 'added ' + str(mix1.type) + '-546'
new_component = Component(componentid, componenttype)

am.insert_redundant_component(new_component)

c = am.evaluate_architecture()

print(am.architecture)
print('Cost: '+str(c))
'''

'''
f = fmp.faults['Blocked-channel-Switch1-Mixer1']

mix1 = am.architecture.component_by_name['Mixer1']
switch1 = am.architecture.component_by_name['Switch1']

print('Mixer1 in connections: '+str(mix1.in_connections))
print('Mixer1 added in connections: '+str(mix1.added_in_connections))
print('Mixer1 total in connections: '+str(mix1.total_in_connections()))
print('Mixer1 out connections: '+str(mix1.out_connections))
print('Mixer1 added out connections: '+str(mix1.added_out_connections))
print('Mixer1 total out connections: '+str(mix1.total_out_connections()))

print('Switch1 in connections: '+str(switch1.in_connections))
print('Switch1 added in connections: '+str(switch1.added_in_connections))
print('Switch1 total in connections: '+str(switch1.total_in_connections()))
print('Switch1 out connections: '+str(switch1.out_connections))
print('Switch1 added out connections: '+str(switch1.added_out_connections))
print('Switch1 total out connections: '+str(switch1.total_out_connections()))

print('Inserting connection')
am.add_connection_between_two_components(switch1, mix1)

print('Mixer1 in connections: '+str(mix1.in_connections))
print('Mixer1 added in connections: '+str(mix1.added_in_connections))
print('Mixer1 total in connections: '+str(mix1.total_in_connections()))
print('Mixer1 out connections: '+str(mix1.out_connections))
print('Mixer1 added out connections: '+str(mix1.added_out_connections))
print('Mixer1 total out connections: '+str(mix1.total_out_connections()))

print('Switch1 in connections: '+str(switch1.in_connections))
print('Switch1 added in connections: '+str(switch1.added_in_connections))
print('Switch1 total in connections: '+str(switch1.total_in_connections()))
print('Switch1 out connections: '+str(switch1.out_connections))
print('Switch1 added out connections: '+str(switch1.added_out_connections))
print('Switch1 total out connections: '+str(switch1.total_out_connections()))

print('Adding fault to architecture')
am.architecture.add_fault(f)

print('Mixer1 in connections: '+str(mix1.in_connections))
print('Mixer1 added in connections: '+str(mix1.added_in_connections))
print('Mixer1 total in connections: '+str(mix1.total_in_connections()))
print('Mixer1 out connections: '+str(mix1.out_connections))
print('Mixer1 added out connections: '+str(mix1.added_out_connections))
print('Mixer1 total out connections: '+str(mix1.total_out_connections()))

print('Switch1 in connections: '+str(switch1.in_connections))
print('Switch1 added in connections: '+str(switch1.added_in_connections))
print('Switch1 total in connections: '+str(switch1.total_in_connections()))
print('Switch1 out connections: '+str(switch1.out_connections))
print('Switch1 added out connections: '+str(switch1.added_out_connections))
print('Switch1 total out connections: '+str(switch1.total_out_connections()))

print('Restoring architecture')
am.architecture.restore()
print('Mixer1 in connections: '+str(mix1.in_connections))
print('Mixer1 added in connections: '+str(mix1.added_in_connections))
print('Mixer1 total in connections: '+str(mix1.total_in_connections()))
print('Mixer1 out connections: '+str(mix1.out_connections))
print('Mixer1 added out connections: '+str(mix1.added_out_connections))
print('Mixer1 total out connections: '+str(mix1.total_out_connections()))

print('Switch1 in connections: '+str(switch1.in_connections))
print('Switch1 added in connections: '+str(switch1.added_in_connections))
print('Switch1 total in connections: '+str(switch1.total_in_connections()))
print('Switch1 out connections: '+str(switch1.out_connections))
print('Switch1 added out connections: '+str(switch1.added_out_connections))
print('Switch1 total out connections: '+str(switch1.total_out_connections()))

print('Undoing')
am.undo_last_move()
print('Mixer1 in connections: '+str(mix1.in_connections))
print('Mixer1 added in connections: '+str(mix1.added_in_connections))
print('Mixer1 total in connections: '+str(mix1.total_in_connections()))
print('Mixer1 out connections: '+str(mix1.out_connections))
print('Mixer1 added out connections: '+str(mix1.added_out_connections))
print('Mixer1 total out connections: '+str(mix1.total_out_connections()))

print('Switch1 in connections: '+str(switch1.in_connections))
print('Switch1 added in connections: '+str(switch1.added_in_connections))
print('Switch1 total in connections: '+str(switch1.total_in_connections()))
print('Switch1 out connections: '+str(switch1.out_connections))
print('Switch1 added out connections: '+str(switch1.added_out_connections))
print('Switch1 total out connections: '+str(switch1.total_out_connections()))
'''



#am.insert_component_to_make_random_component_redundant()
#am.add_connection_between_two_random_components()
#am.remove_random_component()

#for x in range(0,15):
#    am.insert_component_to_make_random_component_redundant()
#    if (x % 3) == 0:
#        #print('UNDO MOVE')
#        #am.undo_last_move()
#        print('REMOVE COMP MOVE')
#        am.remove_random_component()
#        print('UNDO MOVE')
#        am.undo_last_move()
#    am.add_connection_between_two_random_components()

#print(sa.cost)
#print(sa.architecture)
#a = am.make_random_component_fault_tolerant()
#am.add_connection_between_two_random_components()
#am.make_random_component_non_fault_tolerant()
#print(am.architecture)
#am.add_connection_between_two_random_components()
#for x in range(0, 10):
#    am.add_connection_between_two_random_components()
#print(am.connections_added)
#am.remove_random_component()
#print(am.connections_added)
#am.undo_last_move()
#print(am.connections_added)

#for x in range(0, 10):
#    am.remove_random_connection()



#c = 6570230.0 - 311096.0
#print(c)
#i = c / 0.9458
#print(i)
#d = math.exp(i)
#print(d)
#print(c)
#i = c / 9900.448802097482
#print(i)
#print(sa.architecture)
#print(am.architecture)
#for each in sa.architecture.components:
#    print(each)
#    print('Out connections: '+each.out_connections)
#    print('In connections: '+each.in_connections)


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