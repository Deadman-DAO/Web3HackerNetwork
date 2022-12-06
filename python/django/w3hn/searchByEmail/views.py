from django.http import HttpResponse

import boto3
import configparser
import duckdb
import json
import os
import pyarrow.fs as pafs
import pyarrow.parquet as papq

# pip install boto3 duckdb pyarrow pandas # logging

pipeline_path = 'web3hackernetwork/data_pipeline'

def read_parquet_table(profile, bucket, path):
    cred_path = os.path.expanduser("~")+"/.aws/credentials"
    credentials = configparser.ConfigParser()
    credentials.read(filenames=[cred_path])
    key_id = credentials.get(profile, "aws_access_key_id")
    secret = credentials.get(profile, "aws_secret_access_key")
    fs = pafs.S3FileSystem(access_key=key_id, secret_key=secret)
    return papq.read_table(f'{bucket}/{path}', filesystem=fs)

def get_aliases(requested_email_hash):
    dataset_path = f'{pipeline_path}/web_data/hacker_alias/'
    repo_hacker = read_parquet_table('w3hn-at-risk', 'deadmandao-at-risk', dataset_path)
    conn = duckdb.connect()
    sql = f"""
      SELECT distinct alias_name, alias_email_domain, alias_email_hash
        FROM repo_hacker
        WHERE author_email_hash = '{requested_email_hash}'
    """
    df = conn.query(sql).to_df()
    names = list(df['alias_name'])
    domains = list(df['alias_email_domain'])
    hashes = list(df['alias_email_hash'])
    zipped = zip(names, domains, hashes)
    aliases = [{'name':n, 'domain':d, 'hash':h} for (n, d, h) in zipped]
    return aliases

def get_recommendations(requested_email_hash):
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
    zipped = zip(owners, repos, licenses, num_starss, num_forkss)
    recommendations= [{
        'owner':o,
        'repo_name':r,
        'license':l,
        'num_stars':s,
        'num_forks':f,
    } for (o,r,l,s,f) in zipped]
    return recommendations

def get_projects(requested_email_hash):
    dataset_path = f'{pipeline_path}/web_data/repo_hacker/'
    repo_hacker = read_parquet_table('w3hn-at-risk', 'deadmandao-at-risk', dataset_path)
    conn = duckdb.connect()
    sql = f"""
      SELECT distinct owner, repo_name
        FROM repo_hacker
        WHERE author_email_hash = '{requested_email_hash}'
    """
    df = conn.query(sql).to_df()
    owners = list(df['owner'])
    repos = list(df['repo_name'])
    zipped = zip(owners, repos)
    projects= [{
        'owner':o,
        'repo_name':r,
    } for (o,r) in zipped]
    return projects

def index(request):
    requested_email_hash = request.GET.get("email_hash")
    aliases = get_aliases(requested_email_hash)
    projects = get_projects(requested_email_hash)
    recommendations = get_recommendations(requested_email_hash)
    outer_dict = {
        'aliases': aliases,
        'projects': projects,
        'recommendations': recommendations,
    }
    jason = json.dumps(outer_dict, indent=2)
    return HttpResponse(jason, content_type='application/json')
