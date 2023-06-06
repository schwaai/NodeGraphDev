raw = [{'client_id': 'ea86091cccda4c8db451892713fa9db8',
        'prompt': {'2': {'inputs': {'key': 'response', 'text': ['9', 0]}, 'class_type': 'LastExecResultKV'},
                   '7': {'inputs': {'text': ['14', 0]}, 'class_type': 'ShowText'},
                   '9': {'inputs': {'key': 'prompt', 'overridden_value': 'hia    ', 'hidden': ''},
                         'class_type': 'RequestInput'}, '14': {'inputs': {'text': ''}, 'class_type': 'ShowLastExec'}},
        'extra_data': {'extra_pnginfo': {'workflow': {'last_node_id': 14, 'last_link_id': 18, 'nodes': [
            {'id': 7, 'type': 'ShowText', 'pos': [1640, 464], 'size': {'0': 510.0979919433594, '1': 419.8348388671875},
             'flags': {}, 'order': 3, 'mode': 0, 'inputs': [{'name': 'text', 'type': 'STRING', 'link': 18}],
             'outputs': [{'name': 'STRING_OUT', 'type': 'STRING', 'links': None}],
             'properties': {'Node name for S&R': 'ShowText'}, 'widgets_values': [
                "### REDACTED ###"]},
            {'id': 2, 'type': 'LastExecResultKV', 'pos': [1136, 675], 'size': {'0': 400, '1': 200}, 'flags': {},
             'order': 2, 'mode': 0, 'inputs': [{'name': 'text', 'type': 'STRING', 'link': 17,
                                                'widget': {'name': 'text', 'config': ['STRING', {'multiline': True}]}}],
             'outputs': [{'name': 'STRING', 'type': 'STRING', 'links': [], 'slot_index': 0}],
             'properties': {'Node name for S&R': 'LastExecResultKV'}, 'widgets_values': ['response', 'what']},
            {'id': 9, 'type': 'RequestInput', 'pos': [673, 667], 'size': {'0': 400, '1': 200}, 'flags': {}, 'order': 0,
             'mode': 0, 'outputs': [{'name': 'STRING', 'type': 'STRING', 'links': [17], 'slot_index': 0}],
             'properties': {'Node name for S&R': 'RequestInput'}, 'widgets_values': ['prompt', 'hia    ', '']},
            {'id': 14, 'type': 'ShowLastExec', 'pos': [1188, 378], 'size': {'0': 400, '1': 200}, 'flags': {},
             'order': 1, 'mode': 0, 'outputs': [{'name': 'STRING', 'type': 'STRING', 'links': [18], 'slot_index': 0}],
             'properties': {'Node name for S&R': 'ShowLastExec'}, 'widgets_values': ['']}],
                                                      'links': [[17, 9, 0, 2, 0, 'STRING'],
                                                                [18, 14, 0, 7, 0, 'STRING']], 'groups': [],
                                                      'config': {}, 'extra': {}, 'version': 0.4}},
                       'client_id': 'ea86091cccda4c8db451892713fa9db8'}}]

if __name__ == '__main__':
    for i, d in enumerate(raw):
        print(f'idx--{i}--\n{raw[i]}', end="\n\n\n")
