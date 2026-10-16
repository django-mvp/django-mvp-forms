# Modal

`Modal` puts fields in a daisyUI modal, drawn as a `<dialog>`. It comes from
`crispy_forms.bootstrap`. The pack draws nothing that opens it: your page does,
by the modal's `css_id`. The example page has a button that calls `showModal()`.

Open the modal with the button, then close it and send the form empty. The
modal opens by itself with the errors inside it.

```{live-example} /examples/modal/
:title: An address in a modal

../../../examples/layout_objects/modal.py
../../../templates/demo/examples/modal_form.html
```
