# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.conf import settings


class FriendAbstract(models.Model):
    class Meta:
        abstract = True

    def send_friend_request(self, user):
        Friendship.objects.create(request_from=self, request_to=user)

    def unfriend(self, user):
        Friendship.objects.get(
            Q(request_from=self, request_to=user) |
            Q(request_from=user, request_to=self)
        ).delete()

    @property
    def friend_requests_to_user(self):
        return self.user2.filter(status=Friendship.STATUS_PENDING)

    @property
    def friendships(self):
        return Friendship.objects.filter(
            Q(request_from=self) |
            Q(request_to=self)
        )

    @property
    def friends(self):
        friendships = list(
            self.friendships.filter(status=Friendship.STATUS_ACCEPTED)
                .select_related('request_to__user')
                .select_related('request_from__user')
        )
        friends = self.__class__.objects.filter(
            Q(user__in=[f.request_from.user for f in friendships if f.request_to == self]) |
            Q(user__in=[f.request_to.user for f in friendships if f.request_from == self]))
        return friends


class Friendship(models.Model):
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_PENDING = 'PENDING'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHOICES = (
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_REJECTED, 'Rejected'),
    )

    request_from = models.ForeignKey(settings.FRIEND_MODEL, related_name="user1")
    request_to = models.ForeignKey(settings.FRIEND_MODEL, related_name="user2")
    status = models.CharField(max_length=255, choices=STATUS_CHOICES,
                              default=STATUS_PENDING)

    def accept(self):
        self.status = self.STATUS_ACCEPTED
        self.save()
