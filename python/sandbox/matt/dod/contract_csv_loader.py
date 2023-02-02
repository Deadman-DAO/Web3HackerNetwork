import csv
from datetime import datetime
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

    def parse_date(self, date_str):
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        return None

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
                    for y, idx in enumerate(self.column_idx):
                        value = line[idx]
                        if self.column_list[y] in self.date_fields:
                            date = self.parse_date(value)
                            if date is None:
                                raise Exception(f'Error parsing date: {value}')
                            value = date
                        needed_params.append(value)
                    batch.append(needed_params)
                    if len(batch) > 9:
                        self.get_cursor().executemany(self.sql, batch)
                        batch = []

    def run(self):
        self.load_contract_list()

if __name__ == '__main__':
    CSVLoader('ContractOpportunitiesFullCSV.csv').run()