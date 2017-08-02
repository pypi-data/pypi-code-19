'''
fim - fIND imPROVED

Like `find -exec` or `xargs` but can specify more complicated commands, e.g.
pipe-chained commands, redirections, etc. and more sophisticated substitutions.
fim takes as input either a list of paths or new line delimited input taken from
standard input and executes a command on each.

The command is specified as the argument to `-e`, which should be a quoted
command that can be run on the command line after replacing the substitution
string with the input line.

The substitution string must be two characters (default {}), and can take the
following forms:

- {} : substitute the input argument as is in the command

- {s:patt:repl:[gi]} : do on-the-fly substitutions of the input argument (e.g.,
  stripping extensions). `patt` and ``repl` are passed to `re.sub` like
  `re.sub(patt,repl,{})`
  
- {c:command %s} form for executing embedded commands on the input argument
  (e.g. basename).
  
If no substution string is supplied in the cmd argument each argument is
appended to the cmd.

Examples:

  $ seq 1 3 | fim - -e 'seq 1 {} > {}.txt'
  seq 1 1 > 1.txt
  seq 1 2 > 2.txt
  seq 1 3 > 3.txt
  $ ls
  1.txt 2.txt 3.txt
  $ fim *.txt -e 'mv {} number_{}'
  mv 1.txt number_1.txt
  mv 2.txt number_2.txt
  mv 3.txt number_3.txt
  $ ls
  number_1.txt number_2.txt number_3.txt
  $ fim *.txt -e 'cp {} {s:number_(\d).txt:number_\1by\1.txt:}'
  cp number_1.txt number_1by1.txt
  cp number_2.txt number_2by2.txt
  cp number_3.txt number_3by3.txt
  $ ls
  number_1.txt number_1by1.txt number_2.txt number_2by2.txt number_3.txt
  number_3by3.txt
  $ fim *by* -e 'echo number | cat - {} > {s:.txt:_label.txt:}'
  echo number | cat - number_1by1.txt > number_1by1_label.txt
  echo number | cat - number_2by2.txt > number_2by2_label.txt
  echo number | cat - number_3by3.txt > number_3by3_label.txt
  $ ls *_label.txt
  number_1by1_label.txt number_2by2_label.txt number_3by3_label.txt
  $ fim *_label.txt -e 'ln -s {} symlink_to_{}'
  ln -s number_1by1_label.txt symlink_to_number_1by1_label.txt
  ln -s number_2by2_label.txt symlink_to_number_2by2_label.txt
  ln -s number_3by3_label.txt symlink_to_number_3by3_label.txt
  $ ls *_label.txt
  symlink_to_number_1by1_label.txt symlink_to_number_2by2_label.txt
  symlink_to_number_3by3_label.txt
  $ fim *_label.txt -e 'mv {} {c:basename %s .txt}.pdf' # rename .txt to .pdf
  mv number_1by1_label.txt number_1by1_label.pdf
  mv number_2by2_label.txt number_2by2_label.pdf
  mv number_3by3_label.txt number_3by3_label.pdf
  $ ls *.pdf
  number_1by1_label.pdf number_2by2_label.pdf number_3by3_label.pdf
  
Usage:
    fim [options] (-|PATH...) [-e CMD]
    
Options:
    -e CMD --cmd=CMD           the command to run, with applied substitutions
                               if specified, on each argument [default: echo]
    -s SUBSTR --substr=SUBSTR  substitution string [default: {}]
    -q --quiet                 suppress echo of the commands being executed
    -d --dry                   do not execute commands
    -x --exit-on-interrupt     exit script on interrupt signal, do not
                               continue executing commands
    -p N --procs=N             run N subprocesses concurrently using
                               multiprocess
    -g --glob                  do not omit arguments that look like globs - use
                               with care!
'''
from docopt import docopt, DocoptExit
import glob
import os
import re
import sys
import time

from functools import partial
from optparse import OptionParser
from subprocess import call, Popen, PIPE

