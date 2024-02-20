import tomllib

with open("pyproject.toml", "rb") as toml_file:
    data = tomllib.load(toml_file)

print(data["tool"]["poetry"]["name"])
print(data["tool"]["poetry"]["version"])

with open("content_settings/__init__.py", "w") as f:
    f.write(f'__version__ = "{data["tool"]["poetry"]["version"]}"\n')
