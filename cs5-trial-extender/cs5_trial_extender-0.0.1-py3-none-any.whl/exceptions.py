class InvalidConfigFile(Exception):
    '''Raise when the configuration file is corrupted or don't exists'''
    def __init__(self, message):
        super(InvalidConfigFile, self).__init__(message)

class InvalidConfigException(Exception):
    '''Raise when application.xml is not valid'''
    def __init__(self, message):
        super(InvalidConfigException, self).__init__(message)

class ExpirationDateExeption(Exception):
    '''Raise when there is no ExpirationDate node'''
    def __init__(self, message):
        super(ExpirationDateExeption, self).__init__(message)

class TrialSerialNumberException(Exception):
    '''Raise when ther is no TrialSerialNumber node'''
    def __init__(self, message):
        super(TrialSerialNumberException, self).__init__(message)