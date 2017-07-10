from io import StringIO
import io
from PIL import Image
from PIL.Image import ANTIALIAS
import numpy as np
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


def resize(img=None, w=0, h=0, options='', format=''):
    img_w, img_h = img.size

    if w > 0 and h > 0:
        if options and ('f' in options or 't' in options):
            img.thumbnail((w, h))
        else:
            # Crop
            n_pct_w = w / float(img_w)
            n_pct_h = h / float(img_h)

            if n_pct_h < n_pct_w:
                n_pct = n_pct_w
            else:
                n_pct = n_pct_h
            if format == 'GIF':
                img.resize(int(img_w * n_pct), int(img_h * n_pct))
                new_img_w, new_img_h = img.size
                x_offset = int((new_img_w - w) / 2)
                y_offset = int((new_img_h - h) / 2)
                img.crop(x_offset, y_offset, w + x_offset, h + y_offset)
            else:
                img = img.resize(
                    (int(img_w * n_pct), int(img_h * n_pct)),
                    resample=ANTIALIAS)

                new_img_w, new_img_h = img.size

                x_offset = int((new_img_w - w) / 2)
                y_offset = int((new_img_h - h) / 2)

                img = img.crop(
                    (x_offset, y_offset, w + x_offset, h + y_offset))
    elif w > 0:
        # resize from width
        h = w * img_h / img_w
        if format == 'GIF':
            img.resize(w, h)
        else:
            img = img.resize((w, h), resample=ANTIALIAS)
    elif h > 0:
        # resize from height
        w = h * img_w / img_h
        if format == 'GIF':
            img.resize(w, h)
        else:
            img = img.resize((w, h), resample=ANTIALIAS)
    if options and "g" in options:
        # Grayscale
        if format == 'GIF':
            img.type = 'grayscalematte'
        else:
            img = img.convert('L')

    return img


def convert_and_resize(data, q=100, w=0, h=0, options=''):
    with Image.open(StringIO(data)) as img:
        format = img.format

        """frames = []
        if format == 'GIF':
            if w == 0 and h == 0 and not options:
                return data
            duration = img.info.get("duration", 0)
            for frame in images2gif.readGif(img, False):
                frame = resize(frame, w, h, options, format)
                b = StringIO()
                frame.save(b, format)
                frames.append(Image.open(b))"""

        with io.BytesIO() as response:
            if format == 'GIF':
                from wand.image import Image as WandImage
                with WandImage(blob=data) as gif:
                    resize(gif, w, h, options, format)
                    gif.compression_quality = q
                    gif.save(response)

                """images2gif.writeGif(
                    response,
                    frames, duration=duration / 1000.0,
                    subRectangles=False)"""
            else:
                img = resize(
                    img=img,
                    w=int(w),
                    h=int(h),
                    options=options,
                    format=format)
                if not (img.mode in ('RGBA', 'LA') or
                        (img.mode == 'P' and 'transparency' in img.info)):
                    img = img.convert('RGB')
                    format = 'JPEG'

                img.save(response, dpi=[72, 72], quality=int(q), format=format,
                         optimize=True, progressive=True)

            return response.getvalue()


def get_image_info(data):
    """Get image info"""
    with Image.open(StringIO(data)) as img:
        return {
            'width': img.size[0],
            'height': img.size[1],
            'mode': img.mode,
            'format': img.format
        }


def __centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=num_labels)

    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()

    # return the histogram
    return hist


def __get_colors(hist, centroids):
    colors = []
    for (percent, color) in zip(hist, centroids):
        colors.append({
            'color': '#%02x%02x%02x' % (color[0], color[1], color[2]),
            'percent': percent
        })
    return colors


def get_image_colors(data, n_clusters=5):
    """Get image's dominant colors"""
    with Image.open(StringIO(data)) as img:
        img = img.convert('RGB')
        img = img.resize((150, 150))

        # Convert image to 3D numpy array
        img_array = np.array(img.getdata(), np.uint8).reshape(
            img.size[1], img.size[0], 3)

        # Load Image and transform to a 2D numpy array.
        w, h, d = original_shape = tuple(img_array.shape)
        assert d == 3
        img_array = np.reshape(img_array, (w * h, d))

        # Fitting model on a small sub-sample of the data
        image_array_sample = shuffle(img_array, random_state=0)[:1000]

        # cluster the pixel intensities
        clt = KMeans(n_clusters=n_clusters)
        clt.fit(image_array_sample)

        # build a histogram of clusters and then create a figure
        # representing the number of pixels labeled to each color
        hist = __centroid_histogram(clt)
        colors = __get_colors(hist, clt.cluster_centers_)
        return sorted(colors, key=lambda k: -k['percent'])
