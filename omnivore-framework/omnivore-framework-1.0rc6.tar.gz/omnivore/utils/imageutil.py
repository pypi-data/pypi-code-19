#!/usr/bin/env python
import cStringIO

import numpy as np
from PIL import Image


def get_numpy_from_data(data):
    image = Image.open(cStringIO.StringIO(data))
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    arr = np.array(image)
    return arr


def get_rect(w, h, color=None, opaque_border=False):
    arr = np.empty((h, w, 4), np.uint8)

    # just some indexes to keep track of which byte is which
    R, G, B, A = range(4)

    if color is None:
        red, green, blue, alpha = (35, 142,  35, 128)
    else:
        red, green, blue, alpha = color
    # initialize all pixel values to the values passed in
    arr[:,:,R] = red
    arr[:,:,G] = green
    arr[:,:,B] = blue
    arr[:,:,A] = alpha

    if opaque_border:
        # Set the alpha for the border pixels to be fully opaque
        arr[0,   0:w, A] = 255  # first row
        arr[h-1, 0:w, A] = 255  # last row
        arr[0:h, 0,   A] = 255  # first col
        arr[0:h, w-1, A] = 255  # last col

    return arr


def get_checkerboard(w, h, sq=16):
    # Algorithm from http://stackoverflow.com/questions/2169478/how-to-make-a-checkerboard-in-numpy
    color1 = (64, 64, 64, 32)
    color2 = (255, 255, 255, 32)
    coords = np.ogrid[0:h, 0:w]
    idx = (coords[0] // sq + coords[1] // sq) & 1
    vals = np.array([color1, color2], dtype=np.uint8)
    arr = vals[idx]
    return arr


def get_square(size):
    return get_rect(size, size)


def get_image_from_data(array):
    image = Image.fromarray(array)
    return image


def save_image(array, filename):
    image = get_image_from_data(array)
    image.save(filename)


if __name__ == "__main__":
    # Create a Jumpman peanut allergy mask
    hx = 0
    hy = 6
    xb = lambda x:x+0x30+hx
    yb = lambda y:2*y+0x20+hy

    def is_allergic(x, y, hx, hy):
        return (x + 0x30 + hx) & 0x1f < 7 or (2 * y + 0x20 + hy) & 0x1f < 5
    w = 160
    h = 88
    good = (64, 178, 200, 100)
    bad = (203, 144, 161, 100)
    playfield = get_rect(w, h, good)
    for x in range(w):
        for y in range(h):
            if is_allergic(x, y, hx, hy):
                playfield[y, x] = bad
    save_image(playfield, "bad_peanut.png")

    print "X bomb location,hx=0,hx=16,hx=f0,hx=fc"
    hy = 6
    for x in range(w):
        #print "$%02x,%s" % (x, "OK" if not is_allergic(x, 0, hx, 6) else "BAD!")
        badlist = []
        for hx in [0, 16, -16, -4]:
            badlist.append("ok" if not is_allergic(x, 0, hx, hy) else "BAD!")
        print "$%02x,%s" % (x, ",".join(badlist))

    print "Y bomb location,hy=0,hy=2,hy=4,hy=6,hy=f6"
    hx = 0
    for y in range(h):
        #print "$%02x,%s" % (x, "OK" if not is_allergic(x, 0, hx, 6) else "BAD!")
        badlist = []
        for hy in [0, 2, 4, 6, -10]:
            badlist.append("ok" if not is_allergic(0, y, hx, hy) else "BAD!")
        print "$%02x,%s" % (y, ",".join(badlist))
