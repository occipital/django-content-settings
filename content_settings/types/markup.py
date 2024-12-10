"""
The module contains types of different formats such as JSON, YAML, CSV, and so on.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from typing import List, Optional, Tuple, Dict, Union

from content_settings.utils import remove_same_ident
from .basic import SimpleText, PREVIEW, SimpleString
from .each import EachMixin, Keys, Item
from .mixins import EmptyNoneMixin
from . import optional, BaseSetting, required


# TODO: should have Empty None as well as JSON
class SimpleYAML(SimpleText):
    """
    YAML content settings type. Requires yaml module.
    """

    admin_preview_as = PREVIEW.PYTHON
    yaml_loader = None

    def __init__(
        self, default: Optional[Union[str, required, optional]] = None, *args, **kwargs
    ):
        if isinstance(default, str):
            default = remove_same_ident(default)
        super().__init__(default, *args, **kwargs)

    def get_help_format(self):
        return _(
            "Simple <a href='https://en.wikipedia.org/wiki/YAML' target='_blank'>YAML format</a>"
        )

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


class SimpleJSON(EmptyNoneMixin, SimpleText):
    """
    JSON content settings type.
    """

    admin_preview_as = PREVIEW.PYTHON
    decoder_cls = None

    def get_help_format(self):
        return _(
            "Simple <a href='https://en.wikipedia.org/wiki/JSON' target='_blank'>JSON format</a>"
        )

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


class SimpleRawCSV(SimpleText):
    """
    Type that converts simple CSV to list of lists.
    """

    admin_preview_as = PREVIEW.PYTHON

    csv_dialect = "unix"

    def get_help_format(self):
        return _(
            "Simple <a href='https://en.wikipedia.org/wiki/Comma-separated_values' target='_blank'>CSV format</a>"
        )

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

    def to_python(self, value):
        reader = self.get_csv_reader(value)
        return [list(row) for row in reader if row]


class KeysFromList(Keys):
    def to_python(self, value):
        return super().to_python({k: v for k, v in zip(self.cs_types.keys(), value)})

    def give_python_to_admin(self, value, name, **kwargs):
        return {
            k: cs.give_python_to_admin(v, name, **kwargs)
            for (k, cs), v in zip(self.cs_types.items(), value)
        }


class KeysFromListByList(KeysFromList):
    def __init__(self, cs_type, keys):
        super().__init__(**{k: cs_type for k in keys})


class SimpleCSV(EachMixin, SimpleRawCSV):
    """
    Type that converts simple CSV to list of dictionaries.

    Attributes:

    - `csv_fields` (dict, tuple or list): defines the structure of the CSV. The structure definition used by `EachMixin`
    - `csv_fields_list_type` (BaseSetting): the type of the list elements in the `csv_fields` if it is not dict.

    Examples:

    ```python
    SimpleCSV(csv_fields=["name", "price"])
    SimpleCSV(csv_fields={"name": SimpleString(), "price": SimpleDecimal()})
    SimpleCSV(csv_fields=["name", "price"], csv_fields_list_type=SimpleString())
    ```
    """

    csv_fields: Optional[Union[List, Tuple, Dict]] = None
    csv_fields_list_type: BaseSetting = SimpleString(optional)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.csv_fields is not None, "csv_fields cannot be None"
        assert isinstance(
            self.csv_fields, (list, tuple, dict)
        ), "csv_fields must be list, tuple or dict"

        self.each = Item(
            KeysFromList(**self.csv_fields)
            if isinstance(self.csv_fields, dict)
            else KeysFromListByList(self.csv_fields_list_type, self.csv_fields)
        )
