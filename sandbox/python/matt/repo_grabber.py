class RepoGrabber:
    def __init__(self):
        self.s3r = boto3.resource('s3')
        self.bucket = self.s3r.Bucket('numstat-bucket')

    def get_numstat(self, owner, repo_name):
        numstat = None
        for obj in self.bucket.objects.filter(Prefix=f'repo/{owner}/{repo_name}/'):
            obj = self.s3r.Object('numstat-bucket', obj.key)
            numstat_bz2 = obj.get()['Body'].read()
            numstat = json.loads(bz2.decompress(numstat_bz2))
        return numstat