__author__ = 'laurynas@joberate.com'

from DataAccess.FileSystemIO import FileSystemIO
from LocationClients.LocationClient import LocationClient
from Utils import try_get_value_from_dictionary
from Utils.TextFunctions import process_text, remove_stop_words

io = FileSystemIO()
location_client = LocationClient()

sites_blacklist =  io.read_csv('Datasets/site_blacklist.csv')
company_stopwords = io.read_csv('Datasets/company_stopwords.csv')
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
area_stopwords = ['greater', 'area', 'city', 'south', 'north', 'west', 'east']
area_stopwords = ['greater', 'area', 'city']


def extract_bio(profile, bio_key):
    """

    :param profile:
    :param bio_key: 
    :return:
    """
    try:
        bio = profile[bio_key]
        bio = process_text(bio)
        return bio
    except:
        return ''


def calculate_location_score(location):
    """

    :param location:
    :return:
    """
    score = 0
    if len(location['country']) > 0:
        score += 1
    if len(location['state']) > 0:
        score += 1
    if len(location['area']) > 0:
        score += 1

    return score


def compare_locations(location_a, location_b):
    """

    :param location_a:
    :param location_b:
    :return:
    """
    location_a_score = calculate_location_score(location_a)
    location_b_score = calculate_location_score(location_b)

    if location_a_score < location_b_score:
        return -1
    elif location_a_score > location_b_score:
        return 1
    else:
        return 0


def extract_location_twitter(profile):
    """

    :param profile:
    :return:
    """
    try:
        locations = []
        bio = profile['bio']
        bio = remove_stop_words(' '.join([word for word in bio.split() if len(word) > 1]))
        locations.append(location_client.determine_location(bio))
        locations.append(location_client.determine_location(profile['location_name']))
        return [loc for loc  in sorted(locations, compare_locations) if loc['empty'] == False][0]
    except:
        return {'country': '',
                'state': '',
                'area': '',
                'empty': True}


def extract_skills(profile, skills_key):
    """
    
    :param profile: 
    :param skills_key: 
    :return: 
    """
    skills = try_get_value_from_dictionary(profile, skills_key)
    for i in range(0, len(skills)):
        skills[i] = skills[i].lower()

    return skills


def extract_github_company(profile):
    """

    :param profile:
    :return:
    """
    company_raw = profile['company']
    if not company_raw or len(company_raw) == 0:
        return ''

    return clean_company(company_raw.lower())


def extract_stackoverflow_company(profile):
    """

    :param profile:
    :return:
    """
    position_company_terms = profile['currentPosition'].split(' at ')
    if len(position_company_terms) == 2:
        company_raw = position_company_terms[-1]
        if not company_raw or len(company_raw) == 0:
            return ''

        return clean_company(company_raw.lower())

    return ''


def extract_stackoverflow_position(profile):
    """

    :param profile:
    :return:
    """
    position_company_terms = profile['currentPosition'].split(' at ')
    if len(position_company_terms) == 2:
        return position_company_terms[0]

    return ''


def clean_company(company):
    """
    
    :param company: 
    :return: 
    """
    values = []
    # company_stopwords.collect()
    stopwords = company_stopwords['stopwords'].values.tolist()
    for term in company.split():
        term = term.replace(',', '').replace('.', '')
        if term not in stopwords:
            values.append(term)

    return ' '.join(values)


def extract_linkedin_company(profile):
    """

    :param profile:
    :return:
    """
    position_company_terms = profile['headline'].split(' at ')
    if len(position_company_terms) == 2:
        company_raw = position_company_terms[-1]
        if not company_raw or len(company_raw) == 0:
            return ''

        return clean_company(company_raw.lower())

    if profile['experienceCurrent']:
        return profile['experienceCurrent'][0]['company'].lower()

    return ''


def extract_linkedin_position(profile):
    """

    :param profile:
    :return:
    """
    position_company_terms = profile['headline'].lower().split(' at ')
    if len(position_company_terms) == 2:
        return position_company_terms[0]

    if profile['experienceCurrent']:
        return profile['experienceCurrent'][0]['position']

    return ''


def extract_other_names(profile, names_key):
    """

    :param profile:
    :param names_key:
    :return:
    """
    all_names = profile[names_key]
    if all_names is None:
        return []

    all_names = all_names.lower().split()
    return all_names[1:-1]


def extract_fname_fletter(profile, fname_key):
    """
    
    :param profile: 
    :param fname_key: 
    :return: 
    """
    try:
        return profile[fname_key][0].lower()
    except:
        return ''


