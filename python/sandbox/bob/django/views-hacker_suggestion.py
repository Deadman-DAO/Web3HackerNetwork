from django.http import HttpResponse

import boto3
import configparser
import duckdb
import os
import pyarrow.fs as pafs
import pyarrow.parquet as papq

# pip install pyarrow boto3 duckdb pandas # logging

# {
#   "score": 1.293,
#   "author_name": "Eddú Meléndez",
#   "author_email_hash": "cf9e8d46103d66657d9c6817a5aa35d3",
#   "author_email_domain": "gmail.com",
#   "owner": "spring-cloud",
#   "repo_name": "spring-cloud-commons",
#   "num_stars": 627,
#   "num_forks": 600,
#   "license": "apache-2.0"
# }

def read_parquet_table(profile, bucket, path):
    cred_path = os.path.expanduser("~")+"/.aws/credentials"
    credentials = configparser.ConfigParser()
    credentials.read(filenames=[cred_path])
    key_id = credentials.get(profile, "aws_access_key_id")
    secret = credentials.get(profile, "aws_secret_access_key")
    fs = pafs.S3FileSystem(access_key=key_id, secret_key=secret)
    return papq.read_table(f'{bucket}/{path}', filesystem=fs)

def index(request):
    requested_email_hash = '6f1791e52486fcf62b37851c0cc84042'
    pipeline_path = 'web3hackernetwork/data_pipeline'
    dataset_path = f'{pipeline_path}/web_data/hacker_suggestion/'
    hacker_suggestion = read_parquet_table('w3hn-at-risk',
                                           'deadmandao-at-risk',
                                           dataset_path)
    conn = duckdb.connect()
    sql = f"""
      SELECT distinct owner, repo_name, license, num_stars, num_forks
        FROM hacker_suggestion
        WHERE author_email_hash = '{requested_email_hash}'
        ORDER BY score DESC
    """
    df = conn.query(sql).to_df()
    owners = list(df['owner'])
    repos = list(df['repo_name'])
    licenses = list(df['license'])
    num_starss = list(df['num_stars'])
    num_forkss = list(df['num_forks'])
    items = list()
    for i, owner in enumerate(owners):
        repo = repos[i]
        licence = licenses[i]
        num_stars = num_starss[i]
        num_forks = num_forkss[i]
        display = f'{owner} | {repo} | {licence} | {num_stars} | {num_forks}'
        url = f'https://github.com/{owner}/{repo}/'
        link = f'<a href="{url}">{display}</a>'
        item = f'<li>{link}</li>'
        items.append(item)
    items = '\n'.join(items)
    page = f"""
        <html>
          <head><title>Hacker Recommendations</title></head>
          <body>
            Following are the recommended projects for email hash {requested_email_hash}.
            <ul>
              {items}
            </ul>
          </body>
        </html>
    """
    return HttpResponse(page)
