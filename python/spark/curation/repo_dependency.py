import boto3
import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

import logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root_logger.addHandler(handler)
root_logger.info("check")

def delete_recursive(bucket, path):
    root_logger.info(f'recursive delete: s3:// {bucket} / {path}')
    session = boto3.session.Session()
    boto3_s3 = session.client('s3')
    response = boto3_s3.list_objects_v2(Bucket=bucket, Prefix=path)
    for object in response['Contents']:
        key = object['Key']
        root_logger.info(f'deleting s3://{bucket}/{key}')
        boto3_s3.delete_object(Bucket=bucket, Key=key)

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glue = GlueContext(sc)
spark = glue.spark_session

output_bucket = 'deadmandao'
output_key = 'web3hackernetwork/data_pipeline/curated/repo_dependency'
output_path = f's3://{output_bucket}/{output_key}'

database = 'w3hn'
table = 'raw_dependency'
glue_df = glue.create_dynamic_frame.from_catalog(database=database,
                                                 table_name=table)
spark_df = glue_df.toDF() #Convert to Spark data frame
spark_df.registerTempTable("raw_dependency") #Register in-memory table for SparkSQL

# owner, repo_name, extension, dependency, file_count, partition_key
sql = """
WITH repo_extension AS (
  SELECT partition_key, owner, repo_name, owner_repo, dependency,
    SUBSTR(file_path, 1 + LENGTH(file_path) - POSITION('.' IN REVERSE(file_path))) AS extension
  FROM raw_dependency
)

SELECT partition_key, owner, repo_name, owner_repo, extension, dependency,
  COUNT(1) AS file_count
FROM repo_extension
GROUP BY partition_key, owner, repo_name, owner_repo, extension, dependency
ORDER BY partition_key, owner, repo_name, owner_repo, extension, dependency
"""

out_df = spark.sql(sql)

try:
    delete_recursive(output_bucket, output_key)
except Exception as e:
    root_logger.error(str(e))

out_df.coalesce(1).write.parquet(output_path)
