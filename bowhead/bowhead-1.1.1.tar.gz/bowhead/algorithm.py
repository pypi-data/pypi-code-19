import numpy as np
from scipy import ndimage
from skimage.measure import find_contours, perimeter
from skimage.morphology import binary_erosion, binary_opening
from PIL import Image, ImageFilter


def _load(image):
    if isinstance(image, str):
        image = Image.open(image)
    elif isinstance(image, np.ndarray):
        if len(image.shape) > 2:
            image = np.sum(image, -1, dtype='uint16')
        image = Image.fromarray(image)
    if not hasattr(image, 'filename'):
        image.filename = None
    filename = image.filename
    image = image.convert('I')
    image.filename = filename
    return image

def _detect(image, sigma, threshold, zone=None, primary=None,
            method='marching'):
    if primary is None:
        smooth = ndimage.filters.gaussian_filter(image, sigma)
        smooth = np.asarray(smooth, dtype=np.float)
        confluency = (smooth**2).sum() / smooth.sum()
    else:
        smooth, confluency = primary['smooth'], primary['confluency']
    binary = ndimage.binary_fill_holes(smooth < threshold * confluency)
    label, count = ndimage.label(binary)
    index = range(1, count+1)
    cms = ndimage.measurements.center_of_mass(binary, label, index)
    mass = ndimage.sum(binary, label, index)
    objects = sorted(zip(cms, mass, index), key=lambda x: x[1])
    for obj in reversed(objects):
        if zone:
            dist = np.linalg.norm(np.array(obj[0])-np.array(zone[0]))
            if dist > zone[1]:
                continue
        cm = obj[0]
        area = obj[1]
        woundzone = label==obj[2]
        edge, perimeter = _contour(woundzone, method=method)
        return {'filename': image.filename,
                'woundzone': woundzone,
                'area': area,
                'center_of_mass': tuple(round(x) for x in cm), 
                'edge': edge,
                'perimeter': round(perimeter),   
                'image_area': np.prod(image.size),
                'smooth': smooth,
                'confluency': confluency,}

def _find_outer_point(arr):
    # initialize chain by finding starting coordinate
    rows = np.arange(arr.shape[0])
    np.random.shuffle(rows)
    for i in rows: 
        for j in range(arr.shape[1]):
            if arr[i,j]:
                return [i], [j]
    raise NotImplementedError('no starting point was found for chain')

def _chain_code(arr):
    # isolate border and find starting point
    arr = binary_opening(arr) ^ binary_erosion(arr)
    x, y = _find_outer_point(arr)
    
    # compute 8-direction chain code start point in lists x and y
    moves = [(1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1), (1,1)]
    perimeter = 0.
    while True:
        for move in moves:
            mx, my = x[-1] + move[0], y[-1] + move[1]  # candidate coord
            if arr[mx,my] and not (mx == x[-1] and my == y[-1]):
                if len(x) > 1 and (mx == x[-2] and my == y[-2]):
                    continue
                if move[0] == 0 or move[1] == 0:  # add to contour length
                    perimeter += 1
                else:
                    perimeter += 1.414213  # sqrt(2)
                x.append(mx)
                y.append(my)
                break
        if mx == x[0] and my == y[0]:
            break
    return np.asarray(x), np.asarray(y), perimeter

def _contour(wound, method='marching'):
    # find image border mask to calculate stucco
    mask = np.zeros_like([s-1 for s in wound.shape])
    mask = np.pad(mask, pad_width=1, mode='constant', constant_values=1)
    mask = np.pad(mask, pad_width=1, mode='constant', constant_values=0)
    wound = np.pad(wound, pad_width=1, mode='constant', constant_values=0)
    stucco = np.sum(wound[mask])  # perimeter touching image border

    # find contour chain with one of following methods
    if method == 'marching':
        contours = find_contours(wound, level=.5)
        if len(contours) > 1:
            raise ValueError('more than one wound contour were detected')
        x, y = np.transpose(contours[0]-1)
        peri = perimeter(wound)
    elif method == 'chain':
        x, y, peri = _chain_code(wound) 
    return (x, y) , peri - stucco
