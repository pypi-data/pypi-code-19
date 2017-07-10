import numpy as np
import cv2
from matplotlib import pyplot as plt
from itertools import compress

####################################################################################################
######################################### Histogram Class ##########################################

class vHist(np.ndarray):

    def __new__(cls, images, channels, mask = None, histSize = None, ranges = None, RGB = None):

        """
        vHist is a class to simplify the display of different kind of histograms. Meant to be used in conjunction
        with the vImg class. By adding a single 3-tuple bool parameter (RGB) to indicate which channels are active 
        in the histogram, we can automatically calculate what type of histogram to show information for. Therefore,
        initialization and show functionality may be standardized.
        
        Content below is copyright Dr. Adrian Rosebrock from his excellent book Practical Python and OpenCV. A must 
        read if you intend to learn how to use OpenCV properly and in the most consumable fashion currently out there.
        I am hoping he doesn't mind me using it in the open here, but I suppose I should really put contacting him 
        and asking his explicit permission to use snippets like these in this library is ok with him. Then 
        the only hard part will be remembering to delete these couple of sentences.
        
        images   : This is the image that we want to compute a histogram for. Wrap it as a list: [myImage] . 
        channels : A list of indexes, where we specify the index of the channel we want to compute a histogram for. 
                   To compute a histogram of a grayscale image, the list would be [0] . To compute a histogram for all 
                   three red, green, and blue channels, the channels list would be [0, 1, 2] . 
        mask     : Remember learning about masks in Section 1.4.8? Well, here we can supply a mask. If a mask is 
                   provided, a histogram will be computed for masked pixels only. If we do not have a mask or do not 
                   want to apply one, we can just provide a value  of None . 
        histSize : This is the number of bins we want to use when computing a histogram. Again, this is a list, one 
                   for each channel we are computing a histogram for. The bin sizes do not all have to be the same. 
                   Here is an example of 32 bins for each channel: [32, 32, 32] . 
        ranges   : The range of possible pixel values. Normally, this is [0, 256] (this is not a typo — the ending 
                   range of the cv2.calcHist  function is non-inclusive so you’ll want to provide a value of 256 rather 
                   than 255) for each channel, but if you are using a color space other than RGB [such as HSV], 
                   the ranges might be different.)
        """

        # Init assert statements. Make sure basic class parameter requirements are met.
        assert hasattr(images, '__iter__'), "images must be a list"

        assert hasattr(channels, '__iter__'), "channels must be a list/iterable"
        if not isinstance(channels, list):
            channels = list(channels)

        assert not(histSize is None), "None check failed for histSize"
        assert hasattr(histSize, '__iter__'), "histSize must be a list/iterable"
        if not isinstance(histSize, list):
            histSize = list(histSize)

        assert not(ranges is None), "None check failed for ranges"
        assert hasattr(ranges, '__iter__'), "ranges must be a list/iterable"
        if not isinstance(ranges, list):
            ranges = list(ranges)

        assert not RGB is None, "None check failed for RGB"

        assert len(RGB) == 3 and isinstance(RGB, tuple) , "Must provide a 3-tuple with True or False " \
            "for each value representing RGB color channel inclusion."

        obj = cv2.calcHist(images, channels, mask, histSize, ranges)

        obj = np.asarray(obj).view(cls)

        obj.__types = {1 : 'flat', 2 : '2D', 3 : '3D'}

        if obj.shape[1] == 1 and len(obj.shape) == 2:
            obj.__type = obj.__types[1]

        elif len(obj.shape) == 2:
            obj.__type = obj.__types[2]

        else:
            obj.__type = obj.__types[3]


        obj.__RGB = RGB
        obj.__images = images
        obj.__channels = channels
        obj.__mask = mask
        obj.__histSize = histSize
        obj.__ranges = ranges

        return obj

    def __array_finalize__(self, obj):
        """ this is where we initialize most of the variables for the vHist class, due to the way
            numpy n-dimensional arrays work.
        """
        if obj is None: return
        self.__images = getattr(obj, '__images')
        self.__channels = getattr(obj, '__channels')
        self.__mask = getattr(obj, '__mask')
        self.__histSize = getattr(obj, '__histSize')
        self.__ranges = getattr(obj, '__ranges')
        self.__type = getattr(obj, '__type')
        self.__types = getattr(obj, '__types')
        self.__RGB = getattr(obj, '__RGB')

    def __array_wrap__(self, out_arr, context=None):
        """__array_wrap__ gets called at the end of numpy ufuncs and
        other numpy functions, to allow a subclass to set the type of
        the return value and update attributes and metadata"""
        self.__images = getattr(out_arr, '__images')
        self.__channels = getattr(out_arr, '__channels')
        self.__mask = getattr(out_arr, '__mask')
        self.__histSize = getattr(out_arr, '__histSize')
        self.__ranges = getattr(out_arr, '__ranges')
        self.__type = getattr(out_arr, '__type')
        self.__types = getattr(out_arr, '__types')
        self.__RGB = getattr(out_arr, '__RGB')
        # return image
        out_arr.__images = getattr(self, '__images')
        return np.ndarray.__array_wrap__(self, out_arr, context)

    def __eq__(self, other):
        return True if np.array_equal(self, other) else False

    def show(self, bins = [256], xlimit = [0, 256]):

        # Check if type is 1-dimensional and RGB is (False, False, False)
        if self.__type == self.__types[1] and sum(1 for e in self.__RGB if e is True) == 0:
            # 1-dimensional grayscale hist
            pass

        elif self.__type == self.types[1]:
            # 1-dimensional hist with at least 1 color channel
            fig = plt.figure()
            fig.title("'Flattened' Color Histogram")
            fig.xlabel("Bins")
            fig.ylabel("# of Pixels")

            colors = ('b', 'g', 'r')
            cczip = (e for e in zip(self.__channels, colors, self.__RGB) if e[2] is True)

            for chan, color in compress(cczip, self.__RGB[::-1]):
                pass

            # Flattened RGB or grayscale Color Histogram
            if len(self.__type) == 1:  # 1 corresponds to "1-dimensional"
                # grab the image channels, initialize the tuple of colors and the
                # figure

                plt.figure()
                if self.__channels > 1:
                    plt.title("'Flattened' Color Histogram")
                else:
                    plt.title("'Flattened' Grayscale Histogram")
                plt.xlabel("Bins")
                plt.ylabel("# of Pixels")
            # let's move on to 2D histograms -- we need to reduce the
            # number of bins in the histogram from 256 to 32 so we can
            # better visualize the results

def plot_histogram(image, title, mask=None):
	# grab the image channels, initialize the tuple of colors and
	# the figure
	chans = cv2.split(image)
	colors = ("b", "g", "r")
	plt.figure()
	plt.title(title)
	plt.xlabel("Bins")
	plt.ylabel("# of Pixels")

	# loop over the image channels
	for (chan, color) in zip(chans, colors):
		# create a histogram for the current channel and plot it
		hist = cv2.calcHist([chan], [0], mask, [256], [0, 256])
		plt.plot(hist, color=color)
		plt.xlim([0, 256])