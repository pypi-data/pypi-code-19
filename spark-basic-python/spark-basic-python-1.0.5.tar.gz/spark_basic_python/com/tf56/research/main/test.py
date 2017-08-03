#!/user/bin/pythom
# -*- coding:UTF-8 -*-

from __future__ import print_function
import json
import os

from pyspark import RDD

from spark_basic_python.com.tf56.research.main.tag_instance import TagInstance
from spark_basic_python.com.tf56.sparkbasic.dataaccess import DataAccess
from spark_basic_python.com.tf56.sparkbasic.contextfactory import ContextFactory

if __name__ == "__main__":
    # conf = SparkConf()
    # conf.setMaster("local[2]")
    # sc = SparkContext(conf=conf)
    # rdd = sc.textFile("file:///aa.txt")
    # print rdd.count()
    # sc.stop()
    os.environ["SPARK_HOME"] = "F:\\spark-1.6.1-bin-hadoop2.6"

    '''
     解析json文件
    '''
    data = {
        'name': 'ACME',
        'shares': 100,
        'price': 542.23
    }

    # 把字典转换为字符串
    json_str = json.dumps(data)

    # json转换为字典
    json_str1 = json.loads(json_str)
    # print(json_str1)
    #
    # print(json_str1['name'])
    # print(json_str1['shares'])
    # print(json_str1['price'])

    '''
        构建的json
    '''

    # class Result(object):
    #     def __init__(self, code, message, response=None):
    #         if response is None:
    #             response = []
    #         self.code = code
    #         self.message = message
    #         self.response = response
    #
    # test_str = '{"code":200,"message":"发送成功","response":[{"code":2,"message":"xxxxxxxx","mobile":"xxxxxx",' \
    #            '"taskId":null},{"code":2,"message":"xxxxxx","mobile":"xxxxxx","taskId":null}]}'
    #
    # result = Result(**json.loads(test_str))

    # import json
    #
    #
    # class JSONObject(object):
    #     def __init__(self):
    #         self.name = 'Ahan'
    #         self.email = 'www@qq.com'
    #         self.age = 26
    #
    #     def set_name(self, name):
    #         self.name = name
    #
    #
    # if __name__ == '__main__':
    #     o = JSONObject()
    #     # o.__setattr__("aaa","bb@qq.com",50)
    #     print (json.dumps(o, default=lambda o: o.__dict__, sort_keys=True, indent=4))

    cf = ContextFactory()
    sc = cf.build_spark_context()

    # TODO 第一步，读取pg的元数据
    meta_sql = "select * from stag.pg_lujing_tags_metadata t where t.tag_key='常发货线路';"
    df = DataAccess.query_pg_inner(meta_sql)
    RDD
    for row in range(len(df)):
        for column in range(len(df[row])):

            # 获取其中某一列的值
            print (df[row][column])

    # TODO 第二步，结合算法输出结果，构造输出的json串
    # TODO 实现tag value的构造
    tag_instance = TagInstance()
    tag_instance.set_target_id(2222)
    tag_instance.set_target_key("常发货地目的地")

    # tag_instance.to_jsonstring是我们标签内部的数据结构
    print(tag_instance.to_jsonstring())

    #
    tag_dic = json.loads(tag_instance.to_jsonstring())

    # TODO 第三步，保存到hive数据库
    day = "2017-08-01"
    
    sc.parallelize(tag_dic).toDF().registerTempTable("table1")
    cf.build_hive_context().sql(
        "insert into pg_lujing_tags_metadata partition(date='${day}') select name,col1,col2 from table1")

