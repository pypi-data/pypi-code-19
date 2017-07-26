#!/usr/bin/env python
import json
import argparse
from dotmap import DotMap
import os
from os import path
import sys
import helpers

def getSettings():
  settings_files = [
    'settings/settings.default.json',
    'settings/settings.json'
  ]

  settings = {}

# get settings.default.json path

  settingsPath = '.'
  lookUpPaths = [
    path.dirname(sys.modules['__main__'].__file__),
    os.getcwd()
  ]
  for lookUpPath in lookUpPaths:
      if os.path.isfile(path.join(lookUpPath, settings_files[0])):
        settingsPath = lookUpPath
        break

  settings_files[0] = path.join(settingsPath, settings_files[0])
  settings_files[1] = path.join(settingsPath, settings_files[1])

  if not os.path.isfile(settings_files[0]):
      print('WARN:Settings not found ' + settings_files[0])

# get available settings from settings.default.json
  nestedArguments = {}
  try:
    with open(settings_files[0]) as settings_file:
        nestedArguments = json.load(settings_file)
  except IOError:
    pass

  arguments = []
  helpers.flatArguments(arguments, nestedArguments)

# init parser with available settings
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--settings', help='settings file in json format')
  for argument in arguments:
    parser.add_argument(argument)

# parse
  args = parser.parse_args()
  if args.settings:
    # search path if not abs
    if path.isabs(args.settings):
      customSettings = path.join(settingsPath, args.settings)
    else:
      customSettingsPath = '.'
      for lookUpPath in lookUpPaths:
          if path.isfile(path.abspath(path.join(lookUpPath, args.settings))):
            customSettingsPath = lookUpPath
            break
      customSettings = path.abspath(path.join(customSettingsPath, args.settings))

    if not path.isfile(customSettings):
        print('WARN: Custom settings not found ' + args.settings)
    else:
      settings_files.append(customSettings)

# get settings from files
  for file in settings_files:
    try:
      with open(file) as setting_file:
          helpers.dict_merge(settings, json.load(setting_file))
    except IOError:
      pass

# merge with argv
  parsedArgs = helpers.nestArguments(vars(args))
  helpers.dict_merge(settings, parsedArgs)

# merge with env
  env_lower = dict((k.lower(), v) for k,v in os.environ.iteritems())
  parsedEnv = helpers.nestArguments(env_lower, '_')
  helpers.dict_merge(settings, parsedEnv)

  settings = DotMap(settings)
  return settings

settings = getSettings()

