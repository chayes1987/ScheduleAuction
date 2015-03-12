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
        print('Scheduler initialized...')
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

    def initialize_subscribers(self, ack_adr, sub_adr, ack_topic, heartbeat_topic, response_topic, service_name):
        ack_thread = threading.Thread(target=self.subscribe_to_ack,
                                      kwargs={'ack_adr': ack_adr, 'ack_topic': str(ack_topic)},
                                      name='subscribe_to_ack')
        ack_thread.daemon = True
        ack_thread.start()

        heartbeat_thread = threading.Thread(target=self.subscribe_to_heartbeat,
                                            kwargs={'sub_adr': sub_adr, 'heartbeat_topic': str(heartbeat_topic),
                                                    'response_topic': response_topic, 'service_name': service_name},
                                            name='subscribe_to_heartbeat')
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

    @staticmethod
    def subscribe_to_ack(ack_adr, ack_topic):
        ack_subscriber = context.socket(zmq.SUB)
        ack_subscriber.connect(ack_adr)
        ack_subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(ack_topic))

        while True:
            print('REC: ' + ack_subscriber.recv().decode())

    @staticmethod
    def subscribe_to_heartbeat(sub_adr, heartbeat_topic, response_topic, service_name):
        heartbeat_subscriber = context.socket(zmq.SUB)
        heartbeat_subscriber.connect(sub_adr)
        heartbeat_subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(heartbeat_topic))

        while True:
            print('REC: ' + heartbeat_subscriber.recv().decode())
            message = response_topic + ' <params>' + service_name + '</params>'
            publisher.send_string(message)
            print('PUB: ' + message)