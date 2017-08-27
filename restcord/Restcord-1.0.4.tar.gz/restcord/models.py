from enum import Enum
import json

CDN_URL = "https://cdn.discordapp.com/"

class ChannelType(Enum):
    text = 0
    private = 1
    voice = 2
    group = 3

    def __str__(self):
        return self.name

class FilterLevel(Enum):
    disabled = 0
    members_without_roles = 1
    all_members = 2
    no = None

class MessageType(Enum):
    default = 0
    recipient_add = 1
    recipient_remove = 2
    call = 3
    channel_name_change = 4
    channel_icon_change = 5
    pins_add = 6
    guild_member_join = 7
    no = None

class ServerRegion(Enum):
    # I should update this.....
    us_west = 'us-west'
    us_east = 'us-east'
    us_south = 'us-south'
    us_central = 'us-central'
    eu_west = 'eu-west'
    eu_central = 'eu-central'
    singapore = 'singapore'
    london = 'london'
    sydney = 'sydney'
    amsterdam = 'amsterdam'
    frankfurt = 'frankfurt'
    brazil = 'brazil'
    vip_us_east = 'vip-us-east'
    vip_us_west = 'vip-us-west'
    vip_amsterdam = 'vip-amsterdam'
    no = None

    def __str__(self):
        return self.value

class VerificationLevel(Enum):
    none = 0
    low = 1
    medium = 2
    high = 3
    table_flip = 3
    very_high = 4
    no = None

    def __str__(self):
        return self.name

def get_from_kwargs(kwargs, key):
    if not kwargs:
        return None
    if key not in kwargs:
        return None
    return kwargs[key]

class Emoji:
    id = None
    name = None
    roles = None
    require_colons = None
    managed = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.name = get_from_kwargs(kwargs, "name")
            self.roles = get_from_kwargs(kwargs, "roles")
            self.require_colons = get_from_kwargs(kwargs, "require_colons")
            self.managed = get_from_kwargs(kwargs, "managed")

def get_emojis(emojis):
    if not emojis:
        return []
    realE = []
    for e in emojis:
        realE.append(Emoji(**e))
    return realE

class Channel:
    id = None
    type = None
    guild_id = None
    position = None
    permission_overwrites = None
    name = None
    topic = None
    last_message_id = None
    bitrate = None
    user_limit = None
    recipients = None
    icon = None
    owner_id = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            type = get_from_kwargs(kwargs, "type")
            if type:
                self.type = ChannelType(int(type))
            self.guild_id = get_from_kwargs(kwargs, "guild_id")
            self.position = get_from_kwargs(kwargs, "position")
            self.permission_overwrites = get_overwrites(get_from_kwargs(kwargs, "permission_overwrites"))
            self.name = get_from_kwargs(kwargs, "name")
            self.topic = get_from_kwargs(kwargs, "topic")
            self.last_message_id = get_from_kwargs(kwargs, "last_message_id")
            self.bitrate = get_from_kwargs(kwargs, "bitrate")
            self.user_limit = get_from_kwargs(kwargs, "user_limit")
            self.recipients = get_from_kwargs(kwargs, "recipients")
            self.icon = get_from_kwargs(kwargs, "icon")
            self.owner_id = get_from_kwargs(kwargs, "owner_id")

def get_channels(chans):
    if not chans:
        return []
    realC = []
    for c in chans:
        realC.append(Channel(**c))
    return realC

