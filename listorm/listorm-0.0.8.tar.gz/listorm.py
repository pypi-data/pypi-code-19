from itertools import chain, groupby, tee
from operator import itemgetter
from heapq import nlargest, nsmallest
from io import BytesIO, StringIO
from collections import namedtuple, Counter, OrderedDict, defaultdict
import csv

import xlrd, xlsxwriter



def str2float(value):
	try:
		ret = float(value)
	except:
		return value
	else:
		return ret


def round_try(value, round_to=2):
	try:
		if not isinstance(value, int):
			r = float(value)
		r = value
	except:
		return value
	else:
		return round(r, round_to)



class Scheme(dict):

	__getattr__ = dict.get

	def __init__(self, *args, **kwargs):
		return super(Scheme, self).__init__(*args, **kwargs)

	def __add__(self, other):
		cp = Scheme(self)
		for k in cp.keys() & other.keys():
			other[k] = cp[k] or other[k]
		cp.update(other)
		return cp
		
	def __iadd__(self, other):
		self = self + other
		return self

	def __sub__(self, other):
		keys = self.keys() - other.keys()
		return Scheme({k:self[k] for k in keys})

	def __isub__(self, other):
		self =self-other
		return self

	def _filter_invalid_keys(self, *keys):
		return (k for k in keys if k in self)

	def select(self, *keys, values=True):
		keys = self._filter_invalid_keys(*keys)
		return tuple(self[key] for key in keys) if values else {key:self[key] for key in keys}

	def delete(self, *keys):
		for key in keys:
			if key in self:
				self.pop(key)
		return self

	def rename(self, **key_map):
		for key in self:
			for ori, new in key_map.items():
				if ori in self:
					value = self.pop(ori)
					self[new]=value
		return self

	def row_update(self, apply_to_record=True, insert_new=False, **key_apply_set):
		for key, func in key_apply_set.items():
			if key in self or insert_new:
				try:
					updated = func(self) if apply_to_record  else func(self[key])
				except:
					continue
				else:
					self[key] = updated
		return self

	def set_index(self, *keys, index_name=None):
		keys = self._filter_invalid_keys(*keys)
		self[index_name] = tuple(self[k] for k in keys)
		return index_name


	def number_format(self, **key_examples):

		for key, format_example in key_examples.items():
			fmtfunc = type(format_example)
			val_ori = self.get(key)
			try:
				val_formated = fmtfunc(val_ori)
			except:
				val_ori = str2float(self.get(key))
				try:
					val_formated = fmtfunc(val_ori)
				except:
					val_formated = format_example
			finally:
				if key in self:
					self[key] = val_formated
		return self



