__author__ = 'Conor'

# The official documentation was consulted for all three 3rd party libraries used
# 0mq -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html
# APScheduler -> https://apscheduler.readthedocs.org/en/latest/userguide.html#code-examples

from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime
import zmq
import threading

publisher = None
context = zmq.Context()


class ScheduleAuction:

    @staticmethod
    def publish_start_auction_command(item_id, topic):
        if None != publisher:
            message = topic + ' <id>{id}</id>'.format(id=item_id)
            publisher.send_string(message)
            print('PUB: ' + message)

    def schedule_jobs(self, sched, auction_items, topic):
        for item in auction_items:
            start_time = datetime.strptime(item['start_time'], '%d-%m-%Y %H:%M:%S')
            if start_time > datetime.now():
                item_id = item['_id']
                sched.add_job(self.publish_start_auction_command,
                              'date', run_date=start_time, kwargs={'item_id': item_id, 'topic': topic})

    def initialize_scheduler(self, db_jobs, topic):
        scheduler = BlockingScheduler()
        self.schedule_jobs(scheduler, db_jobs, topic)
        print('Scheduler Running...')

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print('Scheduler Stopped...')
            pass

    @staticmethod
    def initialize_publisher(pub_addr):
        global publisher
        publisher = context.socket(zmq.PUB)
        publisher.bind(pub_addr)

    def initialize_subscriber(self, ack_adr, ack_topic):
        threading.Thread(target=self.subscribe,
                         kwargs={'ack_adr': ack_adr, 'ack_topic': str(ack_topic)},
                         name='subscribe').start()

    @staticmethod
    def subscribe(ack_adr, ack_topic):
        subscriber = context.socket(zmq.SUB)
        subscriber.connect(ack_adr)
        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(ack_topic))

        while True:
            print(subscriber.recv().decode())