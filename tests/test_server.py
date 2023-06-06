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
            "graph_name": "basic_test",
            "infer_uuid": "test_uuid",
            "client_prompt": "test prompt",

        }
        # set the json header
        headers = {"Content-Type": "application/json"}

        response = requests.post("http://127.0.0.1:3389/infer", json=test_req_data, headers=headers)
        print(response.text)
        self.assertEqual(200, response.status_code)


if __name__ == "__main__":
    unittest.main()
