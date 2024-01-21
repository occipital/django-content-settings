from functools import cached_property

from django.core.exceptions import ValidationError

from .basic import SimpleText, PREVIEW_PYTHON, SimpleString
from . import required, optional


class SimpleYAML(SimpleText):
    help_format = "Simple <a href='https://en.wikipedia.org/wiki/YAML' target='_blank'>YAML format</a>"
    admin_preview_as = PREVIEW_PYTHON
    yaml_loader = None
    tags = {"yaml"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            import yaml
        except ImportError:
            raise AssertionError("Please install pyyaml package")

    def get_yaml_loader(self):
        if self.yaml_loader is None:
            try:
                from yaml import CLoader as Loader
            except ImportError:
                from yaml import Loader
            return Loader
        return self.yaml_loader

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return None

        from yaml import load

        try:
            return load(value, Loader=self.get_yaml_loader())
        except Exception as e:
            raise ValidationError(str(e))


class SimpleJSON(SimpleText):
    help_format = "Simple <a href='https://en.wikipedia.org/wiki/JSON' target='_blank'>JSON format</a>"
    admin_preview_as = PREVIEW_PYTHON
    decoder_cls = None
    tags = {"json"}

    def get_decoder_cls(self):
        return self.decoder_cls

    def to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return None
        from json import loads

        try:
            return loads(value, cls=self.get_decoder_cls())
        except Exception as e:
            raise ValidationError(str(e))


class SimpleCSV(SimpleText):
    help_format = "Simple <a href='https://en.wikipedia.org/wiki/Comma-separated_values' target='_blank'>CSV format</a>"
    admin_preview_as = PREVIEW_PYTHON
    tags = {"csv"}

    csv_dialect = "unix"
    csv_fields = None
    csv_default_row = None
    csv_fields_list_type = SimpleString(optional)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.csv_fields is not None, "csv_fields cannot be None"
        assert isinstance(
            self.csv_fields, (list, tuple, dict)
        ), "csv_fields must be list, tuple or dict"

        if self.csv_default_row is None:
            self.csv_default_row = {
                k: (v.default if v.default == required else v.to_python(v.default))
                for k, v in self.dict_csv_fields.items()
                if v.default != optional
            }

    @cached_property
    def dict_csv_fields(self):
        if isinstance(self.csv_fields, dict):
            return self.csv_fields
        return {f: self.csv_fields_list_type for f in self.csv_fields}

    def get_csv_reader(self, value):
        value = super().to_python(value)
        if value is None:
            return None

        from csv import reader
        from io import StringIO

        try:
            return reader(StringIO(value), dialect=self.csv_dialect)
        except Exception as e:
            raise ValidationError(str(e))

    def gen_to_python(self, value):
        yield from self.gen_rows_to_python(self.get_csv_reader(value))

    def gen_rows_to_python(self, csv):
        for row in csv:
            if not row:
                continue
            yield {
                **self.csv_default_row,
                **{
                    name: c_type.to_python(value)
                    for (name, c_type), value in zip(self.dict_csv_fields.items(), row)
                },
            }

    def validate_raw_value(self, value: str) -> None:
        super().validate_raw_value(value)

        for i, row in enumerate(self.get_csv_reader(value), start=1):
            if not row:
                continue
            for (name, c_type), value in zip(self.dict_csv_fields.items(), row):
                try:
                    c_type.validate_value(value)
                except ValidationError as e:
                    raise ValidationError(f"row #{i}, {name}: {e}")

    def validate(self, rows):
        super().validate(rows)

        if rows is None:
            return

        for i, row in enumerate(rows, start=1):
            for name, value in row.items():
                if value == required:
                    raise ValidationError(f"row #{i}, {name}: Value is required")

    def to_python(self, value):
        val = self.gen_to_python(value)
        if val is None:
            return None
        return list(val)

    def give(self, value, suffix=None):
        if not value:
            return value
        return [
            {k: self.dict_csv_fields[k].give(v, suffix) for k, v in row.items()}
            for row in value
        ]
