import boto3
import botocore
import bz2
import configparser
import json
import os
import pyarrow.fs as pafs

class AWSUtil:
    def __init__(self,
                 profile="default",
                 key_id=None,
                 secret=None):
        if profile != None and (key_id == None or secret == None):
            home_dir = os.path.expanduser("~")
            aws_credentials_path = home_dir+"/.aws/credentials"
            credentials = configparser.ConfigParser()
            credentials.read(filenames=[aws_credentials_path])
            key_id = credentials.get(profile, "aws_access_key_id")
            secret = credentials.get(profile, "aws_secret_access_key")

        if key_id != None and secret != None:
            self.key_id = key_id
            self.secret = secret
            self.session = boto3.session.Session(
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.secret
            )
        else:
            self.session = boto3.session.Session()

class S3Util(AWSUtil):
    def __init__(self,
                 bucket_name="numstat-bucket",
                 profile="default",
                 key_id=None,
                 secret=None):
        super().__init__(profile, key_id, secret)
        self.s3r = self.session.resource('s3')
        self.client = self.session.client('s3')
        self.bucket = self.s3r.Bucket(bucket_name)

    def pyarrow_fs(self):
        return pafs.S3FileSystem(access_key=self.key_id,
                                 secret_key=self.secret)

    def path_exists(self, path):
        bucket_path = f"{self.bucket.name}/{path}/"
        path_info = self.pyarrow_fs().get_file_info(bucket_path)
        return path_info.type != pafs.FileType.NotFound

    # suffix should be something like 'dependency_map.json.bz2'
    # or 'log_numstat.out.json.bz2' or 'blame_map.json.bz2'
    def get_json_obj_from_bz2(self, owner, repo_name, suffix):
        key = f'repo/{owner}/{repo_name}/{suffix}'
        s3_obj = self.client.get_object(Bucket=self.bucket.name,Key=key)
        compressed = s3_obj['Body'].read()
        text = bz2.decompress(compressed)
        obj = json.loads(text)
        return obj

    def get_blame_map(self, owner, repo_name):
        suffix = 'blame_map.json.bz2'
        return self.get_json_obj_from_bz2(owner, repo_name, suffix)
    
    def get_dependency_map(self, owner, repo_name):
        suffix = 'dependency_map.json.bz2'
        return self.get_json_obj_from_bz2(owner, repo_name, suffix)

    def get_numstat(self, owner, repo_name):
        suffix = 'log_numstat.out.json.bz2'
        return self.get_json_obj_from_bz2(owner, repo_name, suffix)

    # arg: path: everything after s3://bucket-name/
    #   example: 'web3hackernetwork/data_pipeline/curated/hacker_extension
    def delete_recursive(self, path):
        response = self.client.list_objects_v2(Bucket=self.bucket.name,
                                               Prefix=path)
        for object in response['Contents']:
            print('Deleting', object['Key'])
            self.client.delete_object(Bucket=self.bucket.name, Key=object['Key'])
