The module contains types of different formats such as JSON, YAML, CSV, and so on.

# class SimpleYAML(SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py#L14)

YAML content settings type. Requires yaml module.

# class SimpleJSON(EmptyNoneMixin, SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py#L54)

JSON content settings type.

# class SimpleRawCSV(SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py#L79)

Type that converts simple CSV to list of lists.

# class SimpleCSV(EachMixin, SimpleRawCSV) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/markup.py#L124)

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