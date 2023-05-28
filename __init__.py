import importlib
import os

# get this files folder
folder = os.path.dirname(os.path.abspath(__file__))

# import every node class from the SWAIN folder

NODE_CLASS_MAPPINGS = {}

for file in os.listdir(folder):
    if file.endswith(".py") and not file.startswith("__"):
        # import the NODE_CLASS_MAPPINGS from the file
        module = importlib.import_module("custom_nodes.SWAIN." + file[:-3])
        NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)

# here we add the nodes from the SWAIN folder
for k, v in NODE_CLASS_MAPPINGS.items():
    NODE_CLASS_MAPPINGS[k] = v
