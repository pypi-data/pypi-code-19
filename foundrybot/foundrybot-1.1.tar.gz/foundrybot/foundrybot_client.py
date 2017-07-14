from foundrybot.error import FoundrybotError
from foundrybot.resources.domain_crawl import DomainCrawlResource
from foundrybot.resources.event import EventResource
from foundrybot.resources.org import OrgResource
from foundrybot.resources.url_snapshot import UrlSnapshotResource
from foundrybot.resources.url_snapshot_content import UrlSnapshotContentResource
from foundrybot.resources.url_snapshot_link import UrlSnapshotLinkResource
from foundrybot.resources.url_snapshot_media import UrlSnapshotMediaResource
from foundrybot.resources.url_snapshot_metadata import UrlSnapshotMetadataResource
from foundrybot.resources.url_snapshot_tag import UrlSnapshotTagResource
from foundrybot.resources.webhook_setting import WebhookSettingResource


class FoundrybotClient:
    @staticmethod
    def create(secret_key):
        return FoundrybotClient(secret_key)

    def __init__(self, secret_key):
        self.secret_key = secret_key

        if self.secret_key is None:
            raise FoundrybotError('Missing required "secretKey".', 'authentication_error')

        self.domain_crawl = DomainCrawlResource(secret_key)
        self.event = EventResource(secret_key)
        self.org = OrgResource(secret_key)
        self.url_snapshot = UrlSnapshotResource(secret_key)
        self.url_snapshot_content = UrlSnapshotContentResource(secret_key)
        self.url_snapshot_link = UrlSnapshotLinkResource(secret_key)
        self.url_snapshot_media = UrlSnapshotMediaResource(secret_key)
        self.url_snapshot_metadata = UrlSnapshotMetadataResource(secret_key)
        self.url_snapshot_tag = UrlSnapshotTagResource(secret_key)
        self.webhook_setting = WebhookSettingResource(secret_key)