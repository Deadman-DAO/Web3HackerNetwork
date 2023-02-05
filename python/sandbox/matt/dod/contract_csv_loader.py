import csv
from datetime import datetime
from dateutil import parser
from lib.db_dependent_class import DBDependent
from lib.utils import md5_hash

class CSVLoader(DBDependent):
    def __init__(self, file_name):
        DBDependent.__init__(self)
        self.file_name = file_name
        self.column_list = ['PostedDate', 'ArchiveDate', 'ResponseDeadLine', 'Type', 'BaseType', 'SetASideCode', 'SetASide', 'State', 'City', 'Link', 'Description']
        self.column_idx = []
        self.date_fields = ['PostedDate', 'ArchiveDate', 'ResponseDeadLine']
        self.sql = 'insert ignore into dod_contract (posted, archive, response_deadline, type, basetype, set_aside_code, set_aside, state, city, link, description, md5) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        self.running = True
        self.EOF = '>>>WTF<<<'

    def parse_date(self, date_str):
        if not date_str or date_str.strip() == '':
            return None
        try:
            return parser.parse(date_str)
        except Exception as e:
            raise ValueError(f"Error parsing date {date_str}: {e}")

    def load_contract_list(self):
        with open(self.file_name, 'rt') as f:
            reader = csv.reader(f)
            columns = next(reader)
            for desired_col in self.column_list:
                for idx, val in enumerate(columns):
                    if val == desired_col:
                        self.column_idx.append(idx)
            if len(self.column_idx) != len(self.column_list):
                raise Exception('Column list does not match')
            batch = []
            while self.running:
                line = next(reader, self.EOF)
                if line == self.EOF:
                    self.running = False
                else:
                    needed_params = []
                    md5 = None
                    for y, idx in enumerate(self.column_idx):
                        needed_params.append(line[idx])
                        temp_val = line[idx]
                        if y == self.column_list.index('Description'):
                            md5 = md5_hash(temp_val)
                        if self.column_list[y] in self.date_fields:
                            needed_params[-1] = self.parse_date(temp_val)
                    needed_params.append(md5)
                    batch.append(needed_params)
                    if len(batch) > 100:
                        try:
                            self.get_cursor().executemany(self.sql, batch)
                            print("Batch of data successfully inserted into the database")
                        except Exception as e:
                            print(f"Error inserting data into the database: {e}")
                        batch = []
            if len(batch) > 0:
                try:
                    self.get_cursor().executemany(self.sql, batch)
                    print("Batch of data successfully inserted into the database")
                except Exception as e:
                    print(f"Error inserting data into the database: {e}")

    def run(self):
        self.load_contract_list()

if __name__ == '__main__':
    CSVLoader('ContractOpportunitiesFullCSV.csv').run()
