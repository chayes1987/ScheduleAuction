__author__ = 'Conor'

from pymongo import MongoClient
from apscheduler.schedulers.background import BlockingScheduler
from datetime import datetime
import zmq

publisher = None
context = zmq.Context()


class AuctionScheduler:

    @staticmethod
    def initialize_publisher():
        global publisher
        publisher = context.socket(zmq.PUB)
        publisher.bind('tcp://127.0.0.1:1000')

    @staticmethod
    def get_auction_items(database):
        print('Retrieving auction items...')
        return database.auctions.find()

    def schedule_jobs(self, sched, auction_items):
        for item in auction_items:
            start_time = datetime.strptime(item['start_time'], '%d-%m-%Y %H:%M:%S')
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


if __name__ == '__main__':
    auctionScheduler = AuctionScheduler()
    client = MongoClient()
    db = client.AuctionData
    jobs = auctionScheduler.get_auction_items(db)
    auctionScheduler.initialize_publisher()
    auctionScheduler.initialize_scheduler(jobs)