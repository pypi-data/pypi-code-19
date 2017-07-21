# -*- coding: utf-8 -*-
"""Some helpers for processing images"""

import os.path

FMT = 'JPEG'
EXT = 'jpg'
QUAL = 95


def resized_path(path, size, method):
    "Returns the path for the resized image."

    dir, name = os.path.split(path)
    image_name, ext = name.rsplit('.', 1)
    return os.path.join(dir, '%s_%s_%s.%s' % (image_name, method, size, EXT))


def scale(imagefield, size, method='scale', check_path=True):
    """
    Returns the url of the resized image.
    """

    # imagefield can be a dict with "path" and "url" keys
    if imagefield.__class__.__name__ == 'dict':
        imagefield = type('imageobj', (object,), imagefield)

    image_path = resized_path(imagefield.path, size, method)

    if check_path:
        if not os.path.exists(image_path):
            try:
                import Image
            except ImportError:
                try:
                    from PIL import Image
                except ImportError:
                    raise ImportError(
                        'Cannot import the Python Image Library.')

            image = Image.open(imagefield.path)

            # normalize image mode
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # parse size string 'WIDTHxHEIGHT'
            width, height = [int(i) for i in size.split('x')]

            # use PIL methods to edit images
            if method == 'scale':
                image.thumbnail((width, height), Image.ANTIALIAS)
                image.save(image_path, FMT, quality=QUAL)

            elif method == 'crop':
                try:
                    import ImageOps
                except ImportError:
                    from PIL import ImageOps

                ImageOps.fit(image, (width, height), Image.ANTIALIAS
                             ).save(image_path, FMT, quality=QUAL)

    return resized_path(imagefield.url, size, method)


def crop(imagefield, size):
    """
    croped image

    """
    return scale(imagefield, size, 'crop')


def add_logo(imagepath, logopath):
    try:
        import Image
    except ImportError:
        try:
            from PIL import Image
        except ImportError:
            raise ImportError('Cannot import the Python Image Library.')

    img = Image.open(imagepath, 'r')
    img_w, img_h = img.size
    root = os.path.abspath(os.path.dirname(__file__))
    logo = Image.open(logopath)
    logo_w, logo_h = logo.size
    background = Image.new('RGBA', (img_w, img_h + logo_h),
                           (255, 255, 255, 255))
    bg_w, bg_h = background.size
    background.paste(img, (0, 0))
    logo_offset = (img_w - logo_w, bg_h - logo_h)
    background.paste(logo, logo_offset)
    background.save(imagepath)
