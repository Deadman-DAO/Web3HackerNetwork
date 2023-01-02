import hashlib

def repo_partition_key(owner, repo_name):
    partition_name = f'{owner}/{repo_name}'
    # print(f'Partition Name: {partition_name}')
    key_hash = hashlib.md5(partition_name.encode('utf-8')).hexdigest()
    synthetic_key = key_hash[slice(0, 2)]
    return f'pk{synthetic_key}'

def owner_repo(owner, repo_name):
    return f'{owner}/{repo_name}'
