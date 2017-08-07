from trunity_migrator import settings
from trunity_migrator.trunity_2_client import Client as Trunity2Client
from trunity_migrator.fixers import *
from trunity_migrator.html_fixer import HTMLFixer

from trunity_3_client import (
    initialize_session_from_creds,
    TopicsClient,
    ContentsClient,
    ContentType,
    SitesClient,
    SiteType,
)


class RootTopicIdError(IOError):
    """
    Raise when can't find root topic in Trunity 2
    """
    pass


class Vertex(object):

    def __init__(self, uploaded_topic_id, join):
        self.uploaded_topic_id = uploaded_topic_id
        self.join = join


class Migrator(object):

    def __init__(self, trunity_2_login, trunity_2_password,
                 trunity_3_login, trunity_3_password,
                 html_fixer: HTMLFixer=None):

        self._trunity_2_client = Trunity2Client(
            trunity_2_login, trunity_2_password
        )

        self._trunity_3_session = initialize_session_from_creds(
            trunity_3_login, trunity_3_password
        )
        self._topics_client = TopicsClient(self._trunity_3_session)
        self._contents_client = ContentsClient(self._trunity_3_session)

        self._trunity_3_side_id = None

        self._trunity_2_root_topic_id, self._trunity_2_site_id = None, None
        self._cur_topic_id = None

        self._queue = []

        self._html_fixer = html_fixer

    def _create_new_site(self, title: str):
        """
        Create new book (site) on Trunity 3 and return site_id.
        :param title:
        :return: site_id
        """
        print("Creating new book: {}".format(title), end='')

        sites_client = SitesClient(self._trunity_3_session)
        site_id = sites_client.list.post(
            name=title,
            site_type=SiteType.TEXTBOOK,
            description=''
        )

        # TODO: make description argument optional.

        print('\t\t[SUCCESS!]')
        return site_id

    def _get_trunity_2_site_info(self, site_name):
        """
        Returns root_topic_id and site_id.
        :param site_name:
        :return:
        """
        sites = self._trunity_2_client.get_user_sites('All')
        for site in sites:
            if site['name'] == site_name:
                return site['rootTopic'], site['siteId']

        raise RootTopicIdError(
            "Can't retrieve Trunity 2 book info by book name!"
        )

    def upload_content(self, title, body, topic_id=None):
        print("Uploading content: {}".format(title), end='')

        if self._html_fixer:
            body = self._html_fixer.apply(body)

        self._contents_client.list.post(
            site_id=self._trunity_3_side_id,
            content_title=title,
            content_type=ContentType.ARTICLE,
            text=body,
            topic_id=topic_id,
        )

        print('\t\t[SUCCESS!]')

    def _create_chapter(self, title, topic_id=None, short_name=None):
        print('Creating new chapter: {}'.format(title), end='')

        new_chapter_id = self._topics_client.list.post(
            site_id=self._trunity_3_side_id,
            name=title,
            topic_id=topic_id,
            short_name=short_name,
        )

        print('\t\t[SUCCESS!]')

        return new_chapter_id

    def _get_topic_joins(self, topic_id):
        return self._trunity_2_client.get_topic_joins(
            self._trunity_2_site_id, topic_id
        )

    @staticmethod
    def _get_type_of_join(join):
        return join.get('type', None)

    def _is_join_is_content(self, join):

        content_type = self._get_type_of_join(join)

        if content_type in settings.CONTENT_TYPES:
            return True
        else:
            return False

    def _is_join_is_chapter(self, join):

        content_type = self._get_type_of_join(join)

        if content_type == 'topics':
            return True
        else:
            return False

    def _update_queue_by_joins(self, topic_id, topic_joins):
        queue = [
            Vertex(uploaded_topic_id=topic_id, join=join)
            for join in topic_joins
        ]
        self._queue.extend(queue)

    def _upload_topic_joins(self):

        while self._queue:
            vertex = self._queue.pop(0)

            if self._is_join_is_content(vertex.join):

                self.upload_content(
                    title=vertex.join['title'],
                    body=vertex.join['body'],
                    topic_id=vertex.uploaded_topic_id
                )

            elif self._is_join_is_chapter(vertex.join):

                new_topic_id = self._create_chapter(
                    title=vertex.join['title'],
                    topic_id=vertex.uploaded_topic_id,
                    short_name=None,  # TODO: add short_name
                )

                topic_joins = self._get_topic_joins(vertex.join['_id'])
                self._update_queue_by_joins(
                    topic_id=new_topic_id,
                    topic_joins=topic_joins,
                )

    def migrate_book(self, book_title, new_book_title):

        self._trunity_3_side_id = self._create_new_site(new_book_title)

        self._trunity_2_root_topic_id, self._trunity_2_site_id = \
            self._get_trunity_2_site_info(book_title)

        root_topic_joins = self._get_topic_joins(self._trunity_2_root_topic_id)

        self._update_queue_by_joins(
            topic_id=None,
            topic_joins=root_topic_joins
        )
        self._upload_topic_joins()


if __name__ == '__main__':

    migrator = Migrator(
        trunity_2_login=settings.TRUNITY_2_LOGIN,
        trunity_2_password=settings.TRUNITY_2_PASSWORD,
        trunity_3_login=settings.TRUNITY_3_LOGIN,
        trunity_3_password=settings.TRUNITY_3_PASSWORD,
    )

    # print(migrator._trunity_2_root_topic_id)

    migrator.migrate_book(
        settings.TRUNITY_2_BOOK_NAME,
        settings.TRUNITY_3_BOOK_NAME
    )

