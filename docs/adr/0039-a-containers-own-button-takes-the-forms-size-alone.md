# ADR 0039 — A button a container draws for itself takes the form's size, and nothing else

**Status:** accepted

## Decision

The close button of a `Modal` and the dismiss button of an `Alert` take the size stated for the
form, and the size of a `Choice` around the container wins over it. They take no colour and no
variant: `button_color`, `button_variant` and the colour and variant of a `Choice` pass them by,
and a `Choice` around the container is never checked against them.

With no size stated they are drawn as before. The close button carries no size, and the dismiss
button carries `btn-sm`, which is also what `None` in a `Choice` gives it.

The alert reads the size from its context with the tag `daisyui_button_size`. The modal cannot:
django-crispy-forms renders a `Modal` with its fields and itself and no context. Its template
writes the class `daisyui-size` where the size goes. A `Choice` that states a size replaces it in
what it holds, and `daisyui_sized`, in `daisyui/display_form.html`, replaces what is left with
the form's size or removes it.

What is replaced is the button's whole class attribute, quotes included. A value a person typed
is escaped before it is drawn, so it can never be taken for a waiting button.

## Why

ADR 0021 already says a form's size reaches every input and every button the form draws, because
size is the one choice that always wants to match. A small form in a modal with small Save and
Cancel buttons and an ordinary Close button is the mismatch that decision exists to prevent.
Buttons attached to a field were settled the same way in ADR 0026.

Colour and variant say what a button a developer placed is for. These two are not placed by
anyone. A close button drawn in the colour of the form's Save button competes with it, and a
coloured dismiss button sits on an alert that has a colour of its own, where the pack could no
longer say the pairing can be read (ADR 0033).

The dismiss button keeps `btn-sm` when nothing is stated so that a form which states nothing is
drawn exactly as it was.

For the modal, the alternatives were a `Modal` subclass of the pack's, or state kept outside the
context while a form is drawn. The first breaks the promise that layout objects are imported from
django-crispy-forms as its documentation says. The second is hidden state for one class name. The
placeholder is the approach the pack already takes for the radios of a tab holder (ADR 0015),
and when a host project's replacement template skips the step, what is left is a class that does
nothing.

## Revisit if

django-crispy-forms passes the context to a `Modal`'s template, which makes the placeholder
unnecessary, or a real form needs the close button in a colour of its own.
