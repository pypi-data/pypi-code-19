#!/user/bin/pythom
# -*- coding:UTF-8 -*-
from pyspark import SparkContext
from pyspark import SparkConf

if __name__ == "__main__":
    conf = SparkConf()
    conf.setMaster("local[2]")
    sc = SparkContext(conf=conf)
    rdd = sc.textFile("file:///aa.txt")
    print rdd.count()
    sc.stop()

