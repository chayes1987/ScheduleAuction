# Schedule Auction

This is the scheduler service for my FYP. It is written in Python. It uses APScheduler for scheduling and also connects to a MongoDB database. It is responsible for scheduling auctions based on their start time.

## Project Setup

Requires a MongoDB daemon running on port 27017 with the correct database and collection.

Database: AuctionData
Collection: auctions

Sample Item JSON:
  {
    "_id" : "1",
    "start_time" : "08-02-2015 15:32:00"
  }

## License

None

## Setting up ScheduleAuction service on AWS

- Created AWS EC2 Linux instance
- Connected to instance using FileZilla using Public DNS and .pem keyfile
- Uploaded application directory to server
- Connected to server instance using PuTTy using ec2-user@PublicDNS and .pem keyfile for SSH Auth
- Installed Mongo -> http://michaelconnor.org/2013/07/install-mongodb-on-amazon-64-bit-linux/
  and ran mongo daemon
- Created Mongo database called 'AuctionData' - mongo AuctionData
- Created a collection called 'auctions' in the database and inserted sample objects:
	db.auctions.insert({"_id" : "1", "start_time" : "10-02-2015 16:42:00"})
	db.auctions.insert({"_id" : "2", "start_time" : "10-02-2015 16:43:00"})

## Application Setup Required
- Installed pymongo -> sudo easy_install pymongo
- Installed apscheduler -> sudo easy_install apscheduler
- Installed gcc -> sudo yum install gcc-c++
- Installed python3.4.2 -> sudo wget http://www.python.org/ftp/python/3.4.2/Python-3.4.2.tgz
- Instructions - (http://stackoverflow.com/questions/6630873/how-to-download-python-from-command-line)
- Set python default version to new verion (3.4.2) -> alias python=/usr/local/bin/python3.4
- Installed python-dev -> sudo yum install python-devel
- Installed zmq binding -> sudo easy_install pyzmq
- Installed config parser -> sudo easy_install configparser
- Installed enum -> sudo easy_install enum

- Running the service -> sudo python /home/ec2-user/ScheduleAuction/main.py

- Service runs and works as expected
