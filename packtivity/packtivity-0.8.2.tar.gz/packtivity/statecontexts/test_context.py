import os
import logging
import packtivity.utils as utils
log = logging.getLogger(__name__)

class TestState(object):
    def __init__(self, identifier,metabase):
        self._metadir = os.path.join(metabase,identifier)
        self._identifier = identifier
        utils.mkdir_p(self.metadir)

    def identifier(self):
        return self._identifier

    @property
    def metadir(self):
        return self._metadir

    def add_dependency(self,depstate):
        pass

    def contextualize_data(self,data):
        return 'contextualized {}'.format(data)

    def json(self):
        pass

    @classmethod
    def fromJSON(cls,jsondata):
        pass

class TestProvider(object):
    def __init__(self, *base_states, **kwargs):
        self.metabase = kwargs.get('metabase','pack_meta')

    def new_provider(self,name):
        pass

    def new_state(self,name):
        return TestState(name,self.metabase)

    def json(self):
        return {
            'state_provider_type': 'test_provider',
        }
    
    @classmethod
    def fromJSON(cls,jsondata):
        return cls(TestState.fromJSON())

def setup_provider(dataarg,dataopts):
    return TestProvider()