#!/user/bin/pythom
# -*- coding:UTF-8 -*-


from __future__ import print_function

import os
import sys

import psycopg2

from spark_basic_python.com.tf56.sparkbasic.contextfactory import ContextFactory
from spark_basic_python.com.tf56.sparkbasic import contextfactory

if __name__ == "__main__":

    # 获取当前路径
    # curr_dir = os.path.dirname(os.path.realpath(__file__))
    # config_file = curr_dir + "//..//..//..//..//..//resources//sparkbasic.ini"
    # print (config_file)
    # config = ConfigParser.RawConfigParser()
    # config.read(config_file)
    os.environ["SPARK_HOME"] = "F:\\spark-1.6.1-bin-hadoop2.6"
    # sparkconf = SparkConf()
    # sparkconf.setAppName(config.get("spark", "spark.appName")).setMaster("local[2]")
    # sparkconf.set("spark.streaming.stopGracefullyOnShutdown", "true")
    # sc = SparkContext(conf=sparkconf)
    #
    # hc = ContextFactory.buildhivecontext()
    #
    # lines = sc.textFile("file:////D:\\data\\test.txt", 1)
    # counts = lines.flatMap(lambda x: x.split(' ')) \
    #               .map(lambda x: (x, 1)) \
    #               .reduceByKey(add)
    # output = counts.collect()
    # for (word, count) in output:
    #     print("%s: %i" % (word, count))

    # 原始的连接方式
    # url = "jdbc:postgresql://10.7.12.179:5432/ldw?user=etl-stag-user&password=lujing"
    # driver = {"driver": "org.postgresql.Driver"}
    # table_name = "dwd.dim_region"
    # sqlcontext = SQLContext(sc)
    # data_fram = sqlcontext.read.jdbc(url, table_name, properties=driver)
    # data_fram.show
    # prop = {"dbname": "dwd.dim_region", "user": "etl-stag-user", "password": "lujing", "host": "10.7.12.179",
    #         "port": "5432"}
    # conn = psycopg2.connect(prop)
    try:
        # conn = psycopg2.connect(
        #     database="ldw", user="etl-stag-user", password="lujing", host="10.7.12.179", port="5432")
        # cursor = conn.cursor()
        # conn = ContextFactory.build_pig_connection()
        # cursor = conn.cursor()
        # cursor.execute("SELECT * FROM dwd.dim_region;")
        #
        # #print (cursor.fetchall())
        # pdf = pd.DataFrame(cursor.fetchall())
        # #print (pdf)
        # # todo
        # spark_df = sc.createDataFrame(pdf)
        # #print (spark_df.columns)

        #测试连接pg
        # spark_df = ContextFactory.build_pig_connection("SELECT * FROM dwd.dim_region;")
        # temp = spark_df.collect()
        # for x in temp:
        #     print (x)
        cf = ContextFactory()
        sc1 = cf.build_spark_context()
        print (id(sc1))
        sc2 = cf.build_spark_context()
        print (id(sc2))

        sc30 = cf.build_sql_context()
        print (id(sc30))
        sc31 = cf.build_sql_context()
        print (id(sc31))

        sc4 = cf.build_streaming_context()
        print (id(sc4))
        sc5 = cf.build_hive_context()
        print (id(sc5))

        # print (os.getcwd())
        # print ("----------------")
        # curr_dir = os.path.dirname(os.path.realpath(__file__))
        # print (curr_dir)
    except psycopg2.DatabaseError, exception:
        print (exception)
        sys.exit(1)