class Message:
    id = None
    channel_id = None
    author = None
    content = None
    timestamp = None
    edited_timestamp = None
    tts = None
    mention_everyone = None
    mentions = None
    mention_roles = None
    attachments = None
    embeds = None
    reactions = None
    nonce = None
    pinned = None
    type = None
    webhook_id = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.channel_id = get_from_kwargs(kwargs, "channel_id")
            self.author = get_from_kwargs(kwargs, "author")
            self.content = get_from_kwargs(kwargs, "content")
            self.timestamp = get_from_kwargs(kwargs, "timestamp")
            self.edited_timestamp = get_from_kwargs(kwargs, "edited_timestamp")
            self.tts = get_from_kwargs(kwargs, "tts")
            self.mention_everyone = get_from_kwargs(kwargs, "mention_everyone")
            self.mentions = get_from_kwargs(kwargs, "mentions")
            self.mention_roles = get_from_kwargs(kwargs, "mention_roles")
            self.attachments = get_from_kwargs(kwargs, "attachments")
            self.embeds = get_from_kwargs(kwargs, "embeds")
            self.reactions = get_from_kwargs(kwargs, "reactions")
            self.nonce = get_from_kwargs(kwargs, "nonce")
            self.pinned = get_from_kwargs(kwargs, "pinned")
            self.webhook_id = get_from_kwargs(kwargs, "webhook_id")
            type = get_from_kwargs(kwargs, "type")
            if type:
                self.type = MessageType(int(type))

class Reaction:
    count = None
    me = None
    emoji = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.me = get_from_kwargs(kwargs, "me")
            self.emoji = get_from_kwargs(kwargs, "emoji")

class Overwrite:
    id = None
    type = None
    allow = None
    deny = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.type = get_from_kwargs(kwargs, "type")
            self.allow = get_from_kwargs(kwargs, "allow")
            self.deny = get_from_kwargs(kwargs, "deny")

class Role:
    id = None
    name = None
    color = None
    hoist = None
    position = None
    permissions = None
    managed = None
    mentionable = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.name = get_from_kwargs(kwargs, "name")
            self.color = get_from_kwargs(kwargs, "color")
            self.hoist = get_from_kwargs(kwargs, "hoist")
            self.position = get_from_kwargs(kwargs, "position")
            self.permissions = get_from_kwargs(kwargs, "permissions")
            self.managed = get_from_kwargs(kwargs, "managed")
            self.mentionable = get_from_kwargs(kwargs, "mentionable")

def get_roles(roles):
    if not roles:
        return []
    realR = []
    for r in roles:
        realR.append(Role(**r))
    return realR

def get_overwrites(overwrites):
    if not overwrites:
        return []
    realO = []
    for o in overwrites:
        realO.append(Overwrite(**o))
    return realO

class EmbedThumbnail:
    url = None
    proxy_url =  None
    height = None
    width = None

    def __init__(self, **kwargs):
        if kwargs:
            self.url = get_from_kwargs(kwargs, "url")
            self.proxy_url = get_from_kwargs(kwargs, "proxy_url")
            self.height = get_from_kwargs(kwargs, "height")
            self.width = get_from_kwargs(kwargs, "width")

class EmbedVideo:
    url = None
    height = None
    width = None

    def __init__(self, **kwargs):
        if kwargs:
            self.url = get_from_kwargs(kwargs, "url")
            self.height = get_from_kwargs(kwargs, "height")
            self.width = get_from_kwargs(kwargs, "width")

class EmbedImage:
    url = None
    proxy_url =  None
    height = None
    width = None

    def __init__(self, **kwargs):
        if kwargs:
            self.url = get_from_kwargs(kwargs, "url")
            self.proxy_url = get_from_kwargs(kwargs, "proxy_url")
            self.height = get_from_kwargs(kwargs, "height")
            self.width = get_from_kwargs(kwargs, "width")

class EmbedProvider:
    name = None
    url =  None

    def __init__(self, **kwargs):
        if kwargs:
            self.name = get_from_kwargs(kwargs, "name")
            self.url = get_from_kwargs(kwargs, "url")


class EmbedAuthor:
    name = None
    url =  None
    icon_url =  None
    proxy_icon_url =  None

    def __init__(self, **kwargs):
        if kwargs:
            self.name = get_from_kwargs(kwargs, "name")
            self.url = get_from_kwargs(kwargs, "url")
            self.icon_url = get_from_kwargs(kwargs, "icon_url")
            self.proxy_icon_url = get_from_kwargs(kwargs, "proxy_icon_url")

