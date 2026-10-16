# Inline choices

A radio group or a checkbox group normally stacks its options. `InlineRadios`
and `InlineCheckboxes` draw them along one line instead, and wrap onto the next
line when there are many or the labels are long. Use them for short options
such as sizes or yes and no.

Send the form empty. The radio group is required, so it comes back with its
error. Pick a size and some extras and send it again.

```{live-example} /examples/inline-choices/
:title: A radio group and a checkbox group on one line

../../../examples/special_fields/inline_choices.py
```

The field, its validation and its value are the ones a group has without the
layout object. Only the way the options sit changes, and each stays a `radio`
or `checkbox` input in a label of its own. A text field named in either one is
drawn as it would be without it.
