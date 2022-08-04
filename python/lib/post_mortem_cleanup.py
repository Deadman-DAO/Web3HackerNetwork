from threading import Lock

from db_driven_task import DBDrivenTaskProcessor, DBTask


class PostMortemCleanerUpper(DBDrivenTaskProcessor, DBTask):

    def __init__(self, **kwargs):
        DBDrivenTaskProcessor.__init__(self, **kwargs)
        self.count = None
        self.records_processed = 0

    def init(self):
        self.monitor.single.add_display_methods(cleaned=self.get_records_processed)

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

    def get_records_processed(self):
        return self.records_processed

    def process_db_results(self, result_args):
        self.count = 0
        for goodness in self.cursor.stored_results():
            result = goodness.fetchone()
            if result:
                self.count += int(result[0])
        self.records_processed += self.count
        return self.count > 0


if __name__ == '__main__':
    PostMortemCleanerUpper(Lock()).main()
