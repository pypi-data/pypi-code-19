#! /usr/bin/env python

import sys
import json
import click
import logging
import requests

log = logging.getLogger(__name__)

from snfilter import parse_nameslist, filter_feed, output_json, output_truvu, output_gr

@click.group()
def cli():
    pass

@cli.command()
@click.option("--url", default="http://www.spotternetwork.org/feeds/gr.txt", help="SN Feed to pull")
@click.option("--filename", default="grfeed.txt")
def pull(url, filename):
    r = requests.get(url)
    if r.ok:
        log.debug("successfully requested %s", url)
        f = open(filename, "w")
        f.write(r.text)
        f.close()
    else:
        log.error("Request for %s failed.", url)

@cli.command()
@click.option("--inputfile", default="grfeed.txt", help="file containing the sn gr feed to parse")
@click.option("--nameslist", default="kf5uxa:Matt Dipirro,Daniel Shaw,W5ZFQ:Andrew", help="list of names to include in the filtered output")
@click.option("--outputfile", default=None, help="file to output to, otherwise stdout")
@click.option("--indent", default=None, help="indentation level, when json output")
@click.option("--outputformat", default="gr", help="output format, default is gr, can also be truvu or json")
@click.option("--filtername", default="snfilter", help="set the feed name in gibson ridge output")
def filter(inputfile, nameslist, outputfile, indent, outputformat, filtername):
    filtered_objects = None
    if indent is not None:
        indent = int(indent)
    with open(inputfile, "r") as f:
        d = "".join([ l for l in f.readlines() ])
        names, xlator = parse_nameslist(nameslist)
        filtered_objects = filter_feed(d, names, translator=xlator)
    output = ""
    if outputformat == "json":
        output = output_json(filtered_objects, indent=indent)
    elif outputformat == "truvu":
        output = output_truvu(filtered_objects)
    elif outputformat == "gr":
        output = output_gr(filtered_objects, filtername=filtername)

    if outputfile:
        with open(outputfile, "w") as f:
            f.write(output)
    else:
        click.echo(output)
