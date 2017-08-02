from pyspark.sql import SparkSession


def acquire_session(app_name='SparkBucketResolution'):
    """
    
    :param app_name: 
    :return: 
    """
    spark = SparkSession \
        .builder \
        .appName(app_name) \
        .getOrCreate()

    return spark


def acquire_context(app_name='SparkBucketResolution'):
    """
    Starts spark session
    :return: 
    """
    session = acquire_session()
    sc = session.sparkContext
    sc.setLogLevel('ERROR')
    return sc