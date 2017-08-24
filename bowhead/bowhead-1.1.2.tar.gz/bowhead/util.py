import collections
import numpy
import skimage.filters, skimage.color
from .algorithm import _load


def image_gradient(image):  
    """ Preprocess bright-field or similar type images.

    Applys a Scharr filter and normalizes the output gradient image.
   
    Parameters
    ----------
    image : [file path | numpy.ndarray | PIL.Image]
        A color or grayscale image as file path
        numpy array or PIL image.

    Returns
    -------
    image : PIL.Image (8 bit image mode 'L')
        A normalized image representing the gradient (edge magnitude)
        of the input image. 
 
    """
    image = _load(image)
    filename = image.filename
    image = numpy.asarray(_load(image))
    image = skimage.color.rgb2gray(image)
    image = skimage.filters.scharr(image)
    image = (255 * image / image.max()).astype('uint8')
    image = _load(image).convert('L')
    image.filename = filename
    return image

def sort_and_cutoff(wounds, min_area=.05, abs_area=False):
    """Sort by time and cutoff based on minimum area.

    Utillity function to sort wounds by time and filter out
    wounds by minimum area (pixel^2).

    Parameters
    ----------
    wounds : sequence of dictionaries
        A sequence of wound dictionaries representing an experimental
        time series of the wound healing assay, as returned
        by :func:`detect`.
    min_area : float
        Percentage (or absolute) image size to consider a
        closed wound area.
        After this limit is hit the following time points will be excluded
        from the wound list.
    abs_area : bool
        Wether to use absolute area.

    Returns
    -------
    wounds : list of dictionaries
        A wound list sorted by time point of the wounds.
        The following will remove wounds from the returned list:

            - wound area smaller than ``min_area*image area`` or ``abs_area``
            - wounds with later time point than the first removed
            - None valued wounds


    """
    if not isinstance(wounds, collections.Sequence):
        raise ValueError('wounds argument is not a list')
    wounds = [ws for ws in wounds if ws is not None]
    wounds = sorted(wounds, key=lambda x: x['time'])
    wounds_cut = []
    for test in wounds:
        img_area = test['image_area']
        if abs_area:
            if min_area > test['area']:
                print('too small absolute area at time', test['time'])
                break
        elif min_area * img_area > test['area']:
            print('too small area at time', test['time'])
            break
        wounds_cut.append(test)
    return wounds_cut
