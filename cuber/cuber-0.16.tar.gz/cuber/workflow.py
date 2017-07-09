import importlib
import copy
import json
import logging
from functools32 import lru_cache

logger = logging.getLogger(__name__)

class Workflow():
    def __init__(self, workflow_file):
        '''
        Example:
        {
            'module': 'dcg_metric',
            'class': 'DCGMetric',
            'deps': [
                {
                    'prefix': 'model1',
                    'graph': {

                    }
                },
                {
                    'arg_name': 'data',
                    'graph': {
                        'module': 'lastfm_data',
                        'class': 'LastFMData',
                        'attrs': {
                            'short': False,
                        }
                    }
                }

            ]
        }
        '''
        with open(workflow_file) as f:
            graph_json = f.read()
        logger.debug('Graph json: {}'.format(graph_json))
        self.graph = json.loads(graph_json)

    def get_graph(self, name):
        return self.graph[name]

    def run(self):
        return self.__run_graph('main')

    def __run_graph(self, graph_):
        logger.info('Graph to do: {}'.format(graph_))
        if isinstance(graph_, basestring): # this is graph name
            logger.info('Go to {}'.format(graph_))
            return self.__run_graph(self.get_graph(graph_))

        for key in graph_.keys():
            assert key in {'attrs', 'deps', 'class', 'module'}

        attrs = copy.deepcopy(graph_.get('attrs', {}))
        logger.debug('Fixed attrs keys: {}'.format(attrs.keys()))
        for dep in graph_.get('deps', {}):
            res = self.__run_graph(dep['graph'])
            if 'fields' not in dep:
                for key in res:
                    attrs[dep.get('prefix', '') + key] = res[key]
            else:
                for new_key, old_key in dep['fields'].iteritems():
                    attrs[dep.get('prefix', '') + new_key] = res[old_key]

        module = importlib.import_module(graph_['module'])
        logger.debug('Attrs keys: {}'.format(attrs.keys()))
        cube_init = getattr(module, graph_['class'])(**attrs)
        res = cube_init.get()
        return res
