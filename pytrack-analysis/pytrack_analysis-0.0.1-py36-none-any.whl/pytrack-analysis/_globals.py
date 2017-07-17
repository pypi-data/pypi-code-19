import io
import os
import yaml

def get_globals():
    """
    get_globals function

    Returns profile directory, computername and os name (tested for Windows/MacOS).
    """
    ### get global constants for OS
    if os.name == 'nt': # Windows
        homedir = os.environ['ALLUSERSPROFILE']
        NAME = os.environ["COMPUTERNAME"]
        OS = os.environ["OS"]
    else:
        homedir = os.environ['HOME']
        NAME = os.environ["LOGNAME"]
        OS = os.name
    ### define user data directory
    user_data_dir = os.path.join(homedir, "tracking_user_data")
    check_folder(user_data_dir)
    ### define profile file path
    PROFILE = os.path.join(user_data_dir, "profile.yaml")
    check_file(PROFILE)
    ### check if profile file is linked
    with open(PROFILE, 'r') as stream:
        if '$LINK' in test.keys():
            link = test['$LINK']
            print("Found link to {:}".format(link))
            ### Link to new profile file
            PROFILE = os.path.join(link, "profile.yaml")
            check_file(PROFILE)
    ### return profile file path, computer name, and OS name
    return PROFILE, NAME, OS

def check_file(_file):
    """ If file _file does not exist, function will create it. Or if the file is empty, it will create necessary keywords. """
    if not os.path.exists(_file):
        write_yaml(_file, {'$USERS': [], '$PROJECTS': []})
    else:
        if read_yaml(_file) is None:
            write_yaml(_file, {'$USERS': [], '$PROJECTS': []})
        elif '$USERS' not in test.keys() or '$PROJECTS' not in test.keys():
            write_yaml(PROFILE, {'$USERS': [], '$PROJECTS': []})

def check_folder(_folder):
    """ If folder _folder does not exist, function will create it. """
    if not os.path.exists(_folder):
        os.makedirs(_folder)

def read_yaml(_file):
    """ Returns a dict of a YAML-readable file '_file'. Returns None, if file is empty. """
    with open(_file, 'r') as stream:
        out = yaml.load(stream)
    return out

def write_yaml(_file, _dict):
    """ Writes a given dictionary '_dict' into file '_file' in YAML format. Uses UTF8 encoding and no default flow style. """
    with io.open(_file, 'w+', encoding='utf8') as outfile:
        yaml.dump(_dict, outfile, default_flow_style=False, allow_unicode=True)
