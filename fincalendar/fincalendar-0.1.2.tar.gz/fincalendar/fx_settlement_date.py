from datetime import date,timedelta
from itertools import chain
import pycountry
from dateutil.relativedelta import relativedelta
from calendar import monthrange

from fincalendar.holiday_mapping import get_calendar
from fincalendar.currency_countrycode_mapping import currency_to_countrycode, countrycode_to_currency
from fincalendar.foreign_exchange_config import get_settlement_day_convention


def get_date_info(business_date, country_codes):
    calendars = {}
    for country_code in country_codes:
        if country_code.upper() != 'EUR':  # to circumvent the issue of missing country code for entire eurozone
            country = pycountry.countries.lookup(country_code)
            calendars[country.alpha_3] = get_calendar(country.alpha_3)
        else:
            calendars['EUR'] = get_calendar('EUR')
    date_info = {}
    for calendar_key, calendar in calendars.items():
        date_info[calendar_key] = {'working_day': calendar.is_working_day(business_date)}
    return date_info


def get_fxspot_valuedate(price_date, assetcurrencycountry, pricingcurrencycountry):
    
    cross_pair = False
    if 'USA' not in [assetcurrencycountry, pricingcurrencycountry]: cross_pair = True
    
    date = price_date
    offset = get_settlement_day_convention(countrycode_to_currency(assetcurrencycountry),countrycode_to_currency(pricingcurrencycountry))

    if not cross_pair:
        while offset != 0:          # continue to roll date forward until offset becomes 0
            non_businessday_roll = False
            if offset > 1:              # before t+2, only considers non USD currency's holiday
                countries = [assetcurrencycountry if pricingcurrencycountry == 'USA' else pricingcurrencycountry]
                date = date + timedelta(days=1)
                while date.isoweekday() not in range(1,6) or is_holiday(countries, date):
                    date = date + timedelta(days=1)
                    non_businessday_roll = True              
            if offset == 1:             # on t+2, considers both USD and the other currency's holiday
                countries = [assetcurrencycountry, pricingcurrencycountry]
                date = date + timedelta(days=1)
                while date.isoweekday() not in range(1,6) or is_holiday(countries, date):
                    date = date + timedelta(days=1)
                    non_businessday_roll = True
            offset-=1
        return date
    else:                       # cross pair needs to ensure final settlement date is not US holiday, 
        first_currency_vs_USD = get_fxspot_valuedate(price_date, assetcurrencycountry, 'USA')
        second_currency_vs_USD = get_fxspot_valuedate(price_date,pricingcurrencycountry, 'USA')
        date = first_currency_vs_USD if first_currency_vs_USD > second_currency_vs_USD else second_currency_vs_USD
        countries = [assetcurrencycountry,pricingcurrencycountry,'USA']
        while is_holiday(countries,date) or date.isoweekday() not in range(1,6):
            date = date + timedelta(days=1)
        return date

            
def get_fxforward_valuedate(price_date,tenor,assetcurrencycountry,pricingcurrencycountry):    
    
    spot_valuedate = get_fxspot_valuedate(price_date, assetcurrencycountry, pricingcurrencycountry)
    date =price_date    
    rolldirection = 1  # by default, when rolling dates due to holiday or weekend, roll forward to future dates
    
    if tenor == 'ON':
        date = date + timedelta(days=1)
        while is_holiday([assetcurrencycountry,pricingcurrencycountry],date) or date.isoweekday() not in range(1,6):
            date = date + timedelta(days=1)
        return date
    if tenor == 'SP':
        return spot_valuedate
    if tenor == 'SN':
        date = spot_valuedate + timedelta(days=1)
        while is_holiday([assetcurrencycountry,pricingcurrencycountry],date) or date.isoweekday() not in range(1,6):
            date = date + timedelta(days=1)
        return date

    if tenor[-1] == 'W':
        weeks = int(tenor[:-1])
        date = spot_valuedate + relativedelta(days = weeks * 7 )    
    if tenor[-1] == 'M':
        months = int(tenor[:-1])
        date = spot_valuedate + relativedelta(months = months)
    if tenor[-1] == 'Y':
        years = int(tenor[:-1])
        date = spot_valuedate + relativedelta(years = years)  
        
    # if the date falls on a month end, rolling direction will backward to earlier dates
    if date.day == monthrange(date.year,date.month)[1]: 
        rolldirection = -1   
    
    while date.isoweekday() not in range(1,6) or is_holiday([assetcurrencycountry,pricingcurrencycountry],date):   
        date = date + relativedelta(days = 1 * rolldirection)
    return(date)


def is_holiday(countries, date):
    date_info = get_date_info(date,countries)
    for key, value in date_info.items():
        if value.get('working_day') == False: return True
    return False


def calc_tenor_value_date(price_date, currency, tenor):
    """
    this method returns the settlement date corresponds to a fx forward tenor and pricing date and currency pair passed in. 
    e.g. passing in "1W", USDSGD, 2017-4-28 will return 2017-5-11  
    :return:
    """

    if not price_date:
        raise ValueError('Must specify price_date in querystring')
        
    if not tenor:
        raise ValueError('Must specify a tenor in querystring')
    tenor = str(tenor).upper()
    tenors = ['ON','TN','SP','SN','1W','2W','3W','1M','2M','3M','4M','5M','6M','7M','8M','9M','10M','11M','12M','15M','18M','21M','2Y']
    if tenor not in tenors:
        raise ValueError('Requested tenor is not supported for value date calculation')

    currencypair = currency
    if not currencypair:
        raise ValueError('Must specify a currency pair in querystring')

    currencypair = str(currencypair).upper()
    if len(currencypair) != 6:    
        raise ValueError('Currency pair format error, currency pair length is not 6 characters.')
    assetcurrencycountry = currency_to_countrycode( currencypair[:3])
    pricingcurrencycountry = currency_to_countrycode( currencypair[3:])

    if not assetcurrencycountry:
        raise ValueError("%s is currently not supported currency."% (assetcurrency))
    if not pricingcurrencycountry:
        raise ValueError("%s is currently not supported currency."% (pricingcurrency))
    
    value_date = get_fxforward_valuedate(price_date,tenor,assetcurrencycountry,pricingcurrencycountry)
    return value_date
    
