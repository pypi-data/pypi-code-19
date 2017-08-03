#!/user/bin/pythom
# -*- coding:UTF-8 -*-

from __future__ import print_function
from  spark_basic_python.com.tf56.research.main.tag_values import TagValue
import json
import os
from pyspark.sql import *

from pyspark import RDD
from pyspark.sql.types import *

from spark_basic_python.com.tf56.research.main.tag_instance import TagInstance
from spark_basic_python.com.tf56.sparkbasic.dataaccess import DataAccess
from spark_basic_python.com.tf56.sparkbasic.contextfactory import ContextFactory

if __name__ == "__main__":
    os.environ["SPARK_HOME"] = "F:\\spark-1.6.1-bin-hadoop2.6"

    cf = ContextFactory()
    sc = cf.build_spark_context()
    hc = cf.build_hive_context()
    # tg = TagValue()
    # tg.set_measure(30)
    # tg.set_alias("常发货线路")
    # 结构体数据不支持，“this object is contruct tag-values”
    # data = [{"value":"40-58","alias":"小体积","measure":0.3},{"value":"58-140","alias":"中等体积","measure":0.2},{"value":"140+","alias":"大体积","measure":0.1}]
    # tg.set_value(data)

    data11 = [("aa", 6, 1.0, "常发货线路",
               ([("40-58", "小体积", 0.3), ("58-140", "中等体积", 0.2), ("140+", "大体积", 0.1)]),
               "无", "常发货线路", "cc", "用户，发货")]
    rdd = sc.parallelize(data11)


    # 定义schema好后，保存数据
    # schema = StructType([StructField("refresh_date", StringType, True), [StructField("party_id", IntegerType, True),
    #                     StructField("version", DoubleType, True)], [StructField("tag_key", StringType, True)],
    #                     StructField("tag_value", ArrayType[StructType([StructField("value", StringType, True),
    #                                                                     StructField("alias", StringType, True), StructField("measure", DoubleType, True)])]),
    #                     StructField("unit", StringType, True), StructField("label", StringType, True),
    #                     StructField("tag_desc", StringType, True), StructField("tags", StringType, True)])

    schema = StructType([StructField("refresh_date", StringType(), True), StructField("party_id", IntegerType(), True),
                        StructField("version", DoubleType(), True), StructField("tag_key", StringType(), True),
                        StructField("tag_value", ArrayType(StructType([StructField("value", StringType(), True),
                                                                       StructField("alias", StringType(), True),
                                                                       StructField("measure", DoubleType(), True)]))),
                        StructField("unit", StringType(), True), StructField("label", StringType(), True),
                        StructField("tag_desc", StringType(), True), StructField("tags", StringType(), True)])
    # schema.printTreeString()
    df2 = hc.createDataFrame(rdd, schema)
    # dftest = DataFrame()
    # dftest.printSchema
    # dftest.show
    df2.printSchema()
    df2.show()









