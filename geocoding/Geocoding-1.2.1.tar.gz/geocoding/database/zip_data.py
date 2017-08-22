from zipfile import ZipFile, ZIP_DEFLATED


tables = ['departement', 'postal', 'commune', 'voie', 'localisation',
          'commune_index', 'postal_index', 'voie_index', 'kdtree']

with ZipFile('database.zip', 'w', compression=ZIP_DEFLATED) as myzip:
    for table in tables:
        myzip.write(table + '.dat')
