import csv
from datetime import datetime as datingdays
from lib.db_dependent_class import DBDependent
class CSVLoader(DBDependent):
    def __init__(self, file_name):
        DBDependent.__init__(self)
        self.file_name = file_name
        self.column_list = ['PostedDate', 'ArchiveDate', 'ResponseDeadLine', 'Type', 'BaseType', 'SetASideCode', 'SetASide', 'State', 'City', 'Link', 'Description']
        self.column_idx = []
        self.date_fields = ['PostedDate', 'ArchiveDate', 'ResponseDeadLine']
        self.sql = 'insert into dod_contract (posted, archive, response_deadline, type, basetype, set_aside_code, set_aside, state, city, link, description) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        self.running = True
        self.EOF = '>>>WTF<<<'


    def load_contract_list(self):
        with open(self.file_name, 'rt') as f:
            reader = csv.reader(f)
            columns = next(reader)
            print(columns)
            for desired_col in self.column_list:
                print('Looking for', desired_col)
                for idx, val in enumerate(columns):
                    if val == desired_col:
                        self.column_idx.append(idx)
            if len(self.column_idx) != len(self.column_list):
                raise Exception('Column list does not match')
            else:
                for idx, val in enumerate(self.column_list):
                    print(self.column_list[idx], '->', self.column_idx[idx])
            batch = []
            while self.running:
                line = next(reader, self.EOF)
                print(line)
                if line == self.EOF:
                    self.running = False
                else:
                    needed_params = []
                    for y, idx in enumerate(self.column_idx):
                        needed_params.append(line[idx])
                        if self.column_list[y] in self.date_fields:
                            try:
                                needed_params[-1] = datingdays.strptime(line[idx], '%Y-%m-%d %H:%M:%S')
                            except ValueError as e:
                                print('Error parsing date', line[idx], e)

                    print(needed_params)
                    batch.append(needed_params)
                    if len(batch) > 9:
                        self.get_cursor().executemany(self.sql, batch)
                        batch = []

    def run(self):
        self.load_contract_list()


if __name__ == '__main__':
    CSVLoader('ContractOpportunitiesFullCSV.csv').load_contract_list()
