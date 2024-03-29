import json
import pandas as pd
from sqlalchemy import create_engine
from db_dependent_class import DBDependent
from datetime import datetime as dt


class RedDeadPandademption(DBDependent):

    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)
        with open('./sqlalchemy.cfg', 'rt') as r:
            self.cfg = json.load(r)

    def main(self):
        self.get_cursor()
        start_time = dt.now().timestamp()
        data_frame = []
        self.get_cursor().execute("select stats_json from import_performance_tracking ipt where repo_id = 397485")
        cnt = 0
        for row in self.get_cursor():
            cnt += 1
            data_frame = json.loads(row[0])
        elapsed = dt.now().timestamp() - start_time
        print(cnt, 'record loaded in ', elapsed)

        df = pd.DataFrame(data=data_frame)
        print(df.get('extension_map'))
        elapsed = dt.now().timestamp() - start_time
        print('Total execution time:', elapsed)

        stupid_comment = """
        engine = create_engine("mariadb://{user}:{pw}@{host}/{db}".format(
            host=self.cfg['host'],
            db=self.cfg['database'],
            user=self.cfg['user'],
            pw=self.cfg['password']))
        df.to_sql('hacker_update_queue', engine, index=False, if_exists='append')
"""
        # Does it really need to be *that* difficult to comment out a sectino?


if __name__ == '__main__':
    RedDeadPandademption().main()