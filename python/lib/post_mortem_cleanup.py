import signal, traceback

from db_driven_task import DBDrivenTaskProcessor, DBTask


class PostMortemCleanerUpper(DBDrivenTaskProcessor, DBTask):
    def __init__(self):
        DBDrivenTaskProcessor.__init__(self)
        self.count = None

    def get_job_fetching_task(self):
        return self

    def get_job_completion_task(self):
        return None

    def process_task(self):
        pass

    def get_proc_name(self):
        return 'PostProcessHackerUpdate'

    def get_proc_parameters(self):
        return ['100']

    def process_db_results(self, result_args):
        self.count = 0
        for goodness in self.cursor.stored_results():
            result = goodness.fetchone()
            if result:
                self.count = int(result[0])
                print('Processed ', self.count)
        return self.count > 0


if __name__ == '__main__':
    PostMortemCleanerUpper().main()
