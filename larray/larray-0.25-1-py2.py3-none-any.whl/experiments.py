from larray import *

base = Session()
base.load('c:/tmp/rd/midas_2017', ignore_exceptions=True)

variant = Session()
variant.load('c:/tmp/rd/midas_2017_125/output_*.csv', ignore_exceptions=True)
# compare(base, variant)

diff = variant - base
view(diff)
absdiff = abs(diff)
reldiff = absdiff / base
# view(reldiff.transpose(..., 'period'))
stacked = stack({'base': base, 'variant': variant}, "arrays=base,variant")
view(stacked.transpose(..., 'period'))
view(stack({'base': base, 'variant': variant, 'absdiff': absdiff, 'reldiff': reldiff},
           "arrays=base,variant,absdiff,reldiff"))
