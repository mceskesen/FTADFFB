import os

from parsing import ComponentLibraryParser, NetlistParser, ApplicationParser, ConfigParser, FaultModelParser
from serializing import NetlistSerializer
from architecture_modifier import GreedilyRandomAdaptiveSearchProcedure, SimulatedAnnealing
from faultmodel import RandomFaultScenarioGenerator
import time
'''
Runs the motivation example
'''
clp = ComponentLibraryParser('components/library.json')

# Motivational example
mov_arch_file = 'netlists/arch-mes-example.json'
mov_np_sa = NetlistParser(mov_arch_file)
mov_np_grasp = NetlistParser(mov_arch_file)
mov_sa_config = ConfigParser('config/arch-mes-sa-config.conf')
mov_grasp_config = ConfigParser('config/arch-mes-grasp-config.conf')
mov_ap = ApplicationParser('applications/mes_seq_motivational-example.json')
mov_np_sa.architecture.component_library = clp.get_component_library()
mov_np_sa.parse()
mov_np_grasp.architecture.component_library = clp.get_component_library()
mov_np_grasp.parse()
mov_fmp = FaultModelParser('faultmodels/faultmodel-motivational-example.json')
mov_rfsg = RandomFaultScenarioGenerator(mov_fmp.faultmodel, mov_sa_config.data['faultscenarios'])
mov_rfsg.generate_fault_scenarios()

# Motivational example SA
mov_sa_start = time.clock()
mov_sa = SimulatedAnnealing(mov_np_sa.architecture, mov_ap.application, mov_rfsg.faultscenarios, mov_sa_config.data)
mov_sa_end = time.clock()
runtime_mov_sa = mov_sa_end - mov_sa_start
mov_sa_ns = NetlistSerializer(mov_sa.architecture, mov_sa.initial_cost, mov_sa.cost, len(mov_sa.faultscenarios), runtime_mov_sa, 'simulated_annealing')
mov_sa_ns.export('ftoutputs/ft-sa-arch-mes-example-final.json')

# Motivational example GRASP
mov_grasp_start = time.clock()
mov_grasp = GreedilyRandomAdaptiveSearchProcedure(mov_np_grasp.architecture, mov_ap.application, mov_rfsg.faultscenarios, mov_grasp_config.data, mov_arch_file, clp)
mov_grasp_end = time.clock()
mov_grasp_runtime = mov_grasp_end - mov_grasp_start
mov_grasp_ns = NetlistSerializer(mov_grasp.best_architecture, mov_grasp.initial_cost, mov_grasp.best_cost, len(mov_grasp.faultscenarios), mov_grasp_runtime, 'grasp')
mov_grasp_ns.export('ftoutputs/ft-grasp-arch-mes-example-final.json')