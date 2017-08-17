import pandas as pd
import numpy as np
import math
import os
from sklearn.base import clone
from sklearn.preprocessing import Imputer
import featuretools as ft
from featuretools.primitives import AggregationPrimitive
from featuretools.utils.wrangle import _check_timedelta
from featuretools.variable_types import Numeric, Discrete, Index


def bin_labels(labels, bin_edges):
    num_bins = len(bin_edges) + 1
    new_labels = [int(class_) for class_ in np.digitize(labels.values, bin_edges)]
    bins_used = set()
    bins = []
    for i in xrange(num_bins):
        if i == 0:
            bins.append("<%.1f" % (bin_edges[0]))
        elif i + 1 == num_bins:
            bins.append(">=%.1f" % (bin_edges[-1]))
        else:
            bins.append("[%.1f,%.1f)" % (bin_edges[i - 1], bin_edges[i]))

    for i, lt in enumerate(new_labels):
        new_labels[i] = bins[int(lt)]
        bins_used.add(bins[int(lt)])
    bins = [b for b in bins if b in bins_used]
    return pd.Series(new_labels), bins


def count_elts_by_group(x, by):
    df = pd.DataFrame({'f': x, 'b': by})
    return df.groupby('b')['f'].count()


def most_numerous_group(x, by):
    return count_elts_by_group(x, by).idxmax()


def most_numerous_by_group(x, by):
    return count_elts_by_group(x, by).max()


class MostNumerousGroup(AggregationPrimitive):
    """Finds the group with the most numerous elements and returns the group"""
    name = "most_numerous_group"
    signature = [Index, Discrete]
    default_value = np.nan
    return_type = Discrete

    def __init__(self, base_feature, by, parent_entity, where=None):
        self.by = by
        super(MostNumerousGroup, self).__init__([base_feature, by], parent_entity, where=where)

    def get_function(self):
        return most_numerous_group


class MostNumerousByGroup(AggregationPrimitive):
    name = "most_numerous_by_group"
    signature = [Index, Discrete]
    default_value = np.nan
    return_type = Numeric
    stack_on_self = False

    def __init__(self, base_feature, by, parent_entity, where=None):
        self.by = by
        super(MostNumerousByGroup, self).__init__([base_feature, by], parent_entity, where=where)

    def get_function(self):
        return most_numerous_by_group


class TimeSeriesSplitByDate(object):
    def __init__(self, dates, n_splits=None,
                 combine_single_class_splits=True, ignore_splits=None):
        self.date_name = dates.name
        self.dates = dates.to_frame()
        self.combine_single_class_splits = combine_single_class_splits
        if n_splits is None:
            n_splits = dates.nunique() - 1
        self.nominal_n_splits = n_splits
        self.gen_splits()
        self.splits = None
        self.ignore_splits = ignore_splits

    def split(self, X=None, y=None, groups=None):
        if self.ignore_splits:
            if self.splits is None or (y != self.y).any():
                self.y = y
                self.splits = [x for i, x in enumerate(self.nominal_splits) if i not in self.ignore_splits]
            return self.splits
        elif self.combine_single_class_splits:
            if self.splits is None or self.y is None or (y != self.y).any():
                self.y = y
                self.splits = []
                for i, train_test in enumerate(self.nominal_splits):
                    self.splits.append(train_test)
                    while len(self.splits) > 1 and self.single_class(self.splits[-1], y):
                        last = self.splits.pop(-1)
                        penultimate = self.splits.pop(-1)
                        combined = []
                        for _last, _pen in zip(last, penultimate):
                            combined.append(pd.concat([pd.Series(_last), pd.Series(_pen)])
                                              .drop_duplicates()
                                              .sort_values())
                        self.splits.append(combined)
            return self.splits
        else:
            return self.nominal_splits

    def single_class(self, split, y):
        return pd.Series(y[split[1]]).nunique() == 1

    def get_dates(self, split, X=None, y=None, groups=None):
        if self.splits is None or (y != self.y).any():
            self.split(None, y)
        train_i, test_i = self.splits[split]
        return [self.split_index.iloc[ti][self.date_name].drop_duplicates().tolist()
                for ti in train_i, test_i]

    def gen_splits(self):
        date_index = self.dates.drop_duplicates()
        date_index = date_index.reset_index(drop=True)
        date_index.index.name = 'split'
        date_index = date_index.reset_index(drop=False)
        div = math.ceil(len(date_index) / (self.nominal_n_splits + 1))
        date_index['split'] = (date_index['split'] / (div)).astype(int)
        self.split_index = self.dates.merge(date_index, on=self.date_name, how='left')
        self.split_index.index = range(self.split_index.shape[0])
        splits = self.split_index['split']
        train_splits = [splits[splits < (i + 1)].index.values for i in range(self.nominal_n_splits)]
        test_splits = [splits[splits == (i + 1)].index.values for i in range(self.nominal_n_splits)]
        self.nominal_splits = zip(train_splits, test_splits)

    def get_n_splits(self, X=None, y=None, groups=None):
        return len(self.split(None, y))


