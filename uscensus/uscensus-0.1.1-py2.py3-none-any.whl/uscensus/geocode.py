from __future__ import print_function, unicode_literals

import blaze as bz
import dateparser
import fiona
import geopandas
from gevent.pool import Pool
from io import StringIO
import numpy as np
import geopandas as gpd
import glob
import grequests
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
import shapely


# In[2]:

def parse_date(date):
    if date and date != 'NA':
        return dateparser.parse(date).date()


# In[3]:

str_fields = [
    'Defendant.Addr.ZIP.1',
    'Defendant.Addr.ZIP.2',
    'Defendant.Atty.Addr.2',
    'Defendant.Atty.Phone',
    'Defendant.Atty.ZIP.1',
    'Defendant.Atty.ZIP.2',
    'Defendant.Phone.Nbr',
    'Nature.of.Claim',
    'Next.Event.Desc',
    'Next.Hearing.Date',
    'Next.Hearing.Desc',
    'Plaintiff.Addr.ZIP.1',
    'Plaintiff.Addr.ZIP.2',
    'Plaintiff.Atty.Phone',
    'Plaintiff.Atty.ZIP.1',
    'Plaintiff.Atty.ZIP.2',
    'Plaintiff.Phone.Nbr',
    'Second.Defendant.Addr.ZIP.1',
    'Second.Defendant.Addr.ZIP.2',
    'Second.Defendant.Atty.Addr.1',
    'Second.Defendant.Atty.Addr.2',
    'Second.Defendant.Atty.City',
    'Second.Defendant.Atty.Name',
    'Second.Defendant.Atty.Phone',
    'Second.Defendant.Atty.State',
    'Second.Defendant.Atty.ZIP.1',
    'Second.Defendant.Atty.ZIP.2',
    'Second.Defendant.Phone.Nbr',
    'Second.Plaintiff.Addr.City',
    'Second.Plaintiff.Addr.Line.1',
    'Second.Plaintiff.Addr.Line.2',
    'Second.Plaintiff.Addr.State',
    'Second.Plaintiff.Addr.ZIP.1',
    'Second.Plaintiff.Addr.ZIP.2',
    'Second.Plaintiff.Atty.Addr.1',
    'Second.Plaintiff.Atty.Addr.2',
    'Second.Plaintiff.Atty.City',
    'Second.Plaintiff.Atty.Name',
    'Second.Plaintiff.Atty.Phone',
    'Second.Plaintiff.Atty.State',
    'Second.Plaintiff.Atty.ZIP.1',
    'Second.Plaintiff.Atty.ZIP.2',
    'Second.Plaintiff.Ext.Name',
    'Second.Plaintiff.Name',
    'Second.Plaintiff.Phone.Nbr',
]


# In[4]:

converters = {
    'Next.Event.Date': parse_date,
}
converters.update({x:np.unicode for x in str_fields})


# In[5]:

eviction_df = pd.read_csv('evictions-20170431-final.csv', converters=converters)


# In[6]:

eviction_df.drop('Unnamed: 0', axis=1, inplace=True)
eviction_df.set_index('Case.Number', drop=False, inplace=True)


# In[7]:

address_cols = ["Defendant.Addr.Line.1","Defendant.Addr.City",
                "Defendant.Addr.State","Defendant.Addr.ZIP.1"]
addresses_df = eviction_df[address_cols].apply(lambda x: x.str.lower())


# In[8]:

grps = addresses_df.reset_index().groupby(address_cols).groups


# In[9]:

eviction_df.shape, len(grps)


# In[10]:

keys=[]
address_indexes=[]
for idx,(k,v) in enumerate(grps.items()):
    keys.append((idx, *k))
    address_indexes.append(v)
keys[:5], address_indexes[:5]


# In[11]:

input_df = pd.DataFrame(keys, columns=['key', 'street', 'city', 'state', 'zip']).set_index('key')
# clean street addresses a little
input_df['street'] = input_df['street'].str.replace('''['"()]''','').str.strip()
input_df.head()


# In[9]:

census_geo_colnames = [
        'Key',
        'In.Address',
        'Match',
        'Exact',
        'Geo.Address',
        'Geo.Lon.Lat',
        'Geo.TIGER.LineID',
        'Geo.TIGER.Side',
        'Geo.FIPS.State',
        'Geo.FIPS.County',
        'Geo.Tract',
        'Geo.Block',
    ]


# In[10]:

