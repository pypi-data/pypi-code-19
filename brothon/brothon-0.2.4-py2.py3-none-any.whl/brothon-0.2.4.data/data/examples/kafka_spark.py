from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression, NaiveBayes
from pyspark.ml.feature import HashingTF, Tokenizer, StopWordsRemover, CountVectorizer, IDF
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, col, lit

if __name__ == "__main__":
    spark = SparkSession\
        .builder\
        .appName("KafkaSentiment")\
        .getOrCreate()

    # $example on$
    # Prepare training documents from a list of (id, text, label) tuples.
    training = spark.createDataFrame([
        (0, "a b c d e spark", 1.0),
        (1, "b d", 0.0),
        (2, "spark f g h", 1.0),
        (3, "hadoop mapreduce", 0.0)
    ], ["id", "text", "label"])

    # Configure an ML pipeline, which consists of three stages: tokenizer, hashingTF, and lr.
    tokenizer = Tokenizer(inputCol="text", outputCol="words")
    remover = StopWordsRemover(inputCol=tokenizer.getOutputCol(), outputCol="relevant_words")
    hashingTF = HashingTF(inputCol=remover.getOutputCol(), outputCol="rawFeatures")
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    lr = LogisticRegression(maxIter=10, regParam=0.001)
    nb = NaiveBayes(smoothing=1.0, modelType="multinomial")
    pipeline_lr = Pipeline(stages=[tokenizer, remover, hashingTF, idf, lr])
    pipeline_nb = Pipeline(stages=[tokenizer, remover, hashingTF, idf, nb])

    # Fit the pipeline to training documents.
    model_lr = pipeline_lr.fit(training)
    model_nb = pipeline_nb.fit(training)

    testing_data = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "spark-stream").load()
    test_ml = testing_data.selectExpr("1 as id", "CAST(value AS STRING) as text")

    # Make predictions on test documents and print columns of interest.
    prediction_lr = model_lr.transform(test_ml)
    prediction_nb = model_nb.transform(test_ml)
    selected_lr = prediction_lr.select("id", "text", "prediction")
    selected_nb = prediction_nb.select("id", "text", "prediction")
    print ("printing schema")
    selected_lr.printSchema()
    selected_nb.printSchema()
    test_ml.printSchema()

    query = test_ml.writeStream.outputMode("append").format("console").start()
    selected_all=selected_lr.union(selected_nb)
    selected_all.printSchema()
    kafka_write = selected_all.selectExpr("CAST(id AS STRING) as key", "CONCAT(CAST(text AS STRING),':', CAST(prediction AS STRING)) as value").writeStream.format("kafka").option("checkpointLocation", "/tmp/kaf_tgt").option("kafka.bootstrap.servers", "localhost:9092").option("topic", "topic_tgt").start()

    kafka_write.awaitTermination()

    query.awaitTermination()
