import abc
from custom_nodes.SWAIN.shared import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

wg_text = {"text": ("STRING", {"multiline": True})}
wg_history = {"history": ("STRING", {"multiline": True,"default": ""})}
wg_key = {"key": ("STRING", {"multiline": False, "default": ""})}
wg_uuid = {"uuid": ("STRING", {"multiline": False})}
wg_text2 = {"text2": ("STRING", {"multiline": True})}
wg_role = {"role": (["assistant", "user"],)}
wg_not_used = {"not_used": ("STRING", {"multiline": False})}
wg_overridden_value = {"overridden_value": ("STRING", {"multiline": True, "default": ""})}
wg_hidden = {"hidden": ("STRING", {"default": ""})}


class WidgetMetaclass(abc.ABCMeta):
    """A metaclass that automatically registers classes."""

    def __init__(cls, name, bases, attrs):
        if not abc.ABC in bases:  # don't register ABC itself
            names = [str(base).lower() for base in bases]
            name_check = ["base" in name for name in names]
            if not any(name_check):
                NODE_CLASS_MAPPINGS[name] = cls
        if attrs.get("DISPLAY_NAME"):
            NODE_DISPLAY_NAME_MAPPINGS[name] = attrs["DISPLAY_NAME"]
        super().__init__(name, bases, attrs)


both = lambda a, b: {**a, **b}
required = lambda x: {"required": {k: v for k, v in x.items()}}
optional = lambda x: {"optional": {k: v for k, v in x.items()}}


def ret_type(x):
    first = list(x.items())[0][0]
    if first == "optional" or first == "required":
        raise ValueError("ret_type must be used WITHOUT optional or required")
    return x[first][0]


class BaseSimpleTextWidget(abc.ABC, metaclass=WidgetMetaclass):
    """Abstract base class for simple construction"""

    NODE_DISPLAY_NAME_MAPPINGS = NODE_DISPLAY_NAME_MAPPINGS

    CATEGORY = "text"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "pre_handler"
    PRE_FUNCTION = "handler"

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def INPUT_TYPES(cls):
        """All subclasses must provide an INPUT_TYPES method"""
        pass

    @abc.abstractmethod
    def pre_handler(self, **kwargs):
        """All subclasses must provide a pre_handler method"""
        pass

    @abc.abstractmethod
    def handler(self):
        """All subclasses must provide a handler method"""
        pass
