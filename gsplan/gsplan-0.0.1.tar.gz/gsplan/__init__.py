import os
import itertools
import functools
from collections import defaultdict
import csv
import pandas as pd


__author__ = 'Junya Kaneko <jyuneko@hotmail.com>'


def column_name(model_name, kind, name=None):
    if name is not None:
        return '%s__%s__%s' % (model_name, kind, name)
    else:
        return '%s__%s' % (model_name, kind)


def kind_name(column_name):
    model_name, kind, name = column_name.split('__')
    return name


def create_model_param_grid(recipe_model):
    param_names = [name for name in recipe_model['params']]
    param_grid = list(itertools.product(*[recipe_model['params'][name] for name in param_names]))
    return param_names, param_grid


class Planner:
    def __init__(self, recipe):
        self._recipe = recipe       
        
    def plan(self, n_inputs):
        column_names = ['input_id', 'pipe_id', ]
        model_param_grids = []
        for recipe_model in self._recipe['models']:
            model_param_names, model_param_grid = create_model_param_grid(recipe_model)
            column_names += [column_name(recipe_model['name'], 'param', name)
                              for name in model_param_names]
            column_names += [column_name(recipe_model['name'], 'score', score['name'])
                             for score in recipe_model['scores']]
            model_param_grids.append(model_param_grid)

        grid = []
        for pipe_id, pipe in enumerate(itertools.product(*model_param_grids)):
            grid.append([None, pipe_id, ])
            for model_id, model_params in enumerate(pipe):
                grid[-1] += [param for param in model_params]
                grid[-1] += [None for _ in self._recipe['models'][model_id]['scores']]
        grid = pd.DataFrame(grid, columns=column_names)

        grid = pd.concat([grid.copy().replace({'input_id':None}, i)
                          for i in range(n_inputs)]).reset_index(drop=True)

        phase_io = {}
        for phase in ('train', 'valid', 'test', 'pred'):
            phase_io[phase] = [['input_id', 'pipe_id'], ]
            for recipe_model in self._recipe['models']:
                phase_io[phase][0].append(column_name(recipe_model['name'], 'input', phase))
                phase_io[phase][0].append(column_name(recipe_model['name'], 'output', phase))
                
        for phase in ('train', 'valid', 'test', 'pred'):
            project_input_dir = os.path.join(self._recipe['dirs']['project'],
                                             self._recipe['dirs'][phase])
            for input_id, pipe_id in grid[['input_id', 'pipe_id']].values:
                pipe_io = []
                for recipe_model in self._recipe['models']:
                    model_base_dir = os.path.join(self._recipe['dirs']['project'],
                                                  '%s/%s' % (recipe_model['name'], phase))
                    if not pipe_io:
                        pipe_io.append(os.path.join(project_input_dir,
                                                    'input_%s.csv' % (input_id)))
                    else:
                        pipe_io.append(pipe_io[-1])
                    pipe_io.append(os.path.join(model_base_dir,
                                                'output_%s_%s.csv' % (input_id, pipe_id)))
                phase_io[phase].append([input_id, pipe_id, ] + pipe_io)
                
        phase_io = functools.reduce(lambda x, y: x.merge(y),
                                    [pd.DataFrame(pipes[1:], columns=pipes[0])
                                     for phase, pipes in phase_io.items()])
        return grid.merge(phase_io)
