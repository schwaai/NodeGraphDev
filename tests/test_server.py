import unittest
import json
import requests

a = {'3': {'inputs': {'text': ['4', 0]},
           'class_type': 'ShowText'},
     '4': {'inputs': {'name': 'exec_func',
                      'text_to_eval': 'out_string="test"',
                      'float1': 0},
           'class_type': 'Eval Widget'}}


import json

test_dict = {'client_id': '7cc066a61061469ea800fc9e7ad04157', 'prompt': {'4': {'inputs': {'name': 'exec_func', 'text_to_eval': 'out_string="test"', 'float1': 0}, 'class_type': 'Eval Widget'}, '8': {'inputs': {'text': ['9', 0]}, 'class_type': 'ShowLastExec'}, '9': {'inputs': {'text': ['4', 0]}, 'class_type': 'ShowText'}, '10': {'inputs': {'text': ['8', 0]}, 'class_type': 'ShowText'}}, 'extra_data': {'extra_pnginfo': {'workflow': {'last_node_id': 10, 'last_link_id': 12, 'nodes': [{'id': 4, 'type': 'Eval Widget', 'pos': [-1, 570], 'size': {'0': 400, '1': 200}, 'flags': {}, 'order': 0, 'mode': 0, 'inputs': [{'name': 'image1', 'type': 'IMAGE', 'link': None}], 'outputs': [{'name': 'STRING', 'type': 'STRING', 'links': [11], 'slot_index': 0}, {'name': 'IMAGE', 'type': 'IMAGE', 'links': None, 'slot_index': 1}, {'name': 'FLOAT', 'type': 'FLOAT', 'links': None}], 'properties': {'Node name for S&R': 'Eval Widget'}, 'widgets_values': ['exec_func', 'out_string="test"', 0]}, {'id': 9, 'type': 'ShowText', 'pos': [436, 558], 'size': {'0': 210, '1': 76}, 'flags': {}, 'order': 1, 'mode': 0, 'inputs': [{'name': 'text', 'type': 'STRING', 'link': 11}], 'outputs': [{'name': 'STRING', 'type': 'STRING', 'links': [10], 'slot_index': 0}], 'properties': {'Node name for S&R': 'ShowText'}, 'widgets_values': ['test']}, {'id': 10, 'type': 'ShowText', 'pos': [653, 872], 'size': {'0': 210, '1': 76}, 'flags': {}, 'order': 3, 'mode': 0, 'inputs': [{'name': 'text', 'type': 'STRING', 'link': 12}], 'outputs': [{'name': 'STRING', 'type': 'STRING', 'links': [], 'slot_index': 0}], 'properties': {'Node name for S&R': 'ShowText'}}, {'id': 8, 'type': 'ShowLastExec', 'pos': [699, 580], 'size': {'0': 210, '1': 26}, 'flags': {}, 'order': 2, 'mode': 0, 'inputs': [{'name': 'text', 'type': 'STRING', 'link': 10}], 'outputs': [{'name': 'STRING', 'type': 'STRING', 'links': [12], 'slot_index': 0}], 'properties': {'Node name for S&R': 'ShowLastExec'}}], 'links': [[10, 9, 0, 8, 0, 'STRING'], [11, 4, 0, 9, 0, 'STRING'], [12, 8, 0, 10, 0, 'STRING']], 'groups': [], 'config': {}, 'extra': {}, 'version': 0.4}}, 'client_id': '7cc066a61061469ea800fc9e7ad04157'}}





class TestExecServer(unittest.TestCase):
    def setUp(self):
        with open("test.json", "r") as f:
            self.test_json = json.load(f)




    def test_post_prompt(self):
        response = requests.post("http://127.0.0.1:3389/exec", json=self.test_json)
        print(response.text)
        self.assertEqual(200, response.status_code)


if __name__ == "__main__":
    unittest.main()
