# Frequently Asked Questions

a lot of cases have been covered in [Cookbook](cookbook.md), but here I just want to cover some of the questions I've been asked from the other users

### Can I create variable in Django admin before one was created in content_settings.py?

No. 

### Can I change settings in code?

Well, you can change `value` in `models.ContentSetting` instance, that would trigger the chaching update procedure, but I don't think it is a right way to use it.

Feel free to [post an issue](https://github.com/occipital/django-content-settings/issues/new) where you can explain a usecase where it is useful.

### Why are there two functions, give and to_python, when most of the time the first one just returns what it receives as input?

The function give is designed to adapt data specifically for use in the project's code, while to_python converts a string value into a Python object. The key difference between these two functions is that the conversion to a Python object occurs when there are changes in the string value or at the project's startup. In contrast, adaptation happens when this data is requested (from attribute or from ).
