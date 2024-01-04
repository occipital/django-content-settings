![Django Content Settings](img/title_7.png)

# Frequently Asked Questions

a lot of cases have been covered in [Cookbook](cookbook.md), but here I just want to cover some of the questions I've been asked from the other users

### Can I create variable in Django admin before one was created in content_settings.py?

No. 

### Can I change settings in code?

Well, you can change `value` in `models.ContentSetting` instance, that would trigger the chaching update procedure, but I don't think it is a right way to use it.

Feel free to [post an issue](https://github.com/occipital/django-content-settings/issues/new) where you can explain a usecase where it is useful.
