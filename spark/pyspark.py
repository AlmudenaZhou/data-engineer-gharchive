import argparse

import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def add_last_name_by_id(df, id_colname, name_colname, new_colname):
    actor_last_login_by_id = (df
                              .sort(F.col("created_at").asc())
                              .groupBy(id_colname)
                              .agg(F.last(name_colname).alias(new_colname)))
    
    new_df = df.join(actor_last_login_by_id, on=id_colname, how="left")
    return new_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_path', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    input_path = args.input_path
    output = args.output

    spark = SparkSession.builder \
        .appName("Pyspark bigquery") \
        .getOrCreate()
    
    spark.conf.set('persistentGcsBucket', 'gharchive_capstone_project')

    df = spark.read.parquet(input_path)

    df = add_last_name_by_id(df, id_colname="actor_id",
                             name_colname="actor_login",
                             new_colname="last_actor_login")

    df = add_last_name_by_id(df, id_colname="org_id",
                             name_colname="org_login",
                             new_colname="last_org_login")
    
    df = add_last_name_by_id(df, id_colname="repo_id",
                             name_colname="repo_name",
                             new_colname="last_repo_name")
    
    df = df.withColumnRenamed("created_at", "action_time")
    df = df.withColumn("created_at", F.current_timestamp())

    df = df.select("type", "action_time", "last_repo_name", "last_org_login", "last_actor_login", "created_at")

    df.repartition(1) \
        .write.format('bigquery') \
        .option("partitionField", "action_time") \
        .option("partitionType", "DAY") \
        .option("clusteredFields", "last_actor_login") \
        .option("table", output) \
        .mode("overwrite") \
        .save()