class EmbedFooter:
    text = None
    icon_url =  None
    proxy_icon_url =  None

    def __init__(self, **kwargs):
        if kwargs:
            self.text = get_from_kwargs(kwargs, "text")
            self.icon_url = get_from_kwargs(kwargs, "icon_url")
            self.proxy_icon_url = get_from_kwargs(kwargs, "proxy_icon_url")

class EmbedField:
    name = None
    value =  None
    inline =  None

    def __init__(self, **kwargs):
        if kwargs:
            self.name = get_from_kwargs(kwargs, "name")
            self.value = get_from_kwargs(kwargs, "value")
            self.inline = get_from_kwargs(kwargs, "inline")

def get_fields(fields):
    if not fields:
        return []
    realFields = []
    for field in fields:
        realFields.append(EmbedField(**field))
    return realFields

class Embed:
    title = None
    type = None
    description = None
    url = None
    timestamp = None
    color = None
    footer = None
    image = None
    thumbnail = None
    video = None
    provider = None
    author = None
    fields = None

    def __init__(self, **kwargs):
        if kwargs:
            self.title = get_from_kwargs(kwargs, "title")
            self.type = get_from_kwargs(kwargs, "type")
            self.description = get_from_kwargs(kwargs, "description")
            self.url = get_from_kwargs(kwargs, "url")
            self.timestamp = get_from_kwargs(kwargs, "timestamp")
            self.color = get_from_kwargs(kwargs, "color")
            self.footer = EmbedFooter(**get_from_kwargs(kwargs, "footer"))
            self.image = EmbedImage(**get_from_kwargs(kwargs, "image"))
            self.thumbnail = EmbedThumbnail(**get_from_kwargs(kwargs, "thumbnail"))
            self.video = EmbedVideo(**get_from_kwargs(kwargs, "video"))
            self.provider = EmbedProvider(**get_from_kwargs(kwargs, "provider"))
            self.author = EmbedAuthor(**get_from_kwargs(kwargs, "author"))
            self.fields = get_fields(**get_from_kwargs(kwargs, "fields"))

    def __str__(self):
        return json.dumps(self.__dict__)

class Attachment:
    id = None
    filename =  None
    size =  None
    url =  None
    proxy_url =  None
    height =  None
    width =  None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.filename = get_from_kwargs(kwargs, "filename")
            self.size = get_from_kwargs(kwargs, "size")
            self.url = get_from_kwargs(kwargs, "url")
            self.proxy_url = get_from_kwargs(kwargs, "proxy_url")
            self.height = get_from_kwargs(kwargs, "height")
            self.width = get_from_kwargs(kwargs, "width")

class Guild:
    id = None
    name = None
    icon =  None
    splash =  None
    owner_id =  None
    region =  None
    afk_channel_id =  None
    afk_timeout =  None
    embed_enabled =  None
    embed_channel_id =  None
    verification_level =  None
    default_message_notifications =  None
    explicit_content_filter =  None
    roles =  None
    emojis =  None
    features =  None
    mfa_level =  None
    widget_enabled =  None
    widget_channel_id =  None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.name = get_from_kwargs(kwargs, "name")
            self.icon = "{}icons/{}/{}.png".format(CDN_URL, self.id, get_from_kwargs(kwargs, "icon"))
            self.splash = "{}splashes/{}/{}.png".format(CDN_URL, self.id, get_from_kwargs(kwargs, "splash"))
            self.owner_id = get_from_kwargs(kwargs, "owner_id")
            self.afk_channel_id = get_from_kwargs(kwargs, "afk_channel_id")
            self.afk_timeout = get_from_kwargs(kwargs, "afk_timeout")
            self.embed_enabled = get_from_kwargs(kwargs, "embed_enabled")
            self.embed_channel_id = get_from_kwargs(kwargs, "embed_channel_id")
            if get_from_kwargs(kwargs, "region"):
                self.region = ServerRegion(get_from_kwargs(kwargs, "region"))
            if get_from_kwargs(kwargs, "verification_level"):
                self.verification_level = VerificationLevel(get_from_kwargs(kwargs, "verification_level"))
            self.default_message_notifications = get_from_kwargs(kwargs, "default_message_notifications")
            if get_from_kwargs(kwargs, "explicit_content_filter"):
                self.explicit_content_filter = FilterLevel(int(get_from_kwargs(kwargs, "explicit_content_filter")))
            self.roles = get_roles(get_from_kwargs(kwargs, "roles"))
            self.emojis = get_emojis(get_from_kwargs(kwargs, "emojis"))
            self.features = get_from_kwargs(kwargs, "features")
            self.mfa_level = get_from_kwargs(kwargs, "mfa_level")
            self.widget_enabled = get_from_kwargs(kwargs, "widget_enabled")
            self.widget_channel_id = get_from_kwargs(kwargs, "widget_channel_id")

