# Frequently Asked Questions

a lot of cases have been covered in [Cookbook](cookbook.md), but here I just want to cover some of the questions I've been asked from the other users

### Can I create variable in Django admin before one was created in content_settings.py?

Yes. Check [User Defined Variables](uservar.md)

### Why are there two functions, give and to_python, when most of the time the first one just returns what it receives as input?

The function give is designed to adapt data specifically for use in the project's code, while to_python converts a string value into a Python object. The key difference between these two functions is that the conversion to a Python object occurs when there are changes in the string value or at the project's startup. In contrast, adaptation happens when this data is requested (from attribute or from ).

### Why it is still version 0?

I'm still working on design of the module, the name of the types might be changes soon. Version 1 - will have a much more stable design.

### Can I see the changes on site before applying those to all users

Yes. You can use preview settings functionality, read more about it in [UI artitle](ui.md#preview-functionality)

### I need to change multiple variables at once to get a desirable effect. If I change variables one by one the user has a chance to see a half working project

Yes, this can be done in multiple ways

* In change list form you can edit multiple values and submit those at once. You can use "mark" functionality to put all the values you need on the same page. Read more about it in [UI artitle](ui.md#apply-multiple-settings-at-once)
* Using preview settings functionality you can add multiple changes in preview and then apply those changes in one click. Read more about it in [UI artitle](ui.md#preview-functionality)

### The guide didn't help

That happens, the documentation is still work in progress, so not everything is covered.

If you have a specific question, please use [Discussions in github.com](https://github.com/occipital/django-content-settings/discussions).

If you find a bug, or unexpected behaviour use [Issues in github.com](https://github.com/occipital/django-content-settings/issues).

And, of course, you are very welcome to contribute changes in documentation. You can find markdown sources of the documentation in [docs folder](https://github.com/occipital/django-content-settings/tree/master/docs).

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)