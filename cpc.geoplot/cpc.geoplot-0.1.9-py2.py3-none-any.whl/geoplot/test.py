
# # PLOT SPAGHETTI DIAGRAMS
# from cpc.geogrids import Geogrid
# from cpc.geofiles.loading import load_ens_fcsts
# from cpc.geoplot import Geomap
# from cpc.geoplot import Geofield
#
#
# issued_dates = ['20160515']
# fhrs = range(150, 264, 6)
# members = range(0, 21)
# file_template = '/Users/mike/Work/data/TEST/{yyyy}/{mm}/{dd}/{cc}/gefs_{yyyy}{mm}{dd}_{cc}z_f{fhr}_m{member}.grb2'
# data_type = 'grib2'
# geogrid = Geogrid('1deg-global')
# grib_var = 'HGT'
# grib_level = '500 mb'
# dataset = load_ens_fcsts(issued_dates, fhrs, members, file_template, data_type, geogrid,
#                          grib_var=grib_var, grib_level=grib_level)
#
# map = Geomap()
#
# for member in members:
#     field = Geofield(dataset.ens[0, member, :], geogrid, levels=[5640], fill_colors=None,
#                   contour_colors='#666666')
#     map.plot(field)
#
# map.save('test.png')




# PLOT TERCILES
# import numpy as np
# from cpc.geogrids import Geogrid
# from cpc.geoplot import Geomap
# from cpc.geoplot import Geofield

#
# # Read data into a NumPy array
# heights = np.fromfile('/Users/mike/500hgt_05d_20120515.bin', dtype='float32')
# data = np.fromfile('../../test.bin', dtype='float32').reshape(19, 181*360)
# below = 100 * (1 - data[7])
# above = 100 * data[11]
# normal = 100 * (1 - (below + above))
# combined_forecast = np.zeros((181 * 360))
# combined_forecast = np.where((below > above) & (below > 0.333), -1 * below, combined_forecast)
# combined_forecast = np.where((above > below) & (above > 0.333), above, combined_forecast)
#
# # Define colors
# below_colors = [
#     (0.01, 0.31, 0.48),
#     (0.02, 0.44, 0.69),
#     (0.21, 0.56, 0.75),
#     (0.45, 0.66, 0.81),
#     (0.65, 0.74, 0.86),
#     (0.82, 0.82, 0.9),
#     (0.95, 0.93, 0.96)
# ]
# normal_color = [(0.75, 0.75, 0.75)]
# above_colors = [
#     (1., 0.94, 0.85),
#     (0.99, 0.83, 0.62),
#     (0.99, 0.73, 0.52),
#     (0.99, 0.55, 0.35),
#     (0.94, 0.4, 0.28),
#     (0.84, 0.19, 0.12),
#     (0.6, 0., 0.)
# ]
# combined_colors = below_colors + normal_color + above_colors
# # Create a Geogrid
# geogrid = Geogrid('1deg-global')
# # Create an empty map
# map = Geomap(cbar_type='tercile')
# # Create a Geofield to plot on the Geomap
# heights_field = Geofield(heights, geogrid, levels=np.arange(5000, 6000, 50), contour_colors='black',
#                       smoothing_factor=0.5, contour_labels=True)
# field = Geofield(combined_forecast, geogrid, fill_colors=combined_colors, smoothing_factor=0.5,
#               levels=[-90, -80, -70, -60, -50, -40, -33, 33, 40, 50, 60, 70, 80, 90])
# # Plot the Geofield on the Geomap
# # map.plot()
# map.plot(field, heights_field)
# # Save the plot to a PNG
# map.save('test.png')



# PLOT REGULAR DATA
# import numpy as np
# from cpc.geogrids import Geogrid
# from cpc.geoplot import Geomap, Geofield
#
# # Create a Geogrid
# geogrid = Geogrid('1deg-global')
# # Read data into a NumPy array
# data = np.fromfile('/Users/mike/500hgt_05d_20120515.bin', dtype='float32')
#






