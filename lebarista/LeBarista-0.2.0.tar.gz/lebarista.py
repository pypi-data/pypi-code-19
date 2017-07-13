CONFIG_FILE_PATHS = ['~/.lebarista.yaml', '.lebarista.yaml']

# An empty function to use when configuration or dependencies are missing (as this is not a vital piece)
def notify(text):
  pass
        
try:
  from slackclient import SlackClient
  import yaml
  import os, sys

  for config_file in CONFIG_FILE_PATHS:
    if os.path.exists(os.path.expanduser(config_file)):
      with open(os.path.expanduser(config_file), 'r') as file:
        config = yaml.load(file)
        if config == None:
          print("No configuration data available in {}".format(config_file), file=sys.stderr)
          del config
          continue
        else:
          break

  try:
    slack_notifier = SlackClient(config['slack']['token'])
    
    def notify(text):
      slack_notifier.api_call(
        "chat.postMessage",
        channel=config['slack']['channel'],
        text=text
    );
  except:
    print('No configuration data available', file=sys.stderr)
    print("Configure a '{}' file to enable notifications".format(config_file), file=sys.stderr)
    print("You can use '{}' as an example".format('https://github.com/tnarik/lebarista/blob/master/lebarista.yaml.example'), file=sys.stderr)
  finally:
    del file
  #else:
  #  config_file = None
  #  print('No configuration file available')
  #  print("Create a '{}' file to enable notifications".format('.lebarista.yaml'))
  #  print("You can use '{}' as an example".format('https://github.com/tnarik/lebarista/blob/master/lebarista.yaml.example'))
except (ModuleNotFoundError, ImportError):
  print("There won't be any notifications triggered as dependencies are missing. Please reinstall.", file=sys.stderr)