class GuildEmbed:
    enabled = None
    channel_id = None

    def __init__(self, **kwargs):
        if kwargs:
            self.enabled = get_from_kwargs(kwargs, "enabled")
            self.channel_id = get_from_kwargs(kwargs, "channel_id")

class User:
    id = None
    username = None
    discriminator = None
    avatar = None
    bot = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.username = get_from_kwargs(kwargs, "username")
            self.discriminator = get_from_kwargs(kwargs, "discriminator")
            self.avatar = get_from_kwargs(kwargs, "avatar")
            self.bot = get_from_kwargs(kwargs, "bot")

def get_recipients(recipients):
    if not recipients:
        return []
    realR = []
    for r in recipients:
        realR.append(User(**r))
    return realR

class GuildMember(User):
    nick = None
    roles = None
    joined_at = None
    deaf = None
    mute = None

    def __init__(self, **kwargs):
        if kwargs:
            super(**get_from_kwargs(kwargs, "user"))
            self.nick = get_from_kwargs(kwargs, "nick")
            self.roles = get_from_kwargs(kwargs, "roles")
            self.joined_at = get_from_kwargs(kwargs, "joined_at")
            self.deaf = get_from_kwargs(kwargs, "deaf")
            self.mute = get_from_kwargs(kwargs, "mute")

class Integration:
    id = None
    name = None
    type = None
    enabled = None
    syncing = None
    role_id = None
    expire_behavior = None
    expire_grace_period = None
    user = None
    account = None
    synced_at = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.name = get_from_kwargs(kwargs, "name")
            self.type = get_from_kwargs(kwargs, "type")
            self.enabled = get_from_kwargs(kwargs, "enabled")
            self.syncing = get_from_kwargs(kwargs, "syncing")
            self.role_id = get_from_kwargs(kwargs, "role_id")
            self.syncing = get_from_kwargs(kwargs, "syncing")
            self.expire_behavior = get_from_kwargs(kwargs, "expire_behavior")
            self.expire_grace_period = get_from_kwargs(kwargs, "expire_grace_period")
            self.user = User(**get_from_kwargs(kwargs, "user"))
            self.account = IntegrationAccount(**get_from_kwargs(kwargs, "account"))
            self.synced_at = get_from_kwargs(kwargs, "synced_at")

class IntegrationAccount:
    id = None
    name = None

    def __init__(self, **kwargs):
        if kwargs:
            self.id = get_from_kwargs(kwargs, "id")
            self.name = get_from_kwargs(kwargs, "name")

class Ban:
    reason = None
    user = None

    def __init__(self, **kwargs):
        if kwargs:
            self.reason = get_from_kwargs(kwargs, "reason")
            self.user = User(**get_from_kwargs(kwargs, "user"))

class Invite:
    code = None
    guild = None
    channel = None

    def __init__(self, **kwargs):
        if kwargs:
            self.code = get_from_kwargs(kwargs, "code")
            self.guild = Guild(**get_from_kwargs(kwargs, "guild"))
            self.channel = Channel(**get_from_kwargs(kwargs, "channel"))
