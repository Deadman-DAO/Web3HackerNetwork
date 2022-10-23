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

output_bucket = 'deadmandao'
output_key = 'web3hackernetwork/data_pipeline/curated/hacker_extension'
output_path = f's3://{output_bucket}/{output_key}'

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

## Dunno what this is for, the AWS example doesn't have it:
## https://github.com/aws-samples/aws-glue-samples/blob/master/examples/join_and_relationalize.py
# job = Job(glueContext)
# job.init(args['JOB_NAME'], args)
# job.commit()

glue_hacker_file = glueContext.create_dynamic_frame.from_catalog(database='w3hn', table_name='raw_file_hacker')
hacker_data_frame = glue_hacker_file.toDF() #Convert to Spark data frame
hacker_data_frame.registerTempTable("temp_file_hacker") #Register in-memory table accessible from sparc

extension_sql = """
select author,
  substr(file_path, 1 + length(file_path) - position('.' in reverse(file_path))) as extension,
  sum(total_inserts) as total_inserts,
  sum(total_deletes) as total_deletes,
  count(distinct(commit_date)) as num_commits,
  count(distinct(file_path)) as num_files
from temp_file_hacker
where binary = 0
group by author, substr(file_path, 1 + length(file_path) - position('.' in reverse(file_path)))
order by author, extension
"""
out_df = spark.sql(extension_sql)

try:
    delete_recursive('deadmandao', output_key)
except Exception as e:
    root_logger.error(str(e))

out_df.coalesce(1).write.parquet(output_path)
