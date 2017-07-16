import abc
import random
import time
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List
import pickle

import numpy as np


# Loss calculators

class LossCalculator(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def calculate(self, sample1: 'GenericSample', sample2: 'GenericSample') -> float:
        pass


class LinearMatrixLossCalculator(LossCalculator):
    def calculate(self, sample1: 'GenericSample', sample2: 'GenericSample') -> float:
        return np.sum(
            np.abs(sample1.state() - sample2.state())
        ).item()


class SquaredMeanMatrixLossCalculator(LossCalculator):
    def calculate(self, sample1: 'NumpyArraySample', sample2: 'NumpyArraySample') -> float:
        return np.sqrt(
            np.sum(
                (sample1.state() - sample2.state()) ** 2
            )
        )


# Mutators

class Mutator(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def mutate(self, sample: 'GenericSample') -> 'GenericSample':
        pass


class RandomMatrixFieldChangeMutator(Mutator):
    def mutate(self, sample: 'NumpyArraySample') -> 'NumpyArraySample':
        sample_to_create = sample.clone()
        matrix = sample_to_create.state()

        max_w, max_h = matrix.shape
        x, y = random.randint(0, max_w - 1), random.randint(0, max_h - 1)
        matrix[x, y] = (matrix[x, y] + random.random()) / 2

        return sample_to_create


class RandomMatrixAreasMutator(Mutator):
    def __init__(self, horizontal_size_range: Tuple[int, int], vertical_size_range: Tuple[int, int]):
        self._horizontal_size_range = horizontal_size_range
        self._vertical_size_range = vertical_size_range

    def mutate(self, sample: 'NumpyArraySample') -> 'NumpyArraySample':
        sample_to_create = sample.clone()

        value_to_mix_with = random.random()
        max_w, max_h = sample_to_create.state().shape
        x, y = random.randint(0, max_w), random.randint(0, max_h)
        w, h = random.randint(*self._vertical_size_range), random.randint(*self._horizontal_size_range)

        for i in range(x, min(x + w, max_w)):
            for j in range(y, min(y + h, max_h)):
                sample_to_create.state()[i, j] = (sample_to_create.state()[i, j] + value_to_mix_with) / 2

        return sample_to_create


class SimplePaintbrushMatrixMutator(Mutator):
    def __init__(self, brush_widths_range=(1, 4), moves_length_range=(1, 10)):
        self._brush_widths_range = brush_widths_range
        self._moves_length_range = moves_length_range

    def mutate(self, sample: 'NumpyArraySample') -> 'NumpyArraySample':
        sample_to_create = sample.clone()
        matrix = sample_to_create.state()
        W, H = matrix.shape

        brush_position = np.array([random.randint(0, W - 1), random.randint(0, H - 1)])
        brush_width = random.randint(*self._brush_widths_range)
        move_length = random.randint(*self._moves_length_range)
        move_directions = np.array([random.randint(-1, 1), random.randint(-1, 1)])
        value = random.random()

        moves_done = 0
        while moves_done != move_length:
            x, y = brush_position[0], brush_position[1]
            if x < 0 or x >= W or y < 0 or y >= H:
                break
            matrix[x, y] = (matrix[x, y] + value) / 2
            self._fill_vertical(matrix, x, y, W, brush_width, value)
            self._fill_horizontal(matrix, x, y, H, brush_width, value)
            brush_position += move_directions
            moves_done += 1

        return sample_to_create

    def _fill_vertical(self, matrix, x, y, max_x, length, value):
        for i in range(x, min(x + (length // 2), max_x)):
            distance_covered = abs(x - i) or 1
            matrix[i, y] = (matrix[i, y] + (value / distance_covered)) / 2
        for i in range(x, max(x - (length // 2), 0, -1)):
            distance_covered = abs(x - i) or 1
            matrix[i, y] = (matrix[i, y] + (value / distance_covered)) / 2

    def _fill_horizontal(self, matrix, x, y, max_y, length, value):
        for i in range(y, min(y + (length // 2), max_y)):
            distance_covered = abs(y - i) or 1
            matrix[x, i] = (matrix[x, i] + (value / distance_covered)) / 2
        for i in range(y, max(y - (length // 2), 0, -1)):
            distance_covered = abs(y - i) or 1
            matrix[x, i] = (matrix[x, i] + (value / distance_covered)) / 2


# Crossers

class Crosser(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def cross(self, sample1: 'GenericSample', sample2: 'GenericSample') -> 'GenericSample':
        pass


class MeanValueMatrixCrosser(Crosser):
    def cross(self, sample1: 'NumpyArraySample', sample2: 'NumpyArraySample') -> 'GenericSample':
        return sample1.factory().create(
            (sample1.state() + sample2.state()) / 2
        )


# Sample generics

class GenericSample(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def state(self):
        pass

    def clone(self) -> 'GenericSample':
        return self.factory().clone(self)

    def factory(self) -> 'SampleFactory':
        return GenericFactory(self.__class__)

    def mutated(self, mutator: 'Mutator') -> 'GenericSample':
        return mutator.mutate(self)

    def cross_with(self, sample2: 'GenericSample', crosser: 'Crosser') -> 'GenericSample':
        return crosser.cross(self, sample2)

    def calculate_loss_to(self, blueprint: 'GenericSample', loss_calculator: LossCalculator):
        return loss_calculator.calculate(self, blueprint)


class NumpyArraySample(GenericSample):
    def __init__(self, state: np.array):
        self._state = np.copy(state)

    def state(self) -> np.array:
        return self._state


class SampleFactory(object):
    @abc.abstractmethod
    def create(self, *args, **kwargs) -> 'GenericSample':
        pass

    @abc.abstractmethod
    def clone(self, sample: 'GenericSample') -> 'GenericSample':
        pass


class GenericFactory(SampleFactory):
    def __init__(self, proxied_type: callable):
        self.proxied_type = proxied_type

    def create(self, *args, **kwargs) -> 'GenericSample':
        return self.proxied_type(*args, **kwargs)

    def clone(self, sample: 'GenericSample') -> 'GenericSample':
        return self.create(state=sample.state())


# State generator

class SampleStateGenerator(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate(self) -> object:
        pass


class RandomMatrixGenerator(SampleStateGenerator):
    def __init__(self, shape=(100, 100)):
        self._shape = shape

    def generate(self) -> object:
        return np.random.random(self._shape)


class ZeroMatrixGenerator(SampleStateGenerator):
    def __init__(self, shape=(100, 100)):
        self._shape = shape

    def generate(self) -> object:
        return np.zeros(self._shape)


# Combiners

class Combiner(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def combine(self, samples: List['GenericSample']) -> 'GenericSample':
        pass


class MatrixElementsCombiner(Combiner):
    def combine(self, samples: List['NumpyArraySample']) -> 'NumpyArraySample':
        matrix = []
        for x in range(samples[0].state().shape[0]):
            row = []
            for y in range(samples[0].state().shape[1]):
                element = []
                for sample in samples:
                    element.append(sample.state()[x, y])
                row.append(element)
            matrix.append(row)
        return NumpyArraySample(matrix)


# Step performer

class StepPerformer(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def perform_step(self, solvers: List['GenericSolver']):
        pass


class SequentialStepPerformer(StepPerformer):
    def perform_step(self, solvers: List['GenericSolver']):
        for solver in solvers:
            solver.step()


class ParallelStepPerformer(StepPerformer):
    def __init__(self, threads_count: int=2):
        self._threads_count = threads_count
        self._pool = self._create_thread_pool()

    def perform_step(self, solvers: List['GenericSolver']):
        _execute_in_pool_and_wait_for_results(
            solvers,
            self._pool,
            lambda pool, solver: pool.submit(solver.step)
        )

    def _create_thread_pool(self):
        return ThreadPoolExecutor(max_workers=self._threads_count)

    def __getstate__(self):
        fields = dict(self.__dict__)
        del fields['_pool']
        return fields

    def __setstate__(self, fields):
        self.__dict__.update(fields)
        self._pool = self._create_thread_pool()


# Algorithm itself

SampleAndItsLoss = namedtuple('SampleAndItsLoss', ['sample', 'loss'])


class Executor(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate_initial_population(self,
                                    samples_factory: 'SampleFactory',
                                    initial_sample_state_generator: 'SampleStateGenerator',
                                    population_size: int):
        pass

    @abc.abstractmethod
    def resolve_best_samples(self,
                             loss_calculator: 'LossCalculator',
                             blueprint: 'GenericSample',
                             best_samples_to_take: int) -> List['GenericSample']:
        pass

    @abc.abstractmethod
    def perform_crossing_with_best_samples(self, crosser: 'Crosser', best_samples: List['GenericSample']):
        pass

    @abc.abstractmethod
    def perform_mutation(self, mutator: 'Mutator'):
        pass


class SimpleExecutor(Executor):
    def __init__(self):
        self._population = None

    def generate_initial_population(self,
                                    samples_factory: 'SampleFactory',
                                    initial_sample_state_generator: 'SampleStateGenerator',
                                    population_size: int):
        self._population = []
        for _ in range(population_size):
            self._population.append(
                samples_factory.create(initial_sample_state_generator.generate())
            )

    def resolve_best_samples(self,
                             loss_calculator: 'LossCalculator',
                             blueprint: 'GenericSample',
                             best_samples_to_take: int) -> List['GenericSample']:
        self._population = sorted(
            self._population,
            key=lambda individual: loss_calculator.calculate(individual, blueprint)
        )
        return self._population[:best_samples_to_take]

    def perform_crossing_with_best_samples(self, crosser: 'Crosser', best_samples: List['GenericSample']):
        best_genome_sample = best_samples[0]
        for i in range(1, len(best_samples)):
            best_genome_sample = best_genome_sample.cross_with(best_samples[i], crosser)

        for i in range(len(best_samples), len(self._population)):
            self._population[i] = self._population[i].cross_with(best_genome_sample, crosser)

    def perform_mutation(self, mutator: 'Mutator'):
        for i in range(len(self._population)):
            self._population[i] = self._population[i].mutated(mutator)

    def population(self) -> List['GenericSample']:
        return self._population


class MultithreadedExecutor(Executor):
    def __init__(self, threads_count: int=4):
        self._threads_count = threads_count
        self._pool = self._create_thread_pool()
        self._executors = None

    def generate_initial_population(self,
                                    samples_factory: 'SampleFactory',
                                    initial_sample_state_generator: 'SampleStateGenerator',
                                    population_size: int):
        self._executors = []
        for i in range(self._threads_count):
            executor = SimpleExecutor()
            executor.generate_initial_population(samples_factory, initial_sample_state_generator, population_size)
            self._executors.append(executor)

    def resolve_best_samples(self,
                             loss_calculator: 'LossCalculator',
                             blueprint: 'GenericSample',
                             best_samples_to_take: int) -> List['GenericSample']:
        executors_response = _execute_in_pool_and_wait_for_results(
            self._executors,
            self._pool,
            lambda pool, executor: pool.submit(executor.resolve_best_samples, loss_calculator, blueprint, best_samples_to_take)
        )
        best_samples_of_all_executors = [sample for samples in executors_response for sample in samples]

        best_samples_of_all_executors = sorted(
            best_samples_of_all_executors,
            key=lambda individual: loss_calculator.calculate(individual, blueprint)
        )
        return best_samples_of_all_executors[:best_samples_to_take]

    def perform_crossing_with_best_samples(self, crosser: 'Crosser', best_samples: List['GenericSample']):
        _execute_in_pool_and_wait_for_results(
            self._executors,
            self._pool,
            lambda pool, executor: pool.submit(executor.perform_crossing_with_best_samples, crosser, best_samples)
        )

    def perform_mutation(self, mutator: 'Mutator'):
        _execute_in_pool_and_wait_for_results(
            self._executors,
            self._pool,
            lambda pool, executor: pool.submit(executor.perform_mutation, mutator)
        )

    def _create_thread_pool(self):
        return ThreadPoolExecutor(max_workers=self._threads_count)

    def __getstate__(self):
        fields = dict(self.__dict__)
        del fields['_pool']
        return fields

    def __setstate__(self, fields):
        self.__dict__.update(fields)
        self._pool = self._create_thread_pool()


class StatisticsCollecting(object):
    def __init__(self):
        self._statistics = Statistics()

    def statistics(self) -> 'Statistics':
        return self._statistics

    def _add_observation(self, loss: float):
        self._statistics.add_observation(loss)


class BestSampleSaving(object):
    def __init__(self):
        self._best_sample_and_loss = None

    def best(self) -> 'SampleAndItsLoss':
        return self._best_sample_and_loss

    def _set_best_if_better_than_current(self, sample: GenericSample, loss: float):
        if loss < self._best_sample_and_loss.loss:
            self._force_new_best(sample, loss)

    def _force_new_best(self, sample: GenericSample, loss: float):
        self._best_sample_and_loss = SampleAndItsLoss(
            sample=sample,
            loss=loss
        )


class StateSerializing(object):
    @classmethod
    def load_from_file(cls, file_path: str):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def save_to_file(self, file_path: str):
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)


class GenericSolver(StatisticsCollecting, BestSampleSaving, StateSerializing, metaclass=abc.ABCMeta):
    def __init__(self):
        StatisticsCollecting.__init__(self)
        BestSampleSaving.__init__(self)

    @abc.abstractmethod
    def step(self):
        pass


class SimpleSolver(GenericSolver):
    def __init__(self,
                 population_size: int,
                 best_samples_to_take: int,
                 blueprint: 'GenericSample',
                 mutator: 'Mutator',
                 crosser: 'Crosser',
                 loss_calculator: 'LossCalculator',
                 initial_sample_state_generator: 'SampleStateGenerator',
                 executor: 'Executor'=SimpleExecutor()):
        GenericSolver.__init__(self)

        self._population_size = population_size
        self._best_samples_to_take = best_samples_to_take
        self._blueprint = blueprint
        self._mutator = mutator
        self._crosser = crosser
        self._loss_calculator = loss_calculator
        self._initial_sample_state_generator = initial_sample_state_generator
        self._executor = executor

        self._generate_initial_population()

    def step(self):
        self._perform_crossing_with_best_samples()
        self._mutate_population()
        current_generation_best_individual = self._evaluate_best_sample_and_its_loss()

        self._set_best_if_better_than_current(
            sample=current_generation_best_individual.sample,
            loss=current_generation_best_individual.loss
        )

        self._add_observation(current_generation_best_individual.loss)

    def _generate_initial_population(self):
        self._executor.generate_initial_population(
            self._blueprint.factory(),
            self._initial_sample_state_generator,
            self._population_size
        )

        best_sample = self._executor.resolve_best_samples(self._loss_calculator, self._blueprint, 1)[0]
        self._force_new_best(
            sample=best_sample,
            loss=self._loss_calculator.calculate(best_sample, self._blueprint)
        )

    def _resolve_best_samples(self):
        return self._executor.resolve_best_samples(self._loss_calculator, self._blueprint, self._best_samples_to_take)

    def _perform_crossing_with_best_samples(self):
        self._executor.perform_crossing_with_best_samples(self._crosser, self._resolve_best_samples())

    def _evaluate_best_sample_and_its_loss(self):
        best_samples = self._resolve_best_samples()
        tournament_winner = best_samples[0]
        tournament_winner_loss = self._loss_calculator.calculate(tournament_winner, self._blueprint)

        return SampleAndItsLoss(sample=tournament_winner, loss=tournament_winner_loss)

    def _mutate_population(self):
        self._executor.perform_mutation(self._mutator)


class MultidimensionalSolver(GenericSolver):
    def __init__(self,
                 population_size: int,
                 best_samples_to_take: int,
                 blueprints: List['GenericSample'],
                 mutator: 'Mutator',
                 crosser: 'Crosser',
                 loss_calculator: 'LossCalculator',
                 initial_sample_state_generator: 'SampleStateGenerator',
                 combiner: 'Combiner',
                 step_performer: 'StepPerformer'=SequentialStepPerformer(),
                 executor: 'Executor' = SimpleExecutor()):
        GenericSolver.__init__(self)

        self.dimensions = len(blueprints)
        self._combiner = combiner
        self._step_performer = step_performer
        self._solvers = [SimpleSolver(
            population_size=population_size,
            best_samples_to_take=best_samples_to_take,
            blueprint=blueprints[i],
            mutator=mutator,
            crosser=crosser,
            loss_calculator=loss_calculator,
            initial_sample_state_generator=initial_sample_state_generator,
            executor=executor
        ) for i in range(self.dimensions)]

    def step(self):
        self._step_performer.perform_step(self._solvers)

    def statistics(self) -> 'CombinedStatistics':
        return CombinedStatistics([s.statistics() for s in self._solvers])

    def best(self) -> 'SampleAndItsLoss':
        sample = self._combiner.combine([s.best().sample for s in self._solvers])
        average_loss = np.average([s.best().loss for s in self._solvers])
        return SampleAndItsLoss(sample, average_loss)


# Statistics

class Statistics(object):
    def __init__(self):
        self.iterations = 0
        self.current_loss = 0
        self.current_speed = 0
        self.average_speed = 0
        self.time_per_last_iteration = 0
        self.average_time_per_iteration = 0
        self.learning_rate = 0

        self._last_loss = 0
        self._last_time = time.time()

    def to_dict(self):
        return {
            'iterations': self.iterations,
            'current_loss': self.current_loss,
            'current_speed': self.current_speed,
            'average_speed': self.average_speed,
            'time_per_last_iteration': self.time_per_last_iteration,
            'average_time_per_iteration': self.average_time_per_iteration,
            'learning_rate': self.learning_rate
        }

    def add_observation(self, loss: float):
        self.time_per_last_iteration = (time.time() - self._last_time) * 1000
        self.iterations += 1
        self.current_loss = loss

        if self.iterations > 1:
            self.current_speed = abs(self.current_loss - self._last_loss)
            self.average_speed = self.average_speed + ((self.current_speed - self.average_speed) / self.iterations)

            self.average_time_per_iteration = self.average_time_per_iteration + \
                                              ((self.time_per_last_iteration - self.average_time_per_iteration) / self.iterations)
        else:
            self.average_speed = self.current_speed
            self.average_time_per_iteration = self.time_per_last_iteration

        self.learning_rate = self.average_speed / self.average_time_per_iteration

        self._last_loss = loss
        self._last_time = time.time()


class CombinedStatistics(Statistics):
    def __init__(self, statistics: List['Statistics']):
        Statistics.__init__(self)

        self.iterations = np.average([s.iterations for s in statistics])
        self.current_loss = np.average([s.current_loss for s in statistics])
        self.current_speed = np.average([s.current_speed for s in statistics])
        self.average_speed = np.average([s.average_speed for s in statistics])
        self.time_per_last_iteration = np.average([s.time_per_last_iteration for s in statistics])
        self.average_time_per_iteration = np.average([s.average_time_per_iteration for s in statistics])
        self.learning_rate = np.average([s.learning_rate for s in statistics])


# Utils

def _execute_in_pool_and_wait_for_results(tasks, pool, operation):
    WAIT_EPSILON = 0.00001
    results = []

    for task in tasks:
        results.append(
            operation(pool, task)
        )

    while not all([result.done() for result in results]):
        time.sleep(WAIT_EPSILON)

    return [result.result() for result in results]
