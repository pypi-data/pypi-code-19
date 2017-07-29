# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from django.test import TransactionTestCase

from django.contrib.auth.models import User
from .models import Friendship
from core.models import Person


pytestmark = pytest.mark.django_db


@pytest.fixture
def person1():
    user = User(username='User1')
    user.set_password('testpass')
    user.save()
    return Person.objects.create(user=user)


@pytest.fixture
def person2():
    user = User(username='User2')
    user.set_password('testpass')
    user.save()
    return Person.objects.create(user=user)


@pytest.fixture
def person3():
    user = User(username='User3')
    user.set_password('testpass')
    user.save()
    return Person.objects.create(user=user)


@pytest.fixture
def friendship(personA, personB):
    personA.send_friend_request(personB)
    personB.friend_requests_to_user.first().accept()


def test_first_test():
    assert True


def test_person1_has_no_friends(person1):
    assert person1.friends.count() == 0


def test_person2_has_no_friends(person2):
    assert person2.friends.count() == 0


def test_person1_send_friend_request_to_person_2(person1, person2):
    person1.send_friend_request(person2)
    assert Friendship.objects.count() == 1
    assert Friendship.objects.first().status == Friendship.STATUS_PENDING
    assert person1.friends.count() == 0
    assert person2.friends.count() == 0
    assert list(person2.friend_requests_to_user.all()) == [Friendship.objects.first()]


def test_person2_send_friend_request_to_person_1(person1, person2):
    person2.send_friend_request(person1)
    assert Friendship.objects.count() == 1
    assert Friendship.objects.first().status == Friendship.STATUS_PENDING
    assert person1.friends.count() == 0
    assert person2.friends.count() == 0
    assert list(person1.friend_requests_to_user.all()) == [Friendship.objects.first()]


def test_person2_accepts_friend_request_from_person1(person1, person2):
    person1.send_friend_request(person2)
    person2.friend_requests_to_user.first().accept()
    assert Friendship.objects.count() == 1
    assert Friendship.objects.first().status == Friendship.STATUS_ACCEPTED
    assert person1.friends.count() == 1
    assert list(person1.friends.all()) == [person2]
    assert person2.friends.count() == 1
    assert list(person2.friends.all()) == [person1]


def test_person1_accepts_friend_request_from_person2(person1, person2):
    person2.send_friend_request(person1)
    person1.friend_requests_to_user.first().accept()
    assert Friendship.objects.count() == 1
    assert Friendship.objects.first().status == Friendship.STATUS_ACCEPTED
    assert person1.friends.count() == 1
    assert list(person1.friends.all()) == [person2]
    assert person2.friends.count() == 1
    assert list(person2.friends.all()) == [person1]


def test_unfriend(person1, person2):
    assert person1.friends.count() == 0
    person1.send_friend_request(person2)
    person2.friend_requests_to_user.first().accept()
    assert person1.friends.count() == 1
    person1.unfriend(person2)
    assert person1.friends.count() == 0


class TestFriendsQueryNumbers(TransactionTestCase):
    def test_with_one_friendship(self):
        p1 = person1()
        p2 = person2()
        p3 = person3()
        friendship(p1, p2)
        with self.assertNumQueries(1):
            p1.friends
        assert set(p1.friends) == set([p2])

        friendship(p1, p3)
        with self.assertNumQueries(1):
            p1.friends
        assert set(p1.friends) == set([p2, p3])
