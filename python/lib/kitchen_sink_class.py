'''
for want of a better name, this Queue class has too much stuff embedded in it right now 
  TODO TODO TODO Move more closesly assoicated stuff into separate classes TODO TODO TODO
'''
import requests
import json
import hashlib
import os
from datetime import datetime as datingdays
import time
from pytz import timezone
from git import Repo, Git
import sys
import threading
project_root_path = '../../..'
python_lib_path = project_root_path + '/python/lib'
sys.path.append(python_lib_path)
from commit_log_parser import NumstatRequirementSet
from os.path import exists

def load_single_line_from_file(file_name):
    line = None
    try:
        if exists(file_name):
            with open(file_name) as r:
                line = r.readlines()[0][:-1] #Strip off the stupid carriage return
    except Exception as e:
        print('Error occurred loading',file_name,e)
    return line

class RepoName:
    def key(self):
        return self.owner+'/'+self.repo_name
    def __init__(self, owner, repo_name):
        self.owner = owner
        self.repo_name = repo_name
    
class Hacker:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=2)    
    def __init__(self):
        self.user_id = None
        self.commits = []
        self.aliases = Counter()
    def __init__(self, user_id):
        self.user_id = user_id;
class Repository:
    def __init__(self, repo_id, repo_name):
        self.repo_id = repo_id
        self.repo_name = repo_name
class MyCounter:
    def __init__(self, init_val):
        self.counter = init_val
    def __init__(self):
        self.__init__(0)
    def increment(self):
        self.count += 1
    def val(self):
        return self.counter
    
