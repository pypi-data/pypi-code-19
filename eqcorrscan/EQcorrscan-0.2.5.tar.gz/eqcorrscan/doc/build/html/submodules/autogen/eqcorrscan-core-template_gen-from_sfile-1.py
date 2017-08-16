from eqcorrscan.core.template_gen import from_sfile
import os
sfile = os.path.realpath('../../..') + os.sep +            os.path.join('tests', 'test_data', 'REA',
                 'TEST_', '01-0411-15L.S201309')
template = from_sfile(sfile=sfile, lowcut=5.0, highcut=15.0,
                      samp_rate=50.0, filt_order=4, swin='P',
                      prepick=0.2, length=6)
template.plot(equal_scale=False, size=(800, 600))