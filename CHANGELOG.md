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

- Disabled and read-only fields are drawn from the attributes already on the input, and the pack adds no class or attribute of its own for either. A field with `disabled=True` has `disabled` on its input, on every option of a radio or checkbox group and on a file field's removal checkbox, with its component class and its value (a password input has none). A `readonly` attribute on a widget reaches the input unchanged. Read-only is the browser's and applies only to text inputs and textareas.
- A hidden field's errors are drawn in the form-wide error element, as Django words them, `(Hidden field name) message`, escaped. Before, an invalid hidden field was drawn with its error nowhere, so a form failed with nothing on the page to say why. The element is drawn through `|crispy`, `{% crispy %}` and `|as_crispy_errors`, even when the form has no other form-wide error, and not at all with errors off.
- A file field is drawn as daisyUI's `file-input`, filling the width of its field, and an invalid one carries `file-input-error` and is described by its error. A `ClearableFileInput` whose field already holds a file shows a link to it; an optional field also offers a removal checkbox in a label of its own, tied to it by `for`, and a required one offers none and is not marked `required` in the browser, so the form can be submitted without choosing another file. A widget that allows several files keeps `multiple`, and a file name is escaped. A widget subclass that names its own template is drawn by that template.
- A `RadioSelect` is drawn as a group of daisyUI `radio` inputs and a `CheckboxSelectMultiple` as a group of `checkbox` inputs, each in a `<fieldset>` with a `<legend>` that is described by the field's help text and error. Every option is an input inside a `<label>` of its own, tied to it by `for`; the held options are checked, an invalid group's options carry `radio-error` or `checkbox-error`, choices with named groups sit under their name, and an attribute your widget sets on one option stays on that option. Options of a required checkbox group are not marked `required`. A widget subclass that names its own template or its own option template is drawn by it.
- A boolean field is drawn as daisyUI's `checkbox`, inside its own `<label>` that is tied to it by `for` and carries the required marker. The box is ticked when the field's value is true, an invalid one carries `checkbox-error` and is described by its error, help text describes it, and with labels off it is named by an `aria-label` and no label is drawn. A checkbox keeps its natural size and is not widened.
- A date drawn as three selects by `SelectDateWidget` is one field in a `<fieldset>` with a `<legend>`, one help text and one error element, and each select is named Year, Month or Day by an `aria-label`. A field with several inputs that share one label is framed this way, and a field with one input keeps its `div` and `label`. The pack's own templates need a form renderer that loads Django templates, which the default renderer and `TemplatesSetting` both do. A widget subclass that names its own template is drawn by that template.
- The pack carries a base English catalogue for the text it adds.
- A field with choices is drawn as daisyUI's `select`, filling the width of its field: a `ChoiceField`, a `MultipleChoiceField`, a `NullBooleanField` and choices with named groups, which become `<optgroup>`s. The held choice is selected, an invalid select carries `select-error` and is described by its error, and a class or `data-` attribute you gave the widget is kept.
- The `daisyui` template pack for django-crispy-forms. Select it with `CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]` and `CRISPY_TEMPLATE_PACK = "daisyui"`, and a form's text, email, URL, number, password, date, time and date-time inputs and textareas are drawn as daisyUI components with no layout written, each filling the width of its field. A field with any other widget is still drawn in place.
- Each field is drawn with its label, a required marker, its help text and every error message. The label is tied to the input, and the input is marked required, marked invalid and described by its help text and errors, so assistive technology announces them with the field. Labels, help text and errors are escaped.
- Errors that belong to a form as a whole are drawn once, in an element with `role="alert"`, through `|crispy`, `{% crispy %}` and `|as_crispy_errors`.
- Through `{% crispy %}` the pack draws the form element and its CSRF token, and honours the `FormHelper` settings for the form element, labels, errors, `label_class` and `field_class`. `help_text_inline` and `error_text_inline` are ignored.
- A demo page showing every text input in every state, inside the django-mvp shell and as a standalone page styled by daisyUI's CDN install alone.
- `Fieldset`, `Div`, `Row` and `Column` from django-crispy-forms are drawn by the `daisyui` pack: a daisyUI `fieldset` with its legend, a `div`, and a row that sets its columns side by side on a wide page. Your `css_id`, `css_class` and attributes are kept, and a container given `template=` is drawn with it. A demo page shows them, inside the django-mvp shell and as a standalone page.
- `Submit`, `Reset`, `Button`, `StrictButton`, `ButtonHolder` and `FormActions` from django-crispy-forms are drawn by the `daisyui` pack as daisyUI buttons in one container that wraps on a narrow page, and buttons added to a form helper with `add_input` are drawn after the fields inside the form element, as the same element a layout draws. A `disabled` attribute is kept, and class names written for other template packs, such as `btn-inverse`, are not drawn. The demo's layout objects pages show them.
- `HTML` and `Hidden` from django-crispy-forms work in a layout drawn by the `daisyui` pack. An `HTML` object is drawn where it is placed, including inside a `Fieldset`, `Column`, `ButtonHolder` or `FormActions`, with markup in its context values escaped, and a `Hidden` is an `<input type="hidden">` with no class and no generated id. The demo's layout objects pages show both.
- `MultiField` from django-crispy-forms is drawn by the `daisyui` pack as a daisyUI `fieldset` whose `<legend>` is its label, with each field inside it drawn in its own frame with its own label, help text and error. Your `css_id`, `css_class`, `label_class` and attributes are kept, and class names written for other template packs, such as `ctrlHolder`, `blockLabel` and `error`, are not drawn. With this, all thirteen layout objects of django-crispy-forms that structure a form or add buttons to it are drawn, and the demo's layout objects pages show each of them.
- A second demo page showing every select, boolean, radio and checkbox group, file and hidden input in empty, held-value, required, help-text, error and disabled states, plus a text input drawn disabled and another read-only and a multipart form to submit, inside the django-mvp shell and as a standalone page. A file you submit is checked and dropped, never stored.
- The package skeleton: an installable app, a demo project and the test suite.
