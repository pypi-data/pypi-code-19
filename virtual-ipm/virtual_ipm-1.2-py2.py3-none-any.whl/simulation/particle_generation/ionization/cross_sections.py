# -*- coding: utf-8 -*-

#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2017  The IPMSim collaboration <http://ipmsim.gitlab.io/IPMSim>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import abc

from anna import Action, Duplet, Choice, Integer, PhysicalQuantity, String, parametrize
from ionics.ddcs.random_sampling import InverseTransformSampling
from ionics.ddcs.voitkiv import VoitkivDDCS as Voitkiv
import numpy
from numpy.random import random_sample
import scipy.constants as constants

import virtual_ipm.data.gas_types as gas_types
from virtual_ipm.components import Model
from virtual_ipm.utils import arrange_input_as


# noinspection PyOldStyleClasses
class IonizationCrossSectionModel(Model):
    CONFIG_PATH = 'Ionization/Parameters'
    CONFIG_PATH_TO_IMPLEMENTATION = 'Ionization/Model'

    def __init__(self, configuration=None):
        super(IonizationCrossSectionModel, self).__init__(configuration)

    @abc.abstractmethod
    def generate_momenta(self, count):
        raise NotImplementedError


# noinspection PyOldStyleClasses
class ZeroVelocities(IonizationCrossSectionModel):
    """
    This model creates all particles at rest.
    """

    def __init__(self):
        super(ZeroVelocities, self).__init__()

    def generate_momenta(self, count):
        return numpy.zeros(shape=(count, 3), dtype=float)

Interface = IonizationCrossSectionModel


specific_gas_types = filter(
    lambda x: isinstance(getattr(gas_types, x), gas_types.GasType),
    dir(gas_types)
)
gas_type_choices = Choice(String('GasType'))
for specific_gas_type in specific_gas_types:
    gas_type_choices.add_option(specific_gas_type)
# noinspection PyTypeChecker
gas_type_parameter = Action(
    gas_type_choices,
    lambda x: getattr(gas_types, x)
)


# noinspection PyOldStyleClasses
@parametrize(
    gas_type_parameter,
    Duplet[PhysicalQuantity](
        'EnergyBoundaries',
        unit='eV',
        for_example=(0.01, 100.),
        info='The energies of generated electrons are sampled within this interval.'
    ),
    Integer(
        'EnergyBins',
        for_example=200,
        info='This parameter determines how fine or coarse the given energy range is sampled. '
             'For N energy bins there are exactly N different possible values for electron '
             'energies.'
    ),
    Duplet[PhysicalQuantity](
        'ScatteringAngleBoundaries',
        unit='rad',
        for_example=(0., '%(pi)'),
        info='The polar scattering angles (the angle between an electron velocity and the '
             'z-axis) is sampled within this interval.'
    ),
    Integer(
        'ScatteringAngleBins',
        for_example=200,
        info='This parameter determines how fine or coarse the given scattering angle range is '
             'sampled. For N scattering angle bins there are exactly N different possible values '
             'for scattering angles that generated electrons can have.'
    )
)
class VoitkivModel(IonizationCrossSectionModel):
    """
    This ionization model uses the Voitkiv double differential cross section.
    
    References
    ----------
    A.B. Voitkiv, N. Gruen, W. Scheid: "Hydrogen and helium ionization by relativistic projectiles
    in collisions with small momentum transfer", J.Phys.B: At.Mol.Opt.Phys 32, 1999
    """

    def __init__(self, beam, setup, configuration):
        super(VoitkivModel, self).__init__(configuration)
        self._beam = beam
        self._particle_mass = setup.particle_type.mass
        self.sampler = None

    def prepare(self):
        energy_min, energy_max = self._energy_boundaries
        energy_count = self._energy_bins
        angle_min, angle_max = self._scattering_angle_boundaries
        angle_count = self._scattering_angle_bins

        energies = arrange_input_as(energy_min, energy_max, energy_count, func='log10')
        scattering_angles = arrange_input_as(angle_min, angle_max, angle_count)

        ddcs = Voitkiv(
            self._beam.energy,
            self._beam.particle_type.charge_number,
            self._gas_type.composition
        )

        self.sampler = InverseTransformSampling(ddcs, energies, scattering_angles)
        # sampler = RejectionSampling(ddcs, energy_min, energy_max, angle_min, angle_max)

    def generate_momenta(self, count):
        if count == 0:
            return numpy.empty((0,))
        energies, angles = zip(*self.sampler.create_samples(count))
        energies, angles = numpy.array(energies), numpy.array(angles)
        # Conversion to SI units ([eV] -> [J]).
        energies *= constants.elementary_charge
        # Non-relativistic energies.
        momenta = numpy.sqrt(2. * self._particle_mass * energies)
        # Azimuthal angle:
        phis = 2. * constants.pi * random_sample(energies.shape[0])

        px = momenta * numpy.sin(angles) * numpy.cos(phis)
        py = momenta * numpy.sin(angles) * numpy.sin(phis)
        pz = momenta * numpy.cos(angles)

        return numpy.stack((px, py, pz))


