import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

output_path = "s3://deadmandao/web3hackernetwork/data_pipeline/curated/hacker_extension"

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
out_df.coalesce(1).write.parquet(output_path)
