from enum import Enum, auto


class PREVIEW(Enum):
    HTML = auto()
    TEXT = auto()
    PYTHON = auto()
    NONE = auto()


class required:
    pass


class optional:
    pass


def pre(value: str) -> str:
    return "<pre>{}</pre>".format(str(value).replace("<", "&lt;"))


class BaseSetting:
    pass
