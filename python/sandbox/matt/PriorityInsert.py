from lib.db_dependent_class import DBDependent
class PriorityInsert(DBDependent):
    def __init__(self, file_name):
        DBDependent.__init__(self)
        self.file_name = file_name

    def load_repo_list(self):
        with open(self.file_name, 'rt') as f:
            return [line.strip().split('/') for line in f]

    def run(self):
        for item in self.load_repo_list():
            self.execute_procedure('RequestPriorityRepoInfo', (item[0], item[1]))
            print(f'Processed {item[0]}/{item[1]}')

if __name__ == '__main__':
    PriorityInsert('../data/github/needs_repo_info.txt').run()