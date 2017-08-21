

def recursive_update(base, other):
    """
    Recursively upadtes base with other. Both should be
    dictionary-like mapping types. 

    Returns None as modifies base in place

    This is a module level function and can be used for
    any dictionary like objects including dict, odict
    and naodict

    TODO: check __instancecheck__ for naodict metaclass
    """
    for key, value in other.items():
        if key in base and dictlike(base[key], value):
            recursive_update(base[key], value)
        else:
            base[key] = value
        

# TODO move to _compat.py with od_backport
# TODO remove od_backport

def dictlike(*candidates):
    """checking"""
    for c in candidates:
        if not isinstance(c, (dict,)): return False
    return True


def listlike(*candidates):
    """checking"""
    for c in candidates:
        if not isinstance(c, (list,)): return False
    return True


####################
# padding strings
def padded(string, spaces=4):

    return '\n'.join([' '*spaces+l for l in string.split('\n')])



def obj2xml(obj, level=1):
    """
    recursively transform an object structure to an
    XML structure to be able to view

    to_yaml is more sane!!!
    but need serialization rule for 
    non-standard python objects!
    """
    if isinstance(obj, list):

        return '\n'.join([obj2xml(i, level+1) for i in obj])

    ats = []
    for a in obj.__dict__:
        if not a.startswith('_'):
            val = getattr(obj, a)
            ats.append('{}<attr name="{}">{}{}</attr>'.format(
                "\t"*level,
                a, 
                obj2xml(val, level+1) if isinstance(val, list) else val,
                '\n'+"\t"*level if isinstance(val, list) else '',
            ))

    return '\n{}<obj type="{}">\n{}\n{}</obj>'.format(
        "\t"*(level-1),
        type(obj),
        '\n'.join(ats),
        "\t"*(level-1),
    )




import textwrap

class fake_host(object):
    """
    use as:

    with fake_host('syrus.hu'):
        server.serve(app)
    """

    hosts_files = {
        'posix': r'/etc/hosts',
        'nt': r'C:\Windows\System32\drivers\etc\hosts',
    }

    def __init__(self, host, ip='127.0.0.1'):
        self.insert = textwrap.dedent("""
        
        # Automagically inserted line for OAuth testing follows:
        {} {}

        """.format(ip, host))
        app.logger.debug(self.insert)

        # split between Windows and Linux (need sudo for that)
        try:
            self.hosts_file = hosts_files.get(os.name, None)
        except:
            raise ValueError('OS not supported')

    def __enter__(self):
        with open(hosts, 'r+') as h:
            # save the current in the tool and restore it on server stop
            x = h.read()
            print(x)
            if x.find(insert) == -1:
                h.truncate(0)
                h.seek(0)
                h.write(x + insert)
                print(insert)

    def __exit__(self, exc_type, exc_value, traceback):
        # restore hosts (this is not runninbg as a standalone script in production environment!)
        with open(hosts, 'r+') as h:
            # search for line with special comment and replace
            x = h.read()
            print(x)
            y = x.replace(insert, '')
            print(y)
            h.truncate(0)
            h.seek(0)
            h.write(y)



