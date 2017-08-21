# Softwareentwicklung ueber Fa. www.inqbus.de im Auftrag der Hamm AG
# Sandra Rum, Dr.Volker Jaehnisch
# Anpassungen Markus Golbs Hamm AG, im
# Ubuntu und Debian Linux Basis
# virtualenvwrapper installieren
# dann diesen Befehl nutzen: mkvirtualenv -p /path/to/python3 NAMEdervirtuellenUmgebung
# Rueckstellung moeglich ueber pip uninstall inqbus.rainflow
# update über (https://github.com/sandrarum/inqbus.rainflow)
# git clone https://github.com/sandrarum/inqbus.graphdemo.git
# python setup.py develop


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
testdatafile = 'db-set-2016-05-18_Felddata_H211_0743.cp.h5_08.06.2017_12.53.45_Berechnungsdatenexport.h5'

# create_testdata

if not os.path.isfile(testdatafile):
    # creat
    import inqbus.rainflow.examples.create_hdf5_testfile

# base algorithm
# Reiter
source_path = testdatafile + ':/Ausgabe_Hamm/Zusatzdaten'
# Spaltenname
source_column = 'DrehmofahrmoBandage'
target_group = testdatafile + ':/statistics/Zusatzdaten/DrehmofahrmoBandage'

rfc.Rainflow.on_hdf5_file(source_path, source_column, target_group)


# add some classification afterwards
source_path = target_group + '/RF_Pairs'

rfc.Binning.as_table_on_hdf5_file(
    source_path,
    target_group,
    bin_count=64,
    maximum=450,
    minimum=-450,
    counted_table_name='RF_Counted_64_DrehmofahrmoBandage',
    pairs_table_name='RF_Pairs_64_DrehmofahrmoBandage')

rfc.Binning.as_matrix_on_hdf5_file(
    source_path,
    target_group,
    bin_count=64,
    maximum=450,
    minimum=-450,
    axis=[
        'top',
        'left'],
    counted_table_name='RF_Matrix_64_DrehmofahrmoBandage',
    remove_small_cycles=False)

print('Calculation finished have a look at hdf5-file.')
