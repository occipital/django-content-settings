# Frequently Asked Questions

Many common use cases are covered in the [Cookbook](cookbook.md) and [Possible Extensions](extends.md), but here I want to address some frequently asked questions from other users.

---

### Can I create a variable in the Django admin before it’s defined in `content_settings.py`?

Yes, you can. Check out the [User Defined Variables](uservar.md) section for more information.

---

### Why are there two functions, `give` and `to_python`, when `give` often just returns its input?

The `give` function is designed to adapt data specifically for use in the project’s code, whereas `to_python` converts a string value into a Python object.

The key difference:
- **`to_python`**: Converts a string value to a Python object when the string value changes or at project startup.
- **`give`**: Adapts the Python object for use in the project, and this happens whenever the data is requested (e.g., from an attribute or another source).

---

### Why is the version still 0?

The module is still in active development. The design, including the naming conventions for types, may change. Version 1.0 will include a more stable and finalized design.

---

### Can I see the changes on the site before applying them to all users?

Yes. The preview functionality allows you to see changes before applying them globally. Learn more about it in the [UI article](ui.md#preview-functionality).

---

### I need to change multiple variables at once for a desired effect. How can I avoid users seeing an incomplete configuration?

This can be handled in several ways:

1. **Edit Multiple Values in the Change List**: 
   - Use the "mark" functionality to edit multiple settings on the same page and submit them together. Read more in the [UI article](ui.md#apply-multiple-settings-at-once).
   
2. **Use Preview Settings**: 
   - Add multiple changes to the preview and apply them all in one click. Read more in the [UI article](ui.md#preview-functionality).

---

### The guide didn’t help. What should I do?

This happens, as the documentation is still a work in progress and not all scenarios are covered yet.

Here’s how you can get additional support:

- **Have a specific question?** Use [Discussions on GitHub](https://github.com/occipital/django-content-settings/discussions).
- **Found a bug or unexpected behavior?** Report it on [Issues in GitHub](https://github.com/occipital/django-content-settings/issues).
- **Want to improve the documentation?** Contributions are welcome! You can find the Markdown sources in the [docs folder](https://github.com/occipital/django-content-settings/tree/master/docs).

---

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
