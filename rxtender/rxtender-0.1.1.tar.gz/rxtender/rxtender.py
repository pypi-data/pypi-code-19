import os
import argparse
import tatsu
from codecs import open
from pprint import pprint

from jinja2 import Environment, PackageLoader

def generate_feature(template, streams, items):
    generated_code = {
    'header':  template['header'].render(streams=streams, items=items),
    'content': template['content'].render(streams=streams, items=items),
    'footer': template['footer'].render(streams=streams, items=items)
    }
    return generated_code

def split_template_location(location):
    return location.split('.', maxsplit=1)

def get_template(package_name):
    env = Environment(
        loader=PackageLoader(package_name, '')
    )

    template = {
        'header': env.get_template('source.header.tpl'),
        'footer': env.get_template('source.footer.tpl'),
        'content': env.get_template('source.content.tpl')
    }
    return template

def generate_code(ast, generate):
    items = []
    for entry in ast:
        if 'item' in entry and entry['item'] is not None:
            items.append(entry['item'])

    streams = []
    for entry in ast:
        if 'stream' in entry and entry['stream'] is not None:
            streams.append(entry['stream'])

    generated_serialization = {'header':'', 'content':'', 'footer':''}
    generated_sink = {'header':'', 'content':'', 'footer':''}

    if 'serialization' in generate:
        generated_serialization = generate_feature(get_template(generate['serialization']), streams, items)
    if 'sink' in generate:
        generated_sink = generate_feature(get_template(generate['sink']), streams, items)
    if 'source' in generate:
        generated_sink = generate_feature(get_template(generate['source']), streams, items)

    print(generated_serialization['header'])
    print(generated_sink['header'])
    print(generated_serialization['content'])
    print(generated_sink['content'])
    print(generated_serialization['footer'])
    print(generated_sink['footer'])
    return

def parse_idl(input):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    grammar = open(dir_path + '/rxtender.ebnf').read()
    definitions = open(input).read()

    parser = tatsu.compile(grammar)
    ast = parser.parse(definitions)

    #pprint(ast, width=20, indent=4)
    return ast

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input-source', help='rxtender definition file of a source stream')
    parser.add_argument('--input-sink', help='rxtender definition file of a sink stream')
    #parser.add_argument('-g','--generate',nargs='+', choices=['serialization', 'observable'], required=True)
    parser.add_argument('--serialization', help='module used for serialization')
    parser.add_argument('--source', help='module used for source streams')
    parser.add_argument('--sink', help='module used for sink streams')
    args = parser.parse_args()

    source_ast = parse_idl(args.input_source) if args.input_source else None
    sink_ast = parse_idl(args.input_sink) if args.input_sink else None
    generate = {}
    if args.serialization:
        generate['serialization'] = args.serialization
    if args.source:
        generate['source'] = args.source
    if args.sink:
        generate['sink'] = args.sink

    if source_ast:
        generate_code(source_ast, generate)
    if sink_ast:
        generate_code(sink_ast, generate)

    #generate_code(ast, args.generate or [])


if __name__ == '__main__':
    main()
