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
        """
        input is text : List[List[str]]
        Returns a dict to be displayed by the UI and passed to the next function
        output like ret["ui"]["text"] needs to be a list of strings
        output like ret["result"] should mirror the input

        >>> notify([["Hello", "world"], ["How", "are", "you?"]])
        {'ui': {'text': ["Hello", "world", "How", "are", "you?"]}, 'result': [["Hello", "world"], ["How", "are", "you?"]]}

        >>> notify([])
        {'ui': {'text': []}, 'result': []}
        """

        if not isinstance(text, list):
            raise TypeError('Input should be a list of list of strings')

        flat_text = []
        for sublist in text:
            if not isinstance(sublist, list):
                raise ValueError('All elements in the list should be list of strings')
            for item in sublist:
                if not isinstance(item, str):
                    raise ValueError('All elements in the sublists should be strings')
                flat_text.append(item)

        ret = {"ui": {"text": flat_text}, "result": text}
        return ret


NODE_CLASS_MAPPINGS = {
    "ShowText": ShowText,
}
