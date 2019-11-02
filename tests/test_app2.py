import unittest
import requests

server_address = "http://127.0.0.1:5000"


class FeatureTest(unittest.TestCase):

    def test_page_exsits(self):
        pages = ["", "/register", "/login", "/spell_check"]
        for page in pages:
            req = requests.get(server_address + page)
            self.assertEqual(req.status_code, 200)
