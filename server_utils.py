from aiohttp import web

import folder_paths
import json
import uuid


def is_valid_uuid(uuid_string):
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return str(uuid_obj) == uuid_string
    except TypeError:
        return False
    except ValueError:
        return False


def safe_read_saved_graphs():
    import os
    import json
    # make a random lock file name
    lock_file = folder_paths.saved_requests_json + str(uuid.uuid4()) + ".lock"

    # Try to create the lock file
    while True:
        try:
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL)
            with os.fdopen(fd, 'w'):
                break
        except FileExistsError:
            pass

    with open(folder_paths.saved_requests_json, 'r') as f:
        try:
            tmp = f.read()
            saved_requests = json.loads(tmp)
        except Exception as e:
            # Handle the exception
            return web.json_response({"error": "error loading saved requests json: " + str(e)}, status=400)

    # Remove the lock file
    os.remove(lock_file)

    return saved_requests


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


def get_json_dict(fname) -> dict:
    """ assumes data is dict kv pair"""
    # read the json file

    with open(fname, "r") as f:
        json_data = json.load(f)
    return json_data
