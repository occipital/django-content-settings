from functools import cached_property

from django.core.exceptions import ValidationError

from .basic import SimpleText, PREVIEW_PYTHON, SimpleString


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
    csv_dialect = "unix"
    fields = None
    tags = {"csv"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.fields is not None, "fields cannot be None"
        assert isinstance(
            self.fields, (list, tuple, dict)
        ), "fields must be list, tuple or dict"

    @cached_property
    def dict_fields(self):
        if isinstance(self.fields, dict):
            return self.fields
        return {f: SimpleString() for f in self.fields}

    def gen_to_python(self, value):
        value = super().to_python(value)
        if value is None:
            return None

        from csv import reader
        from io import StringIO

        try:
            csv = reader(StringIO(value), dialect=self.csv_dialect)
        except Exception as e:
            raise ValidationError(str(e))

        yield from self.gen_rows_to_python(csv)

    def gen_rows_to_python(self, csv):
        for row in csv:
            yield {
                name: c_type.to_python(value)
                for (name, c_type), value in zip(self.dict_fields.items(), row)
            }

    def to_python(self, value):
        val = self.gen_to_python(value)
        if val is None:
            return None
        return list(val)

    def give(self, value):
        if not value:
            return value
        return [
            {k: self.dict_fields[k].give(v) for k, v in row.items()} for row in value
        ]
