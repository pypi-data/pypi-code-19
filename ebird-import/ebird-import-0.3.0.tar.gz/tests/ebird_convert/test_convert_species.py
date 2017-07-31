import pkg_resources
import unittest

from ebird_import.handlers import WorldbirdsHandler


class LoadSpeciesTests(unittest.TestCase):
    """Tests for the function convert_species()."""

    def setUp(self):
        super(LoadSpeciesTests, self).setUp()
        self.obj = WorldbirdsHandler()
        location_file = pkg_resources.resource_filename(
            __name__, '../../data/birdlife_species_names.csv')
        self.obj.load_species(self.obj.species, location_file)

    def test_convert_known_species(self):
        """Species is updated with table values."""
        record = {
            'BirdLife common name': 'Manx Shearwater',
        }
        result = self.obj.convert_species(record)
        self.assertTrue(result['Species Converted'])

    def test_rename_species(self):
        """Species are renamed where appropriate."""
        record = {
            'BirdLife common name': 'Cinereous Vulture',
            }
        result = self.obj.convert_species(record)
        self.assertEquals(result['Common Name'], 'Black Vulture')

    def test_convert_unknown_species(self):
        """Species not in the table are unchanged."""
        record = {
            'BirdLife common name': 'Dodo',
            }
        result = self.obj.convert_species(record)
        self.assertEquals(result['Common Name'], 'Dodo')
        self.assertFalse(result['Species Converted'])
