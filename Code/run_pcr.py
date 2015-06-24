import os

from parsing import ComponentLibraryParser, NetlistParser, ApplicationParser, ConfigParser, FaultModelParser
from serializing import NetlistSerializer
from architecture_modifier import GreedilyRandomAdaptiveSearchProcedure, SimulatedAnnealing
from faultmodel import RandomFaultScenarioGenerator
import time

'''
Runs the PCR benchmarks
'''

clp = ComponentLibraryParser('components/library.json')

# PCR
pcr_arch_file = 'netlists/archPCR1s.json'
pcr_np_sa = NetlistParser(pcr_arch_file)
pcr_np_grasp = NetlistParser(pcr_arch_file)
pcr_sa_config = ConfigParser('config/pcr-sa-config.conf')
pcr_grasp_config = ConfigParser('config/pcr-grasp-config.conf')
pcr_ap = ApplicationParser('applications/pcr_seq.json')
pcr_np_sa.architecture.component_library = clp.get_component_library()
pcr_np_sa.parse()
pcr_np_grasp.architecture.component_library = clp.get_component_library()
pcr_np_grasp.parse()
pcr_fmp = FaultModelParser('faultmodels/faultmodel-pcr-example.json')
pcr_rfsg = RandomFaultScenarioGenerator(pcr_fmp.faultmodel, pcr_sa_config.data['faultscenarios'])
pcr_rfsg.generate_fault_scenarios()

# PCR SA
pcr_sa_start = time.clock()
pcr_sa = SimulatedAnnealing(pcr_np_sa.architecture, pcr_ap.application, pcr_rfsg.faultscenarios, pcr_sa_config.data)
pcr_sa_end = time.clock()
runtime_pcr_sa = pcr_sa_end - pcr_sa_start
pcr_sa_ns = NetlistSerializer(pcr_sa.architecture, pcr_sa.initial_cost, pcr_sa.cost, len(pcr_sa.faultscenarios), runtime_pcr_sa, 'simulated_annealing')
pcr_sa_ns.export('ftoutputs/ft-sa-archPCR1s-final.json')

# PCR GRASP
pcr_grasp_start = time.clock()
pcr_grasp = GreedilyRandomAdaptiveSearchProcedure(pcr_np_grasp.architecture, pcr_ap.application, pcr_rfsg.faultscenarios, pcr_grasp_config.data, pcr_arch_file, clp)
pcr_grasp_end = time.clock()
pcr_grasp_runtime = pcr_grasp_end - pcr_grasp_start
pcr_grasp_ns = NetlistSerializer(pcr_grasp.best_architecture, pcr_grasp.initial_cost, pcr_grasp.best_cost, len(pcr_grasp.faultscenarios), pcr_grasp_runtime, 'grasp')
pcr_grasp_ns.export('ftoutputs/ft-grasp-archPCR1s-final.json')