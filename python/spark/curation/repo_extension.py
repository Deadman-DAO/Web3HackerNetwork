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
extension_df.registerTempTable("repo_ext")
# owner repo_name extension total_inserts total_deletes num_files total_commits

summary_sql = """
select js.owner, js.repo_name,
-- 1 	.js 	26752659 	6782193447 	35514 	matt 	
  js.total_inserts as js_inserts, js.total_deletes as js_deletes,
  js.num_files as js_files, js.total_commits as js_commits,
-- 7 	.py 	7744299 	2204378266 	30277 	matt 	
  py.total_inserts as py_inserts, py.total_deletes as py_deletes,
  py.num_files as py_files, py.total_commits as py_commits,
-- 9 	.c 	7107148 	3344883640 	16678 	matt 	
  c.total_inserts as c_inserts, c.total_deletes as c_deletes,
  c.num_files as c_files, c.total_commits as c_commits,
-- 10 	.java 	14416580 	2502998391 	9809 	bob 	done
  java.total_inserts as java_inserts, java.total_deletes as java_deletes,
  java.num_files as java_files, java.total_commits as java_commits,
-- 13 	.go 	11739795 	4664082430 	5782 	bob 	done
  go.total_inserts as go_inserts, go.total_deletes as go_deletes,
  go.num_files as go_files, go.total_commits as go_commits,
-- 16 	.ts 	5255447 	1137896274 	11218 	matt 	
  ts.total_inserts as ts_inserts, ts.total_deletes as ts_deletes,
  ts.num_files as ts_files, ts.total_commits as ts_commits,
-- 17 	.cpp 	4027283 	1589483149 	11263 	matt 	
  cpp.total_inserts as cpp_inserts, cpp.total_deletes as cpp_deletes,
  cpp.num_files as cpp_files, cpp.total_commits as cpp_commits,
-- 18 	.php 	6557862 	1316149573 	7282 	bob 	weird
  php.total_inserts as php_inserts, php.total_deletes as php_deletes,
  php.num_files as php_files, php.total_commits as php_commits,
-- 22 	.rb 	3048170 	348731047 	9426 	bob 	weird
  rb.total_inserts as rb_inserts, rb.total_deletes as rb_deletes,
  rb.num_files as rb_files, rb.total_commits as rb_commits,
-- 24 	.cs 	3475557 	623920043 	3972 	matt 	
  cs.total_inserts as cs_inserts, cs.total_deletes as cs_deletes,
  cs.num_files as cs_files, cs.total_commits as cs_commits,
-- 25 	.cc 	1352095 	619479180 	6673 	matt 	
  cc.total_inserts as cc_inserts, cc.total_deletes as cc_deletes,
  cc.num_files as cc_files, cc.total_commits as cc_commits,
-- 35 	.rs 	964655 	295521616 	2991 	bob 	hard
  rs.total_inserts as rs_inserts, rs.total_deletes as rs_deletes,
  rs.num_files as rs_files, rs.total_commits as rs_commits,
-- 38 	.tsx 	839036 	111013387 	3969 	matt 	
  tsx.total_inserts as tsx_inserts, tsx.total_deletes as tsx_deletes,
  tsx.num_files as tsx_files, tsx.total_commits as tsx_commits,
-- 54 	.scala 	926666 	123227766 	1414 	bob 	should be doable
  scala.total_inserts as scala_inserts, scala.total_deletes as scala_deletes,
  scala.num_files as scala_files, scala.total_commits as scala_commits,
-- 55 	.jsx 	345476 	51432270 	3575 	matt 	
  jsx.total_inserts as jsx_inserts, jsx.total_deletes as jsx_deletes,
  jsx.num_files as jsx_files, jsx.total_commits as jsx_commits
-- 1 	.js 	26752659 	6782193447 	35514 	matt 	
from repo_ext js
-- 7 	.py 	7744299 	2204378266 	30277 	matt 	
join repo_ext py on py.owner = js.owner and py.repo_name = js.repo_name
-- 9 	.c 	7107148 	3344883640 	16678 	matt 	
join repo_ext c on c.owner = js.owner and c.repo_name = js.repo_name
-- 10 	.java 	14416580 	2502998391 	9809 	bob 	done
join repo_ext java on java.owner = js.owner and java.repo_name = js.repo_name
-- 13 	.go 	11739795 	4664082430 	5782 	bob 	done
join repo_ext go on go.owner = js.owner and go.repo_name = js.repo_name
-- 16 	.ts 	5255447 	1137896274 	11218 	matt 	
join repo_ext ts on ts.owner = js.owner and ts.repo_name = js.repo_name
-- 17 	.cpp 	4027283 	1589483149 	11263 	matt 	
join repo_ext cpp on cpp.owner = js.owner and cpp.repo_name = js.repo_name
-- 18 	.php 	6557862 	1316149573 	7282 	bob 	weird
join repo_ext php on php.owner = js.owner and php.repo_name = js.repo_name
-- 22 	.rb 	3048170 	348731047 	9426 	bob 	weird
join repo_ext rb on rb.owner = js.owner and rb.repo_name = js.repo_name
-- 24 	.cs 	3475557 	623920043 	3972 	matt 	
join repo_ext cs on cs.owner = js.owner and cs.repo_name = js.repo_name
-- 25 	.cc 	1352095 	619479180 	6673 	matt 	
join repo_ext cc on cc.owner = js.owner and cc.repo_name = js.repo_name
-- 35 	.rs 	964655 	295521616 	2991 	bob 	hard
join repo_ext rs on rs.owner = js.owner and rs.repo_name = js.repo_name
-- 38 	.tsx 	839036 	111013387 	3969 	matt 	
join repo_ext tsx on tsx.owner = js.owner and tsx.repo_name = js.repo_name
-- 54 	.scala 	926666 	123227766 	1414 	bob 	should be doable
join repo_ext scala on scala.owner = js.owner and scala.repo_name = js.repo_name
-- 55 	.jsx 	345476 	51432270 	3575 	matt 	
join repo_ext jsx on jsx.owner = js.owner and jsx.repo_name = js.repo_name
-- 1 	.js 	26752659 	6782193447 	35514 	matt 	
where js.extension = '.js'
-- 7 	.py 	7744299 	2204378266 	30277 	matt 	
and py.extension = '.py'
-- 9 	.c 	7107148 	3344883640 	16678 	matt 	
and c.extension = '.c'
-- 10 	.java 	14416580 	2502998391 	9809 	bob 	done
and java.extension = '.java'
-- 13 	.go 	11739795 	4664082430 	5782 	bob 	done
and go.extension = '.go'
-- 16 	.ts 	5255447 	1137896274 	11218 	matt 	
and ts.extension = '.ts'
-- 17 	.cpp 	4027283 	1589483149 	11263 	matt 	
and cpp.extension = '.cpp'
-- 18 	.php 	6557862 	1316149573 	7282 	bob 	weird
and php.extension = '.php'
-- 22 	.rb 	3048170 	348731047 	9426 	bob 	weird
and rb.extension = '.rb'
-- 24 	.cs 	3475557 	623920043 	3972 	matt 	
and cs.extension = '.cs'
-- 25 	.cc 	1352095 	619479180 	6673 	matt 	
and cc.extension = '.cc'
-- 35 	.rs 	964655 	295521616 	2991 	bob 	hard
and rs.extension = '.rs'
-- 38 	.tsx 	839036 	111013387 	3969 	matt 	
and tsx.extension = '.tsx'
-- 54 	.scala 	926666 	123227766 	1414 	bob 	should be doable
and scala.extension = '.scala'
-- 55 	.jsx 	345476 	51432270 	3575 	matt 	
and jsx.extension = '.jsx'
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

