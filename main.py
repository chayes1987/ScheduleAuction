__author__ = 'Conor'

# Mongo -> http://api.mongodb.org/python/current/tutorial.html
# Config file -> https://docs.python.org/2/library/configparser.html
# Coding Standards -> https://www.python.org/dev/peps/pep-0008/

from scheduleauction import ScheduleAuction
from pymongo import MongoClient
from configparser import ConfigParser, Error
from config import Config


def initialize_mongo():
    """
    Initializes a Mongo client object
    :return: The Mongo client
    """
    mongo_client = None
    try:
        mongo_client = MongoClient()
    except (Exception, SystemExit):
        print('Error connecting to MongoDB...')
        pass

    return mongo_client


def read_config():
    """
    Reads the configuration file
    :return: A tuple with the entries from the file, None if exception
    """
    conf = ConfigParser()
    try:
        # Open the file and extract the contents
        conf.read_file(open('config.ini'))
        pub_address = conf.get('Addresses', 'PUB_ADDR')
        ack_address = conf.get('Addresses', 'ACK_ADDR')
        start_auction_topic = conf.get('Topics', 'START_AUCTION_TOPIC')
        ack_topic = conf.get('Topics', 'START_AUCTION_ACK_TOPIC')
        heartbeat_topic = conf.get('Topics', 'CHECK_HEARTBEAT_TOPIC')
        response_topic = conf.get('Topics', 'CHECK_HEARTBEAT_TOPIC_RESPONSE')
        heartbeat_address = conf.get('Addresses', 'HEARTBEAT_ADDR')
        service_name = conf.get('Service Name', 'SERVICE_NAME')
    except (IOError, Error):
        print('Error with config file...')
        return None

    return pub_address, ack_address, start_auction_topic, ack_topic, heartbeat_topic, response_topic,\
        heartbeat_address, service_name


def setup_scheduler(jobs, config):
    """
    Setup the scheduling, pub/sub functionality
    :param jobs: The jobs to schedule
    :param config: The contents of the configuration file
    :return: Nothing
    """
    scheduler = ScheduleAuction()
    scheduler.initialize_publisher(config[Config.PUB_ADDR])
    print('Publisher initialized...')
    scheduler.initialize_ack_subscriber(config[Config.ACK_ADDR], config[Config.ACK_TOPIC])
    scheduler.initialize_heartbeat_subscriber(config[Config.HEARTBEAT_ADDR], config[Config.HEARTBEAT_TOPIC],
                                              config[Config.HEARTBEAT_RESPONSE], config[Config.SERVICE_NAME])
    print('Subscribers initialized...')
    scheduler.initialize_scheduler(jobs, config[Config.TOPIC])


if __name__ == '__main__':
    mongo = initialize_mongo()
    # Check Mongo
    if None != mongo:
        print('Connected to MongoDB...')
        database = mongo.AuctionData
        # Check Database
        if None != database:
            auctions = database.auctions.find()
            configuration = read_config()
        # Check configuration and auctions
        if None != configuration and None != auctions:
            print('Auction items retrieved...\nConfiguration read...')
            setup_scheduler(auctions, configuration)