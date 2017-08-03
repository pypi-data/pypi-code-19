#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import ConfigParser
from pyspark import SparkConf

curr_dir = os.path.dirname(os.path.realpath(__file__))
relative_path = os.sep + ".." + os.sep + ".." + os.sep + ".." + os.sep + "resources"


def load(filename):
    spark_conf = SparkConf()
    spark_conf.setAppName(buildconfig(filename).get("spark", "spark.appName"))
    spark_conf.set("spark.streaming.stopGracefullyOnShutdown", "true")
    spark_conf.setMaster(buildconfig(filename).get("spark", "spark.master"))
    return spark_conf


def get(filename, group, key):
    return buildconfig(filename).get(group, key)


def buildconfig(filename):
    filepath = curr_dir + relative_path + os.sep + filename
    config = ConfigParser.RawConfigParser()
    config.read(filepath)
    return config


def build_config(file_path):
    config = ConfigParser.RawConfigParser()
    config.read(file_path)
    return config
