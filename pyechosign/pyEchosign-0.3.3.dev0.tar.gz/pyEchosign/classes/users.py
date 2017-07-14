__all__ = ['Recipient']


class UserEndpoints(object):
    @classmethod
    def get_users_from_bulk_agreements(cls, data: dict):
        """ Takes a response from the GET /agreements call and returns a set of `DisplayUser` """
        users = []
        for user_data in data:
            email = user_data.get('email')
            name = user_data.get('fullName', None)
            company = user_data.get('company', None)
            user = DisplayUser(email, full_name=name, company=company)
            users.append(user)
        return users


class DisplayUser(object):
    """ Maps to the DisplayUserInfo provided by Echosign for agreements fetched in bulk """
    def __init__(self, email: str, **kwargs):
        self.email = email
        self.company = kwargs.pop('company', None)
        self.full_name = kwargs.pop('full_name', None)

    def __str__(self):
        if self.full_name:
            return self.full_name
        else:
            return self.email


class Recipient(DisplayUser):
    """ Provides additional attributes to facilitate sending documents to recipients, such as Security Options.

     Attributes:
         authentication_method (str): "The authentication method for the recipients to have access to
            view and sign the document" (Echosign API Docs). Available options are 'NONE' (string),
            'INHERITED_FROM_DOCUMENT' or 'PASSWORD' or 'WEB_IDENTITY' or 'KBA' or 'PHONE'.
         password (str): Optional - "The password required for the recipient to view and sign the document"

     """
    def __init__(self, email: str, **kwargs):
        super().__init__(email, **kwargs)
        self.authentication_method = kwargs.get('authentication_method', 'NONE')
        self.password = kwargs.get('password', None)


class RecipientInfo(object):
    email = None
    fax = None
    role = None
    private_message = None
    signing_order = None

    # Acceptable Options for role
    SIGNER = 'SIGNER'
    APPROVER = 'APPROVER'
    ACCEPTOR = 'ACCEPTOR'
    FORM_FILLER = 'FORM_FILLER'
    CERTIFIED_RECIPIENT = 'CERTIFIED_RECIPIENT'
    DELEGATE_TO_SIGNER = 'DELEGATE_TO_SIGNER'
    DELEGATE_TO_APPROVER = 'DELEGATE_TO_APPROVER'
    DELEGATE_TO_ACCEPTOR = 'DELEGATE_TO_ACCEPTOR'
    DELEGATE_TO_FORM_FILLER = 'DELEGATE_TO_FORM_FILLER'
    DELEGATE_TO_CERTIFIED_RECIPIENT = 'DELEGATE_TO_CERTIFIED_RECIPIENT'