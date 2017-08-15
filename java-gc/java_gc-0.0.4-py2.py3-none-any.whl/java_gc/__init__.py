import os, re, io, signal
import logging, subprocess

from argparse import ArgumentParser

__VERSION__ = '0.0.4'

def sighandler(signum, frame):
  logging.warning("Timed out waiting for jcmd, killing jcmd process")
  jcmd_proc.terminate()

def parse_cmdline():
  p = ArgumentParser(description='Trigger a full GC on a java process')

  p.add_argument('proc', help='The service name, or pid, to trigger the GC on')
  p.add_argument('-u', '--user', default=os.getenv('USER'), help='User owning the process (default to current user)')
  p.add_argument('-t', '--timeout', type=float, default=30, metavar='T', help='seconds to wait for GC before raising error')
  p.add_argument('-r', '--restart', action='store_true', help='restart the service if timeout occurred, else exit with error')
  p.add_argument('-l', '--loglevel', choices=['debug', 'info', 'warning', 'error', 'critical'], default='info', help='set log level')
  p.add_argument('-v', '--version', action='version', version=__VERSION__, help='print program version and exit')

  return p.parse_args()

def _process_systemd_output(output, user):
  proc = {}
  pid  = -1

  for l in io.StringIO(unicode(output)).readlines():
    (b, s, e) = l.partition('=')
    proc[b.lower()] = e.strip()

  if user == proc['user']:
    pid = proc['mainpid']
    logging.debug("systemd found pid: %s", pid)
  
  return pid

def find_pid(proc, user):
  is_service  = False
  systemd_cmd = ['systemctl', 'show', '-p', 'User,MainPID', proc]
  pgrep_cmd = ['pgrep', '-u', user, '-f', proc]

  if not re.search("^\d+$", proc):
    proc = -1

    try:
      logging.debug(' '.join(systemd_cmd))
      out = subprocess.check_output(systemd_cmd)
    except (subprocess.CalledProcessError, OSError) as e:
      logging.warning("systemd process query failed: %s", e)

      try:
        logging.debug(' '.join(pgrep_cmd))
        out = subprocess.check_output(pgrep_cmd)
      except (subprocess.CalledProcessError, OSError) as e:
        logging.warning("pgrep process query failed: %s", e)
      else:
        proc = out.strip()
        logging.debug("pgrep found pid: %s", proc)
    else:
      is_service = True
      proc = _process_systemd_output(out, user)
  else:
    logging.info("Provided proc looks like a pid, may fortune be forever in your favor")

  return (int(proc), is_service)

def _run_jcmd(pid, user, timeout):
  global jcmd_proc

  # NOTE: it seems that even if we see the 'AttachNotSupportedException' error, the process still exits with 0
  # maybe that's OK, because we'll get that if it's not a java process
  # if it's a java proc we care about, hopefully we don't see that before we hit the timeout
  cmd = ['sudo', '-u', user, 'jcmd', str(pid), 'GC.run']
  logging.debug(' '.join(cmd))

  signal.signal(signal.SIGALRM, sighandler)
  signal.setitimer(signal.ITIMER_REAL, timeout, 0)

  logging.info("Starting garbage collection for pid: %d", pid)
  jcmd_proc = subprocess.Popen(cmd)
  jcmd_proc.wait()

  signal.setitimer(signal.ITIMER_REAL, 0)
  rc = jcmd_proc.returncode
  logging.debug("jcmd exited with rc: %d", rc)

  return rc

##########
#  MAIN  #
##########
def main():
  opts = parse_cmdline()
  logging.basicConfig(level=opts.loglevel.upper())
  logging.debug("setting timeout to %d seconds", opts.timeout)

  (pid, is_service) = find_pid(opts.proc, opts.user)
  logging.debug("PID: %d, SERVICE: %s", pid, is_service)

  if pid < 2:
    logging.warning("No process found for %s", opts.proc)
    raise RuntimeError("No process named %s found" % (opts.proc,))

  rc = _run_jcmd(pid, opts.user, opts.timeout)

  if rc != 0:
    if is_service and opts.restart:
      logging.info("Attempting restart of service '%s'", opts.proc)
      cmd = ['sudo', 'systemctl', 'restart', opts.proc]
      out = subprocess.check_output(cmd)
    else:
      logging.debug("Either not a service, or --restart not provided, exiting with error")
      raise RuntimeError("jcmd exited with rc: %d" % (rc,))
