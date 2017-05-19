import unittest
from multiprocessing import Process
import zeep

from .common import spyne_app_process, get_client, generate_random_str


class MainTestSet(unittest.TestCase):
    def setUp(self):
        self.p = Process(target=spyne_app_process)
        self.p.start()

    def tearDown(self):
        self.p.terminate()

    def test_simple_request(self):
        self.assertEqual(get_client().service.ping("data"), "data")

    def test_big_request(self):
        req_data = generate_random_str(1024 ** 2)
        self.assertEqual(get_client().service.ping(req_data), req_data)

    def test_too_bit_request(self):
        with self.assertRaises(zeep.exceptions.TransportError) as ctx:
            req_data = generate_random_str(1024**2 * 2)
            self.assertEqual(get_client().service.ping(req_data), req_data)
