#!/user/bin/pythom
# -*- coding:UTF-8 -*-
from spark_basic_python.com.tf56.research.main.tag_values import TagValue
from spark_basic_python.com.tf56.sparkbasic.contextfactory import ContextFactory
import json
import time

if __name__ == "__main__":
    tagvalue_list = []
    tag_value = TagValue()
    tag_value.set_value("杭州-南京")
    tag_value.set_alias("杭州-南京")
    tag_value.set_measure(3.0)

    tag_value1 = TagValue()
    tag_value1.set_value("北京-南京")
    tag_value1.set_alias("北京-南京")
    tag_value1.set_measure(5.0)
    tagvalue_list.append(tag_value)
    tagvalue_list.append(tag_value1)

    json_str = json.dumps(tagvalue_list, default=lambda o: o.__dict__, sort_keys=True)

    print (json_str)
    print (json_str())

    # print (time.time())


    # print tag_value.to_json_array()
    #
    # data = [
    #     {
    #         "value": "value1",
    #         "measure":"",
    #         "alias":""
    #     },
    #     {
    #         "value": "value2",
    #         "measure": "",
    #         "alias":""
    #     }
    # ]
    #
    # json_str = json.dumps(data)
    # json_str = json.loads(json_str)
    #
    # print (json_str)


    # cf = ContextFactory()
    # sqc = cf.build_sql_context()
    # sqc.read.json()

