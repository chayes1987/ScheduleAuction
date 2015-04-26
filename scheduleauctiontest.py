__author__ = 'Conor'

# Unit Testing -> https://docs.python.org/3/library/unittest.html
# Coding Standards -> https://www.python.org/dev/peps/pep-0008/

import unittest
import threading
import zmq
import time

context = zmq.Context()


class ScheduleAuctionTests(unittest.TestCase):
    """
    This class is responsible for testing 0mq pub/sub

    Attributes:
      context (0mq context): A 0mq context.
    """

    def test_pub_sub(self):
        """
        Tests the functionality of 0mq pub/sub
        :return: Nothing
        """
        publisher = context.socket(zmq.PUB)
        # Bind to an address on localhost
        publisher.bind('tcp://127.0.0.1:9999')
        # Allow time to bind
        time.sleep(1)

        # Create a thread to subscribe with
        subscriber_thread = threading.Thread(target=self.subscribe, name='subscribe')
        subscriber_thread.start()

        # Allow time to connect
        time.sleep(1)
        publisher.send_string('Test')

    def subscribe(self):
        """
        Subscribes to the message published in the test_pub_sub function
        :return: Assertion results
        """
        subscriber = context.socket(zmq.SUB)
        # Connect to the address on localhost and set the topic
        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode('Test'))
        subscriber.connect('tcp://127.0.0.1:9999')
        message = None

        while None == message:
            message = subscriber.recv().decode()

        # Check that the message is as expected
        self.assertEqual('Test', message)
        self.assertNotEqual('Tes', message)
        self.assertNotEqual('', message)

if __name__ == '__main__':
    unittest.main()