from parsing import NetlistParser, ComponentLibraryParser, ApplicationParser, FaultModelParser, ConfigParser
from faultmodel import RandomFaultScenarioGenerator
from scheduling import ListScheduler
from architecture_modifier import ArchitectureModifier, SimulatedAnnealing, GreedilyRandomAdaptiveSearchProcedure
from architecture import Component
import random
import math

clp = ComponentLibraryParser('components/library.json')

arch_file = 'netlists/arch-mes-example.json'
np = NetlistParser(arch_file)
config = ConfigParser('config/arch-mes-config.conf')
ap = ApplicationParser('applications/mes_seq_motivational-example.json')

np.architecture.component_library = clp.get_component_library()
np.parse()
fmp = FaultModelParser('faultmodels/faultmodel-motivational-example.json')
rfsg = RandomFaultScenarioGenerator(fmp.faultmodel, config.data['faultscenarios'])
rfsg.generate_fault_scenarios()
am = ArchitectureModifier(np.architecture, ap.application, rfsg.faultscenarios, config.data)
#c = am.evaluate_architecture(am.architecture)
#print('Cost: '+str(c))

grasp = GreedilyRandomAdaptiveSearchProcedure(np.architecture, ap.application, rfsg.faultscenarios, config.data, arch_file, clp)
print(grasp.best_architecture)
print(grasp.best_cost)
