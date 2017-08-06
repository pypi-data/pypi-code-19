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

from __future__ import absolute_import, print_function, unicode_literals

import abc

from anna import Action, Duplet, PhysicalQuantity, SubstitutionGroup, parametrize
from anna.utils import use_docs_from
import injector
import numpy
from scipy.constants import physical_constants

from virtual_ipm.components import Mutable
import virtual_ipm.di as di
from virtual_ipm.simulation.beams.utils import convert_lab_frame_bunch_length_to_bunch_frame, \
    compute_beta_and_gamma_from_energy
from . import bunch_parameters


_SPEED_OF_LIGHT = physical_constants['speed of light in vacuum'][0]


class BunchShape(Mutable):
    """
    (Abstract) Base class for bunch shape classes.
    """
    
    __metaclass__ = abc.ABCMeta

    CONFIG_PATH_TO_IMPLEMENTATION = 'BunchShape/Model'
    CONFIG_PATH = 'BunchShape/Parameters'

    def __init__(self, configuration=None):
        """
        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor` derived class, optional
        """
        super(BunchShape, self).__init__(configuration)

    def as_json(self):
        return dict(
            super(BunchShape, self).as_json(),
            length=self.length
        )

    @property
    def density_as_string(self):
        raise NotImplementedError

    @abc.abstractproperty
    def length(self):
        """
        The bunch length in the bunch frame. There is no fixed definition of the bunch length but
        it should be reasonably chosen for each implementation (e.g. 2*3sigma for
        a Gaussian bunch).

        .. note::
        This is the full length, not the half length of the bunch.

        Returns
        -------
        bunch_length : float
            The bunch length in the bunch frame, given in units of [m].
        """
        raise NotImplementedError

    @abc.abstractmethod
    def normalized_density_at(self, positions):
        """
        Retrieve the particle density at the given positions. The density is normalized to a bunch
        population of 1.

        Parameters
        ----------
        positions : :class:`~numpy.ndarray`, shape (3, N)
            Positions are stored as column vectors and are given in the bunch frame,
            in units of [m].

        Returns
        -------
        particle_densities : :class:`~numpy.ndarray`, shape (N,)
            The particle densities at the given positions, in units of [1/m^3].
        """
        raise NotImplementedError

    @abc.abstractmethod
    def normalized_linear_density_at(self, z_positions):
        """
        Retrieve the linear particle density at the given z-positions. The density is normalized to
        a bunch population of 1.

        Parameters
        ----------
        z_positions : :class:`~numpy.ndarray`, shape (N,)
            Given in the bunch frame, in units of [m].

        Returns
        -------
        linear_particle_densities : :class:`~numpy.ndarray`, shape (N,)
            The linear particle densities at the given z-positions, in units of [1/m].
        """
        raise NotImplementedError

    @abc.abstractmethod
    def generate_positions_in_transverse_plane(self, count, z):
        """
        Generate positions in the transverse plane specified by the `z`-coordinate according to
        the bunch shape's particle density.

        Parameters
        ----------
        count : int
            The number of transverse positions to be generated.
        z : float
            The longitudinal position specifying the transverse plane,
            given in the bunch frame, in units of [m].

        Returns
        -------
        transverse_positions : :class:`~numpy.ndarray`, shape (2, `count`)
            Positions are stored as column vectors and are given in the bunch frame,
            in units of [m].
        """
        raise NotImplementedError

Interface = BunchShape


