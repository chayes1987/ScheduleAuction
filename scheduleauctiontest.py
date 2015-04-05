__author__ = 'Conor'

import unittest
import threading
import zmq
import time

context = zmq.Context()


class ScheduleAuctionTests(unittest.TestCase):

    def test_pub_sub(self):
        publisher = context.socket(zmq.PUB)
        publisher.bind('tcp://127.0.0.1:9999')
        # Allow time to bind
        time.sleep(1)

        subscriber_thread = threading.Thread(target=self.subscribe, name='subscribe')
        subscriber_thread.start()

        # Allow time to connect
        time.sleep(1)
        publisher.send_string('Test')

    def subscribe(self):
        subscriber = context.socket(zmq.SUB)
        subscriber.setsockopt(zmq.SUBSCRIBE, str.encode('Test'))
        subscriber.connect('tcp://127.0.0.1:9999')
        message = None

        while None == message:
            message = subscriber.recv().decode()

        self.assertEqual('Test', message)
        self.assertNotEqual('Tes', message)
        self.assertNotEqual('', message)

if __name__ == '__main__':
    unittest.main()