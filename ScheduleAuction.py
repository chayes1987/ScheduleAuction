__author__ = 'Conor'

# The official documentation was consulted for all three 3rd party libraries used
# Mongo -> http://api.mongodb.org/python/current/tutorial.html
# ZeroMQ -> https://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/patterns/pubsub.html
# APScheduler -> https://apscheduler.readthedocs.org/en/latest/userguide.html#code-examples

from pymongo import MongoClient
from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime
import zmq

publisher = None
context = zmq.Context()
PUBLISHER_ADDRESS = 'tcp://127.0.0.1:1000'
DATE_FORMAT = '%d-%m-%Y %H:%M:%S'


class AuctionScheduler:

    @staticmethod
    def get_auction_items(database):
        return database.auctions.find()

    @staticmethod
    def publish_start_auction_command(item_id):
        if None != publisher:
            message = "StartAuction <id>{id}</id>".format(id=item_id)
            publisher.send_string(message)
            print(message + " command published...")

    def schedule_jobs(self, sched, auction_items):
        for item in auction_items:
            start_time = datetime.strptime(item['start_time'], DATE_FORMAT)
            if start_time > datetime.now():
                item_id = item['_id']
                sched.add_job(self.publish_start_auction_command, 'date', run_date=start_time, args=[item_id])

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


if __name__ == '__main__':
    auctionScheduler = AuctionScheduler()
    client = MongoClient()
    print('Connected to MongoDB...')
    db = client.AuctionData
    jobs = auctionScheduler.get_auction_items(db)
    print('Auction items retrieved...')
    auctionScheduler.initialize_publisher()
    print('Publisher initialized...')
    auctionScheduler.initialize_scheduler(jobs)
    print('Scheduler initialized...')