import unittest
import json
from recastrestapi.server import app
from recastrestapi.server import db
from recastdb.models import AccessToken, User
import random
import string

from flask import url_for

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True
        self.app.app_context().push()
        db.create_all()
        self.client = self.app.test_client()
        self.token = self.random_string()
        
    def tearDown(self):
        db.session.remove()

    def test_show_user(self):
        user = User(name="john alex", email="johnalex@example.com")
        db.session.add(user)
        db.session.commit()
        
        response = self.client.get('/users/'+str(user.id), headers=self.get_api_header(self.token))
        self.assertTrue(response.status_code == 200)
        
    def test_analyses(self):
        """Analyses"""
        response = self.client.get('/analyses/1', headers=self.get_api_header(self.token))
        self.assertTrue(response.status_code == 200)

    def test_home(self):
        """Page not requiring TOKEN(not implemented)"""
        pass
        
    def test_users(self):
        user = User.query.first()
        self.assertIsNotNone(user)
        user1 = User(name='john', email='john@example.com')
        user2 = User(name='Alex', email='alex@example.com')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        response = self.client.get('/users/1', headers=self.get_api_header(self.token))
        self.assertTrue(response.status_code == 200)

    def test_POST_USER(self):
        """Add user through POST(Not implemented)"""
        user = {'name': 'Matt',
                'email': 'matt@example.com'
                }
        
        response = self.client.get('/users', headers=self.get_api_header(self.token))
        print response.status_code

    def test_add_token(self):
        """Adding Random Token"""

    def tearDown(self):
        db.session.remove()
        #self.app.app_context().pop()

    def test_add_token(self):
        test_user = User(name="Rest API test user", email="testapi@email.com")
        db.session.add(test_user)
        db.session.commit()
        token = AccessToken(token=self.token, user_id=test_user.id)
        db.session.add(token)
        db.session.commit()

    def get_api_header(self, token="test_token"):
        return {
            'Authorization': 'Basic ' + token, 
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            }

    def test_404(self):
        """Wrong URL"""
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_header())
        self.assertTrue(response.status_code == 404)


    def test_401(self):
         """Unauthorized access"""
         response = self.client.get(
             '/users',
             headers=self.get_api_header("invalid_token"))
         self.assertTrue(response.status_code == 401)

    def test_token_auth(self):
        """(Not implemented)"""
        pass

    def test_GET(self):
        """(Not implemented)"""
        pass

    def test_POST(self):
        """(Not implemented)"""
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEquals(json_response['_error']['code'],404)

    def test_token_auth(self):
        pass

    def test_GET(self):
        pass

    def test_POST(self):
        pass

    def random_string(self, size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
        
