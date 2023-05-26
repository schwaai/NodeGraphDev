import os
import openai
import abc


class Config:
    api_key = os.environ.get('OPENAI_API_KEY')
    organization = os.environ.get('OPENAI_ORG')


NODE_CLASS_MAPPINGS = {}

openai.organization = Config.organization
openai.api_key = Config.api_key


class WidgetMetaclass(abc.ABCMeta):
    """A metaclass that automatically registers classes."""

    def __init__(cls, name, bases, attrs):
        if not abc.ABC in bases:  # don't register ABC itself
            NODE_CLASS_MAPPINGS[name] = cls
        super().__init__(name, bases, attrs)


class SimpleTextWidget(abc.ABC, metaclass=WidgetMetaclass):
    """Abstract base class for simple construction"""

    CATEGORY = "text"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "handler"

    def __init__(self, func):
        self.func = func

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "text": ("STRING", {"multiline": True}),
        },
        }

    @abc.abstractmethod
    def handler(self, text):
        """All subclasses must provide a handler method"""
        pass


class SimpleTextWidget2x1(abc.ABC, metaclass=WidgetMetaclass):
    """Abstract base class for simple construction"""

    CATEGORY = "text"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "handler"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text1": ("STRING", {"multiline": True}),
            },
            "optional": {
                "text2": ("STRING", {"multiline": True}),
            }
        }
    @abc.abstractmethod
    def handler(self, text1,text2):
        """All subclasses must provide a handler method"""
        pass
class SimpleTextWidget2x2(abc.ABC, metaclass=WidgetMetaclass):
    """Abstract base class for simple construction"""

    CATEGORY = "text"
    RETURN_TYPES = ("STRING", "STRING",)
    FUNCTION = "handler"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text1": ("STRING", {"multiline": True}),
                "text2": ("STRING", {"multiline": True}),
            },

        }
    @abc.abstractmethod
    def handler(self, text1,text2):
        """All subclasses must provide a handler method"""
        pass

def OAI_completion(text):
    out_message = [{"role": "user", "content": text}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=out_message
    )
    gpt_message = response["choices"][0]["message"]["content"].strip()

    return gpt_message


"""
all of these classes are plugins for comfyui and follow the same pattern
all of the images are torch tensors and it is unknown and unimportant if they are on the cpu or gpu
all image inputs are (B,W,H,C)

avoid numpy and PIL as much as possible
"""


class LLMCompletion(SimpleTextWidget):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        self.func = OAI_completion
        super().__init__(self.func)
        import uuid
        self.SSID = str(uuid.uuid4())

        from main import server_obj_holder
        self.server_string = server_obj_holder[0]["server_strings"]
        self.server_string[self.SSID] = "empty"

    def handler(self, text):
        if text == "":
            return ("None",)
        completion = self.func(text)
        self.server_string[self.SSID] = completion
        return (completion,)


class LLMCompletionPrepend(SimpleTextWidget2x1):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        self.func = OAI_completion
        super().__init__()
        import uuid
        self.SSID = str(uuid.uuid4())

        from main import server_obj_holder
        self.server_string = server_obj_holder[0]["server_strings"]
        self.server_string[self.SSID] = []

    def handler(self, text1, text2):
        if text1 == "":
            return ("None",)
        completion = self.func(text1+text2)
        self.server_string[self.SSID].append(completion)

        return (completion, )

class LLMConvo(SimpleTextWidget2x2):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        self.func = OAI_completion
        super().__init__()
        import uuid
        self.SSID = str(uuid.uuid4())

        from main import server_obj_holder
        self.server_string = server_obj_holder[0]["server_strings"]
        self.server_string[self.SSID] = []

    def handler(self, text1, text2):
        """
        text1 is the conversation history, text2 is the user input
        for the output the first return is the appended conversation and the second is the completion
        """
        if text1 == "":
            return ("None",)

        completion = self.func(text1+text2)
        self.server_string[self.SSID].append(completion)

        return (text1+"\n"+text2+"\n"+completion, completion,)
class TextConcat(SimpleTextWidget2x1):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        super().__init__()

    def handler(self, text1, text2):
        return (text1+text2,)

class TextConcatNewLine(SimpleTextWidget2x1):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        super().__init__()

    def handler(self, text1, text2):
        return (text1 +"\n"+ text2,)