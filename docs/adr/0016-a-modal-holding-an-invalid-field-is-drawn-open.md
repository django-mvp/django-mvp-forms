# ADR 0016 — A modal holding an invalid field is drawn open

**Status:** accepted

## Decision

`layout/modal.html` draws its `dialog` with the `open` attribute when the fields drawn inside it
contain `aria-invalid="true"`, and with `autofocus`, so the keyboard starts inside it. The modal
can still be closed with its own close button.

A layout object added later that hides fields until asked for follows the same rule: when a field
inside it has an error, it is drawn showing that field.

## Why

A closed modal hides an error as completely as a closed tab does. A person submits the form and
sees nothing wrong. django-crispy-forms opens the tab or accordion group that holds an error and
has no such rule for a modal, so this is the pack's own.

django-crispy-forms hands the modal's template the drawn fields and no form, so the template
cannot read the form's errors. Django writes `aria-invalid="true"` on every visible input of a
field with errors, whether or not the form draws error messages, and escapes anything a person
typed, so the attribute in the drawn fields is reliable evidence. ADR 0008 rules out a `Modal`
subclass that would read the errors directly.

Django does not mark a hidden input invalid, so an error on a hidden field alone does not open
the modal.

A dialog shown by the `open` attribute is not modal to the browser: the Escape key does not close
it and the page behind it stays reachable. Making it modal needs `showModal()`, which is a script
(ADR 0014). `autofocus` puts the keyboard inside the dialog without one, and the README says how
the two cases differ.

The `open` attribute is used and not daisyUI's `modal-open` class, which holds a modal open until
the class is removed.

## Revisit if

django-crispy-forms passes the form to the modal's template, or Django stops marking invalid
inputs.
