import boto3
import os
import uuid
from db_dependent_class import DBDependent
import base64


class CopyCassandra(DBDependent):
    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)
        self.cass_cfg = None
        self.maria_cfg = None
        self.duck = None
        self.from_dbase = None
        self.cursor = None
        self.fetch_sql = 'select n.repo_id, n.tstamp, n.numstat, r.owner, r.name from repo_numstat n join repo r on r.id = n.repo_id where n.numstat is not null and length(n.numstat) > 0'
        self.s3r = boto3.resource('s3')
        self.bucket = self.s3r.Bucket('numstat-bucket')

    def main(self):

        self.get_cursor().execute(self.fetch_sql)
        cnt = 0
        for row in self.get_cursor():
            t = bytearray(row[2])
            ba = base64.b64decode(t)
            key = 'test/'+row[3]+'/'+row[4]+'/numstat.json.bz2'
            file_name = ''.join(('./', str(uuid.uuid4())))
            with open(file_name, 'wb') as w:
                w.write(ba)
            self.bucket.upload_file(file_name, key)
            os.remove(file_name)
            cnt += 1
            if cnt % 10 == 0:
                print(cnt, 'records processed.  Last one:', key)


if __name__ == "__main__":
    CopyCassandra().main()
