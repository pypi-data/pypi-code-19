import os
import apsw
import regex
import datetime
import pycountry
import glob

import configparser
from decorator import decorator
from collections import namedtuple, OrderedDict

def get_currency_numeric(currency):
    country = pycountry.currencies.get(alpha_3=currency)
    country_numeric = int(country.numeric)
    return country_numeric

def get_currency_letter(currency):
    country = pycountry.currencies.get(numeric=str(currency))
    country_letter = country.letter
    return country_letter

Product = namedtuple("Product", "material_description qty product")

class ReadSection:

    description = ""
    pattern = regex.compile('(?<name>[-,.\w]+)/(?<qty>\d+)')
    pattern_sp = regex.compile('(?<=SP)(?<length>\d+,?\d*)')

    def __init__(self, config):
        self.config = config
        self.sections = OrderedDict()
    
    def __call__(self, section):
        config_section = self.config[section]
        items = config_section.get("items", "")
        description = config_section.get("description", "")
        if items:
            items = self.read_string(items)
            self.sections[section] = (items, description)
        return (items, description)

    @classmethod
    def read_names(cls, names):
        m = cls.pattern_sp.search(names)
        if m:
            length = m.group("length")
            length = length.replace(",", ".")
            length = float(length)
            name = names[:m.start()]
            name_variable = "%s_0" %name
            name_length = length
            product = ((name, 1), (name_variable, name_length))
        else:
            product = ((names, 1),)
        return product

    @classmethod
    def read_string(cls, s):
        items = []
        s = s.strip(";")
        _items = s.split(";")
        for item in _items:
            item = item.strip()
            m = cls.pattern.match(item)
            if m:
                names, qty = m.group("name", "qty")
            else:
                names, qty = item, 1
            qty = int(qty)
            product = cls.read_names(names)
            items.append(Product(names, qty, product))
        return items
    

today = datetime.date.today()

class SAP_price(namedtuple("SAP_price", "material_description, price, currency, type, date")):

    def __add__(self, other):
        new_price = self.price + other.price
        return self._replace(price=new_price)

    def __mul__(self, other):
        new_price = self.price * other
        return self._replace(price=new_price)

    def __float__(self):
        return self.price

    def __int__(self):
        return int(self.price)

    @property
    def currency_letter(self):
        return get_currency_letter(self.currency)

Exchange_rate = namedtuple("Exchange_rate", "base_currency, price_currency, price_type, exchange_rate, tax, precision")
    
class QProduct(namedtuple('QProduct', 'material, qty, material_description, sales_text, price, currency, price_type, application')):
    

    @property
    def exchange_rate(self):
        value = 1       
        if self.price.currency == self.currency:
            value = 1
        key = get_currency_letter(self.price.currency) + get_currency_letter(self.currency)
        if key == "CHFHKD":
            value = 8
        if key == "CHFCNY":
            value = 9/1.17
        if key == "CHFUSD":
            value = 1
        if key == "EURCNY":
            value = 9.5/1.17
        return value

    def calculate_price(self, sap_price=None, currency=None, price_type=None, precision=None):
        
        if sap_price is None:
            sap_price = self.price
        if currency is None:
            currency = self.currency
        if price_type is None:
            price_type = self.price_type
        if precision is None:
            precision = self.precision

        if isinstance(currency, str):
            currency = get_currency_numeric(currency)

        if (sap_price.currency == currency and (sap_price.type % 10) == (price_type %10)):
            return sap_price.price
        
        assert (sap_price.type == price_type)        
        rate = 1.0
        cur = SAP.cur
        t = (sap_price.currency, currency, price_type)
        cur.execute("select * from sap_exchange_rate where base_currency = ? and price_currency = ? and price_type = ?", t)
        sap_exchange_rate = cur.fetchone()
        sap_exchange_rate = Exchange_rate._make(sap_exchange_rate)
        rate = sap_exchange_rate.exchange_rate/sap_exchange_rate.tax
        precision = sap_exchange_rate.precision        
        return round(sap_price.price*rate, precision)

    @property
    def precision(self):
        value = 2
        return value
         
