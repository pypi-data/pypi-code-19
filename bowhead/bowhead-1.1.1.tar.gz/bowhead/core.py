import numpy as np
from PIL.Image import Image
from collections import Sequence
from .algorithm import _detect, _load
from .util import image_gradient


def detect(images, time=None, sigma=25, thresh=.4, err=.05,
           radius=None, use_gradient=False, method='marching'):
    """Detect wound on a image with uncertainty. 

    Parameters
    ----------
    images : sequence of [file paths | numpy.ndarray | PIL.Image]
        Images to detect wound(s) from. A single image path, array, 
        or PIL image can be passed outside a sequence.
    time : sequence
        The time points of the images (same order as images).
    sigma : scalar
        The standard deviation of the image smoothing.
        This should be roughly the same as the distance
        (in pixels) between cells at confluency.
    thresh : scalar
        Threshold factor to calculate wound boundary.
        Between zero and one.
    err : scalar 
        Standard error of the threshold value to calculate uncertainty 
        of the detection.
    radius : scalar, default is None
        If radius is not None and more than 2 images parsed 
        the algorithm uses the mean center of mass of the two first wounds
        to define a circular zone of exclusion with radius ``radius``
        in pixels. Subsequent wound candidates have to been
        inside this zone to be considered valid wounds.
    use_gradient : boolean, default is False
        Whether to preprocess the images with a Scharr edge filter.
        This is useful to better detect wounds on bright-field images
        and other types where cells appear as a both light and
        dark in the microscope image.
    method : string, default is 'marching'
        Which method to use for contour tracing.
        Choose between 'marching' for the marching square algorithm
        or 'chain' for chain code tracing. Chain code is fastest.
        The perimeter found differs slightly because Marching square
        finds interpolated round edges at pixel corners where chain
        code result in a standard pixel chain.

    Returns
    -------
    wound(s) : dictionary or a list of dictionaries
        Returns one dictionary (or a list of several) with the
        detected wound values

            - area
            - perimeter (without parts that touch image border)
            - area and perimeter variances
            - center of mass
            - time
            - edge (tuple of wound edge x and y coordinates)
            - filename, (image file path if loaded from disk)
            - image area

        Returns ``None``, for wounds that can not be detected.

    Notes
    -----
    All image types and bit depth supported by `Pillow
    <http://pillow.readthedocs.io>`_ can be used as input.
    If the images contain more than one color channel the sum of all
    channels will be used.

    """
    allowed = str, np.ndarray, Image
    if not hasattr(images, '__len__') or isinstance(images, allowed):
        images = [images]
    if not isinstance(images[0], allowed):
        raise TypeError('images are wrong type')
    images = [_load(img) for img in images]
    if use_gradient:
        images = [image_gradient(img) for img in images]
    if time is None:
        time = np.arange(len(images))
    elif len(time) != len(images):
        raise ValueError('time should be the same length as images')

    # find the rescricted wound zone on the image (x, y, radius)
    test = 2
    zone = None
    if len(images) > test and radius is not None:
        order = np.argsort(time)[:test]
        test_images = [images[i] for i in order]
        cms = []
        for image in test_images:
            test_wound = _detect(image, sigma, thresh, method=method)
            if test_wound:
                cms.append(test_wound['center_of_mass'])
        if test_wound:
            zone = tuple((np.array(cms).mean(0), radius))

    # detect wounds 
    wounds = []
    for i, image  in enumerate(images):
        wound = _detect(image, sigma, thresh, zone=zone, method=method)
        small = _detect(image, sigma, thresh-err, zone=zone,
                        primary=wound, method=method)
        large = _detect(image, sigma, thresh+err, zone=zone,
                        primary=wound, method=method)
        if not (wound and small and large):
            continue
        a1 = large['area'] - wound['area']
        a2 = small['area'] - wound['area']
        p1 = large['perimeter'] - wound['perimeter'] 
        p2 = small['perimeter'] - wound['perimeter']
        del wound['smooth']
        del wound['confluency']
        del wound['woundzone']
        other = {'area_variance': .5 * (a1**2 + a2**2),
                 'perimeter_variance': .5 * (p1**2 + p2**2),
                 'time': time[i],}
        combined = wound.copy()
        combined.update(other)
        wounds.append(combined)
    if len(wounds) == 1:
        return wounds[0]
    if wounds:
        return wounds