def get_feature_importances(estimator, feature_matrix, labels, splitter, n=100):
    feature_imps_by_time = []
    dates = []
    for i, train_test_i in enumerate(splitter.split(None, labels.values)):
        train_i, test_i = train_test_i
        dates.append(splitter.get_dates(i, y=labels.values))
        X = feature_matrix.values[train_i, :]
        icols_used = [i for i, c in enumerate(X.T) if not pd.isnull(c).all()]
        cols_used = feature_matrix.columns[icols_used].tolist()

        X = X[:, icols_used]
        y = labels.values[train_i]
        clf = clone(estimator)
        clf.fit(X, y)
        feature_importances = (pd.Series(clf.steps[-1][1].feature_importances_, index=cols_used)
                                 .sort_values(ascending=False))
        feature_imps_by_time.append(feature_importances.head(n))
    return feature_imps_by_time, dates


def set_use_previous(features, use_previous, inplace=False):
    use_previous = _check_timedelta(use_previous)
    if not inplace:
        features = [f.copy() for f in features]
    for f in features:
        for g in [f] + f.get_dependencies(deep=True):
            if isinstance(g, AggregationPrimitive) and g.base_features[0].entity.time_index is not None:
                g.use_previous = ft.Timedelta(8, 'years')
    return features


def load_econ_indicators(econ_path='~/olympic_games_data/economic_data/', since_date=None):
    country_cols = ['CountryCode', 'Region', 'IncomeGroup',
                    'SystemOfTrade', 'GovernmentAccountingConcept']
    econ_country = pd.read_csv(econ_path + "Country.csv", encoding='utf-8', usecols=country_cols)

    econ_indicators = pd.read_csv(econ_path + "Indicators.csv", encoding='utf-8')
    econ_indicators['Year'] = pd.to_datetime(econ_indicators['Year'], format='%Y')
    econ_indicators.drop(['CountryName', 'IndicatorCode'], axis=1, inplace=True)
    econ_indicators.set_index('CountryCode', inplace=True)
    econ_indicators.set_index('Year', append=True, inplace=True)
    econ_indicators.set_index('IndicatorName', append=True, inplace=True)
    econ_indicators = (econ_indicators['Value'].unstack(level='IndicatorName')
                                               .reset_index(level='Year', drop=False)
                                               .reset_index(drop=False))
    econ_indicators.columns.name = None
    if since_date is not None:
        econ_indicators = econ_indicators[econ_indicators['Year'] >= since_date]
    intermediate_regions = pd.read_csv(econ_path + 'country_regions.csv')

    cols = ['Region Code', 'Sub-region Code', 'Intermediate Region Code']

    def convert_to_int_str(s):
        max_s = s.dropna().max()
        return s.replace({np.nan: max_s+ 1}).astype(int).astype(str)

    for c in cols:
        intermediate_regions[c] = convert_to_int_str(intermediate_regions[c])

    def make_region_id(regions, subcols):
        return regions[cols[0]].str.cat([regions[c] for c in cols[1:]], sep='').astype(int)

    inter_region_code = make_region_id(intermediate_regions, cols)
    subregion_code = make_region_id(intermediate_regions, cols[:-1])
    intermediate_regions['Intermediate Region Code'] = inter_region_code
    intermediate_regions['Sub-region Code'] = subregion_code
    return intermediate_regions, econ_country, econ_indicators


