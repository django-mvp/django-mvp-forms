# Form text

`FormText` puts a passage of text between fields: an introduction to the form,
a note about a fieldset or a group of fields, or the small print before the
button. Import it from `mvp_forms.layout`.

```python
from mvp_forms.layout import FormText

FormText("Tell us about the event you are planning.", size="large")
FormText("We only use this to reply to you.")
FormText(
    "By sending this enquiry you agree to our booking terms.",
    size="small",
    variant="muted",
)
```

With no size, the text is drawn at the size of the text in the inputs beside
it. `size="small"` draws it smaller and `size="large"` larger.
`variant="muted"` draws it in a lighter shade of the text colour, for text a
person can pass over, such as the small print. The text is
rendered as a template against the page's context, so it can hold markup and
read a value from the page. Markup in a context value is escaped.

A fieldset's `description` is drawn the same way, with no size.

```{live-example} /examples/form-text/
:title: An introduction, a note between fields, and the small print

../../../examples/layout_objects/form_text.py
```

## Sizes and the muted variant

Each size, plain and muted, short and long, beside a field's help text and a
fieldset's legend.

```{live-example} /examples/form-text-sizes/
:title: Small, no size and large, plain and muted

../../../examples/layout_objects/form_text_sizes.py
```
