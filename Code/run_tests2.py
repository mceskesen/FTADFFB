'''
Created 11 June 2015

@author: Morten Chabert Eskesen
'''

from parsing import NetlistParser, ComponentLibraryParser, ApplicationParser, FaultModelParser, ConfigParser
from faultmodel import RandomFaultScenarioGenerator
from scheduling import ListScheduler
from architecture_modifier import ArchitectureModifier, SimulatedAnnealing, GreedilyRandomAdaptiveSearchProcedure
from architecture import Component
from serializing import NetlistSerializer
import time

clp = ComponentLibraryParser('components/library.json')

arch_file = 'netlists/arch-mes-example.json'
np = NetlistParser(arch_file)

config_sa = ConfigParser('config/arch-mes-sa-config.conf')
config_grasp = ConfigParser('config/arch-mes-grasp-config.conf')

ap = ApplicationParser('applications/mes_seq_motivational-example.json')

np.architecture.component_library = clp.get_component_library()
np.parse()

fmp = FaultModelParser('faultmodels/faultmodel-motivational-example.json')

rfsg1 = RandomFaultScenarioGenerator(fmp.faultmodel, 50)
rfsg1.generate_fault_scenarios()

rfsg2 = RandomFaultScenarioGenerator(fmp.faultmodel, 85)
rfsg2.generate_fault_scenarios()

rfsg3 = RandomFaultScenarioGenerator(fmp.faultmodel, 121)
rfsg3.generate_fault_scenarios()

start1 = time.clock()
grasp1 = GreedilyRandomAdaptiveSearchProcedure(np.architecture, ap.application, rfsg1.faultscenarios, config_grasp.data, arch_file, clp)
end1 = time.clock()
runtime1 = end1 - start1

start2 = time.clock()
grasp2 = GreedilyRandomAdaptiveSearchProcedure(np.architecture, ap.application, rfsg2.faultscenarios, config_grasp.data, arch_file, clp)
end2 = time.clock()
runtime2 = end2 - start2


start3 = time.clock()
grasp3 = GreedilyRandomAdaptiveSearchProcedure(np.architecture, ap.application, rfsg3.faultscenarios, config_grasp.data, arch_file, clp)
end3 = time.clock()
runtime3 = end3 - start3

am = ArchitectureModifier(np.architecture, ap.application, rfsg1.faultscenarios, config_grasp.data)
tolerance_grasp1 = am.run_all_faultscenarios_on_architecture(grasp1.best_architecture, rfsg3.faultscenarios)
tolerated_grasp1 = tolerance_grasp1[0]
not_tolerated_grasp1 = tolerance_grasp1[1]

tolerance_grasp2 = am.run_all_faultscenarios_on_architecture(grasp2.best_architecture, rfsg3.faultscenarios)
tolerated_grasp2 = tolerance_grasp2[0]
not_tolerated_grasp2 = tolerance_grasp2[1]

tolerance_grasp3 = am.run_all_faultscenarios_on_architecture(grasp3.best_architecture, rfsg3.faultscenarios)
tolerated_grasp3 = tolerance_grasp3[0]
not_tolerated_grasp3 = tolerance_grasp3[1]


ns_grasp1 = NetlistSerializer(grasp1.best_architecture, grasp1.initial_cost, grasp1.best_cost, len(grasp1.faultscenarios), runtime1, 'grasp', tolerated_grasp1, not_tolerated_grasp1)
ns_grasp1.export('ftoutputs/ft-grasp-arch-mes-example-test1.json')

ns_grasp2 = NetlistSerializer(grasp2.best_architecture, grasp2.initial_cost, grasp2.best_cost, len(grasp2.faultscenarios), runtime2, 'grasp', tolerated_grasp2, not_tolerated_grasp2)
ns_grasp2.export('ftoutputs/ft-grasp-arch-mes-example-test2.json')

ns_grasp3 = NetlistSerializer(grasp3.best_architecture, grasp3.initial_cost, grasp3.best_cost, len(grasp3.faultscenarios), runtime3, 'grasp', tolerated_grasp3, not_tolerated_grasp3)
ns_grasp3.export('ftoutputs/ft-grasp-arch-mes-example-test3.json')