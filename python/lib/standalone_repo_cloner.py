import os
import json
import sys
import mariadb
import time
import hashlib
from git import Repo, Git
local_lib_dir = '.'
sys.path.append(local_lib_dir)
from datetime import datetime as datingdays
from kitchen_sink_class import Query
from kitchen_sink_class import load_single_line_from_file as load_it
from kitchen_sink_class import RepoName
from commit_log_parser import NumstatRequirementSet
from os.path import exists
from shutil import rmtree
from shutil import disk_usage

class Cloner:
    def __init__(self):
        self.repo_base_dir = './repos'
        self.result_base_dir = './results'
        self.make_dir(self.repo_base_dir)
        self.make_dir(self.result_base_dir)
        self.machine_name = os.uname().nodename
        self.database = None
        self.db_config = None
    def make_dir(self, dirName):
        previously_existed = os.path.exists(dirName) and os.path.isdir(dirName)
        if os.path.isdir(dirName) == False and os.path.exists(dirName) == False:
            os.makedirs(dirName)
        return previously_existed
    def establish_dirs(self, owner, repo_name):
        repo_dir = self.repo_base_dir+'/'+owner+'/'+repo_name
        rslt_dir = self.result_base_dir+'/'+owner+'/'+repo_name
        update   = self.make_dir(repo_dir)
        self.make_dir(rslt_dir)
        return (repo_dir, rslt_dir, update)
    def cleanup(self, owner, repo_name):
        rmtree(self.repo_base_dir+'/'+owner+'/'+repo_name)
        rmtree(self.repo_base_dir+'/'+owner)
    def load_db_info(self):
        if self.db_config is None:
            with open('./db.cfg', 'r') as r:
                self.db_config = json.load(r);
    def get_cursor(self):
        if self.database is None:
            self.load_db_info()
            self.database = mariadb.connect(
                port=self.db_config['port'],
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                autocommit=(self.db_config['autocommit']=='true'))
            self.cursor = self.database.cursor()
        return self.cursor
    def reserve_next_repo(self):
        owner = None
        repo_name = None
        
        self.get_cursor()
        self.cursor.callproc('ReserveNextRepo', (self.machine_name, None, None))
        if self.cursor.sp_outparams: #one or more inline results set ready
            rslt = self.cursor.fetchone()
            owner = rslt[0]
            repo_name = rslt[1]
        return owner, repo_name
    def clone_pull_repo(self, url, repo_path, update_repo, json_stats_file_name):
        cache_date = None
        if not update_repo:
            Repo.clone_from(url, repo_path)
        else:
            rp = Repo(repo_path)
            remote = rp.remote()
            remote.pull()
            if exists(json_stats_file_name):
                try:
                    cache_date = os.path.getmtime(json_stats_file_name)
                    with open(json_stats_file_name) as j:
                        numstat_req_set.resultArray = json.load(j)
                except Exception as e:
                    cache_date = None
                    print(datingdays.now().isoformat(),'Error encountered trying to parse', json_stats_file_name, e)
        print(datingdays.now().isoformat(),'Repo cloned/pulled')
        return cache_date
        
    def check_if_updates_are_necessary(self, cache_date, rep):
        need_stats = True
        if cache_date is not None:
            system_tz = timezone(time.tzname[0])        
            then = datingdays.now(system_tz)
            file_date = datingdays.fromtimestamp(cache_date, tz=system_tz)

            # Add call to rep.log('-1') to get the date from the latest change
            #  If that date is less than the date on the cached stats file
            #  then skip this one by loading the previous stats file.
            info = rep.log('-1')
            for n in info.splitlines():
                prefix = 'Date: '
                if n.startswith(prefix):
                    new_date = n[len(prefix):].strip()
                    dt = datingdays.strptime(new_date, '%a %b %d %H:%M:%S %Y %z')
                    then = then - (then - dt)
                    print(datingdays.now().isoformat(),file_date.isoformat(), 'Last stats run')
                    print(datingdays.now().isoformat(),then.isoformat(), 'Last Git Modification')
                    if then < file_date:
                        need_stats = False

                #print(info)
                #Parse the line that starts with Date
                #Date:   Mon May 16 19:14:08 2022 +0200
        return need_stats
        
    def gather_stats_for_repo(self, owner, repo_name):
        repo = RepoName(owner, repo_name)
        print(datingdays.now().isoformat(),'Processing', owner, repo_name)
        repo_path, result_path, update_repo = self.establish_dirs(owner, repo_name)
        json_stats_file_name = result_path+'/commit_stat_log.json'
        numstat_req_set = NumstatRequirementSet()
        last_date = datingdays.fromisoformat('1972-12-26T03:23:01.123456-07:00')
    
        url = 'https://github.com/'+owner+'/'+repo_name+'.git'
        cache_date = self.clone_pull_repo(url, repo_path, update_repo, json_stats_file_name)

        rep = Git(repo_path)
        need_stats = self.check_if_updates_are_necessary(cache_date, rep)

        if need_stats:        
            print(datingdays.now().isoformat(),'Generating Stats for '+repo_path)
            try:
                stat = rep.log('--numstat')
                numstat_req_set.processDocument(stat)
            except Exception as e:
                print('Unable to generate statistics on:',repo_path,'due to',e)
        else:
            print(datingdays.now().isoformat(),'Skipping',repo_path,'no changes found.')

        with open(json_stats_file_name, 'w') as out:
            out.write(json.dumps(numstat_req_set.resultArray, indent=2))
        return numstat_req_set
    
    def store_results_to_database(self, owner, repo_name, numstat_req_set):
        print(datingdays.now().isoformat(), 'writing commit history to database')
        for n in numstat_req_set.resultArray:
            self.cursor.callproc('InsertCommit', 
                                (owner,
                                 repo_name, 
                                 n['commit'], 
                                 hashlib.md5(n['Author'].encode('utf-8')).hexdigest(),
                                 n['Author'],
                                 datingdays.fromisoformat(n['Date']),
                                 n['orig_timezone'],
                                 json.dumps(n['fileTypes']) ) )
        print(datingdays.now().isoformat(), 'DONE writing commit history to database')
    def store_marker_for_secondary_thread(self, owner, repo_name):
        print(datingdays.now().isoformat(), 'storing job for copying data to database in, well, the database')
        self.cursor.callproc('AddJobToUpdateQueue', 
                            (self.machine_name, owner, repo_name))
        


def main():
    running = True
    cloner = Cloner()
    while running:
        du = disk_usage('.')
        free = du.free / (1024*1024)
        if du.free < 10*1024*1024*1024:
            print('Less than 10GB free:', free, 'MB waiting a bit for the disk cleaner-upper to catch up')
            time.sleep(300) #sleep 5 minutes
        else:
            owner, repo_name = cloner.reserve_next_repo()
            if owner is None:
                print('No more repos to process.  Sleeping.')
                time.sleep(60)
            else:
                print(datingdays.now().isoformat(), 'Disk free:', free, 'MB')
                numstat_req_set = cloner.gather_stats_for_repo(owner, repo_name)
    #            cloner.store_results_to_database(owner, repo_name, numstat_req_set)
                cloner.store_marker_for_secondary_thread(owner, repo_name)
                print(datingdays.now().isoformat(), 'cleaning up repo directory', owner, repo_name)
                cloner.cleanup(owner, repo_name)
                print(datingdays.now().isoformat(), 'DONE cleaning up repo directory', owner, repo_name)

if __name__=="__main__":
    main()         
