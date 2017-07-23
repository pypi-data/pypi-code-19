from itertools import chain, groupby, tee
from operator import itemgetter
from heapq import nlargest, nsmallest
from io import BytesIO, StringIO
import csv

import xlrd, xlsxwriter



def str2float(value):
	try:
		ret = float(value)
	except:
		return value
	else:
		return ret


def round_if(value, round_to=2):
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
		self.update(other)
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
					print('faile')
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

	def __init__(self, records, index=None, nomalize=True):
		to_normalize, to_init = tee(records)
		if nomalize:
			uni_keys = self._union_keys(to_normalize)
		records = (Scheme.fromkeys(uni_keys)+Scheme(record) if nomalize else Scheme(record) for record in to_init)
		super(Listorm, self).__init__(records)
		if index:
			self.set_index(*index)

	def _union_keys(self, records):
		return set(chain(*(record.keys() for record in records)))

	def filter(self, where=lambda row: True):
		return Listorm((record for record in self if where(record)), nomalize=False)

	def select(self, *args, values=False):
		records = (record.select(*args, values=values) for record in self)
		return list(records) if values else Listorm(records, nomalize=False)

	def row_values(self, *args, headers=False):
		header = [list(args)] if headers else []
		return header+[[record[k] for k in args] for record in self.select(*args)]

	def column_values(self, column):
		return [record.get(column) for record in self]

	def sort(self, *rules):
		for rule in reversed(rules):
			rvs = rule.startswith('-')
			rule = rule.strip('-')
			super().sort(key=lambda x: x[rule], reverse=rvs)
		return self

	def distinct(self, *column, eliminate=False):
	
		ret = Listorm([])
		for g, l in groupby(sorted(self, key=itemgetter(*column)), key=itemgetter(*column)):
			head, *body = l
			if eliminate and body:
				continue
			else:
				ret.append(head)
		return ret

	def groupby(self, *column, extra_columns=None, renames=None, **aggset):
		ret = Listorm([])
		renames = renames or {}
		ret_columns = list(chain(column, extra_columns or [], aggset))
		for g, lst in groupby(sorted(self, key=itemgetter(*column)), key=itemgetter(*column)):
			grouped = Listorm(lst, nomalize=False).select(*ret_columns)
			row = grouped[0]
			for colnm, aggfn, in aggset.items():
				row[renames.get(colnm, colnm)] = round_if(grouped.apply_column(colnm, aggfn))
			ret.append(row)
		return ret 

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
		records = map(lambda record: record.rename(**key_map), self)
		return Listorm(records, nomalize=False)

	def add_columns(self, **kwargs):
		records = map(lambda record: record.row_update(insert_new=True, **kwargs), self)
		return Listorm(records)

	def top(self, *by, n=10):
		index = round(len(self) * n) if n < 1 else n
		return nlargest(index, self, key=itemgetter(*by))

	def bottom(self, *by, n=10):
		index = round(len(self) * n) if n < 1 else n
		return nsmallest(index, self, key=itemgetter(*by))

	def unique(self, column):
		return set(self.apply_column(column))

	def set_index(self, *column, index_name='__index__'):
		for record in self:
			index = record.set_index(*column, index_name=index_name)
		return index_name

	def join(self, other, **kwargs):
		''' Join With two Listorm
		  	join(lst1, lst2, common=['name'], how='inner')
			how: ['inner', 'left', 'right', 'outer']
		'''
		return join(self, other, **kwargs)

	def to_excel(self, filename=None):
		'''filename 을 전달하지 않으면 file contents 를 반환
		'''
		if not self:
			return

		output = BytesIO()
		wb = xlsxwriter.Workbook(output)
		ws = wb.add_worksheet()
		ws.write_row(0,0, self[0].keys())
		for r, row in enumerate(self, 1):
			ws.write_row(r,0, row.values())
		wb.close()
		if filename:
			with open(filename, 'wb') as fp:
				fp.write(output.getvalue())
		else:
			return output.getvalue()

	def to_csv(self, filename=None):
		if not self:
			return

		output = StringIO()
		writer = csv.DictWriter(output, fieldnames = self[0].keys(), lineterminator='\n')
		writer.writeheader()
		for row in self:
			writer.writerow(row)

		if filename:
			with open(filename, 'w') as fp:
				fp.write(output.getvalue())
		else:
			return output.getvalue()


def join(left, right, left_on=None, right_on=None, common=None, how='inner'):
	'''Join With two Listorm
		join(lst1, lst2, common=['name'], how='inner')
		how: ['inner', 'left', 'right', 'outer']
	'''
	left = Listorm(left, index=left_on or common)
	right = Listorm(right, index=right_on or common)
	if not left or not right:
		return

	index_name = '__index__'
	
	right_on_index = {index: list(lst) for index, lst in groupby(sorted(right, key=itemgetter(index_name)), key=itemgetter(index_name))}
	left_on_index = {index: list(lst) for index, lst in groupby(sorted(left, key=itemgetter(index_name)), key=itemgetter(index_name))}
	# print(right_on_index)
	ret = Listorm([])
	done_list = set()
	
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
				row.pop(index_name)
				ret.append(row)

	return ret



def read_excel(file_name=None, file_contents=None, sheet_index=0, start_row=0, index=None):
	'''엑셀파일 형태의 데이터 전달 하여 RecordParser 객체 생성 
	'''
	wb = xlrd.open_workbook(filename=file_name, file_contents=file_contents)
	ws = wb.sheet_by_index(sheet_index)
	fields = ws.row_values(start_row)
	records = [dict(zip(fields, map(str, ws.row_values(r)))) for r in range(start_row+1, ws.nrows)]
	return Listorm(records, index=index)


def read_csv(filename=None, encoding='utf-8',  fp=None):
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
	return Listorm(records)
