""" the server maintains the graphs remotely, and the client is just a dumb terminal that sends requests to the
server. """

import unittest
import json
import requests
from test_data import raw as test_dict


class TestExecServer(unittest.TestCase):
    def setUp(self):
        pass

    def test_post_prompt(self):
        test_req_data = {
            "graph_name": "test_api_00"
        }

        response = requests.post("http://127.0.0.1:3389/infer", json=json.dumps(test_req_data))
        print(response.text)
        self.assertEqual(200, response.status_code)


if __name__ == "__main__":
    unittest.main()
