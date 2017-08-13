# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.port import *
from simulation.aivika.modeler.stream import *
from simulation.aivika.modeler.data_type import *
from simulation.aivika.modeler.pdf import *

def uniform_random_server(transact_type, min_delay, max_delay, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays distributed uniformly."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomUniformServer '
    code += str(preemptible)
    code += ' '
    code += str(min_delay)
    code += ' '
    code += str(max_delay)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def uniform_int_random_server(transact_type, min_delay, max_delay, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with integer random delays distributed uniformly."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomUniformIntServer '
    code += str(preemptible)
    code += ' '
    code += str(min_delay)
    code += ' '
    code += str(max_delay)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def triangular_random_server(transact_type, min_delay, median_delay, max_delay, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the triangular distribution."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomTriangularServer '
    code += str(preemptible)
    code += ' '
    code += str(min_delay)
    code += ' '
    code += str(median_delay)
    code += ' '
    code += str(max_delay)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def normal_random_server(transact_type, mean_delay, delay_deviation, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the normal distribution."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomNormalServer '
    code += str(preemptible)
    code += ' '
    code += str(mean_delay)
    code += ' '
    code += str(delay_deviation)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def lognormal_random_server(transact_type, normal_mean_delay, normal_delay_deviation, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the lognormal distribution.

       The numerical parameters are related to the normal distribution that
       this distribution is derived from.
    """
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomLogNormalServer '
    code += str(preemptible)
    code += ' '
    code += str(normal_mean_delay)
    code += ' '
    code += str(normal_delay_deviation)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def exponential_random_server(transact_type, mean_delay, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the exponential distribution with the specified mean (a reciprocal of the rate)."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomExponentialServer '
    code += str(preemptible)
    code += ' '
    code += str(mean_delay)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def erlang_random_server(transact_type, scale, shape, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the Erlang distribution with the specified scale (a reciprocal of the rate) and shape parameters."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomErlangServer '
    code += str(preemptible)
    code += ' '
    code += str(scale)
    code += ' '
    code += str(shape)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def poisson_random_server(transact_type, mean_delay, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the Poisson distribution with the specified mean."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomPoissonServer '
    code += str(preemptible)
    code += ' '
    code += str(mean_delay)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def binomial_random_server(transact_type, probability, trials, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the binomial distribution with the specified probability and trials."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomBinomialServer '
    code += str(preemptible)
    code += ' '
    code += str(probability)
    code += ' '
    code += str(trials)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def gamma_random_server(transact_type, shape, scale, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the Gamma distribution by the specified shape and scale."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomGammaServer '
    code += str(preemptible)
    code += ' '
    code += str(shape)
    code += ' '
    code += str(scale)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def beta_random_server(transact_type, alpha, beta, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the Beta distribution by the specified shape parameters (alpha and beta)."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomBetaServer '
    code += str(preemptible)
    code += ' '
    code += str(alpha)
    code += ' '
    code += str(beta)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def weibull_random_server(transact_type, shape, scale, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the Weibull distribution by the specified shape and scale."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomWeibullServer '
    code += str(preemptible)
    code += ' '
    code += str(shape)
    code += ' '
    code += str(scale)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y

def discrete_random_server(transact_type, pdf, preemptible = False, name = None, descr = None):
    """Return a new server that holds the process with random delays having the discrete distribution by the specified probability density function."""
    expect_transact_type(transact_type)
    tp = transact_type.get_data_type()
    model = transact_type.get_model()
    code = 'newPreemptibleRandomDiscreteServer '
    code += str(preemptible)
    code += ' '
    code += encode_pdf(pdf)
    y = ServerPort(model, UNIT_TYPE, tp, tp, name = name, descr = descr)
    y.write(code)
    return y
