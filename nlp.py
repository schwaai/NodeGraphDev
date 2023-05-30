import json
import os
from warnings import warn

import openai
import abc
import time


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
    RETURN_NAMES = ("STRING",)
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
    RETURN_NAMES = ("STRING",)
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
                "role": (["assistant", "user"],),
            }
        }

    @abc.abstractmethod
    def handler(self, history, role, text2=None):
        """All subclasses must provide a handler method"""
        pass


class SimpleTextWidget2x2(abc.ABC, metaclass=WidgetMetaclass):
    """Abstract base class for simple construction"""

    CATEGORY = "text"
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("History", "Result",)
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
            "optional": {
                "role": (["assistant", "user"],),
            }

        }

    @abc.abstractmethod
    def handler(self, history, text2, role="user"):
        """All subclasses must provide a handler method"""
        pass


import os
import openai

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

import os
import openai

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_openai_embedding(model, text):
    """
    Retrieves OpenAI embeddings for a given text using a specified model.

    Args:
    - model (str): The name of the OpenAI model to use for embeddings.
    - text (str): The text to generate embeddings for.

    Returns:
    - A list of embeddings (each as a list of floating-point values) for the input text.

    Raises:
    - openai.error.InvalidRequestError: If unable to generate embeddings for the specified text.
    - openai.error.AuthenticationError: If OpenAI API key is not set or is invalid.
    - requests.exceptions.Timeout: If the request to OpenAI API times out.

    Example usage:
    >>> model = "text-embedding-ada-002"
    >>> text = "The food was delicious and the waiter was very friendly."
    >>> embeddings = get_openai_embedding(model, text)
    >>> len(embeddings)
    1
    >>> len(embeddings[0])
    1536

    >>> text = "The quick brown fox jumped over the lazy dog."
    >>> embeddings = get_openai_embedding(model, text)
    >>> len(embeddings)
    1
    >>> len(embeddings[0])
    1536

    >>> text = "What is the meaning of life?"
    >>> embeddings = get_openai_embedding(model, text)
    >>> len(embeddings)
    1
    >>> len(embeddings[0])
    1536
    """
    embeddings = openai.Embedding.create(model=model, input=text)
    embeddings_list = [e["embedding"] for e in embeddings["data"]]
    return embeddings_list


def OAI_completion(user=None, assistant=None, system=None, history: [{str: str}] = None):
    """
    OpenAI Completion API
    :param user: user input
    :param assistant: assistant input
    :param system: system input
    :param history: list of dicts with keys "role" and "content"
    :return: gpt_message, history
    """
    if history == "undefined":
        history = []
    if history == "":
        history = []
    if isinstance(history, dict):
        history = [history]
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
                    if isinstance(history, list):
                        history = eval(history[0])

                    trimmed = history.replace("[", '').replace("]", '')
                    dqd = trimmed.replace("'", '').replace('"', '')
                    dqds = dqd.split(",")
                    d2 = [dqds[i:i + 2] for i in range(0, len(dqds), 2)]
                    d3 = [[i[0].strip(), i[1].strip()] for i in d2]
                    d4 = [{i[0].split(":")[0].strip(): i[0].split(":")[1].strip(),
                           i[1].split(":")[0].strip(): i[1].split(":")[1].strip()} for i in d3]
                    history = d4
                except Exception as e:

                    warn(f"invalid history: {history} using empty history {e}")
                    history = []

    if user:
        history.append({"role": "user", "content": user})
    if assistant:
        history.append({"role": "assistant", "content": assistant})
    if system:
        history.append({"role": "system", "content": system})

    for i in range(10):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=history
            )
            time.sleep(1)
            break

        except openai.error.RateLimitError as e:
            print(e)

    gpt_message = response["choices"][0]["message"]["content"].strip()
    # update the history
    history.append({"role": "assistant", "content": gpt_message})

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

    def handler(self, history, role, text2=None):
        if history == "":
            return ("None",)

        if role == "user":
            completion, history = self.func(user=history + text2)
        elif role == "assistant":
            completion, history = self.func(assistant=history + text2)

        self.server_string[self.SSID].append(completion)

        return (completion,)


def list_to_hex_str(x: list):
    import binascii, json
    print(len(str(x)))

    # str then json then hex ie str(hex(json(object)))
    x1 = json.dumps(x)
    x2 = binascii.hexlify(x1.encode('utf-8'))
    x3 = str(x2)
    return x3


def hex_str_to_list(x: str):
    import binascii, json
    print(len(str(x)))

    x1 = x[2:-1]
    x2 = binascii.unhexlify(x1)
    x3 = json.loads(x2)
    return x3


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

    INTERNAL_STATE_DISPLAY = True

    def handler(self, history, text2, role="user"):
        """
        text1 is the conversation history, text2 is the user input
        for the output the first return is the appended conversation and the second is the completion
        """
        import binascii

        try:
            history = json.loads(history)
        except:
            pass

        try:
            dehexed = binascii.unhexlify(history[0][2:-1])
            history = json.loads(dehexed)

        except:
            pass

        if history == "" or history == " ":
            history = []

        if isinstance(text2, list):
            text2 = text2[0]

        kwargs = {}
        kwargs[role] = text2
        kwargs["history"] = history
        # completion, history = self.func(user=text2, history=history)
        # completion, history = self.func(**kwargs, history=history)
        completion, history = self.func(**kwargs)

        self.server_string[self.SSID].append(completion)

        if not isinstance(completion, list):
            completion = [completion]

        hist_out = history
        if not isinstance(hist_out, list):
            hist_out = [hist_out]

        ui_result = {"ui": {"text": [completion]}, "result": (hist_out, completion,)}
        return ui_result


class TextConcat(SimpleTextWidget2x1):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        super().__init__()

    def handler(self, history, role, text2):
        if isinstance(history, list):
            history = history[0]
        if isinstance(text2, list):
            text2 = [0]
        return (history + text2,)


class TextConcatNewLine(SimpleTextWidget2x1):
    """Uses the input text to call the specified LLM model and returns the output string"""

    def __init__(self):
        super().__init__()

    def handler(self, history, role, text2):
        # decompose lists to first element
        if isinstance(history, list):
            history = history[0]
        if isinstance(text2, list):
            text2 = [0]
        return (history + "\n\n" + text2,)
