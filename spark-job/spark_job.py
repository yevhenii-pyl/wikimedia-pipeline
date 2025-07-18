import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, BooleanType

# Config
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC_INPUT = os.getenv("KAFKA_TOPIC_INPUT", "input")
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", "cassandra")
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "wikimedia")
CASSANDRA_TABLE = os.getenv("CASSANDRA_TABLE", "page_creations")
BATCH_DURATION = int(os.getenv("BATCH_DURATION", 300))

ALLOWED_DOMAINS = [
    "en.wikipedia.org",
    "www.wikidata.org",
    "commons.wikimedia.org"
]

# Define schema for parsing JSON
schema = StructType([
    StructField("meta", StructType([
        StructField("domain", StringType(), True),
        StructField("dt", StringType(), True)
    ]), True),
    StructField("page_title", StringType(), True),
    StructField("performer", StructType([
        StructField("user_id", StringType(), True),
        StructField("user_is_bot", BooleanType(), True)
    ]), True)
])

def main():
    spark = SparkSession.builder \
        .appName("WikimediaSparkJob") \
        .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    print(f"Reading from Kafka topic: {KAFKA_TOPIC_INPUT}")
    print(f"Writing filtered data to Cassandra table: {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE}")

    # Read from Kafka
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC_INPUT) \
        .option("startingOffsets", "latest") \
        .load()

    # Parse JSON
    df_json = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
        .withColumn("data", from_json(col("json_str"), schema)) \
        .select("data.*")

    # Filter and select required fields
    df_filtered = df_json \
        .filter(col("meta.domain").isin(ALLOWED_DOMAINS)) \
        .filter(col("performer.user_is_bot") == False) \
        .selectExpr(
            "performer.user_id as user_id",
            "meta.domain as domain",
            "meta.dt as created_at",
            "page_title"
        )

    # Write filtered data to Cassandra
    query = df_filtered.writeStream \
        .format("org.apache.spark.sql.cassandra") \
        .option("keyspace", CASSANDRA_KEYSPACE) \
        .option("table", CASSANDRA_TABLE) \
        .option("checkpointLocation", "/tmp/spark-checkpoint") \
        .start()

    query.awaitTermination(BATCH_DURATION)
    query.stop()
    print(f"✅ Spark job finished after {BATCH_DURATION} seconds")

if __name__ == "__main__":
    main()
