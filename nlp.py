import json
import os
from warnings import warn

import openai
import time

from custom_nodes.SWAIN.bases import *


class Config:
    api_key = os.environ.get('OPENAI_API_KEY')
    organization = os.environ.get('OPENAI_ORG')


openai.organization = Config.organization
openai.api_key = Config.api_key

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


class SimpleTextWidget(BaseSimpleTextWidget):
    def __init__(self, func):
        super().__init__()
        self.func = func

    @classmethod
    def INPUT_TYPES(cls):
        use = required(wg_text)
        return use

    def handler(self, text):
        """Do something with text"""
        pass


class SimpleTextWidget2x1(BaseSimpleTextWidget):
    @classmethod
    def INPUT_TYPES(cls):
        use = both(required(wg_history), optional(both(wg_text2, wg_role)))
        return use

    def handler(self, history, role, text2=None):
        """Do something with history, role, and text2"""
        pass


class SimpleTextWidget2x2(BaseSimpleTextWidget):
    RETURN_TYPES = (ret_type(wg_text),ret_type(wg_text))
    RETURN_NAMES = ("History", "Result",)

    @classmethod
    def INPUT_TYPES(cls):
        use = both(required(both(wg_history, wg_text2)), optional(wg_role))
        return use

    def handler(self, history, text2, role="user"):
        """Do something with history, text2, and role"""
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
                        history = eval(history)

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

    @classmethod
    def INPUT_TYPES(cls):
        use = required(wg_text)
        return use

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

    @classmethod
    def INPUT_TYPES(cls):
        use = both(required(wg_history), optional(both(wg_text2, wg_role)))
        return use

    def handler(self, history, role, text2=None):
        if history == "":
            return ("None",)

        if role == "user":
            completion, history = self.func(user=history + text2)
        elif role == "assistant":
            completion, history = self.func(assistant=history + text2)

        self.server_string[self.SSID].append(completion)

        return (completion,)


class LLMConvo(SimpleTextWidget2x2):
    """Uses the input text to call the specified LLM model and returns the output string"""


    RETURN_TYPES = (ret_type(wg_text),ret_type(wg_text),)

    def __init__(self):
        self.func = OAI_completion
        super().__init__()
        import uuid
        self.SSID = str(uuid.uuid4())

        from main import server_obj_holder
        self.server_string = server_obj_holder[0]["server_strings"]
        self.server_string[self.SSID] = []

    INTERNAL_STATE_DISPLAY = True

    @classmethod
    def INPUT_TYPES(cls):
        use = both(required(both(wg_history, wg_text2)), optional(wg_role))
        return use

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
            dehexed = binascii.unhexlify(history[2:-1])
            history = json.loads(dehexed)

        except:
            pass

        if history == "" or history == " ":
            history = []

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
    """Concatenates the input texts and returns the output string"""

    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        use = both(required(wg_history), optional(wg_text2))
        return use

    def handler(self, history, role, text2):
        return (history + text2,)


class TextConcatNewLine(SimpleTextWidget2x1):
    """Concatenates the input texts with a new line and returns the output string"""
    DISPLAY_NAME = "Text Concat New Line"

    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(cls):
        use = both(required(wg_history), optional(wg_text2))
        return use

    def handler(self, history, role, text2):
        # decompose lists to first element
        return (history + "\n\n" + text2,)
