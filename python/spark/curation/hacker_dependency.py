# --- Run Stats ---------------------------
# 2022-11-02: 4 @ G.2X (8 DPU): 2m12s
# 2022-11-02: 2 @ G.2X (4 DPU): 3m51s
# 2022-11-05: 2 @ G.2X (4 DPU): 3m35s
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

register_table(spark, 'deadmandao', 'raw', 'dependency')
register_table(spark, 'deadmandao', 'raw', 'blame')

out_sql = """
WITH repo_extension AS (
  SELECT partition_key, owner_repo, file_path, dependency
  FROM raw_dependency
),
hacker_blame AS (
  SELECT partition_key, owner_repo, file_path, line_count,
    author_name, author_email, concat(author_name, ' <', author_email, '>') as author,
    SUBSTR(file_path, 1 + LENGTH(file_path) - POSITION('.' IN REVERSE(file_path))) AS extension
  FROM raw_blame
)

SELECT b.author, b.extension, e.dependency, sum(b.line_count) as line_count
FROM hacker_blame b
JOIN repo_extension e ON e.partition_key = b.partition_key
                      AND e.owner_repo = b.owner_repo
                      AND e.file_path = b.file_path
GROUP BY b.author, b.extension, e.dependency
ORDER BY b.author, b.extension, e.dependency
"""

log.info(f'executing sql:\n{out_sql}')
out_df = spark.sql(out_sql).coalesce(1)
insert_or_update(out_df, 'deadmandao', 'curated', 'hacker_dependency')
