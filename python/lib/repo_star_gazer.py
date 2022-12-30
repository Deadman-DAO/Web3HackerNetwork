import json

from db_dependent_class import DBDependent
from git_hub_client import GitHubClient
import sys
import boto3
import bz2
import io
import threading
from sandbox.matt.log_trial import clog as log

class RepoStarGazer(DBDependent, GitHubClient):
    def __init__(self, **kwargs):
        self.web_lock = kwargs['web_lock'] if 'web_lock' in kwargs else threading.Lock()
        kwargs['web_lock'] = self.web_lock
        GitHubClient.__init__(self, **kwargs)
        DBDependent.__init__(self, **kwargs)
        self.url_prefix = 'https://api.github.com/repos/'
        self.input_csv_file = kwargs['input_csv_file'] if 'input_csv_file' in kwargs else None
        self.loaded_input = None
        self.formatted_url = None
        self.s3r = boto3.resource('s3')
        self.bucket = self.s3r.Bucket('numstat-bucket')

    def format_url(self, repo_owner, repo_name):
        return ''.join((self.url_prefix, repo_owner, '/', repo_name))

    def get_next_repo_from_database(self):
        return self.execute_procedure('GetNextRepoForEval', [self.machine_name])[0]

    def load_input(self):
        if self.loaded_input is None:
            if self.input_csv_file:
                self.loaded_input = []
                with open(self.input_csv_file, 'r') as f:
                    for line in f:
                        self.loaded_input.append(line.strip().split(','))
        return self.loaded_input

    def get_next_repo(self):
        if self.loaded_input is None and self.input_csv_file:
            self.load_input()

        if self.loaded_input:
            return self.loaded_input.pop(0)
        else:
            return self.get_next_repo_from_database()

    def save_repo_info(self, info, repo_owner, repo_name):
        json.dumps(info)
        repo_info_json = json.dumps(info, ensure_ascii=False)
        repo_info_zip = bz2.compress(repo_info_json.encode('utf-8'))
        key = 'repo/'+repo_owner+'/'+repo_name+'/repo_info.json.bz2'
        self.bucket.upload_fileobj(io.BytesIO(repo_info_zip), key)
        sgc = info['stargazers_count'] if 'stargazers_count' in info else 0
        wc = info['watchers_count'] if 'watchers_count' in info else 0
        size = info['size'] if 'size' in info else 0
        subscribers = info['subscribers_count'] if 'subscribers_count' in info else 0
        self.execute_procedure('SetRepoWatcherCount', [repo_owner, repo_name, sgc if sgc > wc else wc, size, subscribers])

    def get_repo_info(self, repo_owner, repo_name, repo_id):
        info = self.fetch_json_with_lock(self.format_url(repo_owner, repo_name))
        if info:
            self.save_repo_info(info, repo_owner, repo_name)
            log.critical('Saved info for %s/%s [%s]' % (repo_owner, repo_name, repo_id))
        else:
            self.execute_procedure('SetRepoWatcherCount', [repo_owner, repo_name, -1, -1, -1])


    def do_it(self):
        running = True
        while running:
            repo = self.get_next_repo()
            if repo:
                self.get_repo_info(repo[0], repo[1], repo[2] if repo[2] else -1)
            else:
                running = False


if __name__ == '__main__':
    rsg = RepoStarGazer(**{'input_csv_file': sys.argv[1] if len(sys.argv) > 1 else None})
    rsg.do_it()



