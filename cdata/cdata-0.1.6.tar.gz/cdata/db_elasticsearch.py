# encoding=utf-8

import logging
import json
import argparse
import os
import sys
from elasticsearch import Elasticsearch


def initIndexTemplate(template_name, template_filename, host='localhost', port=9200):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/2.4/dynamic-templates.html
    https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html
    https://gist.github.com/deverton/2970285
    """

    es = Elasticsearch(["{}:{}".format(host, port)])

    #init template
    template_body = json.load(open(template_filename))
    logging.info(template_name)
    logging.info(template_body)

    ret = es.indices.put_template(template_name, body=template_body)
    logging.info(ret)

def delIndex(es_index, host='localhost', port=9200):
    es = Elasticsearch(["{}:{}".format(host, port)])

    #create index client
    ret = es.indices.delete(index=es_index)
    logging.info(ret)

def insertData(es_index, es_type, id_field, data_filename, host='localhost', port=9200 ):
    """
    https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html
    """
    logging.info("{}:{}".format(host, port))
    es = Elasticsearch(["{}:{}".format(host, port)])

    items = json.load(open('db_elasticsearch.data.json'))
    logging.info(items)

    for item in items:
        ret = es.index(index=es_index, doc_type=es_type, id=item[id_field], body= item)
        logging.info(ret)


if __name__ == "__main__":
    # stop requests print logging
    logging.getLogger("requests").setLevel(logging.WARNING)
    # show logging information
    logging.basicConfig(format='[%(levelname)s][%(module)s][%(funcName)s][%(lineno)s] %(message)s', level=logging.INFO)

    # [] parse input argument
    parser = argparse.ArgumentParser(description="es example")
    parser.add_argument('option', help='option')
    parser.add_argument('--template_name', required=False)
    parser.add_argument('--filename', required=False)
    parser.add_argument('--host', default='localhost', required=False)
    parser.add_argument('--es_index', required=False)
    parser.add_argument('--es_type', required=False)
    parser.add_argument('--id_field', required=False)
    args = parser.parse_args()

    if args.option == "initIndexTemplate":
        initIndexTemplate(args.template_name, args.filename, host=args.host)
    elif args.option == "delIndex":
        delIndex(args.es_index , host=args.host)
    elif args.option == "insertData":
        insertData(args.es_index, args.es_type, args.id_field, args.filename, host=args.host )
    else:
        logging.info("unsupported")

    """
        python scripts/db_elasticsearch.py initIndexTemplate --template_name=suggest2017 --filename=scripts/estemplate.suggest.json
        python scripts/db_elasticsearch.py delIndex --es_index=schemaorg_20170510
        python db_elasticsearch.py insertData --es_index=schemaorg_20170510 --es_type=test1 --id_field=rid --filename=db_elasticsearch.data.json

    curl -X POST 'localhost:9200/schemaorg_20170510/_suggest?pretty' -d '{
        "concept-suggest" : {
            "text" : "夜",
            "completion" : {
                "field" : "suggest"
            }
        }
    }'

    curl -X POST 'localhost:9200/schemaorg_20170510/_search?pretty' -d '{
        "suggest":{
            "concept-suggest" : {
                "text" : "夜",
                "completion" : {
                    "field" : "suggest"
                }
            }
        }
    }'


curl -X POST 'localhost:9200/schemaorg_20170510/_suggest?pretty' -d '
{"schema-suggest": {"completion": {"field": "suggest"}, "text": "bin"}}
'

    """