# noinspection PyOldStyleClasses
@parametrize(
    PhysicalQuantity('SlopeEnergy', unit='eV', info='See doc string.'),
    PhysicalQuantity('MaxEnergy', unit='eV', info='See doc string.'),
    PhysicalQuantity('MaxProbability', unit='1', info='See doc string.'),
    PhysicalQuantity('ScatteringAngleStdDev', unit='rad', info='See doc string.'),
)
class SimpleDDCS(IonizationCrossSectionModel):
    """
    This ionization cross section models features two independent, simple parametrizations for
    the energy distribution and the scattering angle distribution.
    The energy distribution has two distinct parts and is characterized by three parameters:

    * `SlopeEnergy`: All energies <= `SlopeEnergy` have an equal probability, the probability for
      energies > `SlopeEnergy` decreases linearly until it reaches zero at `MaxEnergy`.
    * `MaxEnergy`: This parameter defines the maximum energy that a generated particle can have.
      The probability for energies ``SlopeEnergy < Energy <= MaxEnergy`` decreases linearly until
      it reaches zero at `MaxEnergy`.
    * `MaxProbability`: The (uniform) probability for energies <= `SlopeEnergy`; this parameter can
      be used to control the steepness of the slope.

    This is a visualization of the energy distribution::

          Probability
          ^
          |
          |
          |---------------      <--- MaxProbability
          |               \\
          |                \\
          |                 \\
          |                  \\
          |                   \\
          |                    \\
        --|---------------|-----|----------> Energy
          |
                          ^     ^
                          |     |
                          |     |
                SlopeEnergy     MaxEnergy

    The (polar) scattering angle is computed from a Gaussian distribution which is characterized by
    one parameter, namely its standard deviation. The distribution is centred around `pi/2` which
    corresponds to transverse scattering.
    The azimuthal angle is chosen randomly from a uniform distribution.
    """

    def __init__(self, setup, configuration):
        """
        Parameters
        ----------
        setup : :class:`Setup`
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super(SimpleDDCS, self).__init__(configuration)
        self._particle_mass = setup.particle_type.mass

    def generate_momenta(self, count):
        energies = self._sample_energies(count) * constants.elementary_charge  # [eV] -> SI units
        polar_angles = self._sample_scattering_angles(count)
        azimuthal_angles = 2.*numpy.pi * numpy.random.uniform(size=count)

        momenta = numpy.sqrt(2. * self._particle_mass * energies)

        px = momenta * numpy.sin(polar_angles) * numpy.cos(azimuthal_angles)
        py = momenta * numpy.sin(polar_angles) * numpy.sin(azimuthal_angles)
        pz = momenta * numpy.cos(polar_angles)

        return numpy.stack((px, py, pz))

    def _sample_energies(self, count):
        p_max = self._max_probability
        e_slope = self._slope_energy
        e_max = self._max_energy

        def flat_part(_):
            return p_max

        def slope_part(e):
            return p_max / (e_max - e_slope) * (e_max - e)

        def distribution(e):
            result = numpy.zeros(e.shape)
            result[e <= e_slope] = flat_part(e[e <= e_slope])
            result[e > e_slope] = slope_part(e[e > e_slope])
            return result

        samples = numpy.random.uniform(0., e_max, count)
        rejected = numpy.argwhere(
            numpy.random.uniform(0., p_max, count)
            <=
            1. - distribution(samples)
        ).flatten()
        while rejected.size > 0:
            samples[rejected] = numpy.random.uniform(0., e_max, len(rejected))
            rejected = rejected[
                numpy.random.uniform(0., p_max, len(rejected))
                <=
                1. - distribution(samples[rejected])
            ]
        return samples

    def _sample_scattering_angles(self, count):
        return numpy.random.normal(
            loc=numpy.pi/2.,
            scale=self._scattering_angle_std_dev,
            size=count
        )
