import folder_paths
import json


def update_json_dict(fname, data_dict=None, data_json_input=None):
    """Works with data_dict or data_json but not both!"""

    if data_dict is None and data_json_input is None:
        raise ValueError("data_dict or data_json must be provided")

    if data_dict is not None and data_json_input is not None:
        raise ValueError("data_dict or data_json must be provided, not both")

    # Read the json file
    try:
        with open(fname, "r") as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        json_data = {}

    # Update the json data
    if data_dict is not None:
        json_data.update(data_dict)
    else:
        json_data.update(json.loads(data_json_input))

    # Write the json file
    with open(fname, "w") as f:
        json.dump(json_data, f, indent=2)


def get_json_dict(fname)->dict:
    """ assumes data is dict kv pair"""
    # read the json file

    with open(fname, "r") as f:
        json_data = json.load(f)
    return json_data
