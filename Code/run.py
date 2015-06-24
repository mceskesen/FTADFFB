'''
Created on 11 June 2015

@author: Morten Chabert Eskesen
'''

import math, sys, getopt, json, time, os
from architecture_modifier import SimulatedAnnealing, GreedilyRandomAdaptiveSearchProcedure
from serializing import NetlistSerializer
from parsing import NetlistParser, ComponentLibraryParser, ApplicationParser, FaultModelParser, ConfigParser
from faultmodel import RandomFaultScenarioGenerator

def _get_command_line_options(argv):    
    '''
    Get configuration options from command line
    '''
    options = {}    
    # Get values from command line
    try:
        opts, _ = getopt.getopt(argv, 'hi:l:a:f:o:c:')
    except getopt.GetoptError:
        print('run.py -i <architecture_file> -l <component_library_file> -a <application_file> -f <faultmodel_file> -o <output_file>  -c <config_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -i <architecture_file> -l <component_library_file> -a <application_file> -f <faultmodel_file> -o <output_file>  -c <config_file>')
        elif opt == '-i':
            options['architecture_file'] = arg
        elif opt == '-l':
        	options['component_library_file'] = arg
        elif opt == '-a':
        	options['application_file'] = arg
        elif opt == '-f':
            options['faultmodel_file'] = arg
        elif opt == '-o':
            options['output_file'] = arg
        elif opt == '-c':
            options['config_file'] = arg
    return options

def run(opt):
    arch_file = opt['architecture_file']
    component_library = opt['component_library_file']
    application = opt['application_file']
    config = opt['config_file']
    output = opt['output_file']
    faultmodel = opt['faultmodel_file']

    clp = ComponentLibraryParser(component_library)
    np = NetlistParser(arch_file)
    config = ConfigParser(config)
    ap = ApplicationParser(application)
    np.architecture.component_library = clp.get_component_library()
    np.parse()
    fmp = FaultModelParser(faultmodel)
    rfsg = RandomFaultScenarioGenerator(fmp.faultmodel, config.data['faultscenarios'])
    rfsg.generate_fault_scenarios()

    if config.data['algorithm'] == 'GRASP':
        print('Starting GRASP')
        start = time.clock()
        grasp = GreedilyRandomAdaptiveSearchProcedure(np.architecture, ap.application, rfsg.faultscenarios, config.data, arch_file, clp)
        end = time.clock()
        runtime = end - start
        ns = NetlistSerializer(grasp.best_architecture, grasp.initial_cost, grasp.best_cost, len(grasp.faultscenarios), runtime, 'grasp')
        ns.export(output)

    #If simulated annealing
    if config.data['algorithm'] == 'SimulatedAnnealing':
        print('Starting Simulated Annealing')
        start = time.clock()
        sa = SimulatedAnnealing(np.architecture, ap.application, rfsg.faultscenarios, config.data)
        end = time.clock()
        runtime = end - start
        ns = NetlistSerializer(sa.architecture, sa.initial_cost, sa.cost, len(sa.faultscenarios), runtime, 'simulated_annealing')
        ns.export(output)


if __name__ == '__main__':
    # Handle command line arguments
    opt = _get_command_line_options(sys.argv[1:])
    # Start program
    run(opt)