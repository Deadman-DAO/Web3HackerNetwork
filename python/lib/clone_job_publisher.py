import pika
import sys
import os
from threading import Lock, Event
from db_dependent_class import DBDependent
from monitor import MultiprocessMonitor, timeit
from child_process import ChildProcessContainer
import json


class CloneJobPublisher(DBDependent):
    class Subscriber:
        def __init__(self, mom):
            self.mom = mom

        def process_message(self, ch, meth, props, body):
            job = json.loads(body.decode())
            try:
                self.mom.execute_procedure('ReleaseRepoFromCloning', (job['repo_id'], job['machine_name'], job['repo_dir']))
            except Exception as e:
                print('Error encountered calling ReleaseRepoFromCloning ', e)
            finally:
                ch.basic_ack(delivery_tag=meth.delivery_tag)

        def main(self):
            self.mom.channel.basic_consume(queue='repo_clone_result', on_message_callback=self.process_message)
            self.mom.channel.start_consuming()

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        DBDependent.__init__(self, **kwargs)
        self.connection = None
        self.channel = None
        self.queue = None
        self.interrupt_event = Event()
        self.idle_wait = int(kwargs['idle_wait'] if 'idle_wait' in kwargs else 5)
        self.error_wait = int(kwargs['error_wait'] if 'error_wait' in kwargs else 5)
        self.running = True
        self.outbound_queue = None
        self.inbound_queue = None
        self.subscriber = None
        self.max_queue_size = 60
        self.queue_threshold_size = 20
        self.monitor = None
        self.repo_clone_jobs = 'repo_clone_jobs'
        self.repo_clone_result = 'repo_clone_result'

    def setup_msg_queues(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.outbound_queue = self.channel.queue_declare(queue=self.repo_clone_jobs, durable=True, passive=True)
        self.inbound_queue = self.channel.queue_declare(queue=self.repo_clone_result, durable=True, passive=True)
        self.channel.basic_qos(prefetch_count=1)

    @timeit
    def idle_sleep(self):
        self.interrupt_event.wait(self.idle_wait)

    def stop(self):
        self.running = False
        self.interrupt_event.set()

    def main(self):
        self.monitor = MultiprocessMonitor(self.kwargs)
        self.setup_msg_queues()
        self.subscriber = ChildProcessContainer(self.Subscriber(self), 'repo_clone_result_subscriber')
        while self.running:
            if self.queue.method.message_count < self.queue_threshold_size:
                self.execute_procedure('ReserveNextNreposForCloning',
                                       self.max_queue_size - self.queue.method.message_count)
                for goodness in self.get_cursor().stored_results():
                    result = goodness.fetchall()
                    for row in result:
                        dic = {'repo_id': row[0], 'repo_owner': row[1], 'repo_name': row[2]}
                        self.channel.basic_publish(exchange='',
                                                   routing_key=self.repo_clone_jobs,
                                                   body=json.dumps(dic),
                                                   properties=pika.BasicProperties(
                                                       delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))


if __name__ == '__main__':
    try:
        CloneJobPublisher(web_lock=Lock()).main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

