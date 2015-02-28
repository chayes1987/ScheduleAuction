__author__ = 'Conor'

# Mongo -> http://api.mongodb.org/python/current/tutorial.html
# Config file -> https://docs.python.org/2/library/configparser.html

from scheduleauction import ScheduleAuction
from pymongo import MongoClient
from configparser import ConfigParser, Error
from config import Config


def initialize_mongo():
    mongo_client = None
    try:
        mongo_client = MongoClient()
    except (Exception, SystemExit):
        print('Error connecting to MongoDB...')
        pass

    return mongo_client


def read_config():
    conf = ConfigParser()
    try:
        conf.read_file(open('config.ini'))
        ack_address = conf.get('Addresses', 'ACK_ADDR')
        pub_address = conf.get('Addresses', 'PUB_ADDR')
        topic = conf.get('Topics', 'START_AUCTION_TOPIC')
        ack_topic = conf.get('Topics', 'START_AUCTION_ACK_TOPIC')
    except (IOError, Error):
        print('Error with config file...')
        return None

    return pub_address, ack_address, topic, ack_topic


def schedule_items(jobs, config):
    sched = ScheduleAuction()
    sched.initialize_publisher(config[Config.PUB_ADDRESS])
    print('Publisher initialized...')
    sched.initialize_subscriber(config[Config.ACK_ADDRESS], config[Config.ACK_TOPIC])
    print('Subscriber initialized...')
    sched.initialize_scheduler(jobs, config[Config.TOPIC])


if __name__ == '__main__':
    client = initialize_mongo()
    if None != client:
        print('Connected to MongoDB...')
        db = client.AuctionData
        if None != db:
            auctions = db.auctions.find()
            configuration = read_config()
        if None != configuration and None != auctions:
            print('Auction items retrieved...\nConfiguration read...')
            schedule_items(auctions, configuration)