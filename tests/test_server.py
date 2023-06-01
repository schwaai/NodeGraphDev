import unittest
import json
import requests
from test_data import raw as test_dict

class TestExecServer(unittest.TestCase):
    def setUp(self):
        with open("test.json", "r") as f:
            self.test_json = json.load(f)

    def test_post_prompt(self):

        response = requests.post("http://127.0.0.1:3389/infer", json=self.test_json)
        print(response.text)
        self.assertEqual(200, response.status_code)


if __name__ == "__main__":
    unittest.main()
