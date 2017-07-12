#!/usr/bin/env python3
#coding:utf-8
'''
python standard logging module wrapper ver 0.12
(C) Taka Suzuki (Opus Studio Inc.)

a wrapper that ready to use in some cases.
 - does not need to learn logging module magics to use
 - generats a template log.conf
 - in dev env, console and file logging with timestamps, source file names and line numbers are ready.
 - it can be replaced with the standard logging module

@issue カレントディレクトリにいろいろ書き込むという流れはpermissionのケアが必要. かけない場合は、homeに書くとか?

'''
import os
import platform
import logging
import logging.config

# default value for the filenames.
pwd = os.path.dirname(os.getcwd())
APPLOG_FN = pwd + '/app.log'
DEVLOG_FN = pwd + '/dev.log'

def filename_normalize(x):
    return x.replace(os.sep, '/')
	
APPLOG_FN = filename_normalize(APPLOG_FN)
DEVLOG_FN =filename_normalize(DEVLOG_FN)
	
found = None
fn = 'log.conf'
pathn_candidates = ['%s' % fn , '~/.%s' % fn, '/etc/%s' % fn]
verbose = False


def _load_conf(*ar):
    if len(ar):
       fn = ar[0]
    else:
       return
    #logging.basicConfig()
    logging.config.fileConfig(fn, defaults=None, disable_existing_loggers=True)
    #logging.config.dictConfig(d)
    if verbose:
        print('loaded a config file %s' % fn)
        
def initial_loader():
    ''' intialize logging settings '''
    logging.basicConfig()
    # if platform.system() == 'windows':
    #     pass
    for x in pathn_candidates:
        if os.path.exists(x) and os.access(x, os.R_OK):
            global found
            found = x
            assert os.access(x, os.W_OK), "the file is readonly"
            break
    if found:
        _load_conf(found)
    else:
        pass

def create_conf(mode, **kw):
    ''' conf creator
    Keyword Arguments:
    overwrite --
    interactive: --
    applog_fn -- file name for app (default: APPLOG_FN)
    applog_pn -- path name for app (default: current directory)
    devlog_fn -- file name for dev (default: DEVLOG_FN)
    devlog_pn -- path name for dev (default: current directory)
    '''

    pref_debug = r'''[loggers]
keys=root,app

[formatters]
keys=default,dev

[handlers]
keys=default,frotate,important,console

[formatter_default]
format=%(asctime)s %(levelname)s %(message)s
datefmt=

[formatter_dev]
class=logging.Formatter
#formatxx=%(name)s %(levelno)s %(levelname)s %(pathname)s %(filename)s %(module)s %(lineno)d %(created)f %(asctime)s %(msecs)d %(relativeCreated)d %(thread)d %(process)d %(message)s
format= %(asctime)s %(filename)12.12s(%(lineno)3d) %(message)s
#datefmt=%d/%m/%Y %H:%M:%S
#datefmt=%H:%M:%S %f

[handler_frotate]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=dev
args=('{devlog_pnfn}', 'w', (64*1024), 8)

[handler_important]
class=handlers.RotatingFileHandler
level=INFO
formatter=default
args=('{applog_pnfn}', 'a', (5*1024*1024), 5)

[handler_console]
class=logging.StreamHandler
level=DEBUG
formatter=dev
args=()

[handler_default]
class=NullHandler
level=DEBUG
args=()

[logger_root]
level=DEBUG
handlers=frotate,console,important
qualname=root

[logger_app]
level=INFO
handlers=important
qualname=app

'''

    pref_prod = r'''[loggers]
keys=root,app

[formatters]
keys=default,dev

[handlers]
#keys=default,frotate,important,console
keys=default,important,console

[formatter_default]
format=%(asctime)s %(levelname)s %(message)s
datefmt=

[formatter_dev]
class=logging.Formatter
#formatxx=%(name)s %(levelno)s %(levelname)s %(pathname)s %(filename)s %(module)s %(lineno)d %(created)f %(asctime)s %(msecs)d %(relativeCreated)d %(thread)d %(process)d %(message)s
format= %(asctime)s %(filename)12.12s(%(lineno)3d) %(message)s
#datefmt=%d/%m/%Y %H:%M:%S
#datefmt=%H:%M:%S %f

[handler_frotate]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=dev
args=('{devlog_pnfn}', 'w', (64*1024), 8)

[handler_important]
class=handlers.RotatingFileHandler
level=INFO
formatter=default
args=('{applog_pnfn}', 'a', (5*1024*1024), 5)

[handler_console]
class=logging.StreamHandler
level=DEBUG
formatter=dev
args=()

[handler_default]
class=NullHandler
level=DEBUG
args=()

[logger_root]
level=CRITICAL
handlers=default,important
#handlers=frotate,console,important
qualname=root

[logger_app]
level=INFO
handlers=important
qualname=app
'''

    preset_preferences = {'debug':pref_debug, 'prod':pref_prod }
    cwd = os.getcwd()
    interactive = kw.get('interactive', False)
    overwrite = kw.get('overwrite', False)
    applog_fn = kw.get('applog_fn', APPLOG_FN)
    applog_pn = kw.get('applog_pn', cwd)
    applog_pnfn = os.path.join(applog_pn, applog_fn)
    devlog_fn = kw.get('devlog_fn', DEVLOG_FN)
    devlog_pn = kw.get('devlog_pn', cwd)
    devlog_pnfn = os.path.join(devlog_pn, devlog_fn)
    if mode in list(preset_preferences.keys()):
       content = preset_preferences[mode]

       # @todo conf content procedural here.
       content = content.format(applog_pnfn=applog_pnfn, devlog_pnfn=devlog_pnfn)
           
       fn = pathn_candidates[0]
       if os.path.exists(fn):
           if overwrite:
               if interactive:
                   # Python 2 vs 3
                   import sys
                   PY3 = sys.version_info[0] == 3
                   if not PY3:
                       input_func = raw_input
                   else:
                       input_func = input
                   answer = input_func("do you want to overwrite the %s> " % fn)
                   if not 'Y' in answer.upper():
                       return
                   else:
                       pass
               else:
                   # notification
                   if verbose:
                       print("a conf file will be over written %s" % fn)
           else:
               # not overwriting
               if verbose:
                   print("the conf file is existing %s, and is not being written" % os.path.abspath(fn))
               return
       with open(fn, 'w') as f:
           f.write(content)
       if verbose:
           print("a conf file created %s" % fn)
    else:
        assert 0, 'mode %s not found' % mode

