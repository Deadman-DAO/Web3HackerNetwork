import boto3
import os
import uuid
from db_dependent_class import DBDependent
import base64
import time
import sys

class CopyCassandra(DBDependent):
    def __init__(self, params=None, **kwargs):
        DBDependent.__init__(self, **kwargs)
        if params and params[1] and params[2]:
            self.start_id = params[1]
            self.end_id = params[2]
        else:
            self.start_id = 1
            self.end_id = 999999999
        self.cass_cfg = None
        self.maria_cfg = None
        self.duck = None
        self.from_dbase = None
        self.cursor = None
        self.fetch_sql = 'select n.repo_id, n.tstamp, n.numstat, r.owner, r.name from repo_numstat n join repo r on r.id = n.repo_id where n.numstat is not null and length(n.numstat) > 0 and n.id between %s and %s'
        self.s3r = boto3.resource('s3')
        self.bucket = self.s3r.Bucket('numstat-bucket')

    def main(self):
        self.get_cursor().execute(self.fetch_sql, (self.start_id, self.end_id))
        cnt = 0
        for row in self.get_cursor():
            t = bytearray(row[2])
            try:
                ba = base64.b64decode(t)
                key = 'repo/'+row[3]+'/'+row[4]+'/log_numstat.out.json.bz2'
                file_name = ''.join(('./', str(uuid.uuid4())))
                with open(file_name, 'wb') as w:
                    w.write(ba)
                self.bucket.upload_file(file_name, key)
                os.remove(file_name)
                cnt += 1
                if cnt % 10 == 0:
                    print(cnt, 'records processed.  Last one:', key)
            except Exception as e:
                print('Error encountered while processing:', row[3], row[4], e)
                time.sleep(5)



if __name__ == "__main__":
    CopyCassandra(params=sys.argv).main()
