import importlib
import os
from custom_nodes.SWAIN.shared import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


""" this module simplifies things by
    1. importing every node class from the SWAIN folder
    2. adding the nodes from the SWAIN folder to the NODE_CLASS_MAPPINGS dict
    
    further improvments could be made by:
    1. adding a way to define better names for the nodes
    2. adding a way to define the category of the nodes
    3. adding a way to define the description of the nodes

"""



# get this files folder
folder = os.path.dirname(os.path.abspath(__file__))

# import every node class from the SWAIN folder


# here we look for the names that are meant for display in the UI
# and we add them to them to the correct dict in this case NODE_DISPLAY_NAME_MAPPINGS
for file in os.listdir(folder):
    if file.endswith(".py") and not file.startswith("__"):
        # import the NODE_CLASS_MAPPINGS from the file
        module = importlib.import_module("custom_nodes.SWAIN." + file[:-3])

        NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)

        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

# here we add the nodes from the SWAIN folder
for k, v in NODE_CLASS_MAPPINGS.items():
    NODE_CLASS_MAPPINGS[k] = v