def _initialize():

    # alias for the standard logging module
    aliases = ['log',
           'exception',
           'disable',
           'addLevelName',
           'getLevelName',
           'makeLogRecord',
           'shutdown',
           'setLoggerClass',
           'captureWarnings',
           'basicConfig',
           'DEBUG',
           'INFO',
           'WARN',
           'WARNING',
           'ERROR',
           'CRITICAL',
           ]

    # overridden module method assign
    for a in aliases:
        globals()[a] = getattr(logging, a)

    #
    # for the with namespace mylog, there are two method "dev", "sys"
    #
    global dev
    dev = logging.getLogger('root')
    globals()['sys'] = getattr(logging.getLogger('app'), 'info')

    names = ['critical',
    'error',
    'warning',
    'info',
    'debug',
    'warn',
    ]
    
    for n in names:
        globals()[n] = getattr(dev, n)
    
# for release
#create_conf('debug', interactive=False)
create_conf('debug', interactive=False, overwrite=True)
#create_conf('debug', interactive=False, overwrite=True, applog_fn="MyApp.log", devlog_fn="MyDev.log")
#create_conf('prod', interactive=False, overwrite=True)

initial_loader()
_initialize()

if __name__ == '__main__':
    print (__file__)

    logging.basicConfig()
    debug("[[Root my abc]]")
    l = logging.getLogger('root')
    l.error('[[ERROR message]]')
    l.warn('[[WARN message]]')
    l.info('[[INFO IMPORTANT dev message]]')
    l.debug('[[debug 9384701293847102983471029384710298347message]]')
    la = logging.getLogger('app')
    la.error('[[app my error]]')
    la.warn('[[app my warn]]')
    la.info('[[app my info]]')
    la.debug('[[app debug 9384701293847102983471029384710298347message]]')

    error('__no ns my Error')
    warn('__no ns my Warn')
    info('__no ns my Info')
    debug('__no ns debug 9384701293847102983471029384710298347message')
    
    print("Bye")
    
    if os.path.exists('app.log'):
        print('app.log size = %d' % os.path.getsize('app.log'))
    if os.path.exists('dev.log'):
        print('dev.log size = %d' % os.path.getsize('dev.log'))
    
__all__ = ['create_conf',
           'initial_loader',
           'dev',
           'sys',
           # aliases for the logging module
           'debug',
           'info',
           'warning',
           'warn',
           'error',
           'log',
           'exception',
           'disable',
           'addLevelName',
           'getLevelName',
           'makeLogRecord',
           'shutdown',
           'setLoggerClass',
           'captureWarnings',
           'basicConfig',
    ]    
