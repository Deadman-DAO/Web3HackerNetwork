import boto3

# Create an S3 client
s3 = boto3.client('s3')

# Set the name of the bucket that you want to scan
bucket_name = 'numstat-bucket'

# Set the prefix for the objects that you want to list.
# This will list only objects that have this prefix in their key.
prefix = 'repo_v01/'

# Set the maximum number of objects that you want to receive in each response
max_keys = 10000

# Set the continuation token to an empty string to start listing objects
continuation_token = None
owner_map = {}
running = True
item_count = 0
repo_count = 0

while running:
    # Call the list_objects_v2 method to list the objects in the bucket
    if continuation_token is None:
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=max_keys
        )
    else:
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=max_keys,
            ContinuationToken=continuation_token
        )


    # Get the list of objects from the response
    if 'Contents' in response:
        objects = response['Contents']
        for obj in objects:
            # Print the object key
            elems = obj['Key'].split('/')
            size = obj['Size']
            if len(elems) == 4:
                owner = elems[1]
                repo = elems[2]
                owner_repo = owner + '/' + repo
                file_name = elems[3]
                item_count += 1
                if owner_repo in owner_map:
                    files = owner_map[owner_repo].files
                    files.append(file_name)
                    if size(files) == 4:
                        print('Eliminating ' + owner_repo + str(files))
                        owner_map.pop(owner_repo)
                else:
                    repo_count += 1
                    owner_map[owner] = [file_name]


    # Get the continuation token from the response, if there is one
    continuation_token = response.get('NextContinuationToken', None)

    # If there is no continuation token, we have reached the end of the list of objects
    if continuation_token is None:
        running = False
    else:
        print(f'Continuation token: {continuation_token} ({item_count} items, {repo_count} repos)')

del_list = []
for owner_repo, file_list in owner_map.items():
    if len(file_list) == 1 and 'repo_info.json.bz2' in file_list:
        del_list.append(owner_repo)

for owner_repo in del_list:
    owner_map.pop(owner_repo)

for owner_repo, file_list in owner_map.items():
    print(owner_repo, file_list)
