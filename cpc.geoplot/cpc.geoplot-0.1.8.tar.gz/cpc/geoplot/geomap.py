"""
Defines a Map object. Maps contain a basemap, title, colorbar, etc. Fields can be plotted on a Map.
"""

# Built-ins
import reprlib
from pkg_resources import resource_filename
import math
import warnings

# Third-party
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, maskoceans
from cpc.geogrids import Geogrid
from cpc.geogrids.manipulation import smooth, fill_outside_mask_borders, interpolate
from mpl_toolkits.axes_grid1 import make_axes_locatable

# This package
from cpc.geoplot import GeomapError, GeofieldError

# Create reprlib
r = reprlib.Repr()
r.maxlist = 4  # max elements displayed for lists
r.maxstring = 50  # max characters displayed for strings


def get_supported_projections():
    """
    Get a list of supported projections for creating a Geomap

    ### Returns

    - *list of strings*: list of supported projections
    """
    return ['equal-area', 'lcc', 'mercator']


def get_supported_domains():
    """
    Get a list of supported domains for creating a Geomap

    ### Returns

    - *list of strings*: list of supported projections
    """
    return ['CONUS', 'global', 'NA', 'US']


def _create_colorbar(ax=None, cbar_type='normal', cbar_label='', cbar_tick_labels=None,
                     tercile_type='normal', levels=None, contours=None):
    if cbar_type == 'tercile':
        # If levels are supplied and cbar_tick_labels is None, make cbar_tick_labels match levels
        if levels is not None and cbar_tick_labels is None:
            cbar_tick_labels = levels
        # Generate probability tick labels
        labels = ['{:.0f}%'.format(math.fabs(level)) for level in levels]
        # Add the colorbar (attached to figure above)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("bottom", size="4%", pad=0.3)
        cb = plt.colorbar(contours, orientation="horizontal", cax=cax,
                          label=cbar_label, ticks=cbar_tick_labels)
        cb.ax.set_xticklabels(labels)
        cb.ax.tick_params(labelsize=8)
        # Add colorbar labels
        fontsize = 8
        tercile_type = tercile_type.capitalize()
        cb.ax.text(0.24, 1.2, 'Probability of Below {}'.format(tercile_type),
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
        cb.ax.text(0.5, 1.2, '{}'.format(tercile_type),
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
        cb.ax.text(0.76, 1.2, 'Probability of Above {}'.format(tercile_type),
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
    elif cbar_type == 'two-cat':
        # If levels are supplied and cbar_tick_labels is None, make cbar_tick_labels match levels
        if levels is not None and cbar_tick_labels is None:
            cbar_tick_labels = levels
        # Generate probability tick labels
        labels = ['{:.0f}%'.format(math.fabs(level)) for level in levels]
        # Add the colorbar (attached to figure above)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("bottom", size="4%", pad=0.3)
        cb = plt.colorbar(contours, orientation="horizontal", cax=cax,
                          label=cbar_label, ticks=cbar_tick_labels)
        cb.ax.set_xticklabels(labels)
        cb.ax.tick_params(labelsize=8)
        # Add colorbar labels
        fontsize = 8
        tercile_type = tercile_type.capitalize()
        cb.ax.text(0.24, 1.2, f'Probability of Below {tercile_type}',
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
        cb.ax.text(0.5, 1.2, 'EC',
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
        cb.ax.text(0.76, 1.2, f'Probability of Above {tercile_type}',
                   horizontalalignment='center', transform=cb.ax.transAxes,
                   fontsize=fontsize, fontstyle='normal')
    else:
        # Add the colorbar (attached to figure above)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("bottom", size="4%", pad=0.3)
        # If cbar_label is set
        if cbar_label and cbar_tick_labels is not None:
            cb = plt.colorbar(contours, orientation="horizontal", cax=cax,
                              label=cbar_label, ticks=cbar_tick_labels)
            cb.set_label(cbar_label, fontsize=8)
            cb.ax.tick_params(labelsize=8)
        elif cbar_label:
            cb = plt.colorbar(contours, orientation="horizontal", cax=cax,
                              label=cbar_label)
            cb.set_label(cbar_label, fontsize=8)
        elif cbar_tick_labels is not None:
            cb = plt.colorbar(contours, orientation="horizontal", cax=cax,
                              ticks=cbar_tick_labels)
            cb.ax.tick_params(labelsize=8)
        else:
            cb = plt.colorbar(contours, orientation="horizontal", cax=cax)
    return cb


class Geomap:
    """
    Geomap object
    """

    def __init__(self,
                 projection='equal-area', domain='US',
                 cbar=True, cbar_ends='triangular', cbar_type='normal',
                 cbar_color_spacing='natural', cbar_label='', cbar_tick_labels=None,
                 tercile_type='normal', title=''):
        # ------------------------------------------------------------------------------------------
        # Attributes
        #
        # Basemap
        self.projection = projection
        self.domain = domain
        # Colorbar
        self.cbar = cbar
        self.cbar_ends = cbar_ends
        self.cbar_type = cbar_type
        self.cbar_color_spacing = cbar_color_spacing
        self.cbar_label = cbar_label
        self.cbar_tick_labels = cbar_tick_labels
        # Other
        self.tercile_type = tercile_type
        self.title = title

        # ------------------------------------------------------------------------------------------
        # Create Basemap
        #
        # Create the figure and axes to store the Basemap
        fig, ax = plt.subplots()
        self.fig, self.ax = fig, ax
        # Mercator projection
        if self.projection == 'mercator':  # mercator projection
            if self.domain == 'US':  # U.S.
                lat_range = (25, 72)
                lon_range = (190, 300)
                latlon_line_interval = 10
            elif self.domain == 'NA':  # North America
                lat_range = (14, 72)
                lon_range = (190, 300)
                latlon_line_interval = 10
            elif self.domain == 'CONUS':  # CONUS
                lat_range = (24, 50)
                lon_range = (230, 295)
                latlon_line_interval = 5
            elif self.domain == 'global':  # global
                lat_range = (-90, 90)
                lon_range = (0, 360)
                latlon_line_interval = 30
            elif type(self.domain) is tuple and len(self.domain) == 4:  # custom box
                lat_range = self.domain[0:2]
                lon_range = self.domain[2:4]
                latlon_line_interval = 10
            else:
                raise GeomapError(
                    'domain must be either one of {}, or be a tuple of 4 numbers defining a custom '
                    'box (lat1, lat2, lon1, lon2)'.format(['US', 'NA', 'CONUS', 'global'])
                )
            basemap = Basemap(
                llcrnrlon=lon_range[0],
                llcrnrlat=lat_range[0],
                urcrnrlon=lon_range[1],
                urcrnrlat=lat_range[1],
                projection='mill',
                ax=ax,
                resolution='l'
            )
            basemap.drawcoastlines(linewidth=1, color='#333333')
            parallels = basemap.drawparallels(
                np.arange(lat_range[0], lat_range[1] + 1, latlon_line_interval),
                labels=[1, 1, 0, 0], fontsize=9
            )
            parallels[list(sorted(parallels.keys()))[0]].remove()
            basemap.drawmeridians(np.arange(lon_range[0], lon_range[1] + 1, latlon_line_interval),
                                  labels=[0, 0, 0, 1], fontsize=9)
            basemap.drawmapboundary(fill_color=(0, 0, 0, 0.8))
            basemap.drawcountries(color='#333333')
        elif self.projection in ['lcc', 'equal-area']:  # lcc or equal-area projection
            # Set the name of the projection for Basemap
            if self.projection == 'lcc':
                basemap_projection = 'lcc'
            elif self.projection == 'equal-area':
                basemap_projection = 'laea'

            if self.domain == 'US':
                basemap = Basemap(width=8000000, height=6600000, lat_0=53., lon_0=260.,
                                  projection=basemap_projection, ax=ax, resolution='l')
            elif self.domain == 'NA':
                basemap = Basemap(width=8000000, height=7500000, lat_0=48., lon_0=260.,
                                  projection=basemap_projection, ax=ax, resolution='l')
            elif self.domain == 'CONUS':
                basemap = Basemap(width=5000000, height=3200000, lat_0=39., lon_0=262.,
                                  projection=basemap_projection, ax=ax, resolution='l')
            else:
                raise GeomapError('When projection is set to lcc or equal-area, domain must be US, '
                               'NA, or CONUS')
            # Draw political boundaries
            basemap.drawcountries(linewidth=0.8, color='#333333')
            basemap.drawcoastlines(0.8, color='#333333')
            if self.domain in ['US', 'CONUS', 'NA']:
                basemap.readshapefile(resource_filename('cpc.geoplot', 'data/states'),
                                      name='states', drawbounds=True)
                for state in basemap.states:
                    x, y = zip(*state)
                    basemap.plot(x, y, marker=None, color='#333333', linewidth=0.5)
            # Fill oceans with dark grey (black with alpha of 0.8)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                basemap.drawlsmask(land_color='#FFFFFF', ocean_color=(0.4, 0.4, 0.4, 0.9))
        else:
            raise GeomapError('projection {} not supported, must be one of {}'.format(
                self.projection, get_supported_projections()))
        # Draw title
        if title != '':
            plt.title(title)
        # Save some things as attributes
        self.basemap = basemap
        self.ax = ax

    def __enter__(self):
        return self

    def closefig(self):
        plt.close('all')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.closefig()

    def save(self, file, dpi=600):
        plt.savefig(file, dpi=dpi, bbox_inches='tight')

    def show(self):
        plt.show()

    def plot(self, *fields):
        # Loop over fields
        first_field = True
        for field in fields:
            # Get grid of lats and lons
            lons, lats = np.meshgrid(field.geogrid.lons, field.geogrid.lats)
            # Get data from field
            data = field.data
            # --------------------------------------------------------------------------------------
            # Set some plotting options based on field attributes. These are mainly options that
            # Basemap.contour() wants one way (eg. colors set to None means Basemap.contour()
            # will automatically set the values), and Geomap.plot() wants another way (eg
            # fill_colors set to 'auto' means the fill colors will be automatically determined)
            #
            # Contour colors - convert 'auto' to None
            contour_colors = None if field.contour_colors == 'auto' else field.contour_colors
            # Fill colors/alpha - these should be None, unless this is the first field
            if first_field:
                fill_colors = field.fill_colors
                fill_alpha = 0.8 if field.fill_alpha == 'auto' else field.fill_alpha
            else:
                fill_colors = None if field.fill_colors == 'auto' else field.fill_colors
                fill_alpha = None if field.fill_alpha == 'auto' else field.fill_alpha
            # Levels - convert 'auto' to None
            if type(field.levels) != np.ndarray and field.levels == 'auto':
                levels = None
            else:
                levels = field.levels
            # --------------------------------------------------------------------------------------
            # Make sure subsequent Fields don't have fill_colors, fill_alpha, etc.
            #
            if not first_field:
                test = field.can_be_plotted_subsequently()
                if not test['result']:
                    raise GeofieldError('For subsequent Fields, ' + test['error'])
            # --------------------------------------------------------------------------------------
            # Reshape data to 2-d (if currently 1-d)
            #
            if data.ndim == 1:
                data = data.reshape((field.geogrid.num_y, field.geogrid.num_x))
            elif data.ndim == 2:
                pass
            else:
                raise GeofieldError('Geofield data must be 1- or 2-dimensional')
            # --------------------------------------------------------------------------------------
            # Smooth data (if necessary)
            #
            if field.smoothing_factor > 0:
                data = smooth(data, field.geogrid, factor=field.smoothing_factor)
            # --------------------------------------------------------------------------
            # Fill coastal values (if requested)
            #
            if field.fill_coastal_vals:
                # Datasets (particularly datasets on a course grid) that are masked out over
                # the water suffer from some missing grid points along the coast. The
                # methodology below remedies this, filling in those values while creating a
                # clean mask along the water. Shift the entire data array 1 grid point in
                # each direction, and for every grid point that becomes "unmissing" after
                # shifting the grid (every grid point that has a non-missing neighbor),
                # set the value of the grid point to the neighbor's value.
                data = fill_outside_mask_borders(data, passes=2)

                # Place data in a high-res grid so the ocean masking looks decent
                high_res_grid = Geogrid('1/6th-deg-global')
                data = interpolate(data, field.geogrid, high_res_grid)
                lons, lats = np.meshgrid(high_res_grid.lons, high_res_grid.lats)
                # Mask the ocean values
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
                    data = maskoceans((lons - 360), lats, data, inlands=True)
            # --------------------------------------------------------------------------------------
            # Plot field on Geomap
            #
            basemap = self.basemap
            # Set extend parameter based on cbar_ends
            if self.cbar_ends == 'triangular':
                extend = 'both'
            elif self.cbar_ends == 'square':
                extend = 'neither'
            else:
                raise GeomapError('cbar_ends must be either \'triangular\' or \'square\'')
            # Plot filled contours (if necessary)
            if fill_colors:
                # Set fill_colors to None instead of auto - pyplot.contourf wants None if we want
                # automated contour fill colors
                fill_colors = None if fill_colors == 'auto' else fill_colors
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    contours = basemap.contourf(lons, lats, data, latlon=True, colors=fill_colors,
                                                alpha=fill_alpha, levels=levels, extend=extend)
                # Also plot contours if contour_colors is not 'auto' or None
                if contour_colors not in ['auto', None]:
                    basemap.contour(lons, lats, data, latlon=True, colors=contour_colors,
                                    levels=levels, linewidths=0.5)
            else:
                contours = basemap.contour(lons, lats, data, latlon=True, colors=contour_colors,
                                           levels=levels, extend=extend, linewidths=0.5)
            # ----------------------------------------------------------------------------------------------
            # Plot contour labels for the first field
            #
            if field.contour_labels:
                self.ax.set_clip_on(True)
                if contours:
                    # If all contours all whole numbers, format the labels as such, otherwise
                    #  they
                    # all get 0.000 added to the end
                    if np.all(np.mod(contours.levels, 1) == 0):
                        fmt = '%d'
                    else:
                        fmt = '%s'
                    plt.clabel(contours, inline=1, fontsize=5, fmt=fmt)
            # --------------------------------------------------------------------------------------
            # Create colorbar
            #
            if first_field and field.fill_colors is not None:
                colorbar = _create_colorbar(ax=self.ax, cbar_type=self.cbar_type,
                                            cbar_label=self.cbar_label,
                                            cbar_tick_labels=self.cbar_tick_labels,
                                            tercile_type=self.tercile_type, levels=levels,
                                            contours=contours)

            first_field = False

    def __repr__(self):
        details = ''
        for key, val in sorted(vars(self).items()):
            details += eval(r.repr('- {}: {}\n'.format(key, val)))
        return 'Geomap:\n{}'.format(details)

if __name__ == '__main__':
    import numpy as np
    from cpc.geogrids import Geogrid
    from cpc.geoplot import Geomap, Geofield

    for i in range(100):
        with Geomap() as geomap:
            data = np.fromfile('/Users/mike/data1.bin', dtype='float32')
            geogrid = Geogrid('1deg-global')
            geofield = Geofield(data, geogrid)
            geomap.plot(geofield)
            geomap.save('test1.png', dpi=50)

    print()