# # Create an empty map
# map = Geomap(title='Example - Default Options')
# # Create a Geofield to plot on the Geomap
# field = Geofield(data, geogrid)
# # Plot the Geofield on the Geomap
# map.plot(field)
# # Save the plot to a PNG
# map.save('example-default-options.png', dpi=100)
#
#
# # Create an empty map
# map = Geomap(title='Example - Mercator Global', projection='mercator', domain='global')
# # Create a Geofield to plot on the Geomap
# field = Geofield(data, geogrid)
# # Plot the Geofield on the Geomap
# map.plot(field)
# # Save the plot to a PNG
# map.save('example-mercator-global.png', dpi=100)
#
#
# # Define tercile colors
# tercile_colors = [
#     (0.01, 0.31, 0.48),
#     (0.02, 0.44, 0.69),
#     (0.21, 0.56, 0.75),
#     (0.45, 0.66, 0.81),
#     (0.65, 0.74, 0.86),
#     (0.82, 0.82, 0.9),
#     (0.95, 0.93, 0.96),
#
#     (0.75, 0.75, 0.75),
#
#     (1., 0.94, 0.85),
#     (0.99, 0.83, 0.62),
#     (0.99, 0.73, 0.52),
#     (0.99, 0.55, 0.35),
#     (0.94, 0.4, 0.28),
#     (0.84, 0.19, 0.12),
#     (0.6, 0., 0.)
# ]
# # Create an empty map
# map = Geomap(title='Example - Tercile Data/Colorbar', cbar_type='tercile')
# # Create a Geofield to plot on the Geomap
# tercile_data = np.fromfile('../../test.bin', dtype='float32').reshape(19, 181*360)
# below = 100 * (1 - tercile_data[7])
# above = 100 * tercile_data[11]
# normal = 100 * (1 - (below + above))
# terciles = np.zeros((181 * 360))
# terciles = np.where((below > above) & (below > 0.333), -1 * below, terciles)
# terciles = np.where((above > below) & (above > 0.333), above, terciles)
# field = Geofield(terciles, geogrid, fill_colors=tercile_colors, smoothing_factor=0.5,
#               levels=[-90, -80, -70, -60, -50, -40, -33, 33, 40, 50, 60, 70, 80, 90])
# # Plot the Geofield on the Geomap
# map.plot(field)
# # Save the plot to a PNG
# map.save('example-tercile.png', dpi=100)
#
#
# # Create an empty map
# map = Geomap(title='Example - Specified Levels')
# # Create a Geofield to plot on the Geomap
# field = Geofield(data, geogrid, levels=range(5000, 6000, 60))
# # Plot the Geofield on the Geomap
# map.plot(field)
# # Save the plot to a PNG
# map.save('example-specified-levels.png', dpi=100)
#
#
# # Create an empty map
# map = Geomap(title='Example - Colored Contours')
# # Create a Geofield to plot on the Geomap
# field = Geofield(data, geogrid, levels=range(5000, 6000, 60), smoothing_factor=1, fill_colors=None)
# # Plot the Geofield on the Geomap
# map.plot(field)
# # Save the plot to a PNG
# map.save('example-colored-contours.png', dpi=100)
#
#
# # Create an empty map
# map = Geomap(title='Example - B & W Contours')
# # Create a Geofield to plot on the Geomap
# field = Geofield(data, geogrid, levels=range(5000, 6000, 60), smoothing_factor=1, fill_colors=None,
#               contour_colors='black')
# # Plot the Geofield on the Geomap
# map.plot(field)
# # Save the plot to a PNG
# map.save('example-BW-contours.png', dpi=100)
#
#
# # Create an empty map
# map = Geomap(title='Example - Specified Fill Colors')
# # Create a Geofield to plot on the Geomap
# field = Geofield(data, geogrid, levels=[5400, 5600], smoothing_factor=1,
#               fill_colors=['blue', 'grey', 'red'])
# # Plot the Geofield on the Geomap
# map.plot(field)
# # Save the plot to a PNG
# map.save('example-specified-fill-colors.png', dpi=100)

import numpy as np
from cpc.geogrids import Geogrid
from cpc.geoplot import Geomap, Geofield

# # Create a Geogrid
# geogrid = Geogrid('1deg-global')
# # Read data into a NumPy array
# data1 = np.fromfile('/Users/mike/data1.bin', dtype='float32')
# data2 = np.fromfile('/Users/mike/data2.bin', dtype='float32')
#
#
# # Create an empty map
# geomap = Geomap(title='Example - Two Fields')
# # Create a Geofield to plot on the Geomap
# levels = np.array([-18., -16., -14., -12., -10.,
#                    -8.,  -6.,  -4.,  -2.,   0.,
#                    2., 4.,   6., 8.,  10.,  12.,
#                    14.,  16.])
# geofield1 = Geofield(data1, geogrid, levels=levels)
# geofield2 = Geofield(data2, geogrid, contour_labels=True)
# # Plot the Geofield on the Geomap
# geomap.plot(geofield1, geofield2)
# # Save the plot to a PNG
# geomap.save('test.png', dpi=100)


from cpc.geoplot.geomap import Geomap, get_supported_domains, get_supported_projections

# print(get_supported_projections())
# print(get_supported_domains())
# Geomap(projection='mercator', domain='CONUS').save('empty-Geomap-{}-{}.png'.format(proj, dom),
#                                                  dpi=100)
for proj in get_supported_projections():
    for dom in get_supported_domains():
        try:
            Geomap(projection=proj, domain=dom).save('empty-Geomap-{}-{}.png'.format(proj, dom), dpi=100)
        except Exception as e:
            pass