def match_countries_to_regions_and_econ_data(countries,
                                             econ_country,
                                             region_countries,
                                             econ_indicators):
    '''
    Match country codes from the `countries` dataframe (from the Kaggle olympics dataset)
    with the codes in the `regions` dataframe (from the UN)
    and the codes in the `econ_country` and `econ_indicators` dataframes (from the Kaggle economics dataset)

    These datasets contain slightly different country codes, and we want to link them up the best we can.
    We also want to pull additional information from the UN region dataset into countries

    The strategy:

    1. Merge `countries` with `region_countries` on the country name
    2. Merge `countries` with `region_countries` on the code (`countries` code is from the IOC, `region_countries` code is `ISO-alpha3 Code`)
    3. Combine these two merges by setting the nulls on Country and Code with the values from the other dataframe
    4. Merge the rest that did not share a name or code on a hand-defined dictionary mapping country names in the two dataframes
    5. Merge `countries` with original `region_countries` to pull in region and other information
    6. Generate a manual mapping on country codes in `countries` and `econ_country`
    7. Merge `countries` with `econ_country` using the `ISO-alpha3 Code` from region_countries as well as this mapping
    8. Pull IOC code from `countries` into `econ_indicators` and remove extraneous countries not present in the Olympics dataset
    '''
    # Step 1
    matching_countries_by_country = countries[['Code', 'Country']].merge(region_countries[['Country or Area', 'ISO-alpha3 Code']], right_on='Country or Area', left_on='Country', how='left')
    matching_countries_by_country.drop(['Country or Area'], axis=1, inplace=True)
    # Step 2
    matching_countries_by_code = countries[['Code', 'Country']].merge(region_countries[['ISO-alpha3 Code']], right_on='ISO-alpha3 Code', left_on='Code', how='left')

    # Step 3
    matching_countries = matching_countries_by_code
    code_mask = matching_countries_by_country['ISO-alpha3 Code'].notnull()
    matching_countries.loc[code_mask, 'ISO-alpha3 Code'] = matching_countries_by_country.loc[code_mask, 'ISO-alpha3 Code']

    # Step 4
    country_region_mapping = {'Brunei': 'Brunei Darussalam',
                              'Burma': 'Myanmar',
                              'Iran': 'Iran (Islamic Republic of)',
                              'Netherlands Antilles': 'Suriname',
                              'Palestine, Occupied Territories': 'State of Palestine',
                              'Taiwan': 'China',
                              'Tanzania': 'United Republic of Tanzania',
                              'Vietnam': 'Viet Nam',
                              'Virgin Islands': 'United States Virgin Islands'}
    region_country_index = region_countries.set_index('Country or Area')['ISO-alpha3 Code']
    region_mapping_codes = {k: region_country_index[v] for k, v in country_region_mapping.items()}
    dict_mapping_mask = matching_countries['Country'].isin(country_region_mapping)
    matching_countries.loc[dict_mapping_mask, 'ISO-alpha3 Code'] = matching_countries.loc[dict_mapping_mask, 'Country'].replace(region_mapping_codes).values
    countries['ISO-alpha3 Code'] = matching_countries['ISO-alpha3 Code'].values

    # Step 5
    region_cols_to_pull = ['ISO-alpha3 Code', 'Intermediate Region Code', 'Land Locked Developing Countries (LLDC)', 'Least Developed Countries (LDC)', 'Small Island Developing States (SIDS)', 'Developed / Developing Countries']
    countries = countries.merge(region_countries[region_cols_to_pull], on='ISO-alpha3 Code', how='left')

    # Step 6
    econ_country_region_country_code_mapping = {
        'ZAR': 'COD',
        'VGB': 'GBR',
        'TMP': 'TLS',
        'WBG': 'PSE',
        'ROM': 'ROU',
        'ADO': 'AND',
    }
    region_country_mapping = {
        'COK': 'NZL',
        'NRU': 'AUS',
        'VGB': 'GBR'
    }
    econ_country['CountryCodeMerge'] = econ_country['CountryCode'].replace(econ_country_region_country_code_mapping)
    countries['ISO-alpha3 Code'] = countries['ISO-alpha3 Code'].replace(region_country_mapping)

    # Step 7
    countries = countries.merge(econ_country,
                                left_on='ISO-alpha3 Code',
                                right_on='CountryCodeMerge',
                                how='left').drop(['CountryCodeMerge', 'Region', 'ISO-alpha3 Code'], axis=1)

    # Step 8
    # make sure econ_indicators are matched with countries on Code,
    # and remove rows from econ_indicators from countries not present
    # in the countries dataframe
    econ_indicators = econ_indicators.merge(countries[['CountryCode', 'Code']],
                                            on='CountryCode',
                                            how='inner').drop(['CountryCode'], axis=1)
    return countries, econ_indicators


