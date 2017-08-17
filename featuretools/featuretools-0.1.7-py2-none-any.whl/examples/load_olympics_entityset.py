import featuretools as ft
import pandas as pd
import os


def load_econ_indicators(econ_path='~/olympic_games_data/economic_data/'):
    # After running end to end, I saw this variable was predictive for some reason, and wasn't parsed correctly
    water_wd = 'LatestWaterWithdrawalData'
    econ_country = pd.read_csv(econ_path + "Country.csv", encoding='utf-8', dtype={water_wd: object})
    econ_country[water_wd] = pd.to_datetime(econ_country[water_wd], format='%Y.0')
    country_to_drop = ['TableName', 'LongName', 'ShortName', 'Alpha2Code', 'CurrencyUnit', 'SpecialNotes']
    econ_country.drop(country_to_drop, axis=1, inplace=True)
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
    return econ_country, econ_indicators


def load_entityset(data_dir='~/olympic_games_data', econ_path='~/olympic_games_data/economic_data/'):
    summer=pd.read_csv(os.path.join(data_dir, 'summer.csv'), encoding='utf-8')
    # winter=pd.read_csv(os.path.join(data_dir, 'winter.csv'), encoding='utf-8')
    # track=pd.read_csv(os.path.join(data_dir, 'track/data.csv'))
    countries=pd.read_csv(os.path.join(data_dir, 'dictionary.csv'), encoding='utf-8')

    summer['Athlete']=summer['Athlete'].str.split(', ').str[::-1].str.join(' ')
    summer['Athlete']=summer['Athlete'].str.title()
    # winter['Athlete']=winter['Athlete'].str.split(', ').str[::-1].str.join(' ')
    # winter['Athlete']=winter['Athlete'].str.title()
    summer['Year'] = pd.to_datetime(summer['Year'], format="%Y") + pd.offsets.MonthEnd(6)
    # winter['Year'] = pd.to_datetime(winter['Year'], format="%Y")

    # summer['Games Type'] = 'Summer'
    # winter['Games Type'] = 'Winter'
    # combined = pd.concat([summer, winter]).sort_values(['Year'])
    combined = summer.sort_values(['Year'])

    olympic_unique = ['Year', 'City']
    olympics = combined[olympic_unique].drop_duplicates().reset_index(drop=True)
    olympics.index.name = 'Olympic ID'
    olympics.reset_index(drop=False, inplace=True)
    combined['Olympic ID'] = combined.merge(olympics, on=olympic_unique, how='left')['Olympic ID']

    econ_country, econ_indicators = load_econ_indicators(econ_path)
    regions = econ_country[['Region']].drop_duplicates()
    regions.index.name = 'RegionId'
    regions.reset_index(drop=False, inplace=True)

    countries = countries.merge(econ_country,
                                left_on='Code',
                                right_on='CountryCode',
                                how='left').drop(['CountryCode'], axis=1)
    countries = countries.merge(regions,
                                left_on='Region',
                                right_on='Region',
                                how='left')
    countries.drop(['Region'], axis=1, inplace=True)

    es = ft.EntitySet("Olympic Games")
    es.entity_from_dataframe("medals",
                             combined,
                             index="medal_id",
                             make_index=True,
                             time_index='Year')
    # TODO: get country of Olympic city
    es.normalize_entity(base_entity_id="medals",
                        new_entity_id="olympics",
                        index="Olympic ID",
                        additional_variables=['City'],  # , 'Games Type'],  # 'Olympic City Country'
                        make_time_index=True)
    es.normalize_entity(base_entity_id="medals",
                        new_entity_id="athletes",
                        index="Athlete",
                        # Athletes might have multiple sports or disciplines?
                        additional_variables=['Sport', 'Country', 'Gender'],
                        copy_variables=['Discipline'])

    es.entity_from_dataframe("countries",
                             countries,
                             index="Code")
    es.entity_from_dataframe('econ_indicators',
                             econ_indicators,
                             index='IndicatorId',
                             make_index=True,
                             time_index='Year')
    es.entity_from_dataframe('regions',
                             regions,
                             index='RegionId')
    es.add_relationships([
        ft.Relationship(es['countries']['Code'], es['athletes']['Country']),
        ft.Relationship(es['countries']['Code'], es['econ_indicators']['CountryCode']),
        ft.Relationship(es['regions']['RegionId'], es['countries']['RegionId']),
        # ft.Relationship(es['countries']['Code'], es['olympics']['Olympic City Country']),
    ])
    es.add_interesting_values()
    return es
