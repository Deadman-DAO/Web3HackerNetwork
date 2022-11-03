import sys
import os
from lib.db_dependent_class import DBDependent

class PriorityRepoInserter(DBDependent):
    def __init__(self):
        DBDependent.__init__(self)
        self.insert_sql = """
        insert into priority_repos(repo_owner, repo_name) values (?, ?);
        """

    def process(self, file_name):
        line_count = 0
        insert_array = []
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                for line in f:
                    line = line.strip()
                    words = line.split(',')
                    if len(line) > 0 and len(words) == 2:
                        insert_array.append((words[0], words[1]))
                        line_count += 1
                        if line_count % 100 == 0:
                            self.get_cursor().executemany(self.insert_sql, insert_array)
                            insert_array = []
                            print(f'Inserted {line_count} records')
                    else:
                        print(f'Invalid line: {line}')
        else:
            print(f'File not found: {file_name}')

        if len(insert_array) > 0:
            self.get_cursor().executemany(self.insert_sql, insert_array)
            print(f'Inserted {line_count} (trailing) records')


if __name__ == '__main__':
    PriorityRepoInserter().process('priority_repos.csv' if sys.argv[1] is None else sys.argv[1])