def load_entityset(data_dir='~/olympic_games_data', with_econ_data=False,
                   econ_path='~/olympic_games_data/economic_data/', since_date=None):
    '''
    1. Load data on each medal won at every summer Olympic Games
    2. Load data about each country that won at least one medal through Olympic history
    3. Do some formatting
    4. Sort on Year
    5. Normalize out Olympics as separate dataframe containing a unique row for each Olympic Games
    6. Initialize Featuretools EntitySet
    7. Optionally load region and economic data
    8. Finish loading Featuretools EntitySet
    '''
    # Step 1
    summer=pd.read_csv(os.path.join(data_dir, 'summer.csv'), encoding='utf-8')
    # winter=pd.read_csv(os.path.join(data_dir, 'winter.csv'), encoding='utf-8')

    # Step 2
    countries = pd.read_csv(os.path.join(data_dir, 'dictionary.csv'), encoding='utf-8')
    countries.drop(['GDP per Capita', 'Population'], axis=1, inplace=True)
    # Some countries had a '*" at their end, which we need to remove
    # in order to match with economic data
    countries['Country'] = countries['Country'].str.replace('*', '')

    # Step 3
    # Make names First Last instead of Last, First?
    # These two lines were taken from https://www.kaggle.com/ash316/great-olympians-eda/notebook
    summer['Athlete']=summer['Athlete'].str.split(', ').str[::-1].str.join(' ')
    summer['Athlete']=summer['Athlete'].str.title()

    # winter['Athlete']=winter['Athlete'].str.split(', ').str[::-1].str.join(' ')
    # winter['Athlete']=winter['Athlete'].str.title()
    summer['Year'] = pd.to_datetime(summer['Year'], format="%Y") + pd.offsets.MonthEnd(6)
    # winter['Year'] = pd.to_datetime(winter['Year'], format="%Y")

    # Step 4
    # summer['Games Type'] = 'Summer'
    # winter['Games Type'] = 'Winter'
    # combined = pd.concat([summer, winter]).sort_values(['Year'])
    combined = summer.sort_values(['Year'])
    if since_date is not None:
        combined = combined[combined['Year'] >= since_date]

    # Step 5
    olympic_unique = ['Year', 'City']
    olympics = combined[olympic_unique].drop_duplicates().reset_index(drop=True)
    olympics.index.name = 'Olympic ID'
    olympics.reset_index(drop=False, inplace=True)
    combined['Olympic ID'] = combined.merge(olympics, on=olympic_unique, how='left')['Olympic ID']

    # Step 6
    es = ft.EntitySet("Olympic Games")
    es.entity_from_dataframe("medals_won",
                             combined,
                             index="medal_id",
                             make_index=True,
                             time_index='Year')
    es.normalize_entity(base_entity_id="medals_won",
                        new_entity_id="olympics",
                        index="Olympic ID",
                        additional_variables=['City'],  # , 'Games Type'],
                        make_time_index=True)
    es.normalize_entity(base_entity_id="medals_won",
                        new_entity_id="athletes",
                        index="Athlete",
                        # Athletes might have multiple sports or disciplines?
                        additional_variables=['Country', 'Gender'])
    es.normalize_entity(base_entity_id="medals_won",
                        new_entity_id="disciplines",
                        index="Discipline",
                        additional_variables=['Sport'])
    es.normalize_entity(base_entity_id="disciplines",
                        new_entity_id="sports",
                        index="Sport")
    if with_econ_data:
        # Step 7
        region_countries, econ_country, econ_indicators = load_econ_indicators(econ_path, since_date=since_date)

        # Match country codes from the `countries` dataframe (from the Kaggle olympics dataset)
        # with the codes in the `regions` dataframe (from the UN)
        # and the codes in the `econ_country` and `econ_indicators` dataframes (from the Kaggle economics dataset)
        countries, econ_indicators = match_countries_to_regions_and_econ_data(countries,
                                                                              econ_country,
                                                                              region_countries,
                                                                              econ_indicators)

        # Create a dataframe that's unique on intermediate regions
        # and drop columns that are now included in countries dataframe
        # Keep columns required to normalize out subregion and region
        region_cols_to_keep = ['Region Code', 'Region Name',
                               'Sub-region Code', 'Sub-region Name',
                               'Intermediate Region Code', 'Intermediate Region Name']
        intermediate_regions = region_countries[region_cols_to_keep].drop_duplicates('Intermediate Region Code')

        es.entity_from_dataframe('econ_indicators',
                                 econ_indicators,
                                 index='IndicatorId',
                                 make_index=True,
                                 time_index='Year')

        es.entity_from_dataframe('intermediate_regions',
                                 intermediate_regions,
                                 index='Intermediate Region Code')

        es.normalize_entity(base_entity_id='intermediate_regions',
                            new_entity_id='subregions',
                            index='Sub-region Code',
                            additional_variables=['Region Code', 'Region Name', 'Sub-region Name'])
        es.normalize_entity(base_entity_id='subregions',
                            new_entity_id='regions',
                            index='Region Code',
                            additional_variables=['Region Name'])

    # Step 8
    es.entity_from_dataframe("countries",
                             countries,
                             index="Code")

    relationships = [
        ft.Relationship(es['countries']['Code'], es['athletes']['Country']),
    ]
    if with_econ_data:
        relationships.extend([
            ft.Relationship(es['countries']['Code'], es['econ_indicators']['Code']),
            ft.Relationship(es['intermediate_regions']['Intermediate Region Code'], es['countries']['Intermediate Region Code'])])

    es.add_relationships(relationships)
    es.add_interesting_values()
    return es


