from __future__ import unicode_literals

from wellaware.client import Subject, Subjects, Token
from wellaware.tests.base import *


class SubjectTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'subjects')
    @responses.activate
    def test_create_subject(self):
        subject = Subject(username='test', given_name='John', family_name='Doe', email='johndoe@example.com',
                          phone='+15555555555', password='testpass')
        resp = {'username': 'test', 'firstName': 'John', 'lastName': 'Doe', 'id': 10, 'email': 'johndoe@example.com',
                'phone': '+15555555555'}
        responses.add(responses.POST, 'http://localhost/subjects', json=resp, status=200)

        s = Subjects.create(self.token, subject=subject)
        self.assertIsInstance(s, Subject)
        self.assertEquals(subject.username, s.username)
        self.assertEquals(subject.given_name, s.given_name)
        self.assertEquals(subject.family_name, s.family_name)
        self.assertEquals(subject.email, s.email)
        self.assertEquals(subject.phone, s.phone)
        self.assertIsNone(s.password)
        self.assertEquals(10, s.id)

    @attr('unit', 'subjects')
    @responses.activate
    def test_retrieve_one_subject(self):
        subject = Subject(username='test', given_name='John', family_name='Doe', email='johndoe@example.com',
                          phone='+15555555555', password='testpass', id=10)
        resp = {'username': 'test', 'firstName': 'John', 'lastName': 'Doe', 'id': 10, 'email': 'johndoe@example.com',
                'phone': '+15555555555'}
        responses.add(responses.GET, 'http://localhost/subjects/10', json=resp, status=200)

        s = Subjects.retrieve_one(self.token, subject_id=subject.id)
        self.assertIsInstance(s, Subject)
        self.assertEquals(subject.username, s.username)
        self.assertEquals(subject.given_name, s.given_name)
        self.assertEquals(subject.family_name, s.family_name)
        self.assertEquals(subject.email, s.email)
        self.assertEquals(subject.phone, s.phone)
        self.assertIsNone(s.password)
        self.assertEquals(10, s.id)

        s = Subjects.retrieve_one(self.token, subject_id=subject)
        self.assertIsInstance(s, Subject)
        self.assertEquals(subject.username, s.username)
        self.assertEquals(subject.given_name, s.given_name)
        self.assertEquals(subject.family_name, s.family_name)
        self.assertEquals(subject.email, s.email)
        self.assertEquals(subject.phone, s.phone)
        self.assertIsNone(s.password)
        self.assertEquals(10, s.id)

    @attr('unit', 'subjects')
    @responses.activate
    def test_retrieve_subject_me(self):
        subject = Subject(username='test', given_name='John', family_name='Doe', email='johndoe@example.com',
                          phone='+15555555555', password='testpass', id=10)
        resp = {'username': 'test', 'firstName': 'John', 'lastName': 'Doe', 'id': 10, 'email': 'johndoe@example.com',
                'phone': '+15555555555'}
        responses.add(responses.GET, 'http://localhost/subjects/me', json=resp, status=200)

        s = Subjects.me(self.token)
        self.assertIsInstance(s, Subject)
        self.assertEquals(subject.username, s.username)
        self.assertEquals(subject.given_name, s.given_name)
        self.assertEquals(subject.family_name, s.family_name)
        self.assertEquals(subject.email, s.email)
        self.assertEquals(subject.phone, s.phone)
        self.assertIsNone(s.password)
        self.assertEquals(10, s.id)

    @attr('unit', 'subjects')
    @responses.activate
    def test_retrieve_all_subjects(self):
        subject = Subject(username='test', given_name='John', family_name='Doe', email='johndoe@example.com',
                          phone='+15555555555', password='testpass', id=10)
        resp = [{'username': 'test', 'firstName': 'John', 'lastName': 'Doe', 'id': 10, 'email': 'johndoe@example.com',
                 'phone': '+15555555555'}]
        responses.add(responses.GET, 'http://localhost/subjects', json=resp, status=200)

        sl = Subjects.retrieve_all(self.token)
        self.assertIsInstance(sl, list)
        s = sl[0]
        self.assertEquals(subject.username, s.username)
        self.assertEquals(subject.given_name, s.given_name)
        self.assertEquals(subject.family_name, s.family_name)
        self.assertEquals(subject.email, s.email)
        self.assertEquals(subject.phone, s.phone)
        self.assertIsNone(s.password)
        self.assertEquals(10, s.id)

    @attr('unit', 'subjects')
    @responses.activate
    def test_update_subject(self):
        subject = Subject(username='test', given_name='John', family_name='Doe', email='johndoe@example.com',
                          phone='+15555555555', password='testpass', id=10)
        resp = {'username': 'test', 'firstName': 'John', 'lastName': 'Doe', 'id': 10, 'email': 'johndoe@example.com',
                'phone': '+15555555555'}
        responses.add(responses.PUT, 'http://localhost/subjects/10', json=resp, status=200)

        s = Subjects.update(self.token, subject=subject)
        self.assertIsInstance(s, Subject)
        self.assertEquals(subject.username, s.username)
        self.assertEquals(subject.given_name, s.given_name)
        self.assertEquals(subject.family_name, s.family_name)
        self.assertEquals(subject.email, s.email)
        self.assertEquals(subject.phone, s.phone)
        self.assertIsNone(s.password)
        self.assertEquals(10, s.id)

    @attr('unit', 'subjects')
    @responses.activate
    def test_delete_subject(self):
        subject = Subject(username='test', given_name='John', family_name='Doe', email='johndoe@example.com',
                          phone='+15555555555', password='testpass', id=10)
        resp = {'username': 'test', 'firstName': 'John', 'lastName': 'Doe', 'id': 10, 'email': 'johndoe@example.com',
                'phone': '+15555555555'}
        responses.add(responses.DELETE, 'http://localhost/subjects/10', body='', status=204)

        r = Subjects.delete(self.token, subject_id=subject)
        self.assertEquals(204, r.status_code)

        r = Subjects.delete(self.token, subject_id=subject.id)
        self.assertEquals(204, r.status_code)
