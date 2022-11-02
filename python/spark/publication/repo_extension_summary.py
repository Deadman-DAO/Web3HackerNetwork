# --- Run Stats ---------------------------
# 2022-11-02: 2 @ G.2X (4 DPU): 1m4s
# 2022-11-02: 2 @ G.1X (2 DPU): 1m12s
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

register_table( spark, 'deadmandao', 'curated', 'repo_extension')

out_sql = """
select repo.owner, repo.repo_name,
  coalesce(js.total_inserts, 0) as js_inserts, coalesce(js.total_deletes, 0) as js_deletes,
    coalesce(js.num_files, 0) as js_files, coalesce(js.total_commits, 0) as js_commits,
  coalesce(py.total_inserts, 0) as py_inserts, coalesce(py.total_deletes, 0) as py_deletes,
    coalesce(py.num_files, 0) as py_files, coalesce(py.total_commits, 0) as py_commits,
  coalesce(c.total_inserts, 0) as c_inserts, coalesce(c.total_deletes, 0) as c_deletes,
    coalesce(c.num_files, 0) as c_files, coalesce(c.total_commits, 0) as c_commits,
  coalesce(java.total_inserts, 0) as java_inserts, coalesce(java.total_deletes, 0) as java_deletes,
    coalesce(java.num_files, 0) as java_files, coalesce(java.total_commits, 0) as java_commits,
  coalesce(go.total_inserts, 0) as go_inserts, coalesce(go.total_deletes, 0) as go_deletes,
    coalesce(go.num_files, 0) as go_files, coalesce(go.total_commits, 0) as go_commits,
  coalesce(ts.total_inserts, 0) as ts_inserts, coalesce(ts.total_deletes, 0) as ts_deletes,
    coalesce(ts.num_files, 0) as ts_files, coalesce(ts.total_commits, 0) as ts_commits,
  coalesce(cpp.total_inserts, 0) as cpp_inserts, coalesce(cpp.total_deletes, 0) as cpp_deletes,
    coalesce(cpp.num_files, 0) as cpp_files, coalesce(cpp.total_commits, 0) as cpp_commits,
  coalesce(php.total_inserts, 0) as php_inserts, coalesce(php.total_deletes, 0) as php_deletes,
    coalesce(php.num_files, 0) as php_files, coalesce(php.total_commits, 0) as php_commits,
  coalesce(rb.total_inserts, 0) as rb_inserts, coalesce(rb.total_deletes, 0) as rb_deletes,
    coalesce(rb.num_files, 0) as rb_files, coalesce(rb.total_commits, 0) as rb_commits,
  coalesce(cs.total_inserts, 0) as cs_inserts, coalesce(cs.total_deletes, 0) as cs_deletes,
    coalesce(cs.num_files, 0) as cs_files, coalesce(cs.total_commits, 0) as cs_commits,
  coalesce(cc.total_inserts, 0) as cc_inserts, coalesce(cc.total_deletes, 0) as cc_deletes,
    coalesce(cc.num_files, 0) as cc_files, coalesce(cc.total_commits, 0) as cc_commits,
  coalesce(rs.total_inserts, 0) as rs_inserts, coalesce(rs.total_deletes, 0) as rs_deletes,
    coalesce(rs.num_files, 0) as rs_files, coalesce(rs.total_commits, 0) as rs_commits,
  coalesce(tsx.total_inserts, 0) as tsx_inserts, coalesce(tsx.total_deletes, 0) as tsx_deletes,
    coalesce(tsx.num_files, 0) as tsx_files, coalesce(tsx.total_commits, 0) as tsx_commits,
  coalesce(scala.total_inserts, 0) as scala_inserts, coalesce(scala.total_deletes, 0) as scala_deletes,
    coalesce(scala.num_files, 0) as scala_files, coalesce(scala.total_commits, 0) as scala_commits,
  coalesce(jsx.total_inserts, 0) as jsx_inserts, coalesce(jsx.total_deletes, 0) as jsx_deletes,
    coalesce(jsx.num_files, 0) as jsx_files, coalesce(jsx.total_commits, 0) as jsx_commits
from (
  select distinct owner, repo_name from curated_repo_extension
) repo
  left outer join curated_repo_extension js
    on js.owner = repo.owner and js.repo_name = repo.repo_name and js.extension = '.js'
  left outer join curated_repo_extension py
    on py.owner = repo.owner and py.repo_name = repo.repo_name and py.extension = '.py'
  left outer join curated_repo_extension c
    on c.owner = repo.owner and c.repo_name = repo.repo_name and c.extension = '.c'
  left outer join curated_repo_extension java
    on java.owner = repo.owner and java.repo_name = repo.repo_name and java.extension = '.java'
  left outer join curated_repo_extension go
    on go.owner = repo.owner and go.repo_name = repo.repo_name and go.extension = '.go'
  left outer join curated_repo_extension ts
    on ts.owner = repo.owner and ts.repo_name = repo.repo_name and ts.extension = '.ts'
  left outer join curated_repo_extension cpp
    on cpp.owner = repo.owner and cpp.repo_name = repo.repo_name and cpp.extension = '.cpp'
  left outer join curated_repo_extension php
    on php.owner = repo.owner and php.repo_name = repo.repo_name and php.extension = '.php'
  left outer join curated_repo_extension rb
    on rb.owner = repo.owner and rb.repo_name = repo.repo_name and rb.extension = '.rb'
  left outer join curated_repo_extension cs
    on cs.owner = repo.owner and cs.repo_name = repo.repo_name and cs.extension = '.cs'
  left outer join curated_repo_extension cc
    on cc.owner = repo.owner and cc.repo_name = repo.repo_name and cc.extension = '.cc'
  left outer join curated_repo_extension rs
    on rs.owner = repo.owner and rs.repo_name = repo.repo_name and rs.extension = '.rs'
  left outer join curated_repo_extension tsx
    on tsx.owner = repo.owner and tsx.repo_name = repo.repo_name and tsx.extension = '.tsx'
  left outer join curated_repo_extension scala
    on scala.owner = repo.owner and scala.repo_name = repo.repo_name and scala.extension = '.scala'
  left outer join curated_repo_extension jsx
    on jsx.owner = repo.owner and jsx.repo_name = repo.repo_name and jsx.extension = '.jsx'
order by repo.owner, repo.repo_name
"""

log.info(f'executing sql:\n{out_sql}')
out_df = spark.sql(out_sql).coalesce(1)
insert_or_update(out_df, 'deadmandao', 'published', 'repo_extension')
