from itertools import izip
from PIL import Image
import StringIO


def validate_image(image):
    """
    Validates if image is not a HTTP error
    :param image: 
    :return: StringIO representation of the image or None, if HTTP error 
    """
    image_string = StringIO.StringIO(image)
    if "<html>" in image_string.getvalue():
        return None
    else:
        return image_string


def compare_images(so_image, gh_image):
    """
    Compares two images
    :return: 1 if matching images, -1 if not 
    """
    so_image = validate_image(so_image)
    gh_image = validate_image(gh_image)
    if so_image and gh_image:
        size = 32, 32
        outfile = []
        for infile in [so_image, gh_image]:
            im = Image.open(infile)
            if im.mode != "RGB":
                try:
                    im.load()
                    new_im = Image.new("RGB", im.size, (255,255,255))
                    pic_parts = im.split()
                    if im.mode == "L":
                        new_im.paste(im, mask=pic_parts[0])
                    elif im.mode == "P":
                        im = im.convert('P', palette=Image.ANTIALIAS, colors=256)
                    elif im.mode == "RGBA":
                        new_im.paste(im, mask=pic_parts[3])
                    else:
                        new_im.paste(im)
                    im = new_im
                except:
                    print "cannot create thumbnail for '%s'" % infile
            try:
                im = im.resize(size, Image.ANTIALIAS)
            except:
                print "cannot resize image for '%s'" % infile
            outfile.append(im)

        i1 = outfile[0]
        i2 = outfile[1]
        assert i1.mode == i2.mode, "Different kinds of images."
        assert i1.size == i2.size, "Different sizes."

        pairs = izip(i1.getdata(), i2.getdata())
        if len(i1.getbands()) == 1:
            # for gray-scale jpegs
            dif = sum(abs(p1 - p2) for p1, p2 in pairs)
        else:
            dif = sum(abs(c1 - c2) for p1, p2 in pairs for c1, c2 in zip(p1, p2))

        ncomponents = i1.size[0] * i1.size[1] * 3
        score = (dif / 255.0 * 100) / ncomponents
        if score <= 9:  # empirically discovered threshold
            return 1
        else:
            return -1
    else:
        return -1