def extract_linkedin_education(profile, education_key, fallback_key='education'):
    """
    
    :param profile:
    :param education_key:
    :param fallback_key:
    :return:
    """
    education_raw = []
    if education_key in profile:
        education_raw.extend( profile[education_key])
    if fallback_key in profile:
        education_raw.extend(profile[fallback_key])

    if len(education_raw) == 0:
        return []

    for ix in range(0, len(education_raw)):
        years = education_raw[ix]['date'].split()
        if len(years) == 2:
            education_raw[ix]['start_year'] = years[0]
            education_raw[ix]['end_year'] = years[1]

        education_raw[ix]['subtitle'] = education_raw[ix]['subtitle'][:len(education_raw[ix]['subtitle']) / 2]

    return education_raw


def extract_linkedin_education_light(profile, education_key, fallback_key='education'):
    """

    :param profile:
    :param education_key:
    :param fallback_key:
    :return:
    """
    education_raw = []
    if education_key in profile:
        education_raw.extend( profile[education_key])
    if fallback_key in profile:
        education_raw.extend(profile[fallback_key])

    return education_raw


def extract_linkedin_experience(profile, experience_key, fallback_key='experience'):
    """

    :param profile:
    :param experience_key:
    :param fallback_key:
    :return:
    """
    experience_raw = []
    if experience_key in profile:
        experience_raw.extend( profile[experience_key])
    if fallback_key in profile:
        experience_raw.extend(profile[fallback_key])

    if len(experience_raw) == 0:
        return []

    for ix in range(0, len(experience_raw)):
        dates = experience_raw[ix]['date'].split()
        month_cnt = len([dt for dt in dates if dt in months])
        if month_cnt == 2:
            experience_raw[ix]['start_year'] = dates[1]
            experience_raw[ix]['start_month'] = dates[0]
            experience_raw[ix]['end_year'] = dates[2]
            experience_raw[ix]['end_month'] = dates[3]
            del experience_raw[ix]['date']
        else:
            pass

    return experience_raw


def extract_linkedin_experience_light(profile, experience_key, fallback_key='experience'):
    """

    :param profile:
    :param experience_key:
    :param fallback_key:
    :return:
    """
    experience_raw = []
    if experience_key in profile:
        experience_raw.extend( profile[experience_key])
    if fallback_key in profile:
        experience_raw.extend(profile[fallback_key])

    return experience_raw

def extract_linkedin_location_raw(profile):
    """

    :param profile:
    :return:
    """
    return location_client.determine_location(profile['location'])


def extract_linkedin_location(profile):
    """
    
    :param profile:  
    :return: 
    """
    location_geocoded = location_client.determine_linkedin_location(profile['location'])
    return location_geocoded


def extract_linkedin_username(profile, username_key):
    """
    
    :param profile: 
    :param username_key: 
    :return: 
    """
    username_raw = profile[username_key]
    username_raw = ''.join(username_raw.lower().split())
    return username_raw


def get_urls(profile, url_keys):
    """
    
    :param profile: 
    :param url_keys: 
    :return: 
    """
    urls = list(filter(lambda x: len(x) > 0,
                       [profile[key].replace('https://', '').replace('http://', '') for key in url_keys if type(profile[key]) in [unicode, str]]))

    for i in range(0, len(urls)):
        url = urls[i]

        pattern = 'linkedin.com'
        if pattern in url:
            urls[i] = url[url.index(pattern) + len(pattern):]

    return list(set(urls))


def extract_id(profile, id_keys, fallback_keys):
    """
    
    :param profile: 
    :param id_keys: 
    :return: 
    """
    _id = try_get_value_from_dictionary(profile, id_keys)
    fallback_id = try_get_value_from_dictionary(profile, fallback_keys)
    return _id or fallback_id


def create_empty_field():
    """
    Creates empty field
    :return: 
    """
    return ''

def extract_viadeo_location(profile, city_key, country_key):
    """

    :param profile:
    :param city_key:
    :param country_key:
    :return:
    """
    location = profile[city_key] + ', ' + profile[country_key]
    return location

def extract_meetup_location(profile, city_key, region_key, country_key):
    """

    :param profile:
    :param city_key:
    :param region_key:
    :param country_key:
    :return:
    """
    location = profile[city_key] + ', ' + profile[region_key] + ', ' + profile[country_key]
    return location

def extract_networks(profile, networks_key):
    """
    :param profile:
    :param networks_key:
    :return:
    """
    networks = profile[networks_key]
    if len(networks) != 0:
        get_urls(networks)
    else:
        networks = []
    return networks

def extract_jentity_username(profile):
    """

    :param profile:
    :return:
    """
    return profile['network_identifier']['url'][0]

def extract_jentity_fname_letter(profile):
    """

    :param profile:
    :return:
    """
    return profile['personal_information']['fname'][0]