from w3hn.aws.aws_util import S3Util

util = S3Util(profile='enigmatt')

owner = 'ADHuan'
repo_name = 'AmiAmi-info-push'

blame = util.get_blame_map(owner, repo_name)
print(f'blame length: {len(blame)}')

deps = util.get_dependency_map(owner, repo_name)
print(f'deps length: {len(deps)}')

nstat = util.get_numstat(owner, repo_name)
print(f'nstat length: {len(nstat)}')

# print(f'{nstat}')