def fit_and_score(X, y, splitter, estimator, scoring_functions, proba=False):
    # TODO: make dataframe with dates as index
    scores = []
    for train, test in splitter.split(X, y):
        cloned = clone(estimator)
        cloned.fit(X[train], y[train])
        actual = y[test]
        predictions = cloned.predict(X[test])
        try:
            probs = cloned.predict_proba(X[test])
            if len(probs.shape) > 1 and probs.shape[1] > 1:
                probs = probs[:, 1]
        except:
            probs = None
        split_scores = []
        for i, sfunc in enumerate(scoring_functions):
            if ((isinstance(proba, list) and proba[i]) or
                    (not isinstance(proba, list) and proba)):
                using = probs
            else:
                using = predictions
            split_scores.append(sfunc(actual, using))
        scores.append(split_scores)
    return pd.DataFrame(scores, columns=[f.__name__ for f in scoring_functions])


def plot_feature(feature_matrix, labels, feature_name, plot_name=None):
    """
    Plot conditional distribution of feature_name when label
    is True, and when label is False

    Args:
        feature_matrix (pd.DataFrame) : DataFrame containing feature data (each column is the data for one feature)
        labels (pd.Series) : Series containing the labels for each instance (for each row of feature matrix)
        feature_name (str) : Name of feature to plot
        plot_name (str, optional) : Name to give title of plot

    Note:
        This function requires the seaborn and matplotlib libraries, both installable by pip.
    """

    vals = feature_matrix[[feature_name]]
    vals = Imputer(missing_values='NaN',
                   strategy="most_frequent",
                   axis=0).fit_transform(vals.values).flatten()

    bin_edges = np.histogram(vals, 'auto')[1]
    import seaborn as sns
    import matplotlib.pyplot as plt
    # Set up the matplotlib figure
    f, axes = plt.subplots(1, 2, figsize=(13, 6), sharex=True)
    if plot_name is not None:
        title = "{}\nFeature: {}".format(plot_name, feature_name)
    else:
        title = "Feature: {}".format(feature_name)
    f.suptitle(title, fontsize=20, y=1.15)
    sns.plt.title(feature_name + " vs. label")
    sns.distplot(vals[labels.values], hist=True, bins=bin_edges, color="g",
                 kde=False, kde_kws={"shade": False}, ax=axes[0])
    axes[0].set_title('Distribution when True')
    sns.distplot(vals[~labels.values], hist=True, bins=bin_edges, color="r",
                 kde=False, kde_kws={"shade": False}, ax=axes[1])
    axes[1].set_title('Distribution when False')
    plt.tight_layout()
