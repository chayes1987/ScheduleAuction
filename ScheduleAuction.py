__author__ = 'Conor'

from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    db = client.AuctionData
    print(db)