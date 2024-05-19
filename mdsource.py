import ast
import os
from pathlib import Path


GITHUB_PREFIX = "https://github.com/occipital/django-content-settings/blob/master/"
SOURCE_FOLDER = "content_settings"
DOCS_FOLDER = os.path.join("docs", "source")


def split_path(path):
    return list(Path(path).parts)


def path_to_linux(path):
    return "/".join(split_path(path))


def get_function_signature(func):
    """Generate the signature for a function or method."""
    args = []
    # Extract arguments and their default values
    defaults = [None] * (
        len(func.args.args) - len(func.args.defaults)
    ) + func.args.defaults
    for arg, default in zip(func.args.args, defaults):
        if isinstance(arg.annotation, ast.expr):
            # Get the annotation if present
            annotation = ast.unparse(arg.annotation)
            arg_desc = f"{arg.arg}: {annotation}"
        else:
            arg_desc = arg.arg

        if default is not None:
            default_value = ast.unparse(default)
            arg_desc += f" = {default_value}"
        args.append(arg_desc)
    return f"({', '.join(args)})"


def md_from_node(node, prefix, file_path):
    for n in node.body:
        if isinstance(n, ast.ClassDef):
            if class_doc := ast.get_docstring(n):
                yield f"\n\n{prefix} Class: {n.name}"
                yield f" [source]({GITHUB_PREFIX}{path_to_linux(file_path)}#L{n.lineno})"
                yield "\n\n"
                yield class_doc

                yield from md_from_node(n, prefix=prefix + "#", file_path=file_path)

        elif isinstance(n, ast.FunctionDef):
            if func_doc := ast.get_docstring(n):
                yield f"\n\n{prefix} {n.name}"
                yield get_function_signature(n)
                yield f" [source]({GITHUB_PREFIX}{path_to_linux(file_path)}#L{n.lineno})"
                yield "\n\n"
                yield func_doc


def md_from_file(file_path):
    with open(file_path, "r") as file:
        node = ast.parse(file.read(), filename=file_path)

        if module_doc := ast.get_docstring(node):
            yield module_doc

        yield from md_from_node(node, prefix="#", file_path=file_path)


nested_dict = {}
for dirname, dirs, files in os.walk(SOURCE_FOLDER):
    if dirname.endswith("__pycache__"):
        continue

    for name in files:
        if not name.endswith(".py"):
            continue

        mddoc = "".join(md_from_file(os.path.join(dirname, name)))
        if not mddoc:
            continue

        # Save generated doc to the docfile

        dir = dirname[len(SOURCE_FOLDER) + 1 :]
        docdir = os.path.join(DOCS_FOLDER, dir)
        os.makedirs(docdir, exist_ok=True)

        mdname = os.path.splitext(name)[0] + ".md"
        docfile = os.path.join(docdir, mdname)
        with open(docfile, "w") as fh:
            fh.write(mddoc)

        # save generated files into a dict

        parts = split_path(dir) + [mdname]
        d = nested_dict
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d.setdefault(parts[-1], None)


with open(os.path.join(DOCS_FOLDER, "index.md"), "w") as fh:

    def dict_to_markdown(d, indent=()):
        for key, value in d.items():

            if isinstance(value, dict):
                fh.write("    " * len(indent) + f"- {key}\n")
                dict_to_markdown(value, indent + (key,))
            else:
                if indent:
                    doc_path = "/".join(indent) + "/" + key
                else:
                    doc_path = key
                fh.write("    " * len(indent) + f"- [{key}]({doc_path})\n")

    dict_to_markdown(nested_dict)
