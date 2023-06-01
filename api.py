import folder_paths
import server_utils
from custom_nodes.SWAIN.bases import ret_type
from custom_nodes.SWAIN.shared import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from custom_nodes.SWAIN import bases


class APITextWidget(bases.BaseSimpleTextWidget):
    CATEGORY = "api"


class ShowLastExec(APITextWidget):
    DISPLAY_NAME = "Show Last Execution Data"

    @classmethod
    def INPUT_TYPES(cls):
        return cls.required(cls._text)

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
    DISPLAY_NAME = "Last Exec's Result's KV pairs"

    @classmethod
    def INPUT_TYPES(cls):
        return cls.required(cls.both(cls._key, cls._text))

    def handler(self, key: str, text: str):
        import main
        key = key[0]
        value = text[0]
        main.server_obj_holder[0]["last_exec_result"] = {key: value}
        text = [value]
        ret = {"ui": {"text": text}, "result": (text,)}
        return ret


class RequestInput(APITextWidget):
    DISPLAY_NAME = "Requests Input Json"

    _hidden_override = {"hidden_override": ("STRING", {"optional": True, "default": None})}

    @classmethod
    def INPUT_TYPES(cls):
        ret = cls.both(cls.required(cls.both(cls._key, cls._overridden_value)),
                       cls.optional(cls._hidden_override))
        return ret

    def handler(self, key: str, overridden_value: str, hidden_override: str = None):
        import main
        if hidden_override == [""]:
            hidden_override = None

        if hidden_override == "":
            hidden_override = None

        if hidden_override is not None:
            overridden_value = hidden_override
            hidden_override = None

        if isinstance(key, list):
            key = key[0]

        if isinstance(overridden_value, list):
            overridden_value = overridden_value[0]

        main.server_obj_holder[0]["last_exec_result"] = {key: overridden_value}

        if not isinstance(overridden_value, list):
            text = [overridden_value]

        ret = {"ui": {"text": text}, "result": (text,)}
        return ret
