# adapted from
# Author: pythongosssss (GitHub: https://github.com/pythongosssss)
# Original code: https://github.com/pythongosssss/ComfyUI-Custom-Scripts
import os


root_path = os.path.abspath(__file__)
for _ in range(3):
    root_path = os.path.dirname(root_path)


class BaseShowNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"forceInput": True}),
        }}

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    FUNCTION = "notify"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    CATEGORY = "utils"

    def notify(self, text):
        raise NotImplementedError("Subclasses must implement the 'notify' method.")


# {'ui': {'text': ['[{"role": "user", "content": "hi !!!"}, {"role": "assistant", "content": "Hello there! How may I assist you today?"}]']}, 'result': (['[{"role": "user", "content": "hi !!!"}, {"role": "assistant", "content": "Hello there! How may I assist you today?"}]'],)}


NODE_CLASS_MAPPINGS = {
}
