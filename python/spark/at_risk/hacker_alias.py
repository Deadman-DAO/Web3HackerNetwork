# --- Run Stats ---------------------------
# 2022-11-02: 2 @ G.2X (4 DPU): 
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

register_table( spark, 'deadmandao', 'athena', 'targetable_hackers')
register_table( spark, 'deadmandao', 'curated', 'repo_hacker')

out_sql = """
WITH dupe_finder AS (
  SELECT regexp_extract(author, '(.*) <(.*)>', 1) AS author_name,
         regexp_extract(author, '(.*) <(.*)>', 2) AS author_email,
         author
    FROM athena_targetable_hackers WHERE time_range = 't24m'
),
same_person AS (
  WITH identity_matcher AS (
    SELECT owner_repo,
           author
      FROM curated_repo_hacker
      WHERE extension = '.java'
  )
  SELECT DISTINCT im1.author AS author1,
         im2.author AS author2
    FROM identity_matcher im1
    JOIN identity_matcher im2 ON im2.owner_repo = im1.owner_repo
                              AND im2.author != im1.author
)
-- same email address
SELECT -- df1.author_name,
       regexp_extract(df1.author_email, '(.*)@(.*)', 2) AS author_email_domain,
       md5(df1.author_email) AS author_email_hash,
       df2.author_name AS alias_name,
       regexp_extract(df2.author_email, '(.*)@(.*)', 2) AS alias_email_domain,
       md5(df2.author_email) AS alias_email_hash
  FROM dupe_finder df1
  JOIN dupe_finder df2 ON df2.author_email = df1.author_email
                       AND df2.author != df1.author
-- remove duplicates
UNION
-- same name AND worked on same project
SELECT -- df1.author_name,
       regexp_extract(df1.author_email, '(.*)@(.*)', 2) AS author_email_domain,
       md5(df1.author_email) AS author_email_hash,
       df2.author_name AS alias_name,
       regexp_extract(df2.author_email, '(.*)@(.*)', 2) AS alias_email_domain,
       md5(df2.author_email) AS alias_email_hash
  FROM dupe_finder df1
  JOIN dupe_finder df2 ON df2.author_name = df1.author_name
                       AND df2.author != df1.author
  JOIN same_person sp ON sp.author1 = df1.author
                      AND sp.author2 = df2.author
"""

log.info(f'executing sql:\n{out_sql}')
out_df = spark.sql(out_sql).coalesce(1)
insert_or_update(out_df, 'deadmandao-at-risk', 'web_data', 'hacker_alias')
