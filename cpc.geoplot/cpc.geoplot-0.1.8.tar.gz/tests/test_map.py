# Built-in
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile
import os

# Third-party
from img_percent_diff import img_percent_diff
from pytest import raises

# This app
from cpc.geoplot import Geomap, GeomapError, GeoPlotError
from cpc.geoplot.geomap import get_supported_projections, get_supported_domains


def test_create_empty_Map():
    """Create empty Geomap images and compare them to pregenerated Mmap images"""
    # Loop over supported projections
    for proj in get_supported_projections():
        # Loop over supported domains
        for domain in get_supported_domains():
            # Create a Geomap with the given projection/domain - for global, only do lcc or equal-area
            if domain == 'global' and proj in ['lcc', 'equal-area']:
                continue
            map = Geomap(projection=proj, domain=domain)
            # Plot the Geomap to a file and compare it to a pregenerated Geomap
            with NamedTemporaryFile(suffix='.png', dir='.') as temp_file:
                test_img = temp_file.name
                map.save(test_img, dpi=100)
                # Compare the resulting Geomap plot to a pregenerated plot
                real_img = resource_filename('cpc.geoplot',
                                             'images/empty-Geomap-{}-{}.png'.format(proj, domain))
                assert img_percent_diff(test_img, real_img) < 0.001


def test_exception_raised_for_unsupported_projection():
    """Ensure an exception is raised for an unsupported projection"""
    with raises(GeomapError):
        map = Geomap(projection='unsupported')


def test_geoplot_exception():
    with raises(GeoPlotError):
        raise GeoPlotError
