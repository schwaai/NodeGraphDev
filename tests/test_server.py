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
            "graph_name": "test_simple_api",
            "prompt": "test prompt",

        }
        # set the json header
        headers = {"Content-Type": "application/json"}

        response = requests.post("http://127.0.0.1:8188/infer", json=test_req_data, headers=headers)
        print(response.text)
        self.assertEqual(200, response.status_code)

    def test_real_estate(self):
        test_req_data = {
            "graph_name": "test_simple_api_real_estate",
            "prompt": "test prompt",

        }
        # set the json header
        headers = {"Content-Type": "application/json"}

        response = requests.post("http://0.0.0.0:8188/infer", json=test_req_data, headers=headers)
        print(f'response:{response.text}')
        self.assertEqual(200, response.status_code)


if __name__ == "__main__":
    unittest.main()
