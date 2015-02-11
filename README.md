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
