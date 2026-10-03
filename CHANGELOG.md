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

- The `daisyui` template pack for django-crispy-forms. Select it with `CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]` and `CRISPY_TEMPLATE_PACK = "daisyui"`, and a form's text, email, URL, number, password, date, time and date-time inputs and textareas are drawn as daisyUI components with no layout written, each filling the width of its field. A field with any other widget is still drawn in place.
- Each field is drawn with its label, a required marker, its help text and every error message. The label is tied to the input, and the input is marked required, marked invalid and described by its help text and errors, so assistive technology announces them with the field. Labels, help text and errors are escaped.
- Errors that belong to a form as a whole are drawn once, in an element with `role="alert"`, through `|crispy`, `{% crispy %}` and `|as_crispy_errors`.
- Through `{% crispy %}` the pack draws the form element and its CSRF token, and honours the `FormHelper` settings for the form element, labels, errors, `label_class` and `field_class`. `help_text_inline` and `error_text_inline` are ignored.
- A demo page showing every text input in every state, inside the django-mvp shell and as a standalone page styled by daisyUI's CDN install alone.
- `Fieldset`, `Div`, `Row` and `Column` from django-crispy-forms are drawn by the `daisyui` pack: a daisyUI `fieldset` with its legend, a `div`, and a row that sets its columns side by side on a wide page. Your `css_id`, `css_class` and attributes are kept, and a container given `template=` is drawn with it. A demo page shows them, inside the django-mvp shell and as a standalone page.
- `Submit`, `Reset`, `Button`, `StrictButton`, `ButtonHolder` and `FormActions` from django-crispy-forms are drawn by the `daisyui` pack as daisyUI buttons in one container that wraps on a narrow page, and buttons added to a form helper with `add_input` are drawn after the fields inside the form element, as the same element a layout draws. A `disabled` attribute is kept, and class names written for other template packs, such as `btn-inverse`, are not drawn. The demo's layout objects pages show them.
- The package skeleton: an installable app, a demo project and the test suite.
