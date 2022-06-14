import pika
import json
import time


class RabbitWhole:
    def __init__(self):
        self.repo_clone_jobs = 'repo_clone_jobs'
        self.connection = None
        self.channel = None
        self.inbound_queue = None

    def setup_msg_queues(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.inbound_queue = self.channel.queue_declare(queue=self.repo_clone_jobs, durable=True)
        self.channel.basic_qos(prefetch_count=1)

    def process_message(self, ch, meth, props, body):
        job = json.loads(body.decode())
        print(job)
        ch.basic_ack(delivery_tag=meth.delivery_tag)

    def main(self):
        self.setup_msg_queues()
        self.channel.basic_consume(queue=self.repo_clone_jobs, on_message_callback=self.process_message)
        print('Starting consumer')
        self.channel.start_consuming()
        time.sleep(60)


if __name__ == '__main__':
    RabbitWhole().main()