def from_csv(
    infile,
    converters={},
    typemap={},
    dropcols=[],
    read_csv=pd.read_csv,
    key='Key'
):
    for x in census_geo_colnames:
        if x.startswith('Geo'):
            if x not in converters:
                converters[x]=str
    typemap.update({
        'Key': int,
        'Match': 'category',
        'Exact': 'category',
        'Geo.TIGER.Side': 'category',
    })
    df = read_csv(infile, converters=converters)
    for col in dropcols:
        df = df.drop(col, axis=1)
    for col, coltype in typemap.items():
        if col in df.columns:
            df[col] = df[col].astype(coltype)
    df = df.set_index(key)
    return df


# In[12]:

# Work around some Windows TLS issues
class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1_2)


# In[318]:

class CensusGeoCoder(object):
    out_cols =  census_geo_colnames
    def filename(self, suffix):
        return self.template.format(suffix)
    def __init__(self,
                 endpoint='https://geocoding.geo.census.gov/geocoder/geographies/addressbatch',
                 benchmark='Public_AR_Current',
                 vintage='Current_Current',
                 chunksize=1000,
                 concurrency=10,
                 template='tmp/geo-{}.csv'
                ):
        self.endpoint = endpoint
        self.benchmark = benchmark
        self.vintage = vintage
        self.chunksize = chunksize
        self.concurrency = concurrency
        self.template = template
        # write headers
        with open(self.filename(''), 'w') as out:
            out.write(','.join(self.out_cols) + '\n')

    def _generate_requests(self, input_df):
        s = requests.Session()
        s.mount('https://', MyAdapter())
        for idx,chunk in enumerate(bz.odo(input_df,
                                          target=bz.chunks(pd.DataFrame),
                                          chunksize=self.chunksize),
                                  1):
            print("Processing chunk #{}: geocoding {} addresses".format(idx, len(chunk)))
            sio = StringIO()
            chunk.to_csv(sio, header=False)
            req = sio.getvalue().rstrip()
            params={
                'benchmark': self.benchmark,
                'vintage': self.vintage,
            }
            files = {
                'addressFile': ('Addresses.csv', StringIO(req), 'text/csv')
            }
            yield grequests.post(self.endpoint, params=params, files=files, stream=False, session=s)
    
    def geocode_addresses(self, input_df):
        reqs = list(self._generate_requests(input_df))
        req_to_idx = {req: idx for idx, req in enumerate(reqs)}
        pool = Pool(self.concurrency)
        #print("Processing {} requests".format(len(reqs)))
        for idx, req in enumerate(pool.imap_unordered(grequests.AsyncRequest.send, reqs)):
            chunkno = req_to_idx[req]
            print("Finished req {}/{} for chunk#{}".format(idx+1, len(reqs), chunkno))
            if req.response is not None:
                r = req.response
                if r.status_code == 200:
                    #f = self.data
                    with open(self.filename('00{}'.format(chunkno)[-3:]), 'w') as f:
                        f.write(r.text)
                        if not r.text.endswith('\n'):
                            f.write('\n');
                else:
                    print("failed: status_code={}".format(r.status_code))
                    req.response = None
                    reqs.append(req)
            else:
                print("failed: exception={}".format(req.exception))
        print("Processed {} responses".format(idx+1))
    def as_dataframe(self):
        sio = StringIO()
        for fn in glob.glob(self.filename('*')):
            with open(fn, encoding='utf-8') as f:
                data = f.read()
                sio.write(data)
                if not data.endswith('\n'):
                    sio.write('\n')
        sio.seek(0, 0)
        return from_csv(sio)


# In[15]:

get_ipython().run_cell_magic('time', '', 'cgc = CensusGeoCoder(concurrency=20)\ndata = cgc.geocode_addresses(input_df)')


# In[20]:

df = cgc.as_dataframe()
df.to_csv('geocoded.csv', index_label='Key', encoding='utf-8')


# In[30]:

df.head()


# In[29]:

df.dtypes


# Let's see how well these got identified

# In[28]:

df[['Match','Exact']].describe()


# 

# In[33]:

84414/96752, 52896/84414, 52896/96752


# Not too bad offhand; around 87% of the records were matched. What is up with the rest? Many of them include a `#` and apartment number, which is not needed for geocoding.  I wonder if it would help to remove these.

# In[41]:

input_df.iloc[df[df['Match']=='No_Match'].index].to_csv('geocoding_failures.csv', encoding='utf-8')


# In[56]:

fail_df = input_df[df['Match']=='No_Match'].copy()
fail_df['street'] = fail_df['street'].str.replace('\b(?:apt *)?(?:no|#) (?:- *)? *[a-z0-9-]','')


# In[58]:

cgc2 = CensusGeoCoder(template='tmp/geo-try2-{}', concurrency=20)
cgc2.geocode_addresses(fail_df)


# In[67]:

df2 = cgc2.as_dataframe()
df2[['Match','Exact']].describe()


# So that didn't do much.  Moving on.... Let's just consider the ones that matched (exact or inexact)

# In[179]:

