import pandas as pd
import MySQLdb
import json

#/Users/yanyunliu/PycharmProjects/CourseraCrawl/DiscussionForumJava/DataExtraction
#/Users/yanyunliu/PycharmProjects/CourseraCrawl/DataExtraction/ExtractionTool/DataExtractionTool.py

def MySQLConnector(your_host, your_username, your_password,your_database):

	conn = MySQLdb.connect(host = your_host,user = your_username,passwd = your_password)
	cursor = conn.cursor()

	initial_sql = "use " + your_database 

	cursor.execute(initial_sql)

	return cursor

def CheckJsonObject(your_object):

	try:
		your_object = json.loads(your_object.decode('string-escape').strip('"'))
		your_object = your_object
	except:
		your_object =  False

	return your_object

def SQLExecuter(sql, col_list,cursor, condition = '', hasjsonfield = "", tocsv_pathname = ''):

	#print sql

	if condition == "" or condition == []:
		cursor.execute(sql)
		#print sql
	elif isinstance(condition,list) and len(condition)>0:
		#print sql

		in_ids = ', '.join(map(lambda x: '%s', condition))
		sql = sql % in_ids

		#print sql
		cursor.execute(sql,condition)
	else:
		print "Wrong condition type!"

	cc = cursor.fetchall()

	if hasjsonfield:

		new_list = []
		key_col = []

		for item in cc[:]:

			new_item = {}

			for sub_item in item:

				#print sub_item

				dict_json = CheckJsonObject(sub_item)

				#print dict_json

				if isinstance(dict_json, dict):
					new_item.update(dict_json)
				else:
					new_item[col_list[item.index(sub_item)]]=sub_item

			new_list.append(new_item)

			if len(new_item.keys())>len(key_col):
				key_col = new_item.keys()


		output_pd = pd.DataFrame.from_records(new_list,columns = key_col)

	else:
		output_pd = pd.DataFrame.from_records(list(cc),columns = col_list)

		
	# elif not hasjsonfield:
	# 	output_pd = pd.DataFrame.from_records(cc,columns = col_list)



	if tocsv_pathname != "":
		output_pd.to_csv(tocsv_pathname,header = col_list)


	return output_pd