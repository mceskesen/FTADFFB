'''
Created on 28 May 2015

@author: Morten Chabert Eskesen
'''

import json
from collections import OrderedDict

class Serializer(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def export(self, to_file):
        raise NotImplementedError
        
class NetlistSerializer(Serializer):
    def __init__(self, architecture, initial_cost, cost, faultscenarios, runtime, generated_by, faultscenarios_tolerated=None, faultscenarios_not_tolerated=None):
        self.architecture = architecture
        self.initial_cost = initial_cost
        self.cost = cost
        self.components = len(architecture.components)
        self.connections = architecture.number_of_connections()
        self.valves = architecture.number_of_valves()
        self.runtime = runtime
        self.faultscenarios = faultscenarios
        self.generated_by = generated_by
        ftcomps = list(filter(lambda c: c.is_fault_tolerant(), architecture.components))
        self.ftcomponents = len(ftcomps)
        self.faultscenarios_tolerated = None
        self.faultscenarios_not_tolerated = None
        if faultscenarios_tolerated != None:
            self.faultscenarios_tolerated = faultscenarios_tolerated
        if faultscenarios_not_tolerated != None:
            self.faultscenarios_not_tolerated = faultscenarios_not_tolerated
        self.data = self.serialize_architecture()

    def serialize_architecture(self):
        arch = self.architecture
        
        d = OrderedDict()
        d['architecture'] = 'ft-'+arch.id
        d['flowPlaced'] = False
        d['flowRouted'] = False
        d['width'] = arch.size[0]
        d['height'] = arch.size[1]
        d['initialCost'] = self.initial_cost
        d['cost'] = self.cost
        d['components'] = self.components
        d['ftcomponents'] = self.ftcomponents
        d['connections'] = self.connections
        d['valves'] = self.valves
        d['faultscenarios'] = self.faultscenarios
        d['generatedByAlgorithm'] = self.generated_by
        d['runtime'] = self.runtime
        if self.faultscenarios_tolerated != None:
            d['faultscenariosTolerated'] = self.faultscenarios_tolerated
        if self.faultscenarios_not_tolerated != None:
            d['faultscenariosNotTolerated'] = self.faultscenarios_not_tolerated
        
        comps = []
        for comp in arch.components:
            o = OrderedDict()
            o['objectType'] = 'component'
            o['name'] = comp.id
            functions = []
            functions.append(comp.type)
            o['functions'] = functions
            o['orientation'] = 0
            comps.append(o)

        d['componentList'] = comps

        cons = []
        for con in arch.connections:
            o = OrderedDict()
            o['objectType'] = 'connection'
            o['name'] = con.name
            o['sourceComponent'] = con.components[0].id
            sinkcomps = []
            sinkcomps.append(OrderedDict({
                            'sinkName': con.components[1].id
                                        })
                            )
            o['sinkComponent'] = sinkcomps
            o['routed'] = False
            o['layer'] = 'flow'
            cons.append(o)

        d['connectionList'] = cons

        return d
    
    def export(self, to_file):
        with open(to_file, 'w') as file_object:
            json.dump(self.data, file_object, sort_keys = False, indent = 4, separators=(',', ': '))
    