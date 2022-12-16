# --- Run Stats ---------------------------
# 2022-12-16: 10 @ G.2X (20 DPU): 3m49
# -----------------------------------------

# ----- BEGIN SPARK JOB BOILERPLATE --------------------------------
import boto3
import logging
import sys
from pyspark.context import SparkContext
from pyspark.sql import SparkSession

job_name = sys.argv[0]
if '--JOB_NAME' in sys.argv:
    if len(sys.argv) > sys.argv.index('--JOB_NAME') + 1:
        job_name = sys.argv[sys.argv.index('--JOB_NAME') + 1]

pipeline_path = 'web3hackernetwork/data_pipeline'
sc = SparkContext()
spark = SparkSession.builder.config("k1", "v1").getOrCreate()

def get_logger(name):
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(fmt))
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger().addHandler(handler)
    log = logging.getLogger(name=name)
    log.setLevel(logging.INFO)
    return log

log = get_logger(f'{job_name}')

def delete_recursive(bucket, prefix):
    log.info(f'recursive delete: s3:// {bucket} / {prefix}')
    boto3_s3 = boto3.session.Session().client('s3')
    response = boto3_s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for object in response['Contents']:
        key = object['Key']
        log.info(f'deleting s3://{bucket}/{key}')
        boto3_s3.delete_object(Bucket=bucket, Key=key)

def register_table(spark, bucket, tier, name):
    path = f's3://{bucket}/{pipeline_path}/{tier}/{name}'
    table = f'{tier}_{name}'
    log.info(f'registering {path} as table {table}')
    df = spark.read.parquet(path)
    df.registerTempTable(table)

def insert_or_update(df, bucket, tier, name):
    key = f'{pipeline_path}/{tier}/{name}'
    try:
        delete_recursive(bucket, key)
    except Exception as e:
        log.error(str(e))
    url = f's3://{bucket}/{key}'
    log.info(f'writing datset to {url}')
    df.write.parquet(url)
# ----- END SPARK JOB BOILERPLATE ----------------------------------

register_table(spark, 'deadmandao', 'curated', 'repo_hacker')

out_sql = """
WITH base_data (
  WITH repo_author AS (
    SELECT distinct
             owner, repo_name, partition_key, author,
             regexp_extract(author, '(.*) <(.*)>', 1) AS author_name,
             regexp_extract(author, '(.*) <(.*)>', 2) AS author_email
    FROM curated_repo_hacker
  )
  SELECT l.author left_author,
         r.author right_author,
         0 AS name_match, 1 AS email_match,
         count(distinct(r.owner, r.repo_name)) AS num_repos
  FROM repo_author l
  JOIN repo_author r ON r.author_email = l.author_email
                     AND r.author_name != l.author_name
  GROUP BY 1, 2, 3, 4
  UNION
  SELECT l.author left_author,
         r.author right_author,
         1 AS name_match, 0 AS email_match,
         count(distinct(r.owner, r.repo_name)) AS num_repos
  FROM repo_author l
  JOIN repo_author r ON r.author_email != l.author_email
                     AND r.author_name = l.author_name
  GROUP BY 1, 2, 3, 4
)
SELECT left_author, right_author, name_match, email_match, num_repos
FROM base_data
ORDER BY left_author, right_author
"""

log.info(f'executing sql:\n{out_sql}')
out_df = spark.sql(out_sql).coalesce(16)
insert_or_update(out_df, 'deadmandao', 'curated2', 'hacker_alias')
