from parsing import NetlistParser, ComponentLibraryParser, ApplicationParser, FaultModelParser, ConfigParser
from faultmodel import RandomFaultScenarioGenerator
from scheduling import ListScheduler
from architecture_modifier import ArchitectureModifier, SimulatedAnnealing, GreedilyRandomAdaptiveSearchProcedure
from architecture import Component
from serializing import NetlistSerializer
import math, sys, getopt, json, time, os
'''
Creates dot file for graphviz for a netlist
'''

def _get_command_line_options(argv):    
    '''
    Get configuration options from command line
    '''
    options = {}    
    # Get values from command line
    try:
        opts, _ = getopt.getopt(argv, 'hi:o:')
    except getopt.GetoptError:
        print('run.py -i <architecture_file> -o <output_file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -i <architecture_file> -o <output_file>')
        elif opt == '-i':
            options['architecture_file'] = arg
        elif opt == '-o':
            options['output_file'] = arg
    return options

def run(opt):
    arch_file = opt['architecture_file']
    output = opt['output_file']

    clp = ComponentLibraryParser('components/library.json')
    np = NetlistParser(arch_file)
    np.architecture.component_library = clp.get_component_library()
    np.parse()

    text = create_graphviz(np.architecture)
    export(output, text)


def create_graphviz(architecture):
	dotfile = 'graph {\n'
	dotfile += 'rankdir=LR;\n'

	comp_to_type = {}
	comp_id_to_usableid = {}

	for comp in architecture.components:
		if '-' in comp.id:
			compid = comp.id.replace('-', '')
		else:
			compid = comp.id
		if 'added ' in compid:
			comp_id = compid.replace('added ','')
		else:
			comp_id = compid
		comp_id_to_usableid[comp.id] = comp_id
		s = comp_id
		if comp.get_type() == 'input' or comp.get_type() == 'output':
			s += '[label='+compid+'][shape=plaintext]'
		elif comp.get_type() == 'switch':
			s += '[label='+compid+'][shape=point]'
		else:
			try:
				number = comp_to_type[comp.get_type()]
				comp_to_type[comp.get_type()] = number + 1
			except KeyError:
				number = 1
				comp_to_type[comp.get_type()] = number + 1
			if comp.is_fault_tolerant():
				label = 'ft'+comp.get_type()+str(number)
			else:
				label = comp.get_type()+str(number)

			s += '[label='+label+'][shape=rectangular]'

		s += ';\n'
		dotfile += s

	for con in architecture.connections:
		firstcomp = comp_id_to_usableid[con.components[0].id]
		secondcomp = comp_id_to_usableid[con.components[1].id]

		s = firstcomp
		s += ' -- '
		s += secondcomp
		s += ';\n'
		dotfile += s

	dotfile += '}'
	return dotfile


def export(to_file, text):
        with open(to_file, 'w') as file_object:
        	file_object.write(text)


if __name__ == '__main__':
    # Handle command line arguments
    opt = _get_command_line_options(sys.argv[1:])
    # Start program
    run(opt)