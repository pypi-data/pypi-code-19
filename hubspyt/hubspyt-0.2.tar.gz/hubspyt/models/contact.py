"""Contact model"""

from hubspyt.models.base_model import BaseModel

class Contact(BaseModel):
    """Wraps a contact entity from HubSpot's API"""

    def __init__(
            self,
            vid=None,
            email=None,
            first_name=None,
            last_name=None,
            company=None,
    ):
        self.vid = vid
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.company = company

    def get_update(self):
        """Gets instance for update to provide to HubSpot"""

        vid = self.vid
        email = self.email
        first_name = self.first_name
        last_name = self.last_name
        company = self.company

        instance = {
            'vid': vid,
            'email': email,
            'properties': [
                {
                    'property': 'firstname',
                    'value': first_name,
                },
                {
                    'property': 'lastname',
                    'value': last_name,
                },
                {
                    'property': 'company',
                    'value': company,
                },
            ],
        }

        return instance