class SAP:

    home = os.path.expanduser("~")    
    data = os.path.join(home, "data")    
    database = os.path.join(data, "database")
    image = os.path.join(data, "image")
    price_date = today.isoformat()

    dbs = glob.glob(os.path.join(database, "sap_*.db3"))
    db_filename = max(dbs)
    db_basename = os.path.basename(db_filename)
   
    base_currency = get_currency_numeric("CHF")
    price_currency = get_currency_numeric("CNY")
    contract_currency =  get_currency_numeric("CHF")
    currency = price_currency
    price_type = 2

    
    name = os.path.splitext(db_basename)[0]
    year = 2016
    view_sap_price = "view_sap_price"
    view_sales_text = "view_sales_text"
    view_sap_material = "view_sap_material"
    view_sap_application = "view_sap_application"
    con = apsw.Connection(db_filename)
    cur = con.cursor()


    def __init__(self, price_currency=None, price_type=None, price_date = None, contract_currency=None, base_currency=None):
        
        contract_currency = contract_currency or self.contract_currency
        price_currency = price_currency or self.price_currency
        if price_type is None:
            price_type = self.price_type
            
        base_currency = base_currency or self.base_currency

        if isinstance(price_currency, str):
            price_currency = get_currency_numeric(price_currency)
            
        if isinstance(base_currency, str):
            base_currency = get_currency_numeric(base_currency)

        if isinstance(contract_currency, str):
            contract_currency = get_currency_numeric(contract_currency)

        self.price_date = price_date or self.price_date            
        self.price_currency = price_currency
        self.price_type = price_type
        self.base_currency = base_currency        
        


    @staticmethod
    def get_currency_numeric(currency):
        country = pycountry.currencies.get(letter=str(currency))
        country_numeric = int(country.numeric)
        return country_numeric

    @staticmethod
    def get_currency_letter(currency):
        country = pycountry.currencies.get(numeric=str(currency))
        country_letter = country.letter
        return country_letter

    @property
    def currency(self):
        return self.get_currency_letter(self.price_currency)

    @property
    def db(self):
        sap_db = "_".join([str(self.name), ]) + ".db3"
        return os.path.join(self.database, sap_db)

    @property
    def tables(self):
        sql = "select name from sqlite_master where type='table' order by name"
        self.cur.execute(sql)
        tables = [v[0] for v in self.cur.fetchall()]
        return tables

    @property
    def views(self):
        sql = "select name from sqlite_master where type='view' order by name"
        self.cur.execute(sql)
        views = [v[0] for v in self.cur.fetchall()]
        return views

    def _get_price(self, material_description, currency = 156, price_type = None, date = None, view = None):
        date = date or self.price_date or today.isoformat()
        view = view or self.view_sap_price
        cur = self.cur

        if price_type is None:
            price_type = self.price_type

        price_type = price_type       
        if not (currency == 156 or price_type == 1000):
            currency = self.base_currency
        t = (view, currency, price_type, date)            
        sql = 'select * from %s where material_description = ? and currency = %d and type = %d  and date < "%s" order by date desc limit 1' % t
        cur.execute(sql, (material_description, ))
        value = cur.fetchone()   
        if isinstance(value, tuple):
            value = SAP_price._make(value)            
        return value

    def get_price(self, material_description, currency = 756, price_type = None, date = None, view = None):
        product = ReadSection.read_names(material_description)
        price = 0
        new_currency, new_price_type, new_date = None, None, None       
        for name, qty in product:
            sap_price = self._get_price(name, currency, price_type, date, view)
            if sap_price is None:
                print(name)
                sap_price = self._get_price(name, 756, 2, date, view)
            if new_price_type is None:
                new_price_type = sap_price.type
            if new_date is None:
                new_date = sap_price.date
            if new_currency is None:
                new_currency = sap_price.currency
                
            sub_price = sap_price.price
            price += sub_price*qty            
        value = sap_price._make([material_description, price, new_currency, new_price_type, new_date])
        return value
            

    def get_sales_text(self, material_description, text_type = None, date = None, view = None):
        date = date or today.isoformat()
        view = view or self.view_sales_text
        cur = self.cur
        names = ReadSection.read_names(material_description)
        material_description = names[0][0]
        
        if text_type is None:
            sql = 'select * from %s where material_description =  ? and date < "%s" order by type desc, date desc limit 1' %(view, date)            
        if isinstance(text_type, int):
            sql = 'select * from %s where material_description =  ? and type = %d and date < "%s" order by type desc, date desc limit 1' %(view, text_type, date)            
        t = (material_description, )
        cur.execute(sql, t)
        value = cur.fetchone()
        if isinstance(value, tuple):
            value = value[1]
        if len(names) == 2:
            length = names[1][1]
            sp_text = ', L=%s m.' % length
            value += sp_text
        return value or None

    def get_material(self, material_description, date = None, view = None):
        date = date or today.isoformat()
        view = view or self.view_sap_material
        cur = self.cur
        material_description = ReadSection.read_names(material_description)[0][0]
        sql = 'select * from %s where material_description =  ? and date < "%s" order by date desc limit 1' %(view, date)
        t = (material_description, )
        cur.execute(sql, t)
        value = cur.fetchone()
        if isinstance(value, tuple):
            value = value[0]
        return value or None

    def get_application(self, material_description, date = None, view = None):
        date = date or today.isoformat()
        view = view or self.view_sap_application
        material_description = ReadSection.read_names(material_description)[0][0]

        cur = self.cur
        sql = 'select * from %s where material_description =  ? limit 1' %(view, )
        t = (material_description, )
        cur.execute(sql, t)
        value = cur.fetchone()
        if isinstance(value, tuple):
            value = value[-1]
        return value or None

    def __call__(self, material_description, qty=1, currency=None, price_type=None,text_type=None, date = None, view=None):
        if isinstance(material_description, Product):
            material_description, qty, product = material_description
        if isinstance(currency, str):
            currency = get_currency_numeric(currency)            
        currency = currency or self.price_currency
        assert isinstance(currency, int)        
        if price_type is None:
            price_type = self.price_type            
        if date is None:
            date = self.price_date

        new_price_type = price_type
        new_currency = currency
        if currency == 156:
            price_type = 4
            new_price_type = 4
            
        sales_text = self.get_sales_text(material_description, text_type=text_type)
        price = self.get_price(material_description, currency=new_currency, price_type=new_price_type, date=date, view=view)
        material = self.get_material(material_description)
        if material in (22001162, ):
            price = self.get_price(material_description, currency=new_currency, price_type=new_price_type+100, date=date, view=view)            
        application = self.get_application(material_description)
        return QProduct._make([material, qty, material_description, sales_text, price, currency, price_type, application])
        
def main():
    sap_hua = SAP()
    material_description = "6157BAE"
    for material_description in ["6157BAE", "6157BAE", "1661ASP", "1661ASP1,0", "1661ASP2,0"]:
        mm = sap_hua(material_description)
        print(mm)
 
if __name__ == "__main__":
    main()