def main(argv=sys.argv[1:]
    ,stdin=sys.stdin
    ,stderr=sys.stderr
    ,exit=sys.exit
    ,cwd=os.getcwd()
    ) :

    opts = docopt(__doc__,argv=argv)
    
    if len(opts['--substr']) != 2 :
        raise DocoptExit('substitution string must be exactly two characters')

    # the arguments to be applied to the specified command as substitutions
    args = opts['PATH']

    # script can accept arguments from stdin if - is in the list of command
    # line arguments, they are not globbed
    if opts['-'] :
        args += [s.strip() for s in stdin.readlines()]

    # globbed arguments are dangerous and in general should not be passed to
    # this script, strip out anything that looks like a glob unless the user
    # tells us not to, basically anything with a * in it
    if not opts['--glob'] :
        for arg in args :
            if '*' in arg :
                stderr.write('Warning: glob-looking argument found, removing %s\n'%arg)
                args.remove(arg)

    sub_start, sub_end = opts['--substr']

    # build dictionary of substitutions
    substitutions = {opts['--substr']:lambda st: st} # identity
    subst_patt = r'%(sub_start)s(?P<cmd>[^%(sub_end)s]*)%(sub_end)s'
    for m in re.finditer(subst_patt%locals(),opts['--cmd']) :
        whole_sub = m.group(0)
        if len(m.group('cmd')) != 0 :
            cmd = m.group('cmd')

            # search/replace
            if cmd[0] == 's' :
                sep_chr = cmd[1]
                srch_bits = re.split(r"(?<!\\)%s"%sep_chr,cmd)
                if len(srch_bits) != 4 :
                    msg = ('Incorrectly formatted substitution: %(cmd)s split '
                           'to %(srch_bits)s\n') % locals()
                    stderr.write(msg)
                    exit(1)

                # make a closure of the substitution using functools.partial
                s, search, repl, mode = srch_bits
                search = re.sub(r'[^\\]%s'%sep_chr,sep_chr,search)
                repl = re.sub(r'[^\\]%s'%sep_chr,sep_chr,repl)

                # by default, first match substituted only
                count = 0 if 'g' in mode else 1 

                # case-sensitive by default
                flags = 'i' if 'i' in mode else '' 
                substitutions[whole_sub] = partial(re.sub,search,repl,
                                                   count=count)

            # command
            elif cmd[0] == 'c' :
                subcmd = cmd[2:]
                if subcmd.count('%s') == 0 :
                    subcmd += ' %s'
                subcmd = subcmd.replace('%s','%(subst)s')
                def f_closure(cmd) :
                    def f(st) :
                        local_cmd = cmd%{'subst':st}
                        p = Popen(local_cmd,shell=True,
                                  stdout=PIPE,stderr=PIPE)
                        stdout, stderr = p.communicate()
                        if p.returncode :
                            r = p.returncode
                            msg = ('Warning: subsitution command exited with '
                                   'non-zero status: %(local_cmd)s %(r)d\n'
                                   '%(stdout)s\n%(stderr)s\n'
                                   ) % locals()
                            stderr.write(msg)
                        return stdout.strip().decode('utf8')
                    return f
                substitutions[whole_sub] = f_closure(subcmd)


    # flexing the functools muscles
    call_cmd = partial(call,shell=True,cwd=cwd)
        
    if opts['--procs'] is not None :
        from multiprocessing import Pool
        pool = Pool(int(opts['--procs']))

        async_results = []

    interrupt_case = 'notset'
    for arg in args :

        cmd = opts['--cmd']
        if not opts['--substr'] in cmd :
            cmd += ' {}'

        # do substitutions
        for subst,subst_f in substitutions.items() :
            cmd = cmd.replace(subst,subst_f(arg))

        if not opts['--quiet'] :
            stderr.write(cmd+'\n')

        if not opts['--dry'] :

            if opts['--procs'] is not None :
                r = pool.apply_async(call_cmd,(cmd,))
                async_results.append(r)
            else :
                try :
                    call_cmd(cmd)
                except KeyboardInterrupt :
                    if interrupt_case != 'all' :
                        interrupt_case = 'notset'
                        while interrupt_case not in ('y','n','all','') :
                            interrupt_case = raw_input('Keyboard interrupt received, '
                                             'continue? (Y/n/all) ').lower()

                        if interrupt_case == '' :
                            interrupt_case = 'y'

                    if interrupt_case == 'n' :
                        stderr.write('User exited with keyboard interrupt\n')
                        break


    if opts['--procs'] is not None :
        while any(not r.ready() for r in async_results) :
            time.sleep(5)

if __name__ == '__main__' :
    main()