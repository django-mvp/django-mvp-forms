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

- A boolean field is drawn as daisyUI's `checkbox`, inside its own `<label>` that is tied to it by `for` and carries the required marker. The box is ticked when the field's value is true, an invalid one carries `checkbox-error` and is described by its error, help text describes it, and with labels off it is named by an `aria-label` and no label is drawn. A checkbox keeps its natural size and is not widened.
- A date drawn as three selects by `SelectDateWidget` is one field in a `<fieldset>` with a `<legend>`, one help text and one error element, and each select is named Year, Month or Day by an `aria-label`. A field with several inputs that share one label is framed this way, and a field with one input keeps its `div` and `label`. The pack's own templates need a form renderer that loads Django templates, which the default renderer and `TemplatesSetting` both do. A widget subclass that names its own template is drawn by that template.
- The pack carries a base English catalogue for the text it adds.
- A field with choices is drawn as daisyUI's `select`, filling the width of its field: a `ChoiceField`, a `MultipleChoiceField`, a `NullBooleanField` and choices with named groups, which become `<optgroup>`s. The held choice is selected, an invalid select carries `select-error` and is described by its error, and a class or `data-` attribute you gave the widget is kept.
- The `daisyui` template pack for django-crispy-forms. Select it with `CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]` and `CRISPY_TEMPLATE_PACK = "daisyui"`, and a form's text, email, URL, number, password, date, time and date-time inputs and textareas are drawn as daisyUI components with no layout written, each filling the width of its field. A field with any other widget is still drawn in place.
- Each field is drawn with its label, a required marker, its help text and every error message. The label is tied to the input, and the input is marked required, marked invalid and described by its help text and errors, so assistive technology announces them with the field. Labels, help text and errors are escaped.
- Errors that belong to a form as a whole are drawn once, in an element with `role="alert"`, through `|crispy`, `{% crispy %}` and `|as_crispy_errors`.
- Through `{% crispy %}` the pack draws the form element and its CSRF token, and honours the `FormHelper` settings for the form element, labels, errors, `label_class` and `field_class`. `help_text_inline` and `error_text_inline` are ignored.
- A demo page showing every text input in every state, inside the django-mvp shell and as a standalone page styled by daisyUI's CDN install alone.
- The package skeleton: an installable app, a demo project and the test suite.
