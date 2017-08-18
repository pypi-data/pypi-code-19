from xml.etree import ElementTree as et
from os.path import isdir, isfile, join
from cs5_trialextender.exceptions import InvalidConfigException, ExpirationDateExeption, TrialSerialNumberException, InvalidConfigFile

def validate_config_xml(path):
    '''Check if path is valid'''
    file_path = join(path, 'application.xml')
    try:
        tree = et.parse(file_path)
        return tree
    except BaseException as e:
        raise InvalidConfigFile("Invalid configuration file")

def trial_extender(path, **kwargs):
    '''Extend the trial date'''

    if 'extend_date' in kwargs:
        extend_date = kwargs['extend_date']
    else:
        extend_date=True
    
    if 'new_date' in kwargs:
        new_date = kwargs['new_date']
    else:
        new_date='2999/9/9'

    if 'replace_serial' in kwargs:
        replace_serial = kwargs['replace_serial']
    else:
        replace_serial=True

    def generate_new_number(number):
        '''Generate a new number for trial serial number'''
        if number == 9:
            return 0
        else:
            return number+1
    
    valid_xml = validate_config_xml(path)
    
    if not valid_xml:
        raise InvalidConfigException("Invalid file or folder")

    valid_xml_root = valid_xml.getroot()
    valid_xml.write(join(path,"application_old.xml"))

    if extend_date:
        try:
            valid_xml_root.find('.//Data[@key="ExpirationDate"]').text = new_date
        except:
            raise ExpirationDateExeption("Couldn't find Expiration Date. Maybe it's not installed as TRIAL")
    
    if replace_serial:
        try:
            trialno = valid_xml_root.find('.//Data[@key="TrialSerialNumber"]').text
            new_number = "%s%i" % (trialno[0:-1], generate_new_number(int(trialno[-1]))) 
            valid_xml_root.find('.//Data[@key="TrialSerialNumber"]').text = new_number
        except:
            raise TrialSerialNumberException("Couldn't find Trial Serial Number. Maybe it's not installed as TRIAL")

    valid_xml.write(join(path, "application.xml"))