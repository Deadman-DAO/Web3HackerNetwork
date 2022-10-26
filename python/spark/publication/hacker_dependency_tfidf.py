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
output_key = 'web3hackernetwork/data_pipeline/published/hacker_dependency_tfidf'
output_path = f's3://{output_bucket}/{output_key}'

database = 'w3hn'
deps_table = 'curated_hacker_dependency'
deps_df = glue.create_dynamic_frame.from_catalog(database=database,
                                                 table_name=deps_table)
deps_df.toDF().registerTempTable(deps_table) #Register table for SparkSQL

def three_steps():
    term_doc_sql = """
      SELECT extension, dependency,
        ln(1 + count(distinct(author))) AS doc_count
      FROM curated_hacker_dependency
      GROUP BY extension, dependency
    """
    spark.sql(term_doc_sql).cache().registerTempTable('term_doc_count')

    doc_term_sql = """
      SELECT author, extension, dependency, ln(1 + line_count) AS term_count
      FROM curated_hacker_dependency
    """
    spark.sql(doc_term_sql).registerTempTable('doc_term_count')

    out_sql = """
    SELECT dt.author, dt.extension, dt.dependency, round(dt.term_count / td.doc_count, 2) AS tfidf
    FROM term_doc_count td
    JOIN doc_term_count dt ON dt.extension = td.extension AND dt.dependency = td.dependency
    """

    out_df = spark.sql(out_sql)
    return out_df

def one_step():
    sql = """
    WITH term_doc_count AS (
      SELECT extension, dependency,
        ln(1 + count(distinct(author))) AS doc_count
      FROM curated_hacker_dependency
      GROUP BY extension, dependency
    ),
    doc_term_count AS (
      SELECT author, extension, dependency, ln(1 + line_count) AS term_count
      FROM curated_hacker_dependency
    )
    SELECT dt.author, dt.extension, dt.dependency, round(dt.term_count / td.doc_count, 2) AS tfidf
    FROM term_doc_count td
    JOIN doc_term_count dt ON dt.extension = td.extension AND dt.dependency = td.dependency
    """

    out_df = spark.sql(out_sql)
    return out_df

out_df = one_step()

try:
    delete_recursive(output_bucket, output_key)
except Exception as e:
    root_logger.error(str(e))

out_df.coalesce(1).write.parquet(output_path)