matched_df = df.loc[df['Match']=='Match'].copy()
matched_df[:5]


# When we made `input_df`, we got unique addresses using a `groupby`. We also saved the `int64` indices of the members of each group (i.e., cases sharing an address)

# In[199]:

address_indexes_arr = np.asarray(address_indexes)
address_indexes_arr[:10]


# With a little pandas magic, we can make a series for mapping from unique address `Key` to case indexes

# In[162]:

matching = pd.DataFrame({'idx': pd.Series(address_indexes_arr[matched_df.reset_index()['Key'].values])})
ad_ix_df = pd.DataFrame({'idx': address_indexes_arr[matched_df.reset_index()['Key']]}, index=matched_df.index)
join_ds = ad_ix_df.apply(lambda x: pd.Series(x['idx']), axis=1).stack().reset_index(level=1, drop=True).astype('int64')
join_ds.head(20)


# We should omit a few fields like the input address, match status, etc.

# In[175]:

stacked_geo_df = matched_df[['Exact', 'Geo.Address', 'Geo.Lon.Lat', 
            'Geo.TIGER.LineID', 'Geo.TIGER.Side',
            'Geo.FIPS.State', 'Geo.FIPS.County', 'Geo.Tract', 'Geo.Block'
           ]].join(
    pd.DataFrame({'case_idx': join_ds})
)


# In[180]:

stacked_geo_df.head(10)


# Including `Defendant.Addr.Line.1` offers a good sanity check, but we can drop it before joining the main evictions dataset.

# In[218]:

geocoded_addresses_df = addresses_df.reset_index()[['Case.Number', 'Defendant.Addr.Line.1']].reset_index().join(stacked_geo_df.set_index('case_idx'))
geocoded_addresses_df.to_csv('geocoded_addresses.csv', encoding='utf-8')

geocoded_addresses_df.head()


# Et voil&agrave;

# In[221]:

geocoded_evictions_df = eviction_df.join(geocoded_addresses_df.drop(['Defendant.Addr.Line.1', 'index'], axis=1).set_index('Case.Number'))
geocoded_evictions_df.to_csv('geocoded_evictions.csv', encoding='utf-8')
geocoded_evictions_df.head()


# In[222]:

geocoded_evictions_df.head()[['Geo.Address','Defendant.Addr.Line.1']]


# Next, we want to load the data in GeoPandas. This will require a transformation of the `Geo.Lon.Lat` column.

# In[11]:

def lonlat_to_point(lonlat):
    if not pd.isnull(lonlat) and lonlat:
        try:
            lon, lat = lonlat.split(',')
            return shapely.geometry.Point(float(lon), float(lat))
        except ValueError as e:
            pass
def read_geocoded_df(filename):
    geocoded_df = gpd.GeoDataFrame(
        from_csv(
            'geocoded_evictions.csv',
            converters={
                'Geo.Lon.Lat': lonlat_to_point,
            },
            key='Case.Number',
        ),
        crs=fiona.crs.from_epsg(4326),
        geometry='Geo.Lon.Lat'
    )
    geocoded_df.dtypes[[
        'Exact',
        'Geo.TIGER.Side',
        'Geo.FIPS.State',
        'Geo.FIPS.County',
        'Geo.Tract',
        'Geo.Block',
    ]] = 'category'
    return geocoded_df


# In[12]:

geocoded_df = read_geocoded_df('geocoded_evictions.csv')


# Next let's for which party (plaintiff/defendant) caaes were decided

# In[13]:

list(filter(lambda x: x.endswith('Date'), geocoded_df.columns))


# In[14]:

geocoded_df[list(filter(lambda x: x.endswith('Date'), geocoded_df.columns))] =     geocoded_df[list(filter(lambda x: x.endswith('Date'), geocoded_df.columns))].apply(pd.to_datetime)


# In[15]:

geocoded_df[list(filter(lambda x: x.endswith('Date'), geocoded_df.columns))].sample(5)


# In[16]:

def count_non_null(df, fld):
    has_field = np.logical_not(pd.isnull(df[fld]))
    return has_field.sum(), df.shape[0]


# In[17]:

count_non_null(geocoded_df, 'Case.File.Date')


# In[18]:

count_non_null(geocoded_df, 'Judgment.Date')


# So it looks like we should use judgment date in preference to filing date. This would be more proximal to homelessness, though we may also want to capture the time between filing and judgment, where both are known.

# In[19]:

idx = pd.isnull(geocoded_df[['Case.File.Date','Judgment.Date']]
               ).apply(lambda x: not (x['Case.File.Date'] or x['Judgment.Date']), axis=1)


# In[20]:

geocoded_df.loc[idx,'Case.Duration'] = geocoded_df.loc[idx,'Judgment.Date']-geocoded_df.loc[idx,'Case.File.Date']


