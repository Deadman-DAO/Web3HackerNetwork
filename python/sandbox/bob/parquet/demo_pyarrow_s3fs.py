# pyarrow.fs.S3FileSystem
import configparser
import os
import pyarrow.fs as pafs

home_dir = os.path.expanduser("~")
aws_credentials_path = home_dir+"/.aws/credentials"
raw_path = "numstat-bucket/data_pipeline/raw"
partition_path = raw_path + "/repo_file/partition_key=fake_partition/"
# partition_path = raw_path + "/repo_file/partition_key=e3/"

credentials = configparser.ConfigParser()
credentials.read(filenames=[aws_credentials_path])

enigmatt_access_key = credentials.get("enigmatt", "aws_access_key_id")
enigmatt_secret_key = credentials.get("enigmatt", "aws_secret_access_key")

s3fs = pafs.S3FileSystem(access_key=enigmatt_access_key,
                         secret_key=enigmatt_secret_key)
info = s3fs.get_file_info(raw_path)
print(str(info))

s3fs.delete_dir(partition_path)

# /repo_file/partition_key=e3/3ffcf541d971456d8d62dffdfdc6dec5-0.parquet

# import pyarrow.parquet as pq

# # using a URI -> filesystem is inferred
# pq.read_table("s3://my-bucket/data.parquet")
# # using a path and filesystem
# s3 = fs.S3FileSystem(..)
# pq.read_table("my-bucket/data.parquet", filesystem=s3)
