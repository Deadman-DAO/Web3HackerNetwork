import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

repo_extension_path = "s3://deadmandao/web3hackernetwork/data_pipeline/curated/repo_extension"

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

## Dunno what this is for, the AWS example doesn't have it:
## https://github.com/aws-samples/aws-glue-samples/blob/master/examples/join_and_relationalize.py
# job = Job(glueContext)
# job.init(args['JOB_NAME'], args)
# job.commit()

repo_file = glueContext.create_dynamic_frame.from_catalog(database='w3hn', table_name='raw_repo_file')
repo_file.toDF().registerTempTable("raw_repo_file")
extension_sql = """
select owner, repo_name,
  substr(file_path, 1 + length(file_path) - position('.' in reverse(file_path))) as extension,
  sum(total_inserts) as total_inserts,
  sum(total_deletes) as total_deletes,
  count(distinct(file_path)) as num_files,
  sum(num_commits) as total_commits
from raw_repo_file
where binary = 0
group by owner, repo_name, substr(file_path, 1 + length(file_path) - position('.' in reverse(file_path)))
order by owner, repo_name, extension
"""
out_df = spark.sql(extension_sql)
out_df.coalesce(1).write.parquet(repo_extension_path)
