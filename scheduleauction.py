__author__ = 'Conor'

# The official documentation was consulted for all 3rd party libraries used
# 0mq -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html
# APScheduler -> https://apscheduler.readthedocs.org/en/latest/userguide.html#code-examples
# Coding Standards -> https://www.python.org/dev/peps/pep-0008/

from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime
import zmq
import threading

publisher = None
context = zmq.Context()


class ScheduleAuction:
    """
    This class is responsible for scheduling auctions based on their start datetime

    Attributes:
      publisher (0mq publisher): A 0mq publisher.
      context (0mq context): A 0mq context.
    """

    @staticmethod
    def publish_start_auction_command(item_id, topic):
        """
        Publishes the StartAuction command
        :param item_id: The ID of the auction
        :param topic: The command topic - StartAuction
        :return: Nothing
        """
        if None != publisher:
            # Build the command and publish it
            start_auction_command = topic + ' <id>{id}</id>'.format(id=item_id)
            publisher.send_string(start_auction_command)
            print('PUB: ' + start_auction_command)

    def schedule_auctions(self, sched, auction_items, topic):
        """
        Schedules the auctions based on start time e.g 26-04-2015 13:54:00
        :param sched: The scheduler object
        :param auction_items: The auction items to be scheduled
        :param topic: The command topic - StartAuction
        :return: Nothing
        """
        for auction_item in auction_items:
            # Extract the start time in the expected format - dd-mm-YY HH:MM:SS
            auction_start_time = datetime.strptime(auction_item['start_time'],
                                                   '%d-%m-%Y %H:%M:%S')
            # Schedule future auctions only
            if auction_start_time > datetime.now():
                # Extract the ID and create the scheduling job
                item_id = auction_item['_id']
                sched.add_job(self.publish_start_auction_command, 'date',
                              run_date=auction_start_time,
                              kwargs={'item_id': item_id, 'topic': topic})

    def initialize_scheduler(self, db_jobs, topic):
        """
        Initializes the scheduler
        :param db_jobs: The jobs to schedule
        :param topic: The command topic - StartAuction
        :return: Nothing
        """
        scheduler = BlockingScheduler()
        print('Scheduler initialized...')
        # Schedule the auctions and start the scheduler running
        self.schedule_auctions(scheduler, db_jobs, topic)
        print('Scheduler Running...')

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print('Scheduler Stopped...')
            pass

    @staticmethod
    def initialize_publisher(pub_addr):
        """
        Initializes the 0mq publisher object
        :param pub_addr: The address to bind to for publishing
        :return: Nothing
        """
        global publisher
        publisher = context.socket(zmq.PUB)
        publisher.bind(pub_addr)

    def initialize_ack_subscriber(self, ack_addr, ack_topic):
        """
        Initialize the subscriber for acknowledgements (separate thread)
        :param ack_addr: The address to subscribe to for acknowledgements
        :param ack_topic: The topic to subscribe to
        :return: Nothing
        """
        ack_thread = threading.Thread(target=self.subscribe_to_ack,
                                      kwargs={'ack_addr': ack_addr, 'ack_topic': str(ack_topic)},
                                      name='subscribe_to_ack')
        ack_thread.daemon = True
        ack_thread.start()

    def initialize_heartbeat_subscriber(self, sub_addr, heartbeat_topic, response_topic, service_name):
        """
        Initializes the subscriber for the heartbeat functionality
        :param sub_addr: The address to connect to
        :param heartbeat_topic: The topic to subscribe to - CheckHeartbeat
        :param response_topic: The topic to respond with - Ok
        :param service_name: The name of the service to respond with - ScheduleAuction
        :return: Nothing
        """
        heartbeat_thread = threading.Thread(target=self.subscribe_to_heartbeat,
                                            kwargs={'sub_addr': sub_addr, 'heartbeat_topic': str(heartbeat_topic),
                                                    'response_topic': response_topic, 'service_name': service_name},
                                            name='subscribe_to_heartbeat')
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

    @staticmethod
    def subscribe_to_ack(ack_addr, ack_topic):
        """
        Subscribe to acknowledgements
        :param ack_addr: The address to connect to
        :param ack_topic: The topic to subscribe to - ACK StartAuction
        :return: Nothing
        """
        ack_subscriber = context.socket(zmq.SUB)
        # Connect to the address and set the topic to subscribe to
        ack_subscriber.connect(ack_addr)
        ack_subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(ack_topic))

        while True:
            print('REC: ' + ack_subscriber.recv().decode())

    @staticmethod
    def subscribe_to_heartbeat(sub_addr, heartbeat_topic, response_topic, service_name):
        """
        Subscribe to the Heartbeat functionality
        :param sub_addr: The address to connect to
        :param heartbeat_topic: The topic to subscribe to - CheckHeartbeat
        :param response_topic: The topic to respond with - Ok
        :param service_name: The name of the service to respond with - ScheduleAuction
        :return: Nothing
        """
        heartbeat_subscriber = context.socket(zmq.SUB)
        # Connect to the address and set the topic to subscribe to
        heartbeat_subscriber.connect(sub_addr)
        heartbeat_subscriber.setsockopt(zmq.SUBSCRIBE, str.encode(heartbeat_topic))

        while True:
            print('REC: ' + heartbeat_subscriber.recv().decode())
            # Build and send the response immediately
            heartbeat_response = response_topic + ' <params>' + service_name + '</params>'
            publisher.send_string(heartbeat_response)
            print('PUB: ' + heartbeat_response)