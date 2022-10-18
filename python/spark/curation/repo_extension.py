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
extension_df = spark.sql(extension_sql)
extension_df.coalesce(1).registerTempTable("repo_ext")
# owner repo_name extension total_inserts total_deletes num_files total_commits

cols_tmpl = """  ifnull(@@ext@@.total_inserts, 0) as @@ext@@_inserts, ifnull(@@ext@@.total_deletes, 0) as @@ext@@_deletes,
    ifnull(@@ext@@.num_files, 0) as @@ext@@_files, ifnull(@@ext@@.total_commits, 0) as @@ext@@_commits"""

join_tmpl = """  left outer join repo_ext @@ext@@ on @@ext@@.owner = js.owner and @@ext@@.repo_name = js.repo_name"""

and_tmpl = "  and @@ext@@.extension = '.@@ext@@'"

def convert(tmpl, ext):
    return tmpl.replace('@@ext@@', ext)

summary_sql = f"""
select js.owner, js.repo_name,
{convert(cols_tmpl, 'js')},
{convert(cols_tmpl, 'py')},
{convert(cols_tmpl, 'c')},
{convert(cols_tmpl, 'java')},
{convert(cols_tmpl, 'go')},
{convert(cols_tmpl, 'ts')},
{convert(cols_tmpl, 'cpp')},
{convert(cols_tmpl, 'php')},
{convert(cols_tmpl, 'rb')},
{convert(cols_tmpl, 'cs')},
{convert(cols_tmpl, 'cc')},
{convert(cols_tmpl, 'rs')},
{convert(cols_tmpl, 'tsx')},
{convert(cols_tmpl, 'scala')},
{convert(cols_tmpl, 'jsx')}
from repo_ext js
{convert(join_tmpl, 'py')}
{convert(join_tmpl, 'c')}
{convert(join_tmpl, 'java')}
{convert(join_tmpl, 'go')}
{convert(join_tmpl, 'ts')}
{convert(join_tmpl, 'cpp')}
{convert(join_tmpl, 'php')}
{convert(join_tmpl, 'rb')}
{convert(join_tmpl, 'cs')}
{convert(join_tmpl, 'cc')}
{convert(join_tmpl, 'rs')}
{convert(join_tmpl, 'tsx')}
{convert(join_tmpl, 'scala')}
{convert(join_tmpl, 'jsx')}
where js.extension = '.js'
{convert(and_tmpl, 'py')}
{convert(and_tmpl, 'c')}
{convert(and_tmpl, 'java')}
{convert(and_tmpl, 'go')}
{convert(and_tmpl, 'ts')}
{convert(and_tmpl, 'cpp')}
{convert(and_tmpl, 'php')}
{convert(and_tmpl, 'rb')}
{convert(and_tmpl, 'cs')}
{convert(and_tmpl, 'cc')}
{convert(and_tmpl, 'rs')}
{convert(and_tmpl, 'tsx')}
{convert(and_tmpl, 'scala')}
{convert(and_tmpl, 'jsx')}
order by js.owner, js.repo_name
"""

extensions = """
-- 1 	.js 	26752659 	6782193447 	35514 	matt 	
-- 7 	.py 	7744299 	2204378266 	30277 	matt 	
-- 9 	.c 	7107148 	3344883640 	16678 	matt 	
-- 10 	.java 	14416580 	2502998391 	9809 	bob 	done
-- 13 	.go 	11739795 	4664082430 	5782 	bob 	done
-- 16 	.ts 	5255447 	1137896274 	11218 	matt 	
-- 17 	.cpp 	4027283 	1589483149 	11263 	matt 	
-- 18 	.php 	6557862 	1316149573 	7282 	bob 	weird
-- 22 	.rb 	3048170 	348731047 	9426 	bob 	weird
-- 24 	.cs 	3475557 	623920043 	3972 	matt 	
-- 25 	.cc 	1352095 	619479180 	6673 	matt 	
-- 35 	.rs 	964655 	295521616 	2991 	bob 	hard
-- 38 	.tsx 	839036 	111013387 	3969 	matt 	
-- 54 	.scala 	926666 	123227766 	1414 	bob 	should be doable
-- 55 	.jsx 	345476 	51432270 	3575 	matt 	
"""

out_df = spark.sql(summary_sql)
out_df.coalesce(1).write.parquet(repo_extension_path)

