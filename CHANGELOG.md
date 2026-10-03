# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
  Everything not yet released goes under [Unreleased], grouped by change type:
  Added, Changed, Deprecated, Removed, Fixed, Security. Prepare Release promotes
  that section to a version heading and dates it.

  Do NOT write a version heading by hand. Tag Release fires on any push to main
  that touches pyproject.toml, and the only thing stopping it cutting a release
  from that push is the absence of a `## [X.Y.Z]` section matching the version
  in pyproject.toml. Writing one here defeats that guard, and the repository
  ends up with a tag and a GitHub Release for a version nobody prepared.

  Write for someone deciding whether to upgrade. Say what changed for them and
  what they have to do about it, not which files moved.
-->

## [Unreleased]

### Added

- The `daisyui` template pack, which draws text, email, URL, number, password, date, time and date-time inputs and textareas as daisyUI components. Select it with `CRISPY_ALLOWED_TEMPLATE_PACKS` and `CRISPY_TEMPLATE_PACK`.
- Each field of the `daisyui` pack has its label tied to the input, a required marker, help text and every error message, and the input is marked required, invalid and described by them. Text in the label, help text and errors is escaped.
- Errors that belong to a form as a whole are drawn by the `daisyui` pack, once, in an element with `role="alert"`, through `|crispy`, `{% crispy %}` and `|as_crispy_errors`.
- The `daisyui` pack honours the `FormHelper` settings for the form element, its CSRF token, labels, errors, `label_class` and `field_class`. With labels off each input is named by an `aria-label`; with errors off no error is drawn and no input points at one. `help_text_inline` and `error_text_inline` are ignored.
- A demo project page for the text inputs, inside the django-mvp shell and linked from its sidebar, and a standalone twin of it that takes its styling from daisyUI's CDN build alone. Each draws every input kind in five states, and a form to submit that comes back with a field error and a form-wide error.
- The README's installation and quickstart sections now work as written: installation is from GitHub, since nothing is on PyPI yet, and the quickstart carries the daisyUI stylesheet link, a view that hands the form to the template, and a submit button.
- The package skeleton: an installable app, a demo project and the test suite. No template pack, fields or widgets yet.
