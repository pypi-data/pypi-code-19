import os
import sys

def wlst_command():
    if os.name == 'nt':
        return "%s\\oracle_common\\common\\bin\\wlst.cmd" % os.environ['ORACLE_HOME']
    else:
        return "%s/oracle_common/common/bin/wlst.sh" % os.environ['ORACLE_HOME']

def main(args):
    if 'ORACLE_HOME' not in os.environ:
        sys.stderr.write("error: ORACLE_HOME is not set. Unable to find a weblogic server installation.\n")
        sys.exit(1)

    os.system("%s %s" % (wlst_command(), ' '.join(args.script)))

