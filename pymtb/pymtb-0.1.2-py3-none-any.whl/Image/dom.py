import scipy.cluster
from PIL import Image
from mtb.qtWidgets.ColorBand import ColorBand
import scipy.misc

NUM_CLUSTERS = 5

print ('reading image')
im = Image.open('/Volumes/4TB/PROJETS/Code/PyQT/MTB_QT_Widgets/01-Image_Compare/b.jpg')
im = im.resize((150, 150))      # optional, to reduce time
ar = scipy.misc.fromimage(im)
shape = ar.shape
ar = ar.reshape(scipy.product(shape[:2]), shape[2])

print ('finding clusters')
codes, dist = scipy.cluster.vq.kmeans(ar.astype(float), NUM_CLUSTERS)
print ('cluster centres:\n', codes)

vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

index_max = scipy.argmax(counts)                    # find most frequent
peak = codes[index_max].astype(int)

colour = ''.join(format(c, '02x') for c in peak)
# colour = ''.join(chr(c) for c in peak).encode('hex')
print ('most frequent is %s (#%s)' % (peak, colour))


ColorBand.showColors([peak])