Types that convert a string into a list of values.

# class SimpleStringsList(SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L37)

    Split a text into a list of strings.

    * comment_starts_with (default: #): if not None, the lines that start with this string are removed
    * filter_empty (default: True): if True, empty lines are removed
    * split_lines (default: 
): the string that separates the lines
    * filters (default: None): a list of additional filters to apply to the lines.
    

## def get_filters(self) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L60)

Get the filters based on the current configuration.

* If filters is not None, it is returned.
* If filter_empty is True, f_empty is added to the filters.
* If comment_starts_with is not None, f_comment is added to the filters.

## def gen_to_python(self, value: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L103)

Converts a string value into a generator of filtered lines.

# def split_validator_in(values: List[str]) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L137)

Returns a validator function that checks if a given value is in the specified list of values.
It uses for SplitTextByFirstLine.split_key_validator.

# class SplitTextByFirstLine(SimpleText) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L149)

Split text by the separator that can be found in the first line.
The result is a dictionary where the keys are the separators and the values are the text after the separator.

If your defaukt key is "EN", the first line can be "===== EN =====" to initialize the separator.
The next separator is initialized by the next line that starts with "=====", ends with "=====" and has a key in the middle.

It has the following new attributes:

* split_default_key: Optional[str] = None - the key which will be used for the first line
* split_default_chooser: Optional[Callable] = None - the function which will be used for chosing default value
* split_not_found - what should be done if the required key not found. `NOT_FOUND.DEFAULT` - return default value, `NOT_FOUND.KEY_ERROR` raise an exception and `NOT_FOUND.VALUE` return value from split_NOT_FOUND.VALUE
* split_not_found_value: Any = None - value that will be returned if the required key not found and split_not_found is `NOT_FOUND.VALUE`
* split_key_validator: Optional[Callable[[str], bool]] = None - function that validates a key. You can use a function `split_validator_in` for validator value
* split_key_validator_failed: str = SPLIT_FAIL.IGNORE - what should be done if the key is not valid. `SPLIT_FAIL.IGNORE` - just use line with unvalid key as value for the previous key. `SPLIT_FAIL.RAISE` - raise `ValidationError`

## def split_value(self, value: str) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L219)

The main function of the type. Split the value into a dictionary of values.

# class SplitByFirstLine(AdminPreviewSuffixesMixin, EachMixin, SplitTextByFirstLine) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L270)

The same as SplitTextByFirstLine, but results are converted to the specified type.

split_type attribute is used to specify the type of the values. It can be a dict to specify the type for each key.

# class SplitTranslation(SplitByFirstLine) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/array.py#L306)

SplitByFirstLine where the default value will be chosen by the current language