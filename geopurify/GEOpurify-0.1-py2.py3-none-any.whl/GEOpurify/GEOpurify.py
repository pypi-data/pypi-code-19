#!/usr/bin/env python
# -*- coding: utf-8 -*-

# * Modules

import os
import pandas as pd
import GEOparse
from os.path import exists
from os import makedirs

# * Constructor


class GEOpurifier:
    def __init__(self, datadir="data/"):

        self.labels = ["ID_REF", "IDENTIFIER"]
        self.DATADIR = datadir
        self.TMPDIR = self.DATADIR + "tmp/"

# * Helpers

    def _list_files(self, dirname):
        '''Return a list of files in a directory.

        Args:
            dirname (str): path to the directory with files
        Returns:
            list: list of files

        '''
        return [f
                for f in os.listdir(dirname)
                if os.path.isfile(dirname + f)]

    def _get_gds(self, gds_id):
        '''Fetch the data according to GDS.

        Args:
            gds_id (str): GDS identification number
        Returns:
            GDS_object

        '''
        GDSDIR = self.DATADIR + "gds"
        if not exists(self.DATADIR):
            makedirs(self.DATADIR)
        if not exists(GDSDIR):
            makedirs(GDSDIR)
        try:
            return GEOparse.get_GEO(geo=gds_id, destdir=GDSDIR)
        except:
            print("Failed to fetch \'{}\'!".format(gds_id))


    def _purify_table(self, df):
        '''Clean a dataframe with GSMs.

        Args:
            df   (DataFrame) : raw dataframa
        Returns:
            DataFrame: a DataFrame for training

        '''

        clean_df_unit = df[self.labels].copy()
        units = []
        for column in df:
            if column not in self.labels:
                new_unit = clean_df_unit.copy()
                new_unit["EXPRESSION"] = df[column]
                new_unit["GSM"] = column
                units.append(new_unit)

        return pd.concat(units, ignore_index = True)

    def _get_GEO_feature(self, feature, dictionary):
        '''Fetch the feature value from the GEO metadata.

        Args:
            feature    (str)  : GEO feature
            dictionary (dict) : dictionary of GEO metadata
        Returns:
            The value corresponding to a feature in the given dictionary.
            If KeyError, return an empty string.


        '''
        try:
            return dictionary[feature][0]
        except KeyError:
            return ""

    def _save_clean_df(self, df, df_id):
        '''Save a cleaned df.

        Args:
            df   (DataFrame) : raw dataframa
        Returns:
            None

        '''

        if not exists(self.TMPDIR):
            makedirs(self.TMPDIR)

        df.to_csv(self.TMPDIR + df_id + '.csv', index=False)
        print("Saved a dataframe {}.".format(df_id))


# * Methods

    def filepurify(self, filepath, separation="\t"):
        '''Using a filepath, return a DataFrame for training.

        Args:
            filepath   (str) : path to a file
            separation (str) : separation in the table
        Returns:
            DataFrame: a DataFrame for training

        '''
        df = pd.read_csv(filepath, sep=separation)
        return self._purify_table(df)

    def dirpurify(self, dirname):
        '''Using a path to the directory, return a DataFrame for training.

        Args:
            dirname    (str) : path to the directory with files
            separation (str) : separation in the table
        Returns:
            DataFrame: a DataFrame for training

        '''
        df_list = []
        for filename in list_files(dirname):
            df_list.append(purify(dirname+filename))
        return pd.concat(df_list, ignore_index = True)

    def gdspurify(self, gds_id, load_extra_features=False):
        '''From GDS, return a DataFrame amicable for training.

        Args:
            gds_id              (str) : GDS identification number
            load_extra_features (bool): boolean switch for loading extra features
        Returns:
            DataFrame: DataFrame of data for training

        '''
        df_csv_path = self.TMPDIR + gds_id + '.csv'
        df_plus_csv_path = self.TMPDIR + gds_id + '_plus' + '.csv'

        if exists(df_csv_path) and not load_extra_features:
            return pd.read_csv(df_csv_path)

        elif exists(df_plus_csv_path) and load_extra_features:
            return pd.read_csv(df_plus_csv_path)

        else:
            gds = self._get_gds(gds_id)

            if not gds:
                return pd.DataFrame()

            platform = self._get_GEO_feature('platform', gds.metadata)
            platform_organism = self._get_GEO_feature('platform_organism', gds.metadata)
            platform_technology_type = self._get_GEO_feature('platform_technology_type', gds.metadata)

            sample_organism = self._get_GEO_feature('sample_organism', gds.metadata)

            df = self._purify_table(gds.table)

            df['PLATFORM'] = platform
            df['PLATFORM_ORGANISM'] = platform_organism
            df['PLATFORM_TECHNOLOGY_TYPE'] = platform_technology_type
            df['SAMPLE_ORGANISM'] = sample_organism

            if load_extra_features:

                extra_features = []
                gsms = gds.columns.index

                for feature in gds.columns:
                    if feature != "description":
                        extra_features.append(gds.columns[feature])

                for feature_df in extra_features:
                    feature_dict = {}
                    for i in range(len(gsms)):
                        feature_dict[gsms[i]] = feature_df[i]
                    for i, row in df.iterrows():
                        df.set_value(i, feature_df.name, feature_dict[row.GSM])
                self._save_clean_df(df, gds_id + "_plus")
            else:
                self._save_clean_df(df, gds_id)

            return df

    def gdspolypurify(self, gds_list_path, load_extra_features=False):
        '''From a list of GDS, return a DataFrame amicable for training.

        Args:
            gds_list_path (str): path to a list of GDS ids.
        Returns:
            DataFrame: DataFrame of data for training

        '''
        gds_list = open(gds_list_path, "r").read().split("\n")

        df_list = []

        for gds_id in gds_list:
            df_list.append(self.gdspurify(gds_id, load_extra_features))

        return pd.concat(df_list, ignore_index=True)
