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
    requested_email_hash = '27b1eb8d546b792bdf8dccf959610097'
    pipeline_path = 'web3hackernetwork/data_pipeline'
    dataset_path = f'{pipeline_path}/web_data/hacker_alias/'
    repo_hacker = read_parquet_table('w3hn-at-risk', 'deadmandao-at-risk', dataset_path)
    conn = duckdb.connect()
    sql = f"""
      SELECT alias_name, alias_email_domain, alias_email_hash
        FROM repo_hacker
        WHERE author_email_hash = '{requested_email_hash}'
    """
    df = conn.query(sql).to_df()
    names = list(df['alias_name'])
    domains = list(df['alias_email_domain'])
    hashes = list(df['alias_email_hash'])
    items = list()
    for i, name in enumerate(names):
        domain = domains[i]
        hazh = hashes[i]
        display = f'{name} *****@{domain}'
        link = f'<a href="/hacker/?email_hash={hazh}">{display}</a>'
        item = f'<li>{link}</li>'
        items.append(item)
    items = '\n'.join(items)
    page = f"""
        <html>
          <head><title>Hacker Aliases</title></head>
          <body>
            Following are the aliases for email hash {requested_email_hash}.
            <ul>
              {items}
            </ul>
          </body>
        </html>
    """
    return HttpResponse(page)
