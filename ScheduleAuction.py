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


if __name__ == '__main__':
    auctionScheduler = AuctionScheduler()
    client = MongoClient()
    db = client.AuctionData
    print(db)
    auctionScheduler.initialize_publisher()