# django-mvp-forms

A daisyUI template pack for django-crispy-forms, with form fields and widgets for django-mvp projects.

> **Status: pre-release.** The repository holds the package skeleton. The template pack is not written yet and nothing is published to PyPI.

## Why

[django-mvp](https://github.com/django-mvp/django-mvp) renders its pages with [daisyUI](https://daisyui.com), and its forms with [django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms). That leaves a gap: a crispy template pack that produces daisyUI markup and covers everything crispy-forms can lay out.

Two packs exist. [crispy-tailwind](https://github.com/django-crispy-forms/crispy-tailwind) emits plain Tailwind utility classes, not daisyUI components, and has had no release since February 2024. [crispy-daisyui](https://github.com/fabge/crispy-daisyui) is a fork of it that its author describes as modified just enough for their own needs, with no test suite. Neither is a base we want django-mvp's form rendering to rest on, so this package provides a pack that is maintained alongside django-mvp and tested against the Django and daisyUI versions it supports.

## Scope & philosophy

The package covers how a form is drawn and what goes in it:

- a complete daisyUI template pack for django-crispy-forms, including its layout objects
- form fields and widgets that have proved useful across django-mvp projects

It stays out of everything around the form. Form views, inline formset handling and form page templates belong to django-mvp. There are no models, no URLs and no migrations here.

The pack's templates are plain Django templates. They do not use [django-cotton](https://github.com/wrabit/django-cotton) or daisy-cotton, so the pack works in any daisyUI project, with or without django-mvp. For the same reason this package does not depend on django-mvp. The dependency runs the other way.

Fields and widgets are collected as real projects need them. They are not planned ahead and do not appear on the roadmap, so the set grows unevenly and that is intended.

When two reasonable designs conflict, stock daisyUI markup wins over custom styling, and matching crispy-forms' documented behaviour wins over inventing a new one.

## Installation

```bash
pip install django-mvp-forms
```

Then add it to `INSTALLED_APPS` alongside crispy-forms:

```python
INSTALLED_APPS = [
    # ...
    "crispy_forms",
    "mvp_forms",
]
```

The host project supplies daisyUI itself. This package ships markup, not a stylesheet.

## Quickstart

To follow once the template pack lands.

## Public surface

Nothing yet. The pack's name, its layout objects, and each field and widget are listed here as they are added.

## Contributing

Standards for this repository live in
[CONSTITUTION.md](https://github.com/django-mvp/django-mvp-forms/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/django-mvp/django-mvp-forms/blob/main/CONTEXT.md).

```bash
uv sync
uv run pytest
uv run pre-commit install
```

`demo/` is a Django project on django-mvp's application shell, for looking at
this package in a browser while working on it:

```bash
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

## License

MIT. See [LICENSE](https://github.com/django-mvp/django-mvp-forms/blob/main/LICENSE).
