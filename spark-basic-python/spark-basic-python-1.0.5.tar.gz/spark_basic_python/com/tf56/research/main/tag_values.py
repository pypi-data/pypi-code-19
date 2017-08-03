#!/user/bin/pythom
# -*- coding:UTF-8 -*-
import json


class TagValue:
    def __init__(self, value=None, alias=None, measure=None):
        self.value = value
        self.alias = alias
        self.measure = measure
        print ("this object is contruct tag-values")

    def set_value(self, value):
        self.value = value

    def set_alias(self, alias):
        self.alias = alias

    def set_measure(self, measure):
        self.measure = measure

    # 转换为json格式,为了
    def to_json_array(self):
        json_string = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
        json_array = "[" + json_string + "]"
        return json_array