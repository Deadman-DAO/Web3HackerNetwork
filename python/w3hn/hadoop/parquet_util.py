import hashlib

def owner_repo(owner, repo_name):
    return f'{owner}/{repo_name}'

def repo_partition_key(owner, repo_name):
    partition_name = owner_repo(owner, repo_name)
    key_hash = hashlib.md5(partition_name.encode('utf-8')).hexdigest()
    synthetic_key = key_hash[slice(0, 2)]
    return f'pk{synthetic_key}'

# version name should be in the form 'vNN', zero indexed
def datapipe_path(version_name):
    return f'w3hn_dp_{version_name}'

def raw_path(version_name):
    return f'{datapipe_path(version_name)}/raw'
