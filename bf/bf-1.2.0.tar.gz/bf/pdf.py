
import os, sys, subprocess
from glob import glob
from bl.file import File
import re

class PDF(File):

    def gswrite(self, fn=None, device='jpeg', res=600, alpha=4, quality=90, gs=None):
        "use ghostscript to create output file(s) from the PDF"
        gs = (gs or self.gs or 'gs')
        # count the number of pages
        if fn is None: 
            fn = os.path.splitext(self.fn)[0] + GS_DEVICE_EXTENSIONS[device]
        pages = int(subprocess.check_output([gs, '-q', '-dNODISPLAY', '-c', 
                "(%s) (r) file runpdfbegin pdfpagecount = quit" % self.fn]).decode('utf-8').strip())
        if pages > 1:
            # add a counter to the filename, which tells gs to create a file for every page in the input
            fb, ext = os.path.splitext(fn)
            n = len(re.split('.', str(pages))) - 1
            counter = "-%%0%dd" % n
            fn = fb + counter + ext
        callargs = [gs, '-dSAFER', '-dBATCH', '-dNOPAUSE',
                    '-sDEVICE=%s' % device,
                    '-r%d' % res]
        if device=='jpeg': 
            callargs += ['-dJPEGQ=%d' % quality]
        if 'png' in device or 'jpeg' in device or 'tiff' in device: 
            callargs += [
                '-dTextAlphaBits=%d' % alpha,
                '-dGraphicsAlphaBits=%d' % alpha]
        callargs += ['-sOutputFile=%s' % fn,
                    self.fn]
        try:
            subprocess.check_output(callargs)
        except subprocess.CalledProcessError as e:
            print(' '.join(callargs))
            print(str(e.output, 'utf-8'), file=sys.stderr)
        fns = glob(re.sub('%\d+d','*', fn))
        return fns


GS_DEVICE_EXTENSIONS = {
    'png16m':'.png', 
    'png256':'.png', 
    'png16':'.png', 
    'pngmono':'.png', 
    'pngmonod':'.png', 
    'pngalpha':'.png',
    'pnggray':'.png',
    'jpeg':'.jpg', 
    'jpeggray':'.jpg',
    'tiffgray':'.tiff', 
    'tiff12nc':'.tiff', 
    'tiff24nc':'.tiff', 
    'tiff48nc':'.tiff', 
    'tiff32nc':'.tiff', 
    'tiff64nc':'.tiff', 
    'tiffsep':'.tiff', 
    'tiffsep1':'.tiff', 
    'tiffscaled':'.tiff', 
    'tiffscaled4':'.tiff', 
    'tiffscaled8':'.tiff', 
    'tiffscaled24':'.tiff', 
    'tiffscaled32':'.tiff', 
    'tiffcrle':'.tiff', 
    'tiffg3':'.tiff', 
    'tiffg32d':'.tiff', 
    'tiffg4':'.tiff', 
    'tifflzw':'.tiff', 
    'tiffpack':'.tiff', 
    'txtwrite':'.txt',
    'psdcmyk':'.psd', 
    'psdrgb':'.psd',
}

