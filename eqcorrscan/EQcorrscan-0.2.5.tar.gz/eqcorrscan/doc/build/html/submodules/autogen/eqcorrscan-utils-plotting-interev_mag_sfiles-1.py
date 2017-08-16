import glob, os
from eqcorrscan.utils.plotting import interev_mag_sfiles
sfiles = glob.glob(
    os.path.realpath('../../../tests/test_data/REA/TEST_/') +
    os.sep + '*L.S*')
print(sfiles)
interev_mag_sfiles(sfiles=sfiles)