class Listorm(list):

	def __init__(self, records=None, index=None, nomalize=True, column_orders=None):
		self.column_orders = column_orders
		to_normalize, to_init = tee(records or [])
		if nomalize:
			uni_keys = self._union_keys(to_normalize)
		records = (Scheme.fromkeys(uni_keys)+Scheme(record) if nomalize else Scheme(record) for record in to_init if record)
		super(Listorm, self).__init__(records)
		if index:
			self.set_index(*index)

	def __add__(self, other):
		return Listorm(super(Listorm, self).__add__(other))

	def __iadd__(self, other):
		return self + other

	def _union_keys(self, records):
		return set(chain(*(record.keys() for record in records)))

	def _is_valid(self, row_value):
		if row_value and isinstance(row_value, dict):
			return True
		return False

	def append(self, row_value, sync_new=True):
		if self._is_valid(row_value):
			new_record = Scheme(row_value)
			if self:
				enough = new_record.keys() - self[-1].keys()
				deficiency = self[-1].keys() - new_record.keys()
				if enough:
					if sync_new:
						for record in self:
							for key in enough:
								record[key] = None
					else:
						new_record.delete(*enough)
				for key in deficiency:
					new_record[key] = None
			super(Listorm, self).append(new_record)

	def filter(self, where=lambda row: True):
		'''filtering by func apply to each record
		   lst.filter(where = lambda row:row['price'] > 500)
		'''
		return Listorm((record for record in self if where(record)), nomalize=False)

	def select(self, *args, values=False):
		'''select columns if you need
		   lst.select('A', 'B', 'c')
		   values: True, then returns 2dArray that only contains values
		'''
		records = (record.select(*args, values=values) for record in self)
		return list(records) if values else Listorm(records, nomalize=False)

	def row_values(self, *args, headers=False):
		'''returns 2dArray contains only value of self
		'''
		header = [list(args)] if headers else []
		return header+[[record[k] for k in args] for record in self.select(*args)]

	def column_values(self, column):
		'''Get virtical Values in List by column name
		'''
		return [record.get(column) for record in self]

	def orderby(self, *rules):
		'''lst.orderby('A', '-B') orderby A asc B desc
		'''
		for rule in reversed(rules):
			rvs = rule.startswith('-')
			rule = rule.strip('-')
			super().sort(key=lambda x: x[rule], reverse=rvs)
		return self

	def distinct(self, *column, eliminate=False):
		'''remove duplicate by columns
		   lst.distinct('A', 'B', 'C')
		'''
		ret = []
		for g, l in groupby(sorted(self, key=itemgetter(*column)), key=itemgetter(*column)):
			head, *body = l
			if eliminate and body:
				continue
			else:
				ret.append(head)
		return Listorm(ret, nomalize=False, column_orders=self.column_orders)

	def groupby(self, *columns, extra_columns=None, renames=None, agg_float_round=2, **aggset):
		'''groupby('location', 'gender',
				extra_columns = ['age', 'phone'], # Any one Extra Value in Grouped, not recomanded
				gender=len, age=sum, # aggregate targets column and apply functions
				renames = {'gender': 'gender_count', 'age': 'age_sum'}  # prevent for overwriting of result column to original column
				agg_float_round: column's rounding point that applied by aggregate function
				when aggregation colunm overlaped with grouped columns name
			)
		'''
		grouped = defaultdict(Listorm)
		renames = renames or {}
		ret_columns = list(chain(columns, extra_columns or [], aggset, renames.values()))

		for record in self:
			g = tuple(record.get(key) for key in columns)
			grouped[g].append(record)

		ret = Listorm()
		for g, lst in grouped.items():
			head = lst[0]
			for column, aggfn in aggset.items():
				head[renames.get(column, column)] = round_try(lst.apply_column(column, aggfn), round_to=agg_float_round)
			ret.append(head, sync_new=False)
		return ret.select(*ret_columns)

	def set_number_type(self, **key_examples):
		'''set_number_format(A=0.0, B=0, C='0'), change number type to default value(if failed, example values are applied to default)
			A: '123' => 123.0, B: 123.2 => 123, C: 123.1 => '123.1' 
		'''
		records = map(lambda record: record.number_format(**key_examples), self)
		return Listorm(records, nomalize=False)

	def apply_row(self, **key_func_to_records):
		'''Function For one record
		'''
		records = map(lambda record: record.row_update(**key_func_to_records), self)
		return Listorm(records, nomalize=False)

	def apply_column(self, column, func=lambda col:col):
		values = [e[0] for e in self.row_values(column)]
		return func(values)

	def map(self, **key_values):
		'''Function for one value in record
		   map(A=lambda val: value_map.get(val, val))
		'''
		return self.apply_row(apply_to_record=False, **key_values)

	def rename(self, **key_map):
		'''change Columns name
		   lst.rename({'OriginCol': 'ChangedCol', 'OriginCol2': 'ChangedCol2'})
		'''
		records = map(lambda record: record.rename(**key_map), self)
		return Listorm(records, nomalize=False)

	def add_columns(self, **kwargs):
		'''adding columns in current scheme by related funcion with neighborhood in record
		   lst.add_columns(C=lambda row: row['A'] -  row['B'], B=lambda row: row['C']*row['D'])
		'''
		records = map(lambda record: record.row_update(insert_new=True, **kwargs), self)
		return Listorm(records)

	def top(self, *by, n=10):
		'''get top n record in current List, if 0<n<1, then n apply as percentage
		   lst.top('age', 1) => returns a oldest peple's record
		   lst.top('sellary', 0.1) => returns top 10% sellary's records in List
		'''
		index = round(len(self) * n) if n < 1 else n
		return nlargest(index, self, key=itemgetter(*by))

	def bottom(self, *by, n=10):
		'''get bottom n record in current List, if 0<n<1, then n apply as percentage
		   lst.bottom('age', 1) => returns a youngest peple's record
		   lst.bottom('sellary', 0.1) => returns bottom 10% sellary's records in List
		'''
		index = round(len(self) * n) if n < 1 else n
		return nsmallest(index, self, key=itemgetter(*by))

	def value_count(self, column):
		'''returns a Column's value count
		'''
		return Counter(row[column] for row in self)

	def unique(self, column):
		'''get column's unique values
		'''
		return set(self.apply_column(column))

	def set_index(self, *column, index_name='__index__'):
		'''set Index each record by column values
		   lst.set_index('A', 'B', 'C')
		'''
		for record in self:
			index = record.set_index(*column, index_name=index_name)
		return index_name

	def join(self, other, **kwargs):
		''' Join With two Listorm
		  	join(lst1, lst2, on='name', how='inner')
			how: 'inner'|'left'| 'right'|'outer'
		'''
		return join(self, other, **kwargs)

	def to_excel(self, filename=None, selects=None):
		'''If filnames is None, returns filecontents
		'''
		if not self:
			return
		selects =  selects or self[0].keys()

		error_columns = set(selects) - self[0].keys()
		for col in error_columns:
			selects.remove(col)

		output = BytesIO()
		wb = xlsxwriter.Workbook(output)
		ws = wb.add_worksheet()
		ws.write_row(0,0, selects)
		for r, row in enumerate(self, 1):
			row_values = [row[k] for k in selects]
			ws.write_row(r,0, row_values)
		wb.close()
		if filename:
			with open(filename, 'wb') as fp:
				fp.write(output.getvalue())
		else:
			return output.getvalue()

	def to_csv(self, filename=None, selects=None):
		if not self:
			return

		selects =  selects or self[0].keys()

		error_columns = set(selects) - self[0].keys()
		for col in error_columns:
			selects.remove(col)

		output = StringIO()
		writer = csv.DictWriter(output, fieldnames = selects, lineterminator='\n')
		writer.writeheader()
		for row in self:
			row_values = OrderedDict((k, row[k]) for k in selects)
			writer.writerow(row_values)

		if filename:
			with open(filename, 'w') as fp:
				fp.write(output.getvalue())
		else:
			return output.getvalue()

	def get_changes(self, other, pk):
		'''Comparison both Lists that has common keys
			lst.get_changes(recs2, pk='primaryKey') 
			pk: primarykey for both Lists
		'''
		if not other:
			return
			
		other = Listorm(other)

		common_keys = self[0].keys() & other[0].keys()

		if not common_keys:
			raise ValueError('Other Listorm Object has no common keys with this')

		if pk not in common_keys:
			raise ValueError('Index must exist in both!')

		origin_select = self.select(*common_keys)
		target_select = other.select(*common_keys)

		origin, target = {row[pk]: row for row in origin_select}, {row[pk]: row for row in target_select}

		missing_keys = origin.keys() - target.keys()
		extra_keys = target.keys() - origin.keys()
		common_keys = origin.keys() & target.keys()
		
		added, deleted, updated = [], [], []

		Added = namedtuple('Added', 'pk rows')
		Deleted = namedtuple('Deleted', 'pk rows')
		Updated = namedtuple('Updated', 'pk before after where')

		for key in extra_keys:
			added.append(Added(key, target[key]))

		for key in missing_keys:
			deleted.append(Deleted(key, origin[key]))

		for key in common_keys:
			diff = origin[key].items() ^ target[key].items()
			if diff:
				updated.append(Updated(key, origin[key], target[key], list(dict(diff))))

		Changes = namedtuple('Changes', 'added deleted updated')
		return Changes(added, deleted, updated)



