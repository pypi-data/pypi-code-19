# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2015-2017 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from . import utils
from .errors import InvalidArgument
from .user import BaseUser, User

class Webhook:
    """Represents a Discord webhook.

    Webhooks are a form to send messages to channels in Discord without a
    bot user or authentication.

    Attributes
    ------------
    id: int
        The webhook's ID
    token: str
        The authentication token of the webhook.
    guild_id: Optional[int]
        The guild ID this webhook is for.
    channel_id: Optional[int]
        The channel ID this webhook is for.
    user: Optional[:class:`abc.User`]
        The user this webhook was created by. If the webhook was
        received without authentication then this will be ``None``.
    name: Optional[str]
        The default name of the webhook.
    avatar: Optional[str]
        The default avatar of the webhook.
    """

    __slots__ = ('id', 'guild_id', 'channel_id', 'user', 'name', 'avatar',
                 'token', '_state', '_session')

    def __init__(self, data, *, session=None, state=None):
        self.id = int(data['id'])
        self.channel_id = utils._get_as_snowflake(data, 'channel_id')
        self.guild_id = utils._get_as_snowflake(data, 'guild_id')
        self.name = data.get('name')
        self.avatar = data.get('avatar')
        self.token = data['token']
        self._state = state

        user = data.get('user')
        if user is None:
            self.user = None
        elif state is None:
            self.user = BaseUser(state=None, data=user)
        else:
            self.user = User(state=state, data=user)

    @classmethod
    def unauthenticated(cls, id, token, session):
        data = {
            'id': id,
            'token': token
        }
        return cls(data, session=session)

    @property
    def guild(self):
        """Optional[:class:`Guild`]: The guild this webhook belongs to.

        If this is an unauthenticated webhook, then this will always return ``None``.
        """
        return self._state and self._state.get_guild(self.guild_id)

    @property
    def channel(self):
        """Optional[:class:`TextChannel`]: The text channel this webhook belongs to.

        If this is an unauthenticated webhook, then this will always return ``None``.
        """
        guild = self.guild
        return guild and guild.get_channel(self.channel_id)

    @property
    def avatar_url(self):
        """Returns a friendly URL version of the avatar the webhook has.

        If the webhook does not have a traditional avatar, their default
        avatar URL is returned instead.

        This is equivalent to calling :meth:`avatar_url_as` with the
        default parameters.
        """
        return self.avatar_url_as()

    def avatar_url_as(self, *, format=None, size=1024):
        """Returns a friendly URL version of the avatar the webhook has.

        If the webhook does not have a traditional avatar, their default
        avatar URL is returned instead.

        The format must be one of 'jpeg', 'jpg', or 'png'.
        The size must be a power of 2 between 16 and 1024.

        Parameters
        -----------
        format: Optional[str]
            The format to attempt to convert the avatar to.
            If the format is ``None``, then it is equivalent to png.
        size: int
            The size of the image to display.

        Returns
        --------
        str
            The resulting CDN URL.

        Raises
        ------
        InvalidArgument
            Bad image format passed to ``format` or invalid ``size``.
        """
        if self.avatar is None:
            # Default is always blurple apparently
            return 'https://cdn.discordapp.com/embed/avatars/0.png'

        if not utils.valid_icon_size(size):
            raise InvalidArgument("size must be a power of 2 between 16 and 1024")

        format = format or 'png'

        if format not in ('png', 'jpg', 'jpeg'):
            raise InvalidArgument("format must be one of 'png', 'jpg', or 'jpeg'.")

        return 'https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.{1}?size={2}'.format(self, format, size)
