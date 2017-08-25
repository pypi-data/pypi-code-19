from __future__ import print_function

if __name__ == '__main__':
    import os
    import sys
    import subprocess
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('paths', nargs='+')
    parser.add_argument('-m', dest='max_size', type=int)

    args = parser.parse_args()

    for file in args.paths:
        p = subprocess.Popen(
            ['identify', '-format', '%[fx:w]', file],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        o, e = p.communicate()

        if p.returncode != 0:
            continue
            
        w = int(o.split()[0])

        if args.max_size and w > args.max_size:
            try:
                stat = os.stat(file)
                subprocess.check_call([
                    'convert', '-resize', str(args.max_size),
                    file, file
                ])
                newstat = os.stat(file)
                print('{0} {1} -> {2} ({3}%)'.format(
                    file, stat.st_size, newstat.st_size,
                    100 - (newstat.st_size * 100 / stat.st_size),
                ))

            except Exception as ex:
                raise
                #print(ex )
                print('{0} failed'.format(file), file=sys.stderr)



