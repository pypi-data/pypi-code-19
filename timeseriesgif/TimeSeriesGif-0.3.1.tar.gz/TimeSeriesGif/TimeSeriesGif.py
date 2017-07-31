import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import imageio
import numpy as np


def matplotlib_figure_to_array(fig):
	# draw the figure first
	fig.canvas.draw()

	# Now we can save it to a numpy array.
	data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
	data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
	return data


def image_arr_to_gif(out_file, image_arr, duration=1):
	imageio.mimsave(out_file, image_arr, duration=duration)


def time_series_to_gif(pandas_df, 
						out_file, 
						window=24, 
						step=3, 
						plot_type='line', 
						use_index_as_title=False,
						gif_duration = 0.5,
						**kwargs):
	image_arr = []

	for row in range(window, len(pandas_df) + window, step):

		curr_df = pandas_df[ row - window : row]

		if use_index_as_title:
			last_val_of_index = curr_df.index[-1]
			fig = curr_df.plot(kind=plot_type, title=last_val_of_index, **kwargs).get_figure()
		else:
			fig = curr_df.plot(kind=plot_type, **kwargs).get_figure()


		img_mat = matplotlib_figure_to_array(fig)
		image_arr.append(img_mat)
		
		plt.close(fig)

	image_arr_to_gif(out_file, image_arr, duration=gif_duration)


if __name__ == '__main__':
	import pandas_datareader.data as web
	df = web.DataReader("CPIAUCSL", "fred", start="1900-01-01", end="2017-07-07")
	df = df['CPIAUCSL'].pct_change(12).to_frame('inflation')
	df = df[df.index >= "1995-01-01"]
	time_series_to_gif(df, 'test.gif', window=24, step=3, 
					   plot_type='line', gif_duration=1,
					   use_index_as_title=True,
					   ylim=(0.005, 0.05))
	