@parametrize(
    Duplet[PhysicalQuantity]('TransverseSigma', unit='m'),
    _longitudinal_sigma=SubstitutionGroup(
        PhysicalQuantity(
            'LongitudinalSigmaBunchFrame',
            unit='m'
        )
    ).add_option(
        Action(
            PhysicalQuantity(
                'LongitudinalSigmaLabFrame',
                unit='s'
            ),
            convert_lab_frame_bunch_length_to_bunch_frame,
            depends_on=(bunch_parameters.aware_energy, bunch_parameters.aware_particle_type)
        ),
        # Do nothing because the conversion is already handled by the ActionParameter.
        lambda x: x
    )
)
class Gaussian(BunchShape):
    """This component represents a bunch that is Gaussian in all dimensions."""

    @injector.inject(configuration=di.components.configuration)
    def __init__(self, configuration):
        """
        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor` derived class
        """
        super(Gaussian, self).__init__(configuration)
        self._sigma = numpy.array(
            self._transverse_sigma + (self._longitudinal_sigma,)
        )

    def as_json(self):
        return dict(
            super(Gaussian, self).as_json(),
            sigma=self.sigma.tolist(),
        )

    @property
    def density_as_string(self):
        from string import Template

        density_template = Template(
            '1. / ($sqrt_two_pi * $sigma) '
            '* exp(- pow(x[$index] / $sigma, 2) / 2.0)'
        )
        density_template = Template(
            density_template.safe_substitute(
                {'sqrt_two_pi': numpy.sqrt(2. * numpy.pi)}
            )
        )
        x_density = density_template.substitute({'index': 0, 'sigma': self.sigma[0]})
        y_density = density_template.substitute({'index': 1, 'sigma': self.sigma[1]})
        z_density = density_template.substitute({'index': 2, 'sigma': self.sigma[2]})
        overall_density = ' * '.join((x_density, y_density, z_density))

        self.log.debug('density: %s', density_template.template)
        self.log.debug('x-density: %s', x_density)
        self.log.debug('y-density: %s', y_density)
        self.log.debug('z-density: %s', z_density)
        self.log.debug('overall density: %s', overall_density)

        return overall_density

    @property
    def sigma(self):
        """
        The standard deviation of the Gaussian charge distribution.

        Returns
        -------
        sigma : :class:`~numpy.ndarray`, shape (3,)
            In the bunch frame, in units of [m].
        """
        return self._sigma

    @property
    @use_docs_from(BunchShape)
    def length(self):
        return 8.0 * self.sigma[2]

    # noinspection PyTypeChecker
    @use_docs_from(BunchShape)
    def normalized_density_at(self, positions):
        two_pi_sqrt = numpy.sqrt(2 * numpy.pi)
        a = 1. / (two_pi_sqrt**3 * self._sigma[0] * self._sigma[1] * self._sigma[2])
        g = a * numpy.exp(
            -0.5 * numpy.dot(1. / self.sigma**2, positions**2)
        )
        return g

    @use_docs_from(BunchShape)
    def normalized_linear_density_at(self, z_positions):
        sigma_z = self.sigma[2]
        return 1. / (numpy.sqrt(2 * numpy.pi) * sigma_z) * numpy.exp(
            -0.5 * z_positions**2 / sigma_z**2
        )

    @use_docs_from(BunchShape)
    def generate_positions_in_transverse_plane(self, count, z):
        xs = numpy.random.normal(scale=self._sigma[0], size=count)
        ys = numpy.random.normal(scale=self._sigma[1], size=count)
        return numpy.vstack((xs, ys))


def convert_beam_current_to_charge_density(
        beam_current, inner_radius, outer_radius, energy, particle_type):
    beta, gamma = compute_beta_and_gamma_from_energy(energy, particle_type.rest_energy)
    velocity = _SPEED_OF_LIGHT * beta
    return (
        beam_current
        / (numpy.pi * (outer_radius**2 - inner_radius**2) * velocity * gamma)
    )


@parametrize(
    PhysicalQuantity('InnerRadius', unit='m'),
    PhysicalQuantity('OuterRadius', unit='m'),
    _charge_density=Action(
        PhysicalQuantity('BeamCurrent', unit='A'),
        convert_beam_current_to_charge_density,
        depends_on=(
                'InnerRadius', 'OuterRadius', bunch_parameters.aware_energy,
                bunch_parameters.aware_particle_type
        )
    )
)
class HollowDCBeam(BunchShape):
    def __init__(self, configuration):
        super(HollowDCBeam, self).__init__(configuration)
        self._particle_density = self._charge_density / physical_constants['elementary charge'][0]

    @property
    def inner_radius(self):
        return self._inner_radius

    @property
    def outer_radius(self):
        return self._outer_radius

    @property
    def length(self):
        return numpy.inf

    def as_json(self):
        return dict(
            super(HollowDCBeam, self).as_json(),
            inner_radius=self._inner_radius,
            outer_radius=self._outer_radius,
            charge_density=self._charge_density
        )

    def density_as_string(self):
        raise NotImplementedError

    def normalized_density_at(self, positions):
        density = numpy.zeros(positions.shape[1], dtype=float)
        radius = numpy.sqrt(positions[0, :]**2 + positions[1, :]**2)
        between_inner_and_outer_radius = numpy.logical_and(
            self._inner_radius <= radius,
            radius <= self._outer_radius
        )
        density[between_inner_and_outer_radius] = self._particle_density
        return density

    def normalized_linear_density_at(self, z_positions):
        return numpy.full(
            z_positions.shape,
            self._particle_density * numpy.pi * (self._outer_radius**2 - self._inner_radius**2)
        )

    def generate_positions_in_transverse_plane(self, count, z):
        radius = numpy.random.uniform(self._inner_radius, self._outer_radius, size=count)
        phi = numpy.random.uniform(0, 2*numpy.pi, size=count)
        return numpy.stack((
            radius * numpy.cos(phi),
            radius * numpy.sin(phi)
        ))


@parametrize(
    PhysicalQuantity('SemiMajorAxis', unit='m'),
    PhysicalQuantity('SemiMinorAxis', unit='m')
)
class ParabolicEllipsoid(BunchShape):
    """
    This bunch shape models a parabolically charged ellipsoid. This is a rotational symmetric
    spheriod (with respect to the z-axis) whose charge decreases parabolically when going from
    the center outwards.
    
    References
    ----------
    M.Dolinska (INR-Kiev), R.W.Mueller (GSI-Darmstadt), P.Strehl (GSI-Darmstadt):
    "The Electric Field of Bunches", July 5th 2000
    """

    def __init__(self, configuration):
        super(ParabolicEllipsoid, self).__init__(configuration)
        a = self.semi_major_axis
        b = self.semi_minor_axis
        self._xi0 = a / numpy.sqrt(a**2 - b**2)

    def as_json(self):
        return dict(
            super(ParabolicEllipsoid, self).as_json(),
            semi_major_axis=self.semi_major_axis,
            semi_minor_axis=self.semi_minor_axis
        )

    @property
    def semi_major_axis(self):
        return self._semi_major_axis

    @property
    def semi_minor_axis(self):
        return self._semi_minor_axis

    @property
    def density_as_string(self):
        """
        .. warning::
        The density string is only valid inside the ellipsoid. Outside of the ellipsoid it yields
        negative values however the density is to be considered zero outside.
        
        Returns
        -------
        density_as_string : unicode
        """
        pi = numpy.pi
        a = self.semi_major_axis
        b = self.semi_minor_axis
        return (
            '%(factor)e * (1. - pow(x[0] / %(b)e, 2)'
            '                 - pow(x[1] / %(b)e, 2)'
            '                 - pow(x[2] / %(a)e, 2))'
        ) % {
            'factor': 15. / (8. * pi * a * b**2),
            'a': a,
            'b': b
        }

    @property
    def length(self):
        return 2. * self.semi_major_axis

    @use_docs_from(BunchShape)
    def normalized_density_at(self, positions):
        result = numpy.empty(positions.shape[1], dtype=float)
        inside = self.inside_from_3d_cartesian_coordinates(positions)
        outside = ~inside
        pi = numpy.pi
        a = self.semi_major_axis
        b = self.semi_minor_axis
        r_square_inside = positions[0, inside]**2 + positions[1, inside]**2
        z_square_inside = positions[2, inside]**2
        result[inside] = 15. / (8. * pi * a * b**2) * (
            1. - r_square_inside/b**2 - z_square_inside/a**2
        )
        result[outside] = 0.
        return result

    @use_docs_from(BunchShape)
    def normalized_linear_density_at(self, z_positions):
        result = numpy.empty(z_positions.size, dtype=float)
        inside = numpy.logical_and(
            -self.semi_major_axis < z_positions,
            z_positions < self.semi_major_axis
        )
        outside = ~inside
        a = self.semi_major_axis
        z_square_inside = z_positions[inside] ** 2
        result[inside] = 15. / (16. * a) * (1. - z_square_inside / a**2) ** 2
        result[outside] = 0.
        return result

    @use_docs_from(BunchShape)
    def generate_positions_in_transverse_plane(self, count, z):
        if numpy.abs(z) >= self.semi_major_axis:
            raise ValueError('z-position outside of the ellipsoid')

        a = self.semi_major_axis
        b = self.semi_minor_axis

        def distribution(position):
            return (
                1. - (position[0]**2 + position[1]**2) / b**2 - z**2 / a**2
            )

        # Transverse plane of the rotational symmetric ellipsoid is a circle.
        # Note that this will generate a fair number of positions outside of the circle which
        # will are certainly rejected. However generating one dimension after another and confining
        # the second dimension to the circle's area would bias the probability of positions lying
        # closer towards the boundaries of the circle.
        # However we can confine the area with respect to the z-coordinate.
        max_xy = numpy.sqrt(1. - z**2 / a**2) * b
        samples = numpy.random.uniform(-1.0 * max_xy, max_xy, size=(2, count))
        rejected = numpy.argwhere(
            numpy.random.uniform(0., 1., count)
            <=
            1. - distribution(samples)
        ).flatten()
        while rejected.size > 0:
            samples[:, rejected] = \
                numpy.random.uniform(-1.0 * max_xy, max_xy, size=(2, len(rejected)))
            rejected = rejected[
                numpy.random.uniform(0., 1., len(rejected))
                <=
                1. - distribution(samples[:, rejected])
            ]
        return samples

    def inside_from_3d_cartesian_coordinates(self, positions):
        """
        Semi-major axis is along `z` (``positions[2]``), semi-minor axes are along `x`, `y`.

        Parameters
        ----------
        positions : :class:`numpy.ndarray`, shape (3, N)
            Cartesian coordinates (x, y, z).

        Returns
        -------
        inside : :class:`numpy.ndarray`, shape (N,), dtype=bool
            True for those who are inside.
        """
        a = self.semi_major_axis
        b = self.semi_minor_axis
        return (
                   positions[0] ** 2 / b ** 2
                   + positions[1] ** 2 / b ** 2
                   + positions[2] ** 2 / a ** 2
               ) <= 1.

    def inside_from_2d_elliptical_coordinates(self, positions):
        """
        Parameters
        ----------
        positions : :class:`numpy.ndarray`, shape (2, N)
            Elliptical coordinates (xi, eta); ``1 <= xi``, ``-1 <= eta <= 1``.

        Returns
        -------
        inside : :class:`numpy.ndarray`, shape (N,), dtype=bool
            True for those who are inside.
        """
        return positions[0] <= self._xi0
