import time
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
            self.inbound_connection = None
            self.inbound_channel = None
            self.inbound_queue = None

        def process_message(self, ch, meth, props, body):
            job = json.loads(body.decode())
            try:
                self.mom.execute_procedure('ReleaseRepoFromCloning', (job['repo_id'], job['machine_name'], job['repo_dir']))
            except Exception as e:
                print('Error encountered calling ReleaseRepoFromCloning ', e)
            finally:
                ch.basic_ack(delivery_tag=meth.delivery_tag)

        def main(self):
            self.inbound_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            self.inbound_channel = self.inbound_connection.channel()
            self.inbound_queue = self.inbound_channel.queue_declare(queue=self.mom.repo_clone_result, durable=True)
            self.inbound_channel.basic_qos(prefetch_count=1)

            self.inbound_channel.basic_consume(queue='repo_clone_result', on_message_callback=self.process_message)
            self.inbound_channel.start_consuming()

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        DBDependent.__init__(self, **kwargs)
        self.outbound_connection = None
        self.outbound_channel = None
        self.size_checker_connection = None
        self.size_checker_channel = None
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
        self.size_checker = None

    def setup_msg_queues(self):
        self.outbound_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.outbound_channel = self.outbound_connection.channel()
        self.size_checker_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.size_checker_channel = self.size_checker_connection.channel()
        self.outbound_queue = self.outbound_channel.queue_declare(queue=self.repo_clone_jobs, durable=True)
        self.outbound_channel.basic_qos(prefetch_count=1)

    @timeit
    def idle_sleep(self):
        self.interrupt_event.wait(self.idle_wait)

    def stop(self):
        self.running = False
        self.interrupt_event.set()

    def main(self):
        self.monitor = MultiprocessMonitor(**self.kwargs)
        self.setup_msg_queues()
        self.subscriber = ChildProcessContainer(self.Subscriber(self), 'repo_clone_result_subscriber')
        while self.running:
            time.sleep(5)
            self.size_checker = self.size_checker_channel.queue_declare(queue=self.repo_clone_jobs, durable=True, passive=True)
            msg_cnt = self.size_checker.method.message_count
            print(msg_cnt, 'messages in queue')
            if msg_cnt < self.queue_threshold_size:
                print('Threshold boundary reached: ', msg_cnt)
                self.execute_procedure('ReserveNextNreposForCloning',
                                       [self.machine_name,
                                        self.max_queue_size - self.outbound_queue.method.message_count])
                for goodness in self.get_cursor().stored_results():
                    result = goodness.fetchall()
                    for row in result:
                        dic = {'repo_id': row[0], 'repo_owner': row[1], 'repo_name': row[2]}
                        self.outbound_channel.basic_publish(exchange='',
                                                            routing_key=self.repo_clone_jobs,
                                                            body=json.dumps(dic),
                                                            properties=pika.BasicProperties(
                                                                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
                    print('Published', len(result), 'jobs')


if __name__ == '__main__':
    try:
        CloneJobPublisher(web_lock=Lock()).main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

