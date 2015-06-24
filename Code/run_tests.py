'''
Created 11 June 2015

@author: Morten Chabert Eskesen
'''

import os

from parsing import ComponentLibraryParser, NetlistParser, ApplicationParser, ConfigParser, FaultModelParser
from serializing import NetlistSerializer
from architecture_modifier import GreedilyRandomAdaptiveSearchProcedure, SimulatedAnnealing
from faultmodel import RandomFaultScenarioGenerator
import time

clp = ComponentLibraryParser('components/library.json')

'''
Runs all tests at once
'''

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
pcr_sa_ns.export('ftoutputs/ft-sa-archPCR1s-2.json')

# PCR GRASP
pcr_grasp_start = time.clock()
pcr_grasp = GreedilyRandomAdaptiveSearchProcedure(pcr_np_grasp.architecture, pcr_ap.application, pcr_rfsg.faultscenarios, pcr_grasp_config.data, pcr_arch_file, clp)
pcr_grasp_end = time.clock()
pcr_grasp_runtime = pcr_grasp_end - pcr_grasp_start
pcr_grasp_ns = NetlistSerializer(pcr_grasp.best_architecture, pcr_grasp.initial_cost, pcr_grasp.best_cost, len(pcr_grasp.faultscenarios), pcr_grasp_runtime, 'grasp')
pcr_grasp_ns.export('ftoutputs/ft-grasp-archPCR1s-2.json')

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
mov_sa_ns.export('ftoutputs/ft-sa-arch-mes-example-2.json')

# Motivational example GRASP
mov_grasp_start = time.clock()
mov_grasp = GreedilyRandomAdaptiveSearchProcedure(mov_np_grasp.architecture, mov_ap.application, mov_rfsg.faultscenarios, mov_grasp_config.data, mov_arch_file, clp)
mov_grasp_end = time.clock()
mov_grasp_runtime = mov_grasp_end - mov_grasp_start
mov_grasp_ns = NetlistSerializer(mov_grasp.best_architecture, mov_grasp.initial_cost, mov_grasp.best_cost, len(mov_grasp.faultscenarios), mov_grasp_runtime, 'grasp')
mov_grasp_ns.export('ftoutputs/ft-grasp-arch-mes-example-2.json')


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
ivd_sa_start = time.clock()
ivd_sa = SimulatedAnnealing(ivd_np_sa.architecture, ivd_ap.application, ivd_rfsg.faultscenarios, ivd_sa_config.data)
ivd_sa_end = time.clock()
runtime_ivd_sa = ivd_sa_end - ivd_sa_start
ivd_sa_ns = NetlistSerializer(ivd_sa.architecture, ivd_sa.initial_cost, ivd_sa.cost, len(ivd_sa.faultscenarios), runtime_ivd_sa, 'simulated_annealing')
ivd_sa_ns.export('ftoutputs/ft-sa-archIVD1s-2.json')

# IVD GRASP
ivd_grasp_start = time.clock()
ivd_grasp = GreedilyRandomAdaptiveSearchProcedure(ivd_np_grasp.architecture, ivd_ap.application, ivd_rfsg.faultscenarios, ivd_grasp_config.data, ivd_arch_file, clp)
ivd_grasp_end = time.clock()
ivd_grasp_runtime = ivd_grasp_end - ivd_grasp_start
ivd_grasp_ns = NetlistSerializer(ivd_grasp.best_architecture, ivd_grasp.initial_cost, ivd_grasp.best_cost, len(ivd_grasp.faultscenarios), ivd_grasp_runtime, 'grasp')
ivd_grasp_ns.export('ftoutputs/ft-grasp-archIVD1s-2.json')