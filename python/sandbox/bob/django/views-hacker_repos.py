from django.http import HttpResponse

import boto3
import configparser
import duckdb
import os
import pyarrow.fs as pafs
import pyarrow.parquet as papq

# pip install pyarrow boto3 duckdb pandas # logging

# {
#   "owner": "GingerGabriela",
#   "repo_name": "pruebaGitHub2",
#   "partition_key": "pk81",
#   "owner_repo": "GingerGabriela\tpruebaGitHub2",
#   "author_name": "David Turner",
#   "author_email_domain": "twosigma.com",
#   "author_email_hash": "fe8f9fd45b86a8756b6ed233d6f13d9a"
# }
# {
#   "owner": "aiven",
#   "repo_name": "cassandra",
#   "partition_key": "pk81",
#   "owner_repo": "aiven\tcassandra",
#   "author_name": "Dave Brosius",
#   "author_email_domain": "mebigfatguy.com",
#   "author_email_hash": "c35777e0d2751654391d03ccdf67edc4"
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
    pipeline_path = 'web3hackernetwork/data_pipeline'
    dataset_path = f'{pipeline_path}/athena/targetable_hackers/20221129_052341_00041_9bdqq_998d7f1d-e656-47d1-bab5-7ea0acafeaa4'
    dataset_path = f'{pipeline_path}/web_data/repo_hacker/'
    dataset_path = 'web3hackernetwork/data_pipeline/web_data/repo_hacker/'
    repo_hacker = read_parquet_table('w3hn-at-risk', 'deadmandao-at-risk', dataset_path)
    conn = duckdb.connect()
    sql = """
      SELECT owner, repo_name
        FROM repo_hacker
        WHERE author_email_hash = 'fe8f9fd45b86a8756b6ed233d6f13d9a'
    """
    df = conn.query(sql).to_df()
    owners = list(df['owner'])
    repos = list(df['repo_name'])
    owner_repos = list()
    for i, owner in enumerate(owners):
        repo = repos[i]
        owner_repos.append(f'<li><a href="https://github.com/{owner}/{repo}/">{owner} | {repo}</a></li>')
    owner_repos = '\n'.join(owner_repos)
    page = f"""
        <html>
          <head><title>I'll be your commander.</title></head>
          <body>
            <h1>Hello, World!</h1>
            <ul>
              {owner_repos}
            </ul>
          </body>
        </html>
    """
    return HttpResponse(page)
