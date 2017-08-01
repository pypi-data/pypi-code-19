#!/user/bin/pythom
# -*- coding:UTF-8 -*-
from pyspark import SparkContext
from pyspark import SparkConf
from spark_basic_python.com.tf56.sparkbasic.contextfactory import ContextFactory

if __name__ == "__main__":
    # 读取本地文件
    # conf = SparkConf()
    # conf.setMaster("local[2]")
    # sc = SparkContext(conf=conf)
    # rdd = sc.textFile("file:///aa.txt")
    # print rdd.count()

    cf = ContextFactory

    # hive本地不支持查询
    df = cf.build_hive_context().sql("select region_area_cd from ldw_dwd.dim_region limit 10;")
    print (df.columns)
    # sc.stop()

