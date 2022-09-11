import json
import pandas as pd
from sqlalchemy import create_engine
from db_dependent_class import DBDependent
import mysql.connector


class RedDeadPandademption(DBDependent):

    def __init__(self, **kwargs):
        DBDependent.__init__(self, **kwargs)
        with open('./sqlalchemy.cfg', 'rt') as r:
            self.cfg = json.load(r)

    def main(self):
        data_frame = []
        self.get_cursor().execute("select md5, name_email from hacker_update_queue")
        for row in self.get_cursor():
            data_frame.append(row)
        df = pd.DataFrame(data=data_frame, columns=['md5', 'name_email'])
        engine = create_engine("mariadb://{user}:{pw}@{host}/{db}".format(
            host=self.cfg['host'],
            db=self.cfg['database'],
            user=self.cfg['user'],
            pw=self.cfg['password']))
        df.to_sql('hacker_update_queue', engine, index=False, if_exists='append')


if __name__ == '__main__':
    RedDeadPandademption().main()