from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json
from db_dependent_class import DBDependent
from datetime import datetime as datingdays
import base64

class CopyCassandra(DBDependent):
    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)
        self.cass_cfg = None
        self.maria_cfg = None
        self.duck = None
        self.from_dbase = None
        self.cass_session = None
        self.cursor = None
        self.fetch_sql = 'select n.repo_id, n.tstamp, n.numstat, r.owner, r.name from repo_numstat n join repo r on r.id = n.repo_id limit 1'
        self.insert_sql = 'insert into repo_numstat (id,tstamp, numstat, owner, name) values (?, ?, ?, ?, ?)'

    def main(self):
        with open('./cassandra.cfg') as f:
            self.cass_cfg = json.load(f)
        ptap = PlainTextAuthProvider(username=self.cass_cfg['user'],password=self.cass_cfg['password'])
        duck = Cluster(auth_provider=ptap)
        self.cass_session = duck.connect()
        self.get_cursor().execute(self.fetch_sql)
        for row in self.get_cursor():
            tstamp_str = row[1].isoformat().replace('T', ' ')+'+0000'
            print(row)
            print(tstamp_str)
            t = bytearray(row[2].decode())
            print(t)
            ba = base64.b64decode(t)
            print(ba)
            params = [row[0], tstamp_str, ba, row[3], row[4]]
            self.cass_session.execute(self.fetch_sql, params)


if __name__ == "__main__":
    CopyCassandra().main()
