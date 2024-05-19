EachMixin is the main mixin of the module, which allows types to have subtypes, that check, preview and converts the structure of the value.

For example `array.TypedStringsList`

# Class: Item [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L48)

Converts each element of the array into a specific type `cs_type`

# Class: Keys [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L110)

Converts values of the specific keys into specific types `cs_types`

# Class: Values [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L202)

Converts each value of the given dict into `cs_type`

# Class: EachMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/each.py#L271)

Attributes:

- `each` - the type of the subvalues.
- `each_suffix_use` - how to use the suffixes. Can be `USE_OWN`, `USE_PARENT`, `SPLIT_OWN`, `SPLIT_PARENT`
- `each_suffix_splitter` - the string that separates the suffixes. Applicable only when `each_suffix_use` is `SPLIT_OWN` or `SPLIT_PARENT`