# adapted from
# Author: pythongosssss (GitHub: https://github.com/pythongosssss)
# Original code: https://github.com/pythongosssss/ComfyUI-Custom-Scripts
import os
import folder_paths
import server_utils

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


class ShowLastExec(BaseShowNode):

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "not_used": ("STRING", {"forceInput": True}),
        }}

    def notify(self, not_used):
        import main
        last_exec_json = main.server_obj_holder[0]["last_exec_json"]

        server_utils.update_json_dict(folder_paths.saved_requests_json,
                                      {"last_exec_json": last_exec_json}
                                      )

        last_exec_json = [last_exec_json]
        res = {"ui": {"text": last_exec_json}, "result": (last_exec_json,)}
        return res


class LastExecResultKV(BaseShowNode):

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "key": ("STRING",
                    {"multiline": False,
                     "default": "result",
                     # "forceInput": True
                     }
                    ),
            "value": ("STRING",
                      {"forceInput": True}),
        }}

    def notify(self, key, value):
        import main
        key = key[0]
        value = value[0]
        main.server_obj_holder[0]["last_exec_result"] = {key: value}
        text = [value]
        ret = {"ui": {"text": text}, "result": (text,)}
        return ret


# {'ui': {'text': ['[{"role": "user", "content": "hi !!!"}, {"role": "assistant", "content": "Hello there! How may I assist you today?"}]']}, 'result': (['[{"role": "user", "content": "hi !!!"}, {"role": "assistant", "content": "Hello there! How may I assist you today?"}]'],)}

class RequestInput:

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "key": ("STRING", {
                "multiline": False,
                "default": "prompt",
            }),
            "overridden_value": ("STRING", {
                "multiline": True,
                "default": "prompt",
            }), },
            "optional": {
                "hidden_override": ("STRING", {
                    "default": None,
                }),

            }}

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    FUNCTION = "notify"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    CATEGORY = "utils"

    def notify(self, key, overridden_value, hidden_override=None):
        import main
        if hidden_override == [""]:
            hidden_override = None
        if hidden_override is not None:
            overridden_value = hidden_override
            hidden_override = None

        key = key[0]
        overridden_value = overridden_value[0]
        main.server_obj_holder[0]["last_exec_result"] = {key: overridden_value}
        text = [overridden_value]
        ret = {"ui": {"text": text}, "result": (text,)}
        return ret


NODE_CLASS_MAPPINGS = {
    "ShowLastExecShowText": ShowLastExec,
    "LastExecResultKVShowText": LastExecResultKV,
    "ClassRequestInputShowText": RequestInput,
}