# Types of queries:
#
#  Single query to derive a user ID
#  Mass commit log
class Query:
    def __init__(self):
        self.MAX_LOOPS = 5
        self.urlPrefix = 'https://api.github.com/search/commits'
        self.startDate = datingdays.now(timezone('US/Arizona'))
        self.hackers = {}
        self.repos = {}
        self.aliases = {}
        self.resolved_alias_map = {}
        self.commit_to_repo_map = {}
        self.json_repo_map = {}
        self.commit_cache_map = {}
        with open('./web3.github.token', 'r') as f:
            self.token = f.readline()
            self.token = self.token.strip('\n')
            self.headers = {'Authorization': 'token %s' % self.token}
    def add_alias(self, alias, commit_key):
        if (alias not in self.aliases.keys()):
            self.aliases[alias] = []
        self.aliases[alias].append(commit_key)
    
    def reset_last_date(self):
        self.startDate = datingdays.now(timezone('US/Arizona'))
    def set_last_date(self, date):
        new_date = self.startDate
        if date.endswith('Z'):
            date = date[:len(date)-2]
        try:
            new_date = datingdays.fromisoformat(date)
            if (new_date < self.startDate):
    #           Note: GitHub rejected dates with timezones other than "-07:00" (like "+02:00")
    #                 By subtracting the difference (in milliseconds?) we represent the "US/Arizona"
    #                 version of the author-date pulled from previous results
                self.startDate = self.startDate - (self.startDate - new_date)
        except:
            #Skip a bit, brother.
            #Even if this is the very last commit in this set
            # it may be repeated at the beginning of the next
            # query, but won't cause an endless loop. If it's the last
            # commit in the whole set for a particular hacker it will
            # still exit the loop due to a < 100 item result set.
            pass
    def format_user_url(self, user_id):
        var = self.urlPrefix+"?q=author:"+user_id+'+author-date:<'+self.startDate.isoformat()+'&sort=author-date&order=desc&per_page=100&page=1'
        return var
    def load_hacker_url(self, user_id, recurse_count=1):
        retVal = None
        resp = requests.get(self.format_user_url(user_id), headers=self.headers)
        if (resp.status_code == 200):
            time.sleep(1)
            retVal = resp.json()
        elif (resp.status_code == 403):
            print('Rate limit EXCEEDED.  Sleeping for a bit. (recursive_count=', recurse_count,')')
            time.sleep(recurse_count * 60)
            return self.load_hacker_url(user_id, recurse_count+1)
        else:
            print('Status code returned:', resp.status_code)
            req_headers = resp.request.headers
            for n in req_headers.keys():
                print('\t', n, req_headers[n])
            print(json.dumps(resp.json(), indent=2))
        return retVal
    def load_file(self, file_name):
        ret_val = {}
        try:
            if (exists(file_name)):
                with open(file_name, 'r') as af:
                    ret_val = json.load(af)
        except Exception as e:
            print('Unable to load', file_name, 'due to:', e)
        return ret_val
    def preload_alias_maps(self):
        self.resolved_alias_map = self.load_file('./aliasMap.json')
        self.hackers = self.load_file('./hackers.json')
        if len(self.resolved_alias_map) < 1:
            print('Fabricating alias map')
            for key in self.hackers.keys():
                for val in self.hackers[key]:
                    self.resolved_alias_map[val] = key
            with open('./aliasMap.json', 'w') as w:
                w.write(json.dumps(self.resolved_alias_map, indent=2))
                    
                
        
    def add_commit_id(self, commit_id, repo_name):
        self.commit_to_repo_map[commit_id] = repo_name
    def format_id_check_url(self, commit_id):
        rn = self.commit_to_repo_map[commit_id]
        return 'https://api.github.com/repos/'+rn.owner+'/'+rn.repo_name+'/commits/'+commit_id
    def retrieve_commit(self, commit_hash, recurse_count=1):
        url = self.format_id_check_url(commit_hash)
        resp = requests.get(self.format_id_check_url(commit_hash), headers=self.headers)
        if (resp.status_code == 422):
            print('ERROR - Status code:', resp.status_code, 'encountered ', url)
            return None
        elif resp.status_code == 403:
            ##We've exceed our 5000 calls per hour!
            print('Maximum calls/hour exceeded! Sleeping', recurse_count, 'minute(s)')
            print('Working on', commit_hash)
            time.sleep(60*recurse_count)
            if recurse_count <= self.MAX_LOOPS:
                return self.retrieve_commit(commit_hash, recurse_count+1)
            else:
                return None
        elif resp.status_code == 200:            
            time.sleep(1)
            return resp
        else:
            return None

    def stop_monitor(self):
        self.monitor_running = False
    def start_monitor(self):
        self.thread = threading.Thread(target=self.monitor_alias, daemon=False)
        self.thread.start()

    def monitor_alias(self):
        self.monitor_running = True
        while self.monitor_running:
            try:
                time.sleep(10)
                print(len(self.hackers), 'root level hackers resolved')
            except Exception as e:
                print('Unexpected error occurred - Leaving',e)
                self.monitor_running = False
                
    def process_commit_response(self, resp, sha_array, alias, recursive_count=0):
        j = resp.json()
        commit_details_block = j['author']
        if (commit_details_block == None):
            commit_details_block = j['committer']
        if (commit_details_block == None):
            if recursive_count < self.MAX_LOOPS and recursive_count < (len(sha_array)-1):
                old_hash = sha_array[recursive_count]
                recursive_count += 1
                new_hash = sha_array[recursive_count]
                self.commit_to_repo_map[new_hash] = self.commit_to_repo_map[old_hash]
                resp = self.retrieve_commit(new_hash)
                if (resp is not None):
                    self.process_commit_response(resp, sha_array, alias, recursive_count)
            else:
                print('Unable to find author node within JSON formatted result set', alias)
        else:
            if 'login' in commit_details_block.keys():                
                committer = commit_details_block['login']
                if (committer not in self.hackers.keys()):
                    #print('Creating new hacker object for '+committer+' ['+alias+']')
                    self.hackers[committer] = []
                self.hackers[committer].append(alias)
                self.resolved_alias_map[alias] = committer
            else:
                print('Cannot find login key', json.dumps(j, indent=2))
        
    def resolve_aliases(self):
        #threading.Thread(target=self.monitor_alias, args=(self,))
        for alias in self.aliases.keys():
            if alias not in self.resolved_alias_map.keys():
                commit_id = q.aliases[alias][0]  #Lookup just the first one
                #print('Resolving ['+alias+'] using commit ID: '+commit_id)
                resp = self.retrieve_commit(commit_id)
                if (resp != None):
                    self.process_commit_response(resp, q.aliases[alias], alias)
class RepoCounter:
    def __init__(self, repo_dict):
        self.repo_name = repo_dict['name']
        self.repo_full_name = repo_dict['full_name']
        owner = repo_dict['owner']
        self.owner = owner['login']
        self.count = 0
    def __init__(self, owner, repo):
        self.repo_name = repo
        self.repo_full_name = owner+'/'+self.repo_name
        self.owner = owner
        self.count = 0
    def add_one(self):
        self.count += 1
        
    def key(self):
        return self.repo_full_name
