from sys import argv
from cs5_trialextender.main import trial_extender

cli_help ='''
---------------------------
Application Trial Extender
---------------------------

Arguments
    - path: (c:/prog~/adb/) - path to the application.xml file
    - extend_date: (True/False) - Default is True. Usedto change the date
    - new_date = (YYYY/M/D) - Used with {extend_date}. Default is '2999/9/9'
    - replace_serial = (True/False) - Default is True. Replace the serial number

Examples:
    - python -m cs5_trialextender.run c:/prog~/adb/
    - python -m cs5_trialextender.run path=c:/prog~/adb/
    - python -m cs5_trialextender.run c:/prog~/adb/ extend_date=False
    - python -m cs5_trialextender.run c:/prog~/adb/ extend_date=False new_date=2018/12/31
    - python -m cs5_trialextender.run path=c:/prog~/adb/ replace_serial=False
'''

def run(*args, verbose=True):
    '''Run the application'''
    arguments = {}

    if len(args) < 2:
        if verbose:
            print(args, cli_help)
        return

    elif len(args) == 2:
        path = args[1].split('=')
        if len(path) == 1:
            trial_extender(path[0])
        else:
            trial_extender(path[1])

    elif len(args) > 2:
        path = args[1]
        for arg in args[2:]:
            split_arg = arg.split('=')
            arguments[split_arg[0]] = split_arg[1]
        
        trial_extender(path, **arguments)

run(*argv, verbose=False)