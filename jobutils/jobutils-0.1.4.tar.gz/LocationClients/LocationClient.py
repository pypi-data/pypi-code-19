import pandas as pd

from DataAccess.FileSystemIO import FileSystemIO

us_location_pattern = r"^\s*(?:\w+\s*,\s*){2,}(?:\w+\s*)$"
area_stopwords = ['greater', 'area']
area_stopwords = ['greater', 'area', 'city', 'south', 'north', 'west', 'east', 'bay', 'city']


class LocationClient:
    def __init__(self):

        self.io = FileSystemIO()

        self.locations = self.io.read_csv('Datasets/location_infos.csv')
        self.us_states = self.io.read_csv('Datasets/us_states.csv', sep=';')
        self.us_cities = self.io.read_csv('Datasets/us_cities.csv')
        self.countries = self.io.read_csv('Datasets/countries.csv')
        self.capitals = self.io.read_csv('Datasets/capitals.csv')

    def determine_linkedin_location(self, location_raw):
        """

        :param location_raw:
        :return:
        """
        location_result = {'country': '', 'state': '', 'area': '', 'empty': True}
        if location_raw is None or len(location_raw) == 0:
            location_result

        location = location_raw.lower().strip('?:!.,;')
        for word in area_stopwords:
            location = location.replace(word, '')

        location_terms = list(reversed(location.strip().split(',')))

        if len(location_terms) == 3 and location_terms[-1].strip() != 'united states':
            if location_terms[-1].strip() in self.countries['country'].values:
                return {'country': location_terms[-1], 'state': location_terms[1], 'area': location_terms[0], 'empty': False}

        for i in range(0, len(location_terms)):
            current_term = location_terms[i].strip()
            if current_term in self.us_states['state'].values:
                values = {'country': 'united states',
                          'state': current_term,
                          'area': ''}

                location_result = self.merge_location_values(location_result, values)
                continue

            if current_term in self.us_states['postal code'].values:
                return self.determine_us_location_postal_code(current_term, i, location_terms)

            if current_term in self.us_cities['city'].values:
                values = self.us_cities.loc[self.us_cities['city'] == current_term].iloc[0]
                values['country'] = 'united states'
                values['area'] = current_term
                location_result = self.merge_location_values(location_result, values)
                continue

            if current_term in self.capitals['capital'].values:
                values = self.capitals.loc[self.capitals['capital'] == current_term].iloc[0]
                values['area'] = values['capital']
                location_result = self.merge_location_values(location_result, values)
                continue

            if current_term in self.countries['country'].values:
                values = {}
                values['country'] = current_term
                location_result = self.merge_location_values(location_result, values)
                continue

            if current_term in self.us_states['postal code'].values:
                values = self.us_states.loc[self.us_states['postal_code'] == current_term]
                values['country'] = 'united states'
                location_result = self.merge_location_values(location_result, values)
                continue

            if current_term in self.locations['area'].values:
                values = self.locations.loc[self.locations['area'] == current_term].iloc[0]
                location_result = self.merge_location_values(location_result, values)
                continue

        return location_result

    def determine_raw_location(self, location_raw):
        """

        :param location_raw:
        :return:
        """
        return {'country': '',
                'state': '',
                'area': '',
                'empty': True}

    def determine_us_location_postal_code(self, current_term, i, location_terms):
        """

        :param current_term:
        :param i:
        :param location_terms:
        :return:
        """
        del location_terms[i]
        return {'country': 'united states',
                'state': self.us_states.loc[self.us_states['postal code'] == current_term].values[0][0],
                'area': ' '.join(location_terms),
                'empty': False}

    def parse_country(self, country_json):
        """

        :param country_json:
        :return:
        """
        try:
            return country_json['Country']['Country']
        except:
            return ''

    def parse_location(self, location_row):
        """

        :param location_row:
        :return:
        """
        result = {'area': '', 'state': '', 'country': '', 'state_code': '', 'state_abbrev': ''}

        if location_row['terms_count'] == 3:
            result = {
                'area': location_row['terms'][0].lower(),
                'state': location_row['terms'][1].lower(),
                'country': location_row['terms'][2].lower()
            }
        elif location_row['terms_count'] == 2:
            if location_row['terms'][1] in self.us_states['State'].values:
                state_info = self.us_states.loc[self.us_states['State'] == location_row['terms'][1]].values[0]
                result = {
                    'area': location_row['terms'][0].lower(),
                    'state': location_row['terms'][1].lower(),
                    'state_code': state_info[2].lower(),
                    'state_abbrev': state_info[1].lower(),
                    'country': 'united states'
                }
            else:
                result = {
                    'area': location_row['terms'][0],
                    'country': location_row['terms'][1]
                }

        return result

    def parse_locations(self):
        """
        Initializes location datasets
        :return:
        """
        locations = pd.read_json('../data/locations.json')
        locations['terms'] = locations['_id'].apply(lambda x: x.split(', '))
        locations['terms_count'] = locations['terms'].apply(lambda x: len(x))

        locations['country'] = locations['country'].apply(lambda x: self.parse_country(x))
        result = locations.apply(lambda x: self.determine_linkedin_location(x), axis=1)

        locations_df = pd.DataFrame.from_records(result.values)
        locations_df.to_csv('../data/location_infos.csv', index=False)

    def merge_location_values(self, location_result, values):
        """

        :param location_result:
        :param values:
        :return:
        """
        location_result['empty'] = False

        for key in values.keys():
            if key not in location_result:
                continue

            if len(location_result[key]) > 0 and location_result[key] != values[key]:
                continue
            else:
                location_result[key] = values[key]

        return location_result