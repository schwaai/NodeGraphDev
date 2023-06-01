import binascii
import json


def list_dict_display_str(x: [{}]):
    ret = [f'{i["role"]}: {i["content"]}' for i in x]
    return ret


class ShowText:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"forceInput": True}),
        }}

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING_OUT",)

    # THIS IS BRYTHON CODE
    INTERNAL_STATE = ""
    FUNCTION = "notify"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)
    description = "Show text in browser"
    CATEGORY = "utils"

    def notify(self, text: [] or [{}] or str):
        """
        input is text : List[List[str]]
        Returns a dict to be displayed by the UI and passed to the next function
        output like ret["ui"]["text"] needs to be a list of strings
        output like ret["result"] should mirror the input

        >>> ShowText.notify([["Hello", "world"], ["How", "are", "you?"]])
        {'ui': {'text': ["Hello", "world", "How", "are", "you?"]}, 'result': [["Hello", "world"], ["How", "are", "you?"]]}

        >>> ShowText.notify([])
        {'ui': {'text': []}, 'result': []}
        """
        # valid types for text
        # #1 [{str,str}]
        # #2 [str]
        # #3 str

        # but the processor on the js side of things expects everything to be
        # [str]

        # so convert as so
        # #1 [{str,str}] -> [str+str, ...]
        # #2 [str] -> [str]
        # #3 str -> [str]

        if text:
            # check for bare str
            if isinstance(text, str):
                text_d = [text]
            else:
                text = text[0]
                # reject all input that is not [] or str
                if not isinstance(text, list):
                    raise TypeError("encapsulating type must be list or must be bare str")
                else:
                    if len(text) == 0:  # empty list but allowed
                        text_d = "none"
                    else:
                        if isinstance(text[0], dict):
                            # this is valid but needs transformed to [str+str, ...]

                            text_d = []
                            for d in text:
                                kvp = []
                                for k, v in d.items():
                                    kvp_str = f'{k}\n{v}'
                                    text_d.append(kvp_str)
                        else:
                            # this is valid and needs no transformation
                            text_d = text
        else:
            text_d = "undefined"

        # catch edge case where we are displaying something with a client_id in [0] (when displaying exec data)
        if "client_id" in text_d[0]:
            text_d = [str(text)]

        if not text_d:
            raise TypeError('Input should be a list of strings, list of dicts, or a single string')

        ret = {"ui": {"text": text_d}, "result": text}
        return ret


NODE_CLASS_MAPPINGS = {
    "ShowText": ShowText,
}
