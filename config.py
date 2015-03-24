__author__ = 'Conor'

# Enums -> http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python

from enum import Enum


class Config(Enum):
    PUB_ADDR = 0
    ACK_ADDR = 1
    TOPIC = 2
    ACK_TOPIC = 3
    HEARTBEAT_TOPIC = 4
    HEARTBEAT_RESPONSE = 5
    SUB_ADDR = 6
    SERVICE_NAME = 7
