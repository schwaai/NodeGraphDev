import json
import os
from warnings import warn

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
                "history": ("STRING", {"multiline": True}),
            },
            "optional": {
                "text2": ("STRING", {"multiline": True}),
            }
        }

    @abc.abstractmethod
    def handler(self, history, text2):
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
                "history": ("STRING", {"multiline": True}),
                "text2": ("STRING", {"multiline": True}),
            },

        }

    @abc.abstractmethod
    def handler(self, history, text2):
        """All subclasses must provide a handler method"""
        pass


def OAI_completion(user=None, agent=None, system=None, history: [{str: str}] = None):
    """
    OpenAI Completion API
    :param user: user input
    :param agent: agent input
    :param system: system input
    :param history: list of dicts with keys "role" and "content"
    :return: gpt_message, history
    """
    if history == "undefined":
        history = []
    if history == "":
        history = []
    if not history:
        history = []
    else:
        if isinstance(history, list) and isinstance(history[0], dict):
            pass
        else:
            try:
                history = json.loads(history)
            except:
                print(f"invalid history: {history} attempting reconstruction")
                try:
                    trimmed = history.replace("[", '').replace("]", '')
                    dqd = trimmed.replace("'", '').replace('"', '')
                    dqds = dqd.split(",")
                    d2 = [dqds[i:i + 2] for i in range(0, len(dqds), 2)]
                    d3 = [[i[0].strip(), i[1].strip()] for i in d2]
                    d4 = [{i[0].split(":")[0].strip(): i[0].split(":")[1].strip(),
                           i[1].split(":")[0].strip(): i[1].split(":")[1].strip()} for i in d3]
                    history = d4
                except:
                    warn(f"invalid history: {history} using empty history")
                    history = []

    if user:
        history.append({"role": "user", "content": user})
    if agent:
        history.append({"role": "assistant", "content": agent})
    if system:
        history.append({"role": "system", "content": system})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )
    gpt_message = response["choices"][0]["message"]["content"].strip()
    # update the history
    history.append({"role": "assistant", "content": gpt_message})
    history = json.dumps(history)
    return gpt_message, history


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
        completion, history = self.func(user=text)
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

    def handler(self, history, text2):
        if history == "":
            return ("None",)
        completion, history = self.func(user=history + text2)
        self.server_string[self.SSID].append(completion)

        return (completion,)


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

    def handler(self, history, text2):
        """
        text1 is the conversation history, text2 is the user input
        for the output the first return is the appended conversation and the second is the completion
        """
        try:
            history = json.loads(history)
        except:
            pass

        if history == "" or history == " ":
            history = []

        completion, history = self.func(user=text2, history=history)
        self.server_string[self.SSID].append(completion)

        return (json.dumps(history), completion,)


class TextConcat(SimpleTextWidget2x1):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        super().__init__()

    def handler(self, history, text2):
        return (history + text2,)


class TextConcatNewLine(SimpleTextWidget2x1):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        super().__init__()

    def handler(self, history, text2):
        return (history + "\n\n" + text2,)
