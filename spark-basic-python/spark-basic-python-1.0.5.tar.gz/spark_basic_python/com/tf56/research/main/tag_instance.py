#!/user/bin/pythom
# -*- coding:UTF-8 -*-
import json


class TagInstance:

    def __init__(self, target_id=None, tag_key=None, unit=None, version=None, label=None, tag_desc=None, tags=None,
                 refresh_cycle=None, is_expired=None, is_enabled=None, refresh_ts=None):
        self.target_id = target_id
        self.tag_key = tag_key
        self.unit = unit
        self.version = version
        self.label = label
        self.tag_desc = tag_desc
        self.tags = tags
        self.refresh_cycle = refresh_cycle
        self.is_expired = is_expired
        self.is_enabled = is_enabled
        self.refresh_cycle = refresh_cycle

    def set_target_id(self, target_id):
        self.target_id = target_id

    def set_target_key(self, target_key):
        self.tag_key = target_key

    def set_unit(self, unit):
        self.unit = unit

    def set_version(self, version):
        self.version = version

    def set_label(self, label):
        self.label = label

    def set_tag_desc(self, tag_desc):
        self.tag_desc = tag_desc

    def set_tags(self, tags):
        self.tags = tags

    def set_refresh_cycle(self, refresh_cycle):
        self.refresh_cycle = refresh_cycle

    def set_is_expired(self, is_expired):
        self.is_expired = is_expired

    def set_is_is_enabled(self, is_enabled):
        self.is_enabled = is_enabled

    def to_jsonstring(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)