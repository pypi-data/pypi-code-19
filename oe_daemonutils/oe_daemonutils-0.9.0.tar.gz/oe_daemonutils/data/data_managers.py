# -*- coding: utf-8 -*-


class DaemonManager(object):
    def __init__(self, session, feed):
        self.feed = feed
        self.session = session

    def retrieve_last_entry_id(self):
        """
        Get the latest entry id

        :return: The latest entry id
        """
        feed_list = self.session.query(self.feed).all()
        return feed_list[0].id if len(feed_list) > 0 else None

    def update_last_entry_id(self, current, last):
        """
        Update the current entry id with the last entry id

        :param current: current entry id
        :param last: last entry id
        """
        if current is None:
            feed_object = self.feed()
            feed_object.id = last
            self.session.add(feed_object)
        else:
            feed_object = self.session.query(self.feed).filter_by(id=current).one()
            feed_object.id = last
            self.session.merge(feed_object)
