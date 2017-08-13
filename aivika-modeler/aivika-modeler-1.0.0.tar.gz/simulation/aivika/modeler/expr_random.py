# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.model import *
from simulation.aivika.modeler.expr import *
from simulation.aivika.modeler.pdf import *

def uniform_random_expr(model, min_value, max_value):
    """Return an expression that returns the random value distributed uniformly."""
    code = '(const $ liftParameter $ '
    code += 'randomUniform '
    code += str(min_value)
    code += ' '
    code += str(max_value)
    code += ')'
    return Expr(model, code)

def uniform_int_random_expr(model, min_value, max_value):
    """Return an expression that returns the integer random value distributed uniformly."""
    code = '(const $ liftParameter $ '
    code += 'randomUniformInt '
    code += str(min_value)
    code += ' '
    code += str(max_value)
    code += ')'
    return Expr(model, code)

def triangular_random_expr(model, min_value, median_value, max_value):
    """Return an expression that returns the random value having the triangular distribution."""
    code = '(const $ liftParameter $ '
    code += 'randomTriangular '
    code += str(min_value)
    code += ' '
    code += str(median_value)
    code += ' '
    code += str(max_value)
    code += ')'
    return Expr(model, code)

def normal_random_expr(model, mean_value, value_deviation):
    """Return an expression that returns the random value having the normal distribution."""
    code = '(const $ liftParameter $ '
    code += 'randomNormal '
    code += str(mean_value)
    code += ' '
    code += str(value_deviation)
    code += ')'
    return Expr(model, code)

def lognormal_random_expr(model, normal_mean_value, normal_value_deviation):
    """Return an expression that returns the random value having the lognormal distribution.

       The numerical parameters are related to the normal distribution that
       this distribution is derived from.
    """
    code = '(const $ liftParameter $ '
    code += 'randomLogNormal '
    code += str(normal_mean_value)
    code += ' '
    code += str(normal_value_deviation)
    code += ')'
    return Expr(model, code)

def exponential_random_expr(model, mean_value):
    """Return an expression that returns the random value having the exponential distribution with the specified mean (a reciprocal of the rate)."""
    code = '(const $ liftParameter $ '
    code += 'randomExponential '
    code += str(mean_value)
    code += ')'
    return Expr(model, code)

def erlang_random_expr(model, scale, shape):
    """Return an expression that returns the random value having the Erlang distribution with the specified scale (a reciprocal of the rate) and shape parameters."""
    code = '(const $ liftParameter $ '
    code += 'randomErlang '
    code += str(scale)
    code += ' '
    code += str(shape)
    code += ')'
    return Expr(model, code)

def poisson_random_expr(model, mean_value):
    """Return an expression that returns the random value having the Poisson distribution with the specified mean."""
    code = '(const $ liftParameter $ '
    code += 'randomPoisson '
    code += str(mean_value)
    code += ')'
    return Expr(model, code)

def binomial_random_expr(model, probability, trials):
    """Return an expression that returns the random value having the binomial distribution with the specified probability and trials."""
    code = '(const $ liftParameter $ '
    code += 'randomBinomial '
    code += str(probability)
    code += ' '
    code += str(trials)
    code += ')'
    return Expr(model, code)

def gamma_random_expr(model, shape, scale):
    """Return an expression that returns the random value having the Gamma distribution by the specified shape and scale."""
    code = '(const $ liftParameter $ '
    code += 'randomGamma '
    code += str(shape)
    code += ' '
    code += str(scale)
    code += ')'
    return Expr(model, code)

def beta_random_expr(model, alpha, beta):
    """Return an expression that returns the random value having the Beta distribution by the specified shape parameters (alpha and beta)."""
    code = '(const $ liftParameter $ '
    code += 'randomBeta '
    code += str(alpha)
    code += ' '
    code += str(beta)
    code += ')'
    return Expr(model, code)

def weibull_random_expr(model, shape, scale):
    """Return an expression that returns the random value having the Weibull distribution by the specified shape and scale."""
    code = '(const $ liftParameter $ '
    code += 'randomWeibull '
    code += str(shape)
    code += ' '
    code += str(scale)
    code += ')'
    return Expr(model, code)

def discrete_random_expr(model, pdf):
    """Return an expression that returns the random value having the discrete distribution by the specified probability density function."""
    code = '(const $ liftParameter $ '
    code += 'randomDiscrete '
    code += encode_pdf(pdf)
    code += ')'
    return Expr(model, code)
