import os
import math
import numpy as np
import pandas as pd
from geopy.geocoders import GoogleV3

class USGeoHelper():
    def __init__(self, zipf=None, cityf=None, geo=None, log=True):
        # what to use when offline lookup fails
        self.geocoder = GoogleV3() if geo is None else geo
        self.log = log

        # read the files from this own directory if custom stuff not passed in
        scriptDir = os.path.dirname(__file__)
        if zipf is None:
            zipf = os.path.join(scriptDir, "zip_info.txt")
        if cityf is None:
            cityf = os.path.join(scriptDir, "city_info.txt")

        self.zips = pd.read_csv(zipf, sep='\t')
        # drop m^2 of land and water; keep just mi^2
        self.zips.drop(["ALAND", "AWATER"], axis=1, inplace=True)
        self.zips.columns = ["zip", "pop", "num_houses", "land_mi2",
                "water_mi2", "lat", "long"]
        self.zips.set_index("zip", inplace=True)

        self.cities = pd.read_csv(cityf, sep='\t', encoding="latin1")
        self.cities.drop(["GEOID", "ANSICODE", "ALAND", "AWATER",
            "LSAD", "FUNCSTAT"], axis=1, inplace=True)
        self.cities.columns = ["state", "city", "pop", "num_houses",
                "land_mi2", "water_mi2", "lat", "long"]
        self.cities.state = self.cities.state.str.lower()
        self.cities.city = self.cities.city.str.lower()
        self.cities.city = self.cities.city.apply(lambda city:
                city.rsplit(' ', 1)[0])
        self.cities.set_index(["state", "city"], inplace=True)
        self.cities.sort_index(level="state", inplace=True)

    def zipToCoord(self, zipcode, useOnline=False):
        zipcode = int(zipcode)
        if not useOnline:
            return tuple(self.zips.loc[zipcode][["lat", "long"]])

        try:
            return tuple(self.zips.loc[zipcode][["lat", "long"]])
        except KeyError:
            if self.log:
                print("using internet for zip", zipcode)
            loc = self.geocoder.geocode(str(zipcode) + " USA")
            return loc.latitude, loc.longitude
    def zipInfo(self, zipcode):
        zipcode = int(zipcode)
        return self.zips.loc[zipcode]

    def stateCityToCoord(self, state, city, useOnline=True):
        state, city = state.lower(), city.lower()
        if not useOnline:
            return self.cities.loc[state, city][["lat", "long"]] \
                .to_records(index=False)[0]

        try:
            # get row from df, make it into array of tuples, get first tuple
            return self.cities.loc[state, city][["lat", "long"]] \
                .to_records(index=False)[0]
        except:
            if self.log:
                print("using internet for", city, ", ", state)
            loc = self.geocoder.geocode(city + ", " + state + " USA")
            return loc.latitude, loc.longitude
    def stateCityInfo(self, state, city):
        return self.cities.loc[state.lower(), city.lower()]

    def coordToZip(self, lat, lon):
        return self.coordToZip_(lat, lon)[0]
    def coordToZip_(self, lat, lon):
        return haverMin(lat, lon, self.zips["lat"], self.zips["long"])

    def coordToStateCity(self, lat, lon):
        return self.coordToStateCity(lat, lon)[0]
    def coordToStateCity_(self, lat, lon):
        return haverMin(lat, lon, self.cities["lat"], self.cities["long"])

    def zipToStateCity(self, zipcode, useOnline=False):
        return self.zipToStateCity_(zipcode, useOnline)[0]
    def zipToStateCity_(self, zipcode, useOnline=False):
        lat, lon = self.zipToCoord(zipcode, useOnline)
        return self.coordToStateCity_(lat, lon)

    def stateCityToZip(self, state, city, useOnline=True):
        return self.stateCityToZip_(state, city, useOnline)[0]
    def stateCityToZip_(self, state, city, useOnline=True):
        lat, lon = self.stateCityToCoord(state, city, useOnline)
        return self.coordToZip_(lat, lon)

    def zipToStateCityDf(self, df, zipCol, useOnline=False, discardThresh=-1):
        discardCt = 0
        def proc(zipcode):
            nonlocal discardCt
            try:
                (state, city), d = self.zipToStateCity_(zipcode, useOnline)
                if discardThresh >= 0 and d > discardThresh:
                    discardCt += 1
                    return np.nan, np.nan
                return state, city
            except:
                discardCt += 1
                return np.nan, np.nan
        df2 = df.copy()
        df2["state"], df2["city"] = zip(*df2[zipCol].map(proc))
        if self.log:
            print(discardCt, " entries discarded")
            print("beware of many zips mapping to 1 state-city!" +
                    " state-city maybe not unique")
        return df2.dropna(subset=["state", "city", zipCol], how="any")

    def stateCityToZipDf(self, df, stateCol, cityCol,
                         useOnline=True, discardThresh=-1):
        discardCt = 0
        def proc(row):
            nonlocal discardCt
            try:
                zipcode, d = self.stateCityToZip_(row[0], row[1], useOnline)
                if discardThresh >= 0 and d > discardThresh:
                    discardCt += 1
                    return np.nan
                return zipcode
            except:
                discardCt += 1
                return np.nan
        df2 = df.copy()
        df2["zip"] = df2[[stateCol, cityCol]].apply(proc, axis=1)
        if self.log:
            print(discardCt, " entries discarded")
            print("beware of non-unique zips! many state-city can map to 1 zip")
        return df2.dropna(subset=["zip", stateCol, cityCol], how="any")

    def cleanZips(self, df, zipCol, useOnline=False, discardThresh=-1):
        if self.log and useOnline:
            print("warning: online zip filling is generally bad " +
                  "and discard threshold doesn't work well here")
        discardCt = 0
        def getZip(zipcode):
            nonlocal discardCt
            try:
                _ = self.zips.loc[zipcode]
                return zipcode
            except:
                if not useOnline:
                    discardCt += 1
                    return np.nan
                lat, lon = self.zipToCoord(zipcode, useOnline)
                zipcode, d = self.coordToZip_(lat, lon)
                if discardThresh >= 0 and d > discardThresh:
                    discardCt += 1
                    return np.nan
                return zipcode
        df2 = df.copy()
        df2.dropna(subset=[zipCol], how="any", inplace=True)
        if self.log:
            print(df.shape[0]-df2.shape[0], "nan zips were dropped")
        df2[zipCol] = df2[zipCol].astype(int).map(getZip)
        if self.log:
            print(discardCt, "bad zips discarded")
        return df2.dropna(subset=[zipCol], how="any")

# given a specific lat/long and two pandas series, find idxmin + min dist
def haverMin(lat, lon, lats, lons):
    lat, lon = math.radians(lat), math.radians(lon)
    latsRad = np.radians(lats)
    lonsRad = np.radians(lons)
    # haversine distance
    tmp = 3958.76 * 2 * np.arcsin(np.sqrt(
            0.5 - 0.5*np.cos(latsRad - lat) +
            np.cos(latsRad)*np.cos(lat)*(0.5 - 0.5*np.cos(lonsRad - lon))
        ))
    return tmp.idxmin(), tmp.min()
