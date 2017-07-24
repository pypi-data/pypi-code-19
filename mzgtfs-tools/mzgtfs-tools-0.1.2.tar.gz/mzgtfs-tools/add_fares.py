#!/usr/bin/python

"""
Takes in a JSON file in the following format:

{
    "fare_id" : {

        "fare_attributes" : {
            "price" : "2.75",
            "currency_type" : "USD",
            "payment_method" : 0|1,
            "transfers" : 0|1|2 (optional),
            "transfer_duration" : (seconds)
        },
        "fare_rules" : {
            // the following are in order of precedence
            // that is, the first key of route_* is the only one used
            "route_id" : ..., // or
            "route_ids" : [], // or
            "route_regex" : '.' // '.' is the wildcard
        }
    }
}
Fare IDs are processed in order, if multiple fares are added, they are added in order of precedence.
For example, special fares with regexes or lists of routes to be processed should go before the wildcard.

Setting fares by origin / destination is not explicitly supported or tested at the moment.

refer to GTFS spec fare_attributes.txt and fare_rules.txt for more information
"""
import re
import json
import shutil
import mzgtfs.feed
import util

ROUTES_WITH_FARES = set()

def add_fare_id(feed, fare_id, rules_attributes):
    """ take in fare_id, rules, and attributes
    add to one or more routes based upon rules"""

    routes = []
    attributes = rules_attributes['fare_attributes']
    rules = rules_attributes['fare_rules']

    if 'route_id' in rules:
        routes.append(rules['route_id'])

    elif 'route_ids' in rules:
        route_ids = rules['route_ids']
        if not isinstance(route_ids, list):
            raise TypeError('route_ids should be a list')
        routes.extend(route_ids)

    elif 'route_regex' in rules:
        print " processing regex " + rules['route_regex']
        regex = rules['route_regex']
        for r in feed.iterread('routes'):
            if re.match(regex, r.id()) is not None:
                routes.append(r.id())

    add_attribute(feed, fare_id, attributes)

    #remove route information from the rules dict.
    #forgive me for the non-pythonic design
    for k in rules.keys():
        if "route" in k:
            del rules[k]

    for route in routes:
        if route in ROUTES_WITH_FARES:
            print route + " already has a fare, skipping"
            continue

        add_rule_to_route(feed, fare_id, route, rules)
        ROUTES_WITH_FARES.add(route)

def add_attribute(feed, fare_id, attributes):
    """ add a fare_attribute to fare_id
    Per the spec, standard fields to go into attribute are:
            "price" : "2.75",
            "currency_type" : "USD",
            "payment_method" : 0|1, (on board, off-board)
            "transfers" : 0|1|2 (optional, unlimited if null and duration is set),
            "transfer_duration" : (optional, seconds)
    """
    if 'fare_attributes' not in feed.by_id:
        feed.by_id['fare_attributes'] = {}

    print "adding fare " + fare_id + " to feed"
    factory = feed.FACTORIES['fare_attributes']
    attributes['fare_id'] = fare_id
    fare_attribute = factory.from_row(attributes)
    feed.by_id['fare_attributes'][fare_id] = fare_attribute

def add_rule_to_route(feed, fare_id, route_id, rules=None):
    """
    add fare_id and an optional dict of rules to route_id
    additional rules (origin_id, desination_id, contains_id) are not supported/tested.
    """

    infostring = "adding fare " + fare_id + " to " + route_id

    if not rules:
        rules = {}
    else:
        infostring += str(repr(rules))

    rules['fare_id'] = fare_id
    rules['route_id'] = route_id

    print infostring

    if 'fare_rules' not in feed.by_id:
        feed.by_id['fare_rules'] = {}

    factory = feed.FACTORIES['fare_rules']
    info = factory.from_row(rules)
    feed.by_id['fare_rules'][route_id] = info

def main(gtfs_file, input_json_file):
    """ load gtfs_file and instructions from JSON"""

    with open(input_json_file) as jsonfile:
        input_json = json.load(jsonfile)

    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)

    for fare_id, rules_attributes in input_json.iteritems():
        add_fare_id(gtfs_feed, fare_id, rules_attributes)

    files = ['fare_attributes.txt', 'fare_rules.txt']
    gtfs_feed.write('fare_attributes.txt', gtfs_feed.fares())
    gtfs_feed.write('fare_rules.txt', gtfs_feed.fare_rules())

    gtfs_feed.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)

    util.delete_temp_files(files)

if __name__ == "__main__":
    import plac
    plac.call(main)