# In[21]:

geocoded_df.loc[idx,['Case.File.Date','Judgment.Date','Case.Duration']].head()


# In[22]:

geocoded_df.loc[idx,'Case.Duration'].dt.days.plot()


# In[23]:

pd.datetime(2016,6,2) - pd.datetime(2016,6,22)


# In[24]:

count_non_null(geocoded_df, 'Disposition.Date')


# In[25]:

count_non_null(geocoded_df, 'Disposition.Desc')


# In[26]:

count_non_null(geocoded_df, 'Judgment.In.Favor.Of')


# In[27]:

count_non_null(geocoded_df, 'Judgment.Against')


# In[28]:

set(geocoded_df['Judgment.Text'].str.lower())


# It would be useful to see who won each case. We can fuzzy match the in-favor-of with each of the plaintiff and defendants' names, and declare whichever is more similar the winner.

# In[29]:

from fuzzywuzzy import fuzz


# In[30]:

def pratio(x, y):
    if isinstance(x, float) or isinstance(y, float):
        return None
    return fuzz.ratio(x, y)


# In[31]:

get_ipython().run_cell_magic('time', '', "like_plaintiff = geocoded_df.apply(lambda x: pratio(x['Plaintiff.Name'], x['Judgment.In.Favor.Of']), axis=1)\n\nlike_defendant = geocoded_df.apply(lambda x: pratio(x['Defendant.Name'], x['Judgment.In.Favor.Of']), axis=1)")


# In[32]:

for_plaintiff = like_plaintiff > like_defendant
for_plaintiff.sum(), for_plaintiff.count()


# That seems high; let's look at a sample:

# In[33]:

pd.DataFrame({'like_plaintiff': like_plaintiff.sample(100)}).join(pd.DataFrame({'like_defendant':like_defendant})).join(geocoded_df[['Plaintiff.Name','Defendant.Name','Judgment.In.Favor.Of']])


# That seems plausible; save this in a column

# Which plaintiffs file the most eviction proceedings?

# In[47]:

geocoded_df.groupby('Plaintiff.Name')['Plaintiff.Name'].count().sort_values(ascending=False).head(50)


# In[34]:

geocoded_df['Judgment.In.Favor.Of.Plaintiff'] = for_plaintiff


# CSV isn't great for mapping (also has no typed data); let's save this as a shapefile or geojson.

# In[59]:

tmp_df = geocoded_df.copy()
tmp_df[[x for x in tmp_df.columns if x.endswith('Date')]] = tmp_df[[x for x in tmp_df.columns if x.endswith('Date')]].astype('str')
tmp_df['Judgment.Date'].head()


# In[100]:

tmp_df[tmp_df.columns[tmp_df.dtypes == 'category']] = tmp_df[tmp_df.columns[tmp_df.dtypes == 'category']].astype(str)
tmp_df['Judgment.In.Favor.Of.Plaintiff'] = tmp_df['Judgment.In.Favor.Of.Plaintiff'].astype(int)
tmp_df['Case.Duration'] = tmp_df['Case.Duration'].dt.days


# In[101]:

tmp_df.to_file('geocoded_evictions.shp')


# Next let's make a DF/file without explicit identifying information, since we don't need it for plotting/analysis.

# In[104]:

tmp_df.columns.sort_values().values


# In[128]:

cols=pd.Series(tmp_df.columns, index=tmp_df.columns)
tmp_df = tmp_df.drop(cols[cols.str.match(r'^(?:Second.)?(?:Defendant|Plaintiff)')], axis=1)
tmp_df = tmp_df.drop(['Case.Type', 'Case.Subtype', 'Nature.of.Claim','Judgment.Against','Judgment.In.Favor.Of',
                      'Next.Hearing.Date', 'Next.Hearing.Desc', 'Next.Hearing.Time', 'Style.Of.Case'
                     ], axis=1)


# In[132]:

tmp_df.columns.sort_values()


# In[133]:

tmp_df.sample(10)


# In[134]:

col='Case.Status'
tmp_df.loc[tmp_df[col]=='null',col] = float('nan')


# In[135]:

col='Case.Status'
set(tmp_df.loc[np.logical_not(tmp_df[col].isnull()),col])


# In[140]:

tmp_df = tmp_df.drop('Case.Number.1', axis=1)


# In[142]:

tmp_df.reset_index().to_file('geocoded_evictions_deidentified.shp')


# In[144]:

tmp_df.reset_index().to_file('geocoded_evictions_deidentified.geojson', driver='GeoJSON')


# In[147]:

tmp_df[np.logical_not(tmp_df['Geo.Lon.Lat'].isnull())].sample(5000).plot()


# In[ ]:



