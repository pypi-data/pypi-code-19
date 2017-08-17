import os

import inqbus.rainflow as rfc
# Example for hdf5-file

# Rainflow.on_hdf5_file:
# run base algorithm, store pairs and counted pairs to file

# Binning.as_table_on_hdf5_file:
# classify results from Rainflow.on_hdf5_file
# stored a table with pairs and a table with counted pairs as table

# Binning.as_matrix_on_hdf5_file:
# classify results from Rainflow.on_numpy_array
# stores a 2d-array matrix like traditional rainflow matrix with
# start in rows and target in columns

# Datenquelle
testdatafile = 'db-set-2016-05-18_Felddata_H211_0743.cp.h5_30.05.2017_15.58.17_Berechnungsdatenexport.h5'

# create_testdata

if not os.path.isfile(testdatafile):
    # creat
    import inqbus.rainflow.examples.create_hdf5_testfile

# base algorithm
# Reiter
source_path = testdatafile + ':/Ausgabe_Hamm/Zusatzdaten'
# Spaltenname
source_column = 'DrehmoAchse'
target_group = testdatafile + ':/statistics/Zusatzdaten/DrehmoAchse'

rfc.Rainflow.on_hdf5_file(source_path, source_column, target_group)


# add some classification afterwards
source_path = target_group + '/RF_Pairs'

rfc.Binning.as_table_on_hdf5_file(source_path,
                                  target_group,
                                  bin_count=32,
                                  maximum=35,
                                  minimum=0,
                                  counted_table_name='RF_Counted_32',
                                  pairs_table_name='RF_Pairs_32')

rfc.Binning.as_matrix_on_hdf5_file(source_path,
                                   target_group,
                                   bin_count=32,
                                   maximum=35,
                                   minimum=0,
                                   counted_table_name='RF_Matrix_32')

print('Calculation finished have a look at hdf5-file.')
