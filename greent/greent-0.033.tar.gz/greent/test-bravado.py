# Setup - virtualenv (Python 2 or 3)
# $ virtualenv -p /PATH/TO/PYTHON venv
# $ source venv/bin/activate
# $ pip install bravado
# $ python test-bravado.py

from bravado.client import SwaggerClient
import datetime
from pprint import pprint

client = SwaggerClient.from_url(
    "https://app.swaggerhub.com/apiproxy/schema/file/mjstealey/environmental_exposures_api/1.0.0/swagger.json",
    config={'use_models': False}
)

# get valid exposures calls
dir_exp = dir(client.exposures)
print( '### dir(client.exposures) ###' )
pprint( dir_exp )

# get exposures types
exp_types = client.exposures.get_exposures().result( timeout=10 )
print( '### client.exposures.get_exposures().result( timeout=10 ) ###' )
pprint( exp_types )

# get exposures date range for pm25
exp_dates = client.exposures.get_exposures_exposure_type_dates( exposure_type='pm25' ).result( timeout=10 )
print( '### client.exposures.get_exposures_exposure_type_dates( exposure_type=\'pm25\' ).result( timeout=10 ) ###' )
pprint( exp_dates )

# get all exposures coordinates for pm25
exp_coords = client.exposures.get_exposures_exposure_type_coordinates( exposure_type='pm25' ).result( timeout=10 )
print( '### client.exposures.get_exposures_exposure_type_coordinates( exposure_type=\'pm25\' ).result( timeout=10 ) ###' )
pprint( exp_coords )

# get exposures values for date range 2010-01-10 to 2010-10-20 for pm25 at latitude=34.15581748, longitude=-77.99258944
string_date='2010-01-10 00:00:00.000'
sdate=datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S.%f").date()
string_date='2010-01-20 00:00:00.000'
edate=datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S.%f").date()
lat='34.15581748'
lon='-77.99258944'

exp_values = client.exposures.get_exposures_exposure_type_values(
    exposure_type = 'pm25',
    start_date = sdate,
    end_date = edate,
    exposure_point = lat + ',' + lon
).result()
print( '### client.exposures.get_exposures_exposure_type_values ... ###' )
pprint( exp_values )

# get exposures scores for date range 2010-01-10 to 2010-10-20 for pm25 at latitude=34.15581748, longitude=-77.99258944
exp_scores = client.exposures.get_exposures_exposure_type_scores(
    exposure_type = 'pm25',
    start_date = sdate,
    end_date = edate,
    exposure_point = lat + ',' + lon
).result()
print( '### client.exposures.get_exposures_exposure_type_scores ... ###' )
pprint( exp_scores )
