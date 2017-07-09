# -*- coding: utf-8 -*-

"""Main module."""

import pandas as pd

class Charges(pd.DataFrame):
    
    @classmethod
    def read(cls, charges_path):
        rows = pd.read_csv(charges_path)[['ChargeDate','ChargeDesc','EmplName','Hrs']]
        rows_bad = rows[rows['ChargeDesc'].isnull() | rows['EmplName'].isnull()]
        rows_good = rows[rows['ChargeDesc'].notnull() & rows['EmplName'].notnull()]
        pd.options.mode.chained_assignment = None
        rows_good['ChargeDate'] = pd.to_datetime(rows_good['ChargeDate']).dt.date
        pd.options.mode.chained_assignment = 'warn'
        return cls(rows_bad, rows_good)
    
    def __init__(self, rows_bad, rows_good):
        super(self.__class__, self).__init__(rows_good)
        self.bad_records = rows_bad
        self.charge_codes = sorted([p for p in set(self['ChargeDesc']) if isinstance(p,basestring) and p!='false'])
        self.employees = sorted([e for e in set(self['EmplName']) if isinstance(e,basestring)])
        set_dates = set(self['ChargeDate'])
        self.hours_nominal = 8*len(pd.bdate_range(min(set_dates),max(set_dates)))
        self.hours_worked = {e:self[self['EmplName']==e]['Hrs'].sum() for e in self.employees}
    
    def fractions_by_charge_code(self, charge_code):
        c = self[self['ChargeDesc']==charge_code].groupby('EmplName').sum()
        c['Fraction'] = c.apply(lambda r: r['Hrs']/self.hours_worked[r.name] \
                        * min(1,round(self.hours_worked[r.name]/self.hours_nominal,1)), axis=1)
        c.drop('Hrs', axis=1, inplace=True)
        return c

