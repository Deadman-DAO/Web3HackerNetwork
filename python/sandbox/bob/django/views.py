from django.http import HttpResponse

import boto3
import configparser
import duckdb
import os
import pyarrow.fs as pafs
import pyarrow.parquet as papq

# pip install pyarrow boto3 duckdb pandas # logging

def read_parquet_table(profile, bucket, path):
    cred_path = os.path.expanduser("~")+"/.aws/credentials"
    credentials = configparser.ConfigParser()
    credentials.read(filenames=[cred_path])
    key_id = credentials.get(profile, "aws_access_key_id")
    secret = credentials.get(profile, "aws_secret_access_key")
    fs = pafs.S3FileSystem(access_key=key_id, secret_key=secret)
    return papq.read_table(f'{bucket}/{path}', filesystem=fs)

def index(request):
    pipeline_path = 'web3hackernetwork/data_pipeline'
    dataset_path = f'{pipeline_path}/athena/targetable_hackers/20221129_052341_00041_9bdqq_998d7f1d-e656-47d1-bab5-7ea0acafeaa4'
    targetable = read_parquet_table('w3hn-admin', 'deadmandao', dataset_path)
    conn = duckdb.connect()
    sql = "SELECT author FROM targetable WHERE author LIKE 'Dav%'"
    df = conn.query(sql).to_df()
    authors = [a.replace('<', '&lt;') for a in list(df['author'])]
    authors = [a.replace('>', '&gt;') for a in authors]
    authors = [f'<li>{a}</li>' for a in authors]
    authors = '\n'.join(authors)
    page = f"""
        <html>
          <head><title>I'll be your commander.</title></head>
          <body>
            <h1>Hello, World!</h1>
            <ul>
              {authors}
            </ul>
          </body>
        </html>
    """
    return HttpResponse(page)
