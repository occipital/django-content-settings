PREVIEW_HTML = "html"
PREVIEW_TEXT = "text"
PREVIEW_PYTHON = "python"

PREVIEW_ALL = [
    value for name, value in globals().items() if name.startswith("PREVIEW_")
]
