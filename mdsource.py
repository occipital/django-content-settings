import ast
import os
from pathlib import Path


GITHUB_PREFIX = "https://github.com/occipital/django-content-settings/blob/master/"
SOURCE_FOLDER = "content_settings"


def split_path(path):
    return list(Path(path).parts)


def path_to_linux(path):
    return "/".join(split_path(path))


def get_base_classes(bases):
    """Extract the names of base classes from the bases list in a class definition."""
    base_class_names = []
    for base in bases:
        if isinstance(base, ast.Name):
            base_class_names.append(base.id)
        elif isinstance(base, ast.Attribute):
            base_class_names.append(ast.unparse(base))
        else:
            base_class_names.append(ast.unparse(base))
    return ", ".join(base_class_names)


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
                yield f"\n\n{prefix} class {n.name}({get_base_classes(n.bases)})"
                yield f"<sup>[source]({GITHUB_PREFIX}{path_to_linux(file_path)}#L{n.lineno})</sup>\n\n"
                yield class_doc

                yield from md_from_node(n, prefix=prefix + "#", file_path=file_path)

        elif isinstance(n, ast.FunctionDef):
            if func_doc := ast.get_docstring(n):
                yield f"\n\n{prefix} def {n.name}"
                yield get_function_signature(n)
                yield f"<sup>[source]({GITHUB_PREFIX}{path_to_linux(file_path)}#L{n.lineno})</sup>\n\n"
                yield "\n\n"
                yield func_doc


def md_from_file(file_path):
    with open(file_path, "r") as file:
        node = ast.parse(file.read(), filename=file_path)

        if module_doc := ast.get_docstring(node):
            yield module_doc

        yield from md_from_node(node, prefix="##", file_path=file_path)


with open(os.path.join("docs", "source.md"), "w") as fh:
    for dirname, dirs, files in os.walk(SOURCE_FOLDER):
        if dirname.endswith("__pycache__"):
            continue

        for name in sorted(files):
            if not name.endswith(".py"):
                continue

            mddoc = "".join(md_from_file(os.path.join(dirname, name)))
            if not mddoc:
                continue

            # Save generated doc to the docfile

            dir = dirname[len(SOURCE_FOLDER) + 1 :]
            module_name = ".".join(Path(dir).parts + (os.path.splitext(name)[0],))

            fh.write(f"# {module_name}\n\n")

            fh.write(mddoc)
            fh.write("\n\n")
