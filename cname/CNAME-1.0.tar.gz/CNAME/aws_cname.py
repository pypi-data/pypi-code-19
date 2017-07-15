#!/usr/bin/env python
import json
import subprocess
import argparse
import logging
import sys
import requests
import json
import csv
import re
JSONPFILE="cname.json"
CSVOPFILE="cname.csv"
HTMLOPFILE="cname.html"
VERSION=""
JSON_DATA=""
def msg(name=None):
        return "python "+ sys.argv[0]
parser= argparse.ArgumentParser(description="""This script gets the CNAMES list from AWS uploads it into confluence page- AWS Route 53 CNAME.\n
        CNAMES which points to only controllers are filtered out and sorted. \n
	You can use either AWS 'CLI' or AWS 'Boto'. \n
        Here AWS CLI is used and assumed already configured before running this script. \n
        For installation follow the link: http://docs.aws.amazon.com/cli/latest/userguide/installing.html \n
        For configuration follow below link : http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html""",usage=msg(), formatter_class=argparse.RawTextHelpFormatter)
args=parser.parse_args() # parse the arguments
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(sys.argv[0])
def key(object):
	return object[0]
def main():
        with open (JSONPFILE, 'r+') as json_file:
		try:
                	logger.info("Fetching CNAME records from AWS SAAS account. This may take few minutes.")
                	proc=subprocess.Popen(['aws','route53','list-resource-record-sets','--hosted-zone-id','XXXXXXXXXXX','--query',' ResourceRecordSets'],stdout=json_file)
			proc.wait()
		
		
        	except Exception, e:
                	logger.critical("Error msg: %s ",str(e))
                	sys.exit(1)
		json_file.seek(0,0)
		JSON_DATA = json.load(json_file)
        logger.info("Fetching data succesful.") 
	logger.info("Proceeding data scrubbing.")
	with open(CSVOPFILE, 'w') as file:
                for data in JSON_DATA:
                	if data['Type'] == 'CNAME' and re.search('PAID', data['ResourceRecords'][0]['Value'], re.IGNORECASE):
                        	file.write(data['ResourceRecords'][0]['Value']+","+data['Name']+"\n")
	data = csv.reader(open(CSVOPFILE),delimiter=',')
        sortedlist = sorted(data, key=key)
        with open("CSVSORTFILE.csv", "wb") as f:
                fileWriter = csv.writer(f, delimiter=',')
                for row in sortedlist:
                        fileWriter.writerow(row)
        with open("CSVSORTFILE.csv") as f:
		text = f.read()
        with open("CSVSORTFILE.csv",'w') as f:
        	f.write("CNAME,Name"+"\n")
        	f.write(text)
        logger.info("Updating confluence page: https://CONFURL/AWS+Route+53+CNAME")
        conf_page_update()
        logger.info("Finish updating records")
def conf_page_update():
        reader = csv.reader(open("CSVSORTFILE.csv"))
        f_html = open(HTMLOPFILE,"w")
        f_html.write('<b><strong><u><title>CNAME from SAAS AWS Account: </title></u></strong></b>Sorted with CNAME')
        f_html.write('<br></br>')
        f_html.write('<table>')

        for row in reader: # Read a single row from the CSV file
                f_html.write('<tr>');# Create a new row in the table
                for column in row: # For each column..
                        f_html.write('<td>' + column + '</td>')
                f_html.write('</tr>')

        f_html.write('</table>')
        f_html = open(HTMLOPFILE,"r")
        data=f_html.read()
        url = 'https://CONFURL/wiki/rest/api/content/CONFPAGEID'
        headers = {'Content-Type': 'application/json'}
        req = requests.get(url,headers=headers, auth=('CONFUSERNAME', 'CONFPASSWORD'))
        temp_var = json.loads(req.text)
        VERSION=int(temp_var['version']['number'])+1
        data = {"id":"CONFPAGEID","type":"page","title":"AWS Route 53 CNAME","space":{"key":"OPS"},"body":{"storage":{"value":data,"representation":"storage"}},"version":{"number":VERSION}}
        req = requests.put(url, data=json.dumps(data), headers=headers, auth=('CONFUSERNAME', 'CONFPASSWORD'))




if __name__ == "__main__":
        main()
