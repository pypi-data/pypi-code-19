# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.port import *
from simulation.aivika.modeler.stream import *
from simulation.aivika.modeler.data_type import *
from simulation.aivika.modeler.pdf import *

def uniform_random_stream(transact_type, min_delay, max_delay):
    """Return a new stream of transacts with random delays distributed uniformly."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomUniformStream ' + str(min_delay) + ' ' + str(max_delay)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def uniform_int_random_stream(transact_type, min_delay, max_delay):
    """Return a new stream of transacts with integer random delays distributed uniformly."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomUniformIntStream ' + str(min_delay) + ' ' + str(max_delay)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def triangular_random_stream(transact_type, min_delay, median_delay, max_delay):
    """Return a new stream of transacts with random delays having the triangular distribution."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomTriangularStream ' + str(min_delay) + ' ' +  str(median_delay) + ' ' + str(max_delay)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def normal_random_stream(transact_type, mean_delay, delay_deviation):
    """Return a new stream of transacts with random delays having the normal distribution."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomNormalStream ' + str(mean_delay) + ' ' + str(delay_deviation)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def lognormal_random_stream(transact_type, normal_mean_delay, normal_delay_deviation):
    """Return a new stream of transacts with random delays having the lognormal distribution.

       The numerical parameters are related to the normal distribution that
       this distribution is derived from.
    """
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomLogNormalStream ' + str(normal_mean_delay) + ' ' + str(normal_delay_deviation)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def exponential_random_stream(transact_type, mean_delay):
    """Return a new stream of transacts with random delays having the exponential distribution with the specified mean (a reciprocal of the rate)."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomExponentialStream ' + str(mean_delay)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def erlang_random_stream(transact_type, scale, shape):
    """Return a new stream of transacts with random delays having the Erlang distribution with the specified scale (a reciprocal of the rate) and shape parameters."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomErlangStream ' + str(scale) + ' ' + str(shape)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def poisson_random_stream(transact_type, mean_delay):
    """Return a new stream of transacts with random delays having the Poisson distribution with the specified mean."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomPoissonStream ' + str(mean_delay)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def binomial_random_stream(transact_type, probability, trials):
    """Return a new stream of transacts with random delays having the binomial distribution with the specified probability and trials."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomBinomialStream ' + str(probability) + ' ' + str(trials)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def gamma_random_stream(transact_type, shape, scale):
    """Return a new stream of transacts with random delays having the Gamma distribution by the specified shape and scale."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomGammaStream ' + str(shape) + ' ' + str(scale)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def beta_random_stream(transact_type, alpha, beta):
    """Return a new stream of transacts with random delays having the Beta distribution by the specified shape parameters (alpha and beta)."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomBetaStream ' + str(alpha) + ' ' + str(beta)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def weibull_random_stream(transact_type, shape, scale):
    """Return a new stream of transacts with random delays having the Weibull distribution by the specified shape and scale."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomWeibullStream ' + str(shape) + ' ' + str(scale)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y

def discrete_random_stream(transact_type, pdf):
    """Return a new stream of transacts with random delays having the discrete distribution by the specified probability density function."""
    expect_transact_type(transact_type)
    model = transact_type.get_model()
    code = 'return $ mapStream (\\a -> ' + transact_type.coerce_arrival('a') + ') $ '
    code += 'randomDiscreteStream ' + encode_pdf(pdf)
    y = StreamPort(model, transact_type.get_data_type())
    y.bind_to_input()
    y.write(code)
    return y
