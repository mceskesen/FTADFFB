import os

from parsing import ComponentLibraryParser, NetlistParser, ApplicationParser, ConfigParser, FaultModelParser
from serializing import NetlistSerializer
from architecture_modifier import GreedilyRandomAdaptiveSearchProcedure, SimulatedAnnealing
from faultmodel import RandomFaultScenarioGenerator
import time

clp = ComponentLibraryParser('components/library.json')

# IVD
ivd_arch_file = 'netlists/archIVD1s.json'
ivd_np_sa = NetlistParser(ivd_arch_file)
ivd_np_grasp = NetlistParser(ivd_arch_file)
ivd_sa_config = ConfigParser('config/ivd-sa-config.conf')
ivd_grasp_config = ConfigParser('config/ivd-grasp-config.conf')
ivd_ap = ApplicationParser('applications/ivd_seq.json')
ivd_np_sa.architecture.component_library = clp.get_component_library()
ivd_np_sa.parse()
ivd_np_grasp.architecture.component_library = clp.get_component_library()
ivd_np_grasp.parse()
ivd_fmp = FaultModelParser('faultmodels/faultmodel-ivd-example.json')
ivd_rfsg = RandomFaultScenarioGenerator(ivd_fmp.faultmodel, ivd_sa_config.data['faultscenarios'])
ivd_rfsg.generate_fault_scenarios()

# IVD SA
#ivd_sa_start = time.clock()
#ivd_sa = SimulatedAnnealing(ivd_np_sa.architecture, ivd_ap.application, ivd_rfsg.faultscenarios, ivd_sa_config.data)
#ivd_sa_end = time.clock()
#runtime_ivd_sa = ivd_sa_end - ivd_sa_start
#ivd_sa_ns = NetlistSerializer(ivd_sa.architecture, ivd_sa.initial_cost, ivd_sa.cost, len(ivd_sa.faultscenarios), runtime_ivd_sa, 'simulated_annealing')
#ivd_sa_ns.export('ftoutputs/ft-sa-archIVD1s-final.json')

# IVD GRASP
ivd_grasp_start = time.clock()
ivd_grasp = GreedilyRandomAdaptiveSearchProcedure(ivd_np_grasp.architecture, ivd_ap.application, ivd_rfsg.faultscenarios, ivd_grasp_config.data, ivd_arch_file, clp)
ivd_grasp_end = time.clock()
ivd_grasp_runtime = ivd_grasp_end - ivd_grasp_start
ivd_grasp_ns = NetlistSerializer(ivd_grasp.best_architecture, ivd_grasp.initial_cost, ivd_grasp.best_cost, len(ivd_grasp.faultscenarios), ivd_grasp_runtime, 'grasp')
ivd_grasp_ns.export('ftoutputs/ft-grasp-archIVD1s-final.json')