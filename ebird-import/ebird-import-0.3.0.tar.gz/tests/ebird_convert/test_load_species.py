import pkg_resources
import unittest

from ebird_import.handlers import WorldbirdsHandler


class LoadSpeciesTests(unittest.TestCase):
    """Tests for the function load_species()."""

    def test_load_species(self):
        """Species file can be loaded from package resources."""
        obj = WorldbirdsHandler()
        location_file = pkg_resources.resource_filename(
            __name__, '../../data/birdlife_species_names.csv')
        obj.load_species(obj.species, location_file)
        self.assertTrue(obj.species)
