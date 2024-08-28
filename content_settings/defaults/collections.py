"""
defaults collections for using in `CONTENT_SETTINGS_DEFAULTS`.

For example:

```python
CONTENT_SETTINGS_DEFAULTS = [
    codemirror_python(),
    codemirror_json(),
]
```

Or:

```python
CONTENT_SETTINGS_DEFAULTS = [
    *codemirror_all(),
]
```
"""

from content_settings.functools import or_

from .modifiers import add_admin_head, add_widget_class
from .filters import full_name_exact

DEFAULT_CODEMIRROR_PATH = "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/"


def _codemirror_raw_js(class_attr: str, mode: str):
    return f"""
    Array.from(document.getElementsByClassName("{class_attr}")).forEach((item, i) => {{
        const cm = CodeMirror.fromTextArea(item, {{
            lineNumbers: true,
            mode: "{mode}"
        }});
        cm.on("change", function(editor) {{
            item.value = editor.getValue();
        }});
        cm.on("focus", function(editor) {{
            item.dispatchEvent(new Event('focus'));
        }});
        cm.display.wrapper.after(item);
    }});
    """


def codemirror_python(
    path: str = DEFAULT_CODEMIRROR_PATH, class_attr: str = "codemirror_python"
):
    """
    Replace Textarea with CodeMirror for python code for SimpleEval and SimpleExec.
    """
    return (
        or_(
            full_name_exact("content_settings.types.template.SimpleEval"),
            full_name_exact("content_settings.types.template.SimpleExec"),
            full_name_exact("content_settings.types.template.SimpleExecNoCompile"),
        ),
        add_admin_head(
            css=[f"{path}codemirror.min.css"],
            js=[
                f"{path}codemirror.min.js",
                f"{path}mode/python/python.min.js",
            ],
            js_raw=[_codemirror_raw_js(class_attr, "python")],
        ),
        add_widget_class(class_attr),
    )


def codemirror_json(
    path: str = DEFAULT_CODEMIRROR_PATH, class_attr: str = "codemirror_json"
):
    """
    Replace Textarea with CodeMirror for json code for SimpleJSON.
    """
    return (
        full_name_exact("content_settings.types.markup.SimpleJSON"),
        add_admin_head(
            css=[f"{path}codemirror.min.css"],
            js=[
                f"{path}codemirror.min.js",
                f"{path}mode/javascript/javascript.min.js",
            ],
            js_raw=[_codemirror_raw_js(class_attr, "javascript")],
        ),
        add_widget_class(class_attr),
    )


def codemirror_yaml(
    path: str = DEFAULT_CODEMIRROR_PATH, class_attr: str = "codemirror_yaml"
):
    """
    Replace Textarea with CodeMirror for yaml code for SimpleYAML.
    """
    return (
        full_name_exact("content_settings.types.markup.SimpleYAML"),
        add_admin_head(
            css=[f"{path}codemirror.min.css"],
            js=[
                f"{path}codemirror.min.js",
                f"{path}mode/yaml/yaml.min.js",
            ],
            js_raw=[_codemirror_raw_js(class_attr, "yaml")],
        ),
        add_widget_class(class_attr),
    )


def codemirror_all(
    path: str = DEFAULT_CODEMIRROR_PATH, class_attr_prefix: str = "codemirror_"
):
    """
    Replace Textarea with CodeMirror for python, json and yaml code.
    """
    return [
        codemirror_python(path, f"{class_attr_prefix}python"),
        codemirror_json(path, f"{class_attr_prefix}json"),
        codemirror_yaml(path, f"{class_attr_prefix}yaml"),
    ]
