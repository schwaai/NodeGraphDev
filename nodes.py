import torch

import os
import sys
import json
import hashlib
import traceback

from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy"))

import importlib

import folder_paths


def before_node_execution():
    pass


def interrupt_processing(value=True):
    pass


def after_node_execution():
    pass


NODE_CLASS_MAPPINGS = {
    # "KSampler": KSampler,

}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Sampling
    "KSampler": "KSampler",
}


def load_custom_node(module_path):
    module_name = os.path.basename(module_path)
    if os.path.isfile(module_path):
        sp = os.path.splitext(module_path)
        module_name = sp[0]
    try:
        if os.path.isfile(module_path):
            module_spec = importlib.util.spec_from_file_location(module_name, module_path)
        else:
            module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(module_path, "__init__.py"))
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)
        if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS") and getattr(module,
                                                                         "NODE_DISPLAY_NAME_MAPPINGS") is not None:
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
        else:
            print(f"Skip {module_path} module for custom nodes due to the lack of NODE_CLASS_MAPPINGS.")
    except Exception as e:
        print(traceback.format_exc())
        print(f"Cannot import {module_path} module for custom nodes:", e)


def load_custom_nodes():
    CUSTOM_NODE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "custom_nodes")
    possible_modules = os.listdir(CUSTOM_NODE_PATH)
    if "__pycache__" in possible_modules:
        possible_modules.remove("__pycache__")

    for possible_module in possible_modules:
        module_path = os.path.join(CUSTOM_NODE_PATH, possible_module)
        if os.path.isfile(module_path) and os.path.splitext(module_path)[1] != ".py": continue
        load_custom_node(module_path)


def init_custom_nodes():
    load_custom_nodes()
    load_custom_node(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy_extras"),
                                  "nodes_upscale_model.py"))
    load_custom_node(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy_extras"),
                                  "nodes_post_processing.py"))
    load_custom_node(
        os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy_extras"), "nodes_mask.py"))
