__author__ = 'Conor'

# Enums -> http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
# Coding Standards -> https://www.python.org/dev/peps/pep-0008/

from enum import Enum


class Config(Enum):
    """
    Class to store enumerations for the configuration file for readability
    """
    PUB_ADDR = 0
    ACK_ADDR = 1
    TOPIC = 2
    ACK_TOPIC = 3
    HEARTBEAT_TOPIC = 4
    HEARTBEAT_RESPONSE = 5
    HEARTBEAT_ADDR = 6
    SERVICE_NAME = 7
