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
        import uuid
        test_req_data = {
            "graph_name": "test_simple_api",
            "prompt": "test prompt",
            "uuid": str(uuid.uuid4()),
        }
        # set the json header
        headers = {"Content-Type": "application/json"}

        response = requests.post("http://127.0.0.1:8188/infer", json=test_req_data, headers=headers)
        print(response.text)
        self.assertEqual(200, response.status_code)

    def test_real_estate(self):
        import uuid
        test_req_data = {
            "graph_name": "test_simple_api_real_estate",
            "prompt": "test prompt",
            "uuid": str(uuid.uuid4()),

        }
        # set the json header
        headers = {"Content-Type": "application/json"}

        response = requests.post("http://192.168.0.25:8188/infer", json=test_req_data, headers=headers)
        print(f'response:{response.text}')
        self.assertEqual(200, response.status_code)

    def test_many(self):
        import multiprocessing
        # send many requests from different processes
        def send_request():
            import random
            import uuid
            test_req_data = {
                "graph_name": "test_simple_api_real_estate",
                "prompt": "test prompt "+str(random.random()),
                "uuid": str(uuid.uuid4()),

            }
            # set the json header
            headers = {"Content-Type": "application/json"}

            response = requests.post("http://0.0.0.0:8188/infer", json=test_req_data, headers=headers)
            print(f'response:{response.text}')
            self.assertEqual(200, response.status_code)
        processes = []
        for i in range(10):
            p = multiprocessing.Process(target=send_request)
            processes.append(p)
            p.start()

        for process in processes:
            process.join()
        print('done')






if __name__ == "__main__":
    unittest.main()
