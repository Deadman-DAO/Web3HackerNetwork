import csv
from datetime import datetime

class CSVLoader:
    def __init__(self, file_name):
        self.file_name = file_name
        self.column_list = ['PostedDate', 'ArchiveDate', 'ResponseDeadLine', 'Type', 'BaseType', 'SetASideCode', 'SetASide', 'State', 'City', 'Link', 'Description']
        self.column_idx = []
        self.date_fields = ['PostedDate', 'ArchiveDate', 'ResponseDeadLine']
        self.running = True
        self.EOF = '>>>WTF<<<'

    def _parse_date(self, date_string):
        """
        Attempt to parse the date string into a datetime object, trying different date formats.

        :param date_string: The date string to parse
        :return: The datetime object corresponding to the date string
        :raises ValueError: If the date string cannot be parsed into a datetime object
        """
        date_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S%z']
        for format in date_formats:
            try:
                return datetime.strptime(date_string, format)
            except ValueError:
                pass
        raise ValueError(f'Cannot parse date string: {date_string}')

    def load_contract_list(self):
        """
        Load contract data from the CSV file and parse dates.
        """
        with open(self.file_name, 'rt') as f:
            reader = csv.reader(f)
            columns = next(reader)
            for desired_col in self.column_list:
                for idx, val in enumerate(columns):
                    if val == desired_col:
                        self.column_idx.append(idx)
            if len(self.column_idx) != len(self.column_list):
                raise Exception('Column list does not match')
            while self.running:
                line = next(reader, self.EOF)
                if line == self.EOF:
                    self.running = False
                else:
                    needed_params = []
                    for y, idx in enumerate(self.column_idx):
                        value = line[idx]
                        if self.column_list[y] in self.date_fields:
                            value = self._parse_date(value)
                        needed_params.append(value)

                    # Do something with the needed parameters
                    print(needed_params)

if __name__ == '__main__':
    CSVLoader('ContractOpportunitiesFullCSV.csv').load_contract_list()