def join(left, right, left_on=None, right_on=None, on=None, how='inner'):
	'''Join With two Listorm
		join(lst1, lst2, on='name', how='inner')
		join(lst1, lst2, left_on='name', right_on='name' how='inner')
		on: if both index names are same else each index names are needed at left_on, right_on
		how: 'inner'|'left'|'right'|'outer'
	'''

	if not (left_on and right_on or on):
		return

	left_on_index, right_on_index = defaultdict(list), defaultdict(list)

	left = Listorm(left)
	right = Listorm(right)

	for record in left:
		key = record.get(left_on or on)
		left_on_index[key].append(record)

	for record in right:
		key = record.get(right_on or on)
		right_on_index[key].append(record)

	ret = []
	
	if how == 'left':
		index_on = left_on_index.keys()
	elif how=='right':
		index_on = right_on_index.keys()
	elif how=='outer':
		index_on = left_on_index.keys() | right_on_index.keys()
	else:
		index_on = left_on_index.keys() & right_on_index.keys()

	for index in index_on:
		left_scheme = Scheme.fromkeys(left[0])
		right_scheme = Scheme.fromkeys(right[0])
		left_list = left_on_index.get(index, [left_scheme])
		rights_list = right_on_index.get(index, [right_scheme])
		
		for left_record in left_list:
			for right_record in rights_list:
				row = left_record+right_record
				ret.append(row)
	return Listorm(ret)


def read_excel(file_name=None, file_contents=None, sheet_index=0, start_row=0, index=None):
	'''Excel File or byte Content of Excel to Listorm object
	'''
	wb = xlrd.open_workbook(filename=file_name, file_contents=file_contents)
	ws = wb.sheet_by_index(sheet_index)
	fields = ws.row_values(start_row)
	records = [dict(zip(fields, map(str, ws.row_values(r)))) for r in range(start_row+1, ws.nrows)]
	return Listorm(records, index=index, column_orders=fields)


def read_csv(filename=None, encoding='utf-8',  fp=None, index=None):
	'''CSV file or filepointer of CSV to Listorm object
	'''
	csvfp = None
	if filename:
		csvfp = open(filename, encoding=encoding)
	elif fp:
		csvfp = fp
	else:
		return
	csv_reader = csv.reader(csvfp)
	fields = next(csv_reader)
	records = [dict(zip(fields, map(str, row))) for row in csv_reader]
	csvfp.close()
	return Listorm(records, index=index, column_orders=fields)
