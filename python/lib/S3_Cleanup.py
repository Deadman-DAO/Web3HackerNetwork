import boto3
import json
import os
from lib.db_dependent_class import DBDependent

class S3Cleanup(DBDependent):
    def __init__(self):
        DBDependent.__init__(self)
        self.s3 = boto3.resource('s3')
        self.bucket_name = 'numstat-bucket'
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.prefix = 'repo_v01/'

        self.max_keys = 1000

        self.continuation_token = None
        self.owner_map = {}
        self.running = True
        self.item_count = 0
        self.repo_count = 0

    def load_info(self):
        if os.path.exists('./repo_bucket_contents.json'):
            with open('./repo_bucket_contents.json', 'r') as f:
                self.owner_map = json.loads(f.read())
        else:
            print('File not found, loading from S3')
            while self.running:
                # Call the list_objects_v2 method to list the objects in the bucket
                if self.continuation_token is None:
                    response = self.s3.list_objects_v2(
                        Bucket=self.bucket_name,
                        Prefix=self.prefix,
                        MaxKeys=self.max_keys
                    )
                else:
                    response = self.s3.list_objects_v2(
                        Bucket=self.bucket_name,
                        Prefix=self.prefix,
                        MaxKeys=self.max_keys,
                        ContinuationToken=self.continuation_token
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
                            self.item_count += 1
                            if owner_repo in self.owner_map:
                                files = self.owner_map[owner_repo]
                                files.append(file_name)
                            else:
                                self.repo_count += 1
                                self.owner_map[owner_repo] = [file_name]


                # Get the continuation token from the response, if there is one
                self.continuation_token = response.get('NextContinuationToken', None)

                # If there is no continuation token, we have reached the end of the list of objects
                if self.continuation_token is None:
                    self.running = False
                else:
                    print(f'Continuation token: {self.continuation_token} {self.item_count} items, {self.repo_count} repos')

            print('Writing out big json file before beginning analysis.')
            with open('repo_bucket_contents.json', 'w') as f:
                f.write(json.dumps(self.owner_map, indent=4))

    def run(self):
        self.load_info()
        print(f'Loaded {self.item_count} items, {self.repo_count} repos')

        count_map = {}
        unique_map = {}

        for owner_repo, file_list in self.owner_map.items():
            dicky = str(file_list)
            if dicky in unique_map:
                count_map[dicky] += 1
            else:
                count_map[dicky] = 1
                unique_map[dicky] = file_list

        for key, value in count_map.items():
            print(f'{key} occurred {value} times')