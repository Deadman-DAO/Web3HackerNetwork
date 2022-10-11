import hashlib

def repo_partition_key(owner, repo_name):
    partition_name = f'{owner}\t{repo_name}'
    print(f'Partition Name: {partition_name}')
    key_hash = hashlib.md5(partition_name.encode('utf-8')).hexdigest()
    synthetic_key = key_hash[slice(0, 2)]
    return synthetic_key
