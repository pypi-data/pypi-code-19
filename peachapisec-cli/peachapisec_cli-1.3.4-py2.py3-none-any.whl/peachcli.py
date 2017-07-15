#!/usr/bin/env python
from __future__ import print_function

'''
Copyright (c) 2017 Peach Fuzzer, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

"""
Peach API Security CLI

This tool is used to control multiple Peach instances at once.
The tool can be used via the command line or as an interactive
tool.

Installation:

  Installation of this tool has two steps.
  
  1. Install Python 2.7
  2. Install dependencies

	pip install -r requirements.txt
  
  3. Start using the tool

Syntax:

  peachcli

"""

try:
	import click
	import peachapisec
except:
	print("Error, missing dependencies.")
	print("Use 'pip install -r requirements.txt'")
	exit(-1)

import os
import json

@click.group(help="Command line interface for Peach API Security.")
@click.option("--api", help="Peach API Security API URL. Defaults to PEACH_API environ.")
@click.option("--api_token", help="Peach API Security API Token. Defaults to PEACH_API_TOKEN environ.")
@click.pass_context
def cli(ctx, api, api_token, **kwargs):

	if not api:
		print("Error, set PEACH_API or provide --api argument")
		exit(1)

	if not api_token:
		print("Error, set PEACH_API_TOKEN or provide --api argument")
		exit(1)

	ctx.obj['API'] = api
	ctx.obj['API_TOKEN'] = api_token

	os.environ['PEACH_API'] = api
	os.environ['PEACH_API_TOKEN'] = api_token

	peachapisec.set_peach_api(api)
	peachapisec.set_peach_api_token(api_token)

@cli.command(help="List all jobs")
def jobs(**kwargs):
	jobs_list = peachapisec.get_jobs()
	print(json.dumps(jobs_list, sort_keys=True, indent=4, separators=(',', ': ')))

@cli.command(help="Stop all running jobs")
def stopall(**kwargs):
	click.echo("Stoping all running jobs...")

	jobs_list = peachapisec.get_jobs()
	stop_cnt = 0

	for job in jobs_list:
		if not (job['State'] in ['Error', 'Running']):
			continue
		
		try:
			peachapisec.stop_job(job['Id'])
			stop_cnt += 1
		except:
			pass
	else:
		click.echo("Stopped %s jobs." % str(stop_cnt))

@cli.command(help="Stop a running job")
@click.argument('id')
def stop(id, **kwargs):

	if not id:
		print("Syntax error, must provide job id")
		exit(1)
	
	peachapisec.stop_job(id)

@cli.command(help="Generate JUnit XML output")
@click.argument('id')
@click.argument('output', type=click.File('wb'))
def junitxml(id, output, **kwargs):

	if not id:
		print("Syntax error, must provide job id")
		exit(1)
	
	if not output:
		print("Syntax error, must provide valid output filename")
		exit(1)

	peachapisec.set_session_id(id)
	junit = peachapisec.junit_xml()

	output.write(junit.encode('utf-8'))
	output.close()
	print(junit)

@cli.command(help="Mark a point in the job history")
def mark(**kwargs):
	jobs_list = peachapisec.get_jobs()
	
	id = jobs_list[0]["Id"]
	print("Marking at job id '%s'" % id)

	with open("checklastjob.mark", "w") as fd:
		fd.write(id)

@cli.command(help="Verify a new job completed with N failures")
@click.argument('count')
def verify(count, **kwargs):

	if not os.path.isfile("checklastjob.mark"):
		print("Error, no mark file found.  Run the 'mark' command first!")
		exit(1)

	with open("checklastjob.mark", "r") as fd:
		id = fd.read()
		try:
			# only works in py3
			id = id.decode("utf-8")
		except:
			pass

	jobs_list = peachapisec.get_jobs()
	stop_cnt = 0

	job = jobs_list[0]

	if job["Id"] == id:
		print("Error, no new job found")
		exit(1)

	if not (job["State"] == "Finished"):
		print("Error, job state was '%s'" % job["State"])
		exit(1)

	if not(int(job['FaultCount']) == int(count)):
		print("Error, fault count missmatch, got %d, expected %d." % (int(job['FaultCount']), int(count)))
		exit(1)

	print("Pass, found expected %d failures" % int(count))

def run():
	'''Start Peach CLI
	'''
	cli(obj={}, auto_envvar_prefix='PEACH')

if __name__ == '__main__':
	run()

# end
