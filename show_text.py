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

    def notify(self, text):
        if isinstance(text, list):
            if len(text)>0:
                if isinstance(text[0], dict):
                    text_d = list_dict_display_str(text)
                    text_r = text
                elif isinstance(text[0], str):
                    if len(text) == 1:
                        text_d = text
                        text_r = text[0]

        if isinstance(text, str):
            text_d = [text]
            text_r = text

        if isinstance(text, dict):
            text_d = list_dict_display_str([text])
            text_r = text

        # try to decode the input to see if it is hex encoded
        try:
            clipped = text_r[2:-1]
            dehexed = binascii.unhexlify(clipped)
            text_r = json.loads(dehexed)
            text_r = json.loads(dehexed)
            text_d = list_dict_display_str(text_r)
        except:
            pass

        return {"ui": {"text": text_d}, "result": (text_r,)}

NODE_CLASS_MAPPINGS = {
    "ShowText": ShowText,
}
