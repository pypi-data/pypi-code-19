from parser import parse

def query(data, qs):
    print qs
    q = parse(qs)
    print q
    if not q.test(data):
        return None
    return q.pick(data)

if __name__ == '__main__':
    data = dict(
        name='guanming',
        level=1,
        age=123,
    )
    print query(data,
        'select .name , .age',
    )
    print query(data,
        'select .name,.age where .age > 200',
    )
    print query(data,
        'select .name, .age where .age > 20',
    )
    print query(data,
        'select .name, .age where .age > 20 and not .level < 1',
    )
    print query(data,
        'select .name, .age where .age > 20 and .level >= 1',
    )
    print query(data,
        'select .name, .age where .age > 20 and (.level > 1 or .level < 2)',
    )
