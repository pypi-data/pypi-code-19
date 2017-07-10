import clarus.api
import logging
from collections import Mapping, defaultdict, OrderedDict
import csv
from six import StringIO
import json

logger = logging.getLogger(__name__)

class ApiResponse(Mapping):
    httpresponse = None
    _stats = None
    __str = None
    __parsed = None
    
    def __init__(self, httpresponse):
        self.httpresponse = httpresponse
        #self._parsed = ParsedCsvResult(httpresponse.text, '\t')
        
    def __getitem__(self, name):
        return self._parsed().__getitem__(name)

    def __iter__(self):
        return self._parsed().__iter__()
    
    def __len__(self):
        return self._parsed().__len__()
    
    def __str__(self):
        #if (self.__str is None):
        #    try:
        #        self.__str = self.to_string();
        #    except Exception as e:
        #        self.__str = self.httpresponse.text;
        #        logger.debug('Exception in __str__: %s' % (e))
        return str(self._parsed());
    
    def _parsed(self):
        if (self.__parsed is None):
            self._parse()
        return self.__parsed
    
    def _parse(self):
        content_type = self.httpresponse.headers.get('Content-Type')
        
        if (content_type is not None):
            if (content_type.lower() == 'text/csv'):
                self._parse_csv()
            elif (content_type.lower() == 'text/tsv'):
                self._parse_tsv()
            elif (content_type.lower() == 'application/json'):
                self._parse_json()
            else:
                self._parse_unknown()
        else:
            self._parse_unknown()
    
    def _parse_csv(self):
        self.__parsed = ParsedCsvResult(self.httpresponse.text, ',')
    
    def _parse_tsv(self):
        self.__parsed = ParsedCsvResult(self.httpresponse.text, '\t')
        
    def _parse_json(self):
        self.__parsed = ParsedJsonResult(self.httpresponse.text)
    
    def _parse_unknown(self):
        self.__parsed = self.httpresponse.text
        
    @property
    def text(self):
        return self.httpresponse.text
    
    @property
    def results(self):
        return self._parsed().results
        
    @property
    def stats(self):
        if (self._stats is None):
            self._stats = clarus.api.getStats(self.httpresponse)
        return self._stats
    
    @property
    def total(self):
        if ("GridTotal" in self.stats):
            return float(self.stats.get("GridTotal"))
        return None
    
    @property
    def warnings(self):
        return clarus.api.getWarnings(self.httpresponse)
    
    @property
    def request_time(self):
        return clarus.api.getRequestTime(self.httpresponse)
    
    def pivot(self, rowAxis='Currency', colAxis='SubType', ccy='USD', view='Latest', output=None):
        httpresp = clarus.api.pivot(self.httpresponse, rowAxis, colAxis, ccy, view, output)
        if (httpresp.status_code!=200):
            raise ApiError(httpresp)
        else:
            return ApiResponse(httpresp);

    def drilldown(self, row='Total', col='Total', view='Default', output=None):
        httpresp = clarus.api.drilldown(self.httpresponse, row, col, view, output)
        if (httpresp.status_code!=200):
            raise ApiError(httpresp)
        else:
            return ApiResponse(httpresp);
        
    def to_string(self):
        return clarus.api.toString(self.httpresponse);
    
    def is_grid(self):
        g = self.stats.get("IsGrid")
        return g == "Yes"
    
    def get_value(self, row, col):
        return self._parsed().get_value(row, col, self.is_grid())
    
    def get_row_headers(self):
        return self._parsed().get_row_headers(self.is_grid())
    
    def get_col_headers(self):
        return self._parsed().get_col_headers(self.is_grid())
    
class ParsedJsonResult(dict):
    def __init__(self, jsontext):
        super(ParsedJsonResult, self).__init__(json.loads(jsontext))
    
    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)
    
    @property
    def results(self):
        return self.get('results')
    
    def get_value(self, r, c, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        if (r not in self.results):
            raise ValueError('No row {} found'.format(r))
        
        row = self.results.get(r)
        
        if (c not in row):
             raise ValueError('No column {} found'.format(c))
         
        return row.get(c)
        
    def get_row_headers(self, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        return list(self.results.keys())
    
    def get_col_headers(self, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        first_r = next(iter(self.results)) #first row header
        first_row = self.results.get(first_r)
        
        return list(first_row.keys())
        
class ParsedCsvResult(Mapping):
    headers = None #array of headers
    valdict = None #dictionary of header -> list of values
    widthdict = None #dictionary of header -> max column width
    maxrow = 0

    def __init__(self, csvtext, delimiter):
        self.valdict = OrderedDict() #dictionary of header -> list of values
        self.widthdict = defaultdict(int) #dictionary of header -> max column width
        
        reader = csv.reader(StringIO(csvtext), delimiter=delimiter)
        for r, row in enumerate(reader):
            self.maxrow = r
            if (r == 0):
                self.headers = row
                for header in self.headers:
                    self.valdict[header] = []
                    self.widthdict[header] = len(header)
            else:
                if (len(row) > len(self.headers)):
                    raise ValueError('Malformed csv at line {}: actual column count {} exceeds expected count {}'.format(r, len(row), len(headers)))
                for c, col in enumerate(row):
                    header = self.headers[c]
                    self.valdict[header].append(col)
                    self.widthdict[header] = max(self.widthdict[header], len(col))    
    
    @property
    def results(self):
        return self.valdict
    
    def __getitem__(self, name):
        return self.valdict.__getitem__(name)

    def __iter__(self):
        return self.valdict.__iter__()
    
    def __len__(self):
        return self.valdict.__len__()
        
    def get_value(self, r, c, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        if (c not in self.valdict):
            raise ValueError('No column {} found'.format(c))
        
        first_c = next(iter(self.valdict)) #first column header
        first_col = self.valdict.get(first_c)
        
        if (r not in first_col):
            raise ValueError('No row {} found'.format(r))
        
        row_idx  = first_col.index(r)
        
        col = self.valdict.get(c)
        
        return col[row_idx]
    
    def get_col_headers(self, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        return list(self.valdict.keys())[1:]
        
    def get_row_headers(self, isGrid):
        if (not isGrid):
            raise AttributeError('This operation is only supported on grid-like results')
        
        first_c = next(iter(self.valdict)) #first column header
        first_col = self.valdict.get(first_c)
        
        return first_col
    
    def __str__(self):
        def pad(c, header, text):
            if (c == 0):
                width = self.widthdict[header] + 1
                return '{x: <{fill}}'.format(x=text, fill=width)
            else:
                width = self.widthdict[header] + 4
                return '{x: >{fill}}'.format(x=text, fill=width)
        
        pp = StringIO()
        #write first line
        for c, header in enumerate(self.headers):
            padded = pad(c, header, header)
            pp.write(padded)
        pp.write('\n')
        
        for r in range(0, self.maxrow):
            for c, header in enumerate(self.headers):
                col = self.valdict[header][r]
                padded = pad(c, header, col)
                pp.write(padded)
            pp.write('\n')
            
        return pp.getvalue()    
    
class ApiError(Exception):
    httpresponse = None
    
    def __init__(self, httpresponse):
        super(ApiError, self).__init__('{} [code {}]'.format(httpresponse.text, httpresponse.status_code))
        
        self.httpresponse = httpresponse
    