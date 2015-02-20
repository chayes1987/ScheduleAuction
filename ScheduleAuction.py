__author__ = 'Conor'

# The official documentation was consulted for all three 3rd party libraries used
# Mongo -> http://api.mongodb.org/python/current/tutorial.html
# 0mq -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html
# APScheduler -> https://apscheduler.readthedocs.org/en/latest/userguide.html#code-examples

from pymongo import MongoClient
from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime
import zmq
import threading

publisher = None
context = zmq.Context()
ACK_ADDRESS = 'tcp://172.31.32.21:2100'
PUBLISHER_ADDRESS = 'tcp://*:2000'
DATE_FORMAT = '%d-%m-%Y %H:%M:%S'


class AuctionScheduler:

    @staticmethod
    def get_auction_items(database):
        return database.auctions.find()

    @staticmethod
    def publish_start_auction_command(item_id):
        if None != publisher:
            message = 'StartAuction <id>{id}</id>'.format(id=item_id)
            publisher.send_string(message)
            print('PUB: ' + message)

    def schedule_jobs(self, sched, auction_items):
        for item in auction_items:
            start_time = datetime.strptime(item['start_time'], DATE_FORMAT)
            if start_time > datetime.now():
                item_id = item['_id']
                sched.add_job(self.publish_start_auction_command,
                              'date', run_date=start_time, args=[item_id])

    def initialize_scheduler(self, db_jobs):
        scheduler = BlockingScheduler()
        self.schedule_jobs(scheduler, db_jobs)
        print('Scheduler Running...')

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print('Scheduler Stopped...')
            pass

    @staticmethod
    def initialize_publisher():
        global publisher
        publisher = context.socket(zmq.PUB)
        publisher.bind(PUBLISHER_ADDRESS)

    def initialize_subscriber(self):
        thread = threading.Thread(target=self.subscribe)
        thread.daemon = True
        thread.start()

    @staticmethod
    def subscribe():
        subscriber = context.socket(zmq.SUB)
        subscriber.connect(ACK_ADDRESS)
        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode('ACK: StartAuction'))

        while True:
            msg = subscriber.recv()
            m = msg.decode()
            print(m)

    @staticmethod
    def initialize_mongo():
        mongo_client = None
        try:
            mongo_client = MongoClient()
        except (Exception, SystemExit):
            print('Error connecting to MongoDB...')
            pass

        return mongo_client

if __name__ == '__main__':
    auctionScheduler = AuctionScheduler()
    client = auctionScheduler.initialize_mongo()
    if None != client:
        print('Connected to MongoDB...')
        db = client.AuctionData
        jobs = auctionScheduler.get_auction_items(db)
        print('Auction items retrieved...')
        auctionScheduler.initialize_publisher()
        print('Publisher initialized...')
        auctionScheduler.initialize_subscriber()
        print('Subscriber initialized...')
        auctionScheduler.initialize_scheduler(jobs)
        print('Scheduler initialized...')