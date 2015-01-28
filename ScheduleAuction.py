__author__ = 'Conor'

from pymongo import MongoClient
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


if __name__ == '__main__':
    auctionScheduler = AuctionScheduler()
    client = MongoClient()
    db = client.AuctionData
    jobs = auctionScheduler.get_auction_items(db)
    print(jobs)
    auctionScheduler.initialize_publisher()