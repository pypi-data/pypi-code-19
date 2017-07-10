import json
import sys
import parser

def cmd(args=None, options=None):
    if args is None:
        args = sys.argv[1:]
    if len(args) == 2:
        infile = open(args[1])
        query_stmt = args[0]
    elif len(args) == 1:
        infile = sys.stdin
        query_stmt = args[0]
    else:
        raise ValueError('invalid args')
    query = parser.parse(query_stmt)
    for line in infile:
        line_data = json.loads(line)
        if not query.test(line_data):
            continue
        row = query.pick(line_data)
        print '\t'.join([str(x) for x in row])

if __name__ == '__main__':
    cmd()
