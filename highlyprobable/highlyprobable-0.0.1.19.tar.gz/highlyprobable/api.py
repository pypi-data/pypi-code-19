import logging
import os
from highlyprobable.base import Base, Output, APIBase

logger = logging.getLogger(os.path.basename(__file__))


class Account(Base):
    @property
    def whoami(self):
        endpoint = self._meta_url('organizations/cli/whoami')
        return Output(self._hp._session.get(endpoint).json())


class Blueprint(Base):
    def __call__(self, *args, **kwargs):
        return self._get

    @property
    def _get(self):
        endpoint = self._meta_url('connect/meta/blueprint')
        blueprints = self._hp._session.get(endpoint).json()
        _blueprints = dict()
        for blueprint in blueprints:
            _blueprints[blueprint['slug_name']] = blueprint
        return Output(_blueprints)

    def __repr__(self):
        return self._format(self._get.data)


    @property
    def show_all(self):
        return self._get


class NLPClassifiers(APIBase):
    def is_text_positive_or_negative(self, text):
        '''
        This API receives a text and returns the language of the text.
        :param text: Any unicode object
        :return: A Language code
        '''
        endpoint = self._ai_url('nlp/classifiers/positive-or-negative/')
        blueprint = self._hp.manage.services.show_all.data['is_positive_or_negative']
        payload = {
            'query': {'text': text},
            'meta': self._get_meta(blueprint)
        }
        response = self._hp._session.post(endpoint, json=payload)
        try:
            result = response.json()
        except Exception as ex:
            print(response.status_code, response.reason, ex)
            return Output(dict())
        else:
            return Output(result)

    def detect_language(self, text):
        '''
        This API receives a text and returns the language of the text.
        :param text: Any unicode object
        :return: A Language code
        '''
        endpoint = self._ai_url('nlp/language/detect/')
        blueprint = self._hp.manage.services.show_all.data['detect_language']
        payload = {
            'query': {'text': text},
            'meta': self._get_meta(blueprint)
        }
        response = self._hp._session.post(endpoint, json=payload)
        try:
            result = response.json()
        except Exception as ex:
            print(response.status_code, response.reason, ex)
            return Output(dict())
        else:
            return Output(result)


class IMGClassifiers(APIBase):

    def detect_objects(self, path_to_image_file):
        legit_file_types = ['jpg', 'png', 'jpeg']
        if path_to_image_file.split('.')[-1] not in legit_file_types:
            print('Only the following image file formats are available for this service: %s' % str(legit_file_types))

        endpoint = self._ai_url('img/classifiers/detect/')
        blueprint = self._hp.manage.services.show_all.data['detect_language']

        try:
            content = None
            with open(path_to_image_file, 'rb') as file:
                content = file.read()
        except Exception as ex:
            print(ex)
            return
        else:
            payload = {
                'query': {
                    'file_content': content
                },
                'meta': self._get_meta(blueprint)
            }
            response = self._hp._session.post(endpoint, json=payload)
            try:
                result = response.json()
            except Exception as ex:
                print(response.status_code, response.reason, ex)
                return Output(dict())
            else:
                return Output(result)


class NLP(APIBase):
    def __init__(self, highlyprobable):
        super().__init__(highlyprobable)
        self.classifiers = NLPClassifiers(highlyprobable)


class IMG(APIBase):
    def __init__(self, highlyprobable):
        super().__init__(highlyprobable)
        self.classifiers = NLPClassifiers(highlyprobable)