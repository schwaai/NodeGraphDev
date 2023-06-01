import folder_paths
import server_utils

from custom_nodes.SWAIN.bases import *




class APITextWidget(BaseSimpleTextWidget):
    CATEGORY = "api"


class ShowLastExec(APITextWidget):
    DISPLAY_NAME = "Show Last Execution Data"

    @classmethod
    def INPUT_TYPES(cls):
        return required(wg_text)

    def handler(self, text: str):
        import main
        last_exec_json = main.server_obj_holder[0]["last_exec_json"]

        server_utils.update_json_dict(folder_paths.saved_requests_json,
                                      {"last_exec_json": last_exec_json}
                                      )

        last_exec_json = [last_exec_json]
        res = {"ui": {"text": last_exec_json}, "result": (last_exec_json,)}
        return res


class LastExecResultKV(APITextWidget):
    DISPLAY_NAME = "Set Api result KV"

    @classmethod
    def INPUT_TYPES(cls):
        return required(both(wg_key, wg_text))

    def handler(self, key: str, text: str):
        import main

        value = text
        main.server_obj_holder[0]["last_exec_result"][key] = value
        text = [value]
        ret = {"ui": {"text": text}, "result": (text,)}
        return ret


class RequestInput(APITextWidget):
    DISPLAY_NAME = "Requests Input Json"

    #_hidden_override = {"hidden_override": ("STRING", {"optional": True, "default": None})}

    @classmethod
    def INPUT_TYPES(cls):
        ret = both(required(both(wg_key, wg_overridden_value)),
                       optional(wg_hidden))
        return ret

    def handler(self, key: str, overridden_value: str, hidden: str = None):
        import main
        to_process = overridden_value
        if hidden == "":
            hidden = None

        if hidden is not None: # if this has been set, then we want to process this value instead
            to_process = hidden
            hidden = None


        #main.server_obj_holder[0]["last_exec_result"] = {key: overridden_value}

        text = to_process

        ret = {"ui": {"text": [text]}, "result": (text,)}
        return ret
