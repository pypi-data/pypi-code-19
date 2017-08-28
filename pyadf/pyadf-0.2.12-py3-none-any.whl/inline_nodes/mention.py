class Mention(object):

    def __init__(self, mention_id, text, access_level=None):
        self.mention_id = mention_id
        self.text = text
        self.access_level = access_level

    def to_doc(self):
        attrs = {
            'id': self.mention_id,
            'text': self.text
        }
        if (self.access_level != None):
            attrs['access_level'] = self.access_level
        
        return {
            'type': 'mention',
            'attrs': attrs
        }