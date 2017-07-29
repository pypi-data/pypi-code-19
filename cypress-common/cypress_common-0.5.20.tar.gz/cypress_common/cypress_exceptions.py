
class LicenseValidationException(Exception):

    def __init__(self, msg):
        super(LicenseValidationException, self).__init__("Invalid license: " + msg)
