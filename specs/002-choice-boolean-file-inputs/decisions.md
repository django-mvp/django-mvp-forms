# Decisions: FS-002 Choice, boolean and file inputs drawn as daisyUI

Each entry is a point the issue left open, the reading the specification takes, and why. The
issue is three sentences long and nobody was asked to settle these, so every one of them is a
reading made while writing the specification. Any of them can be reversed when it is reviewed.

## The reading the specification was written from

The pack already draws text-like fields (#5). This feature draws every other widget in
`django.forms`: select and multiple select, radio groups, single checkboxes, checkbox groups and
file inputs as daisyUI's own inputs, and hidden inputs with nothing shown. Each visible field
reuses the label, required marker, help text and errors #5 delivers, tied to its input for
assistive technology. A disabled field is drawn as unavailable. With #5 and this together, a form
built from Django's own widgets draws completely with no layout and no per-field work. It serves
G1 and G3. Inline groups, uneditable fields, toggles, sizes and colours, and the inputs of a set
of forms stay with #8, #12, #11 and #10.

## D1. Disabled and read-only cover this feature's inputs only

**Ambiguous:** The roadmap lists "disabled and read-only states" as one deliverable of R1, and it
appears in this issue and not in #5. It could mean the states of every input the pack draws, or
only of the inputs drawn here.

**Chosen:** Only the inputs this feature draws (FR-015).

**Why:** The issue's sentence reads "the remaining widgets ... with disabled and read-only
states", so the states belong to those widgets. Specifying the states of #5's text inputs here
would define a sibling's behaviour. If #5 leaves them out, that gap is tracked in its own issue
and does not widen this one.

**ADR:** none — a reading of this feature's boundary

## D2. The pack does not imitate read-only where HTML has none

**Ambiguous:** The issue asks for read-only states, but a select, a checkbox, a radio button and a
file input have no read-only state in HTML. The attribute is ignored on all of them.

**Chosen:** A read-only attribute set by the developer reaches the input unchanged, and the pack
adds nothing to imitate the state. A field that must not be edited is marked disabled, which
Django enforces on the server as well (FR-016).

**Why:** Every imitation has a cost. Disabling the input behind the developer's back stops its
value being submitted, which changes what the form does. Blocking it with script needs JavaScript
the pack does not ship. Styling it to look fixed while it still accepts input misleads the person.
Django itself has no read-only field argument, only `disabled`, and the README says stock
behaviour wins over invention. Showing a field as uneditable from a layout is #8's.

**ADR:** to be written when the feature is built — it is a convention every later input and
widget in the pack follows, and a reader will ask why read-only does nothing on a select

## D3. A widget made of several inputs is split by the kind of each part

**Ambiguous:** Django ships widgets built from several inputs: a date as three selects, a date
and time as two text inputs, and a hidden version of the latter. The issues name none of them.

**Chosen:** Each part is drawn by whichever feature draws that kind of input. The three selects
and the hidden pair are drawn here, the two text inputs by #5. The field keeps one label, one help
text and one set of errors (FR-005).

**Why:** It needs no rule beyond the ones already written, and it leaves no widget in
`django.forms` unowned. The layout object that arranges a multi-widget field is #8's and is not
touched.

**ADR:** none — follows from the two features' existing boundaries

## D4. An error on a hidden field is shown with the form-wide errors

**Ambiguous:** A hidden field has nowhere on the page to show an error. The issue does not say
what happens to one.

**Chosen:** It is shown with the form-wide errors and never dropped (FR-013).

**Why:** Django's own form rendering does this, and G3 asks for errors the way current Django
expects. The alternative is a form that is rejected with nothing on the page to say why. The
drawing of form-wide errors is #5's, and this feature only requires that hidden-field errors reach
it.

**ADR:** none — matches Django's own behaviour

## D5. Required follows Django's rule for each widget

**Ambiguous:** Whether "required" on a checkbox group or on a file field with an existing file
should use the browser's own required check.

**Chosen:** The required marker is always shown. The browser's check is applied only where Django
applies it for that widget (FR-009).

**Why:** A browser check on every checkbox in a group would demand all of them be ticked, and one
on a file input would demand a new upload when a file is already held. Django already leaves the
attribute off in both cases, and the pack keeps what Django decides.

**ADR:** none — matches Django's own behaviour

## D6. Only widgets in `django.forms` are covered

**Ambiguous:** "The remaining widgets Django ships" could include widgets in `django.contrib`,
such as the admin's.

**Chosen:** `django.forms` only. A host project's subclass of one of those widgets draws like its
parent (FR-004).

**Why:** The admin's widgets depend on the admin's own scripts and styles, and third-party
widgets are goal G12, added when a project needs one.

**ADR:** none — a reading of this feature's scope

## D7. A boolean field is a checkbox here, and groups are not set in a line

**Ambiguous:** Whether this feature should also offer a toggle, or options set in a line.

**Chosen:** Neither. A boolean is daisyUI's checkbox, and a group has no inline form.

**Why:** #12 owns toggles and switches and #8 owns inline checkboxes and radios.

**ADR:** none — a sibling boundary

## D8. One demo page, and no prototype before the build

**Ambiguous:** How many demo pages the feature adds, and whether its screens need to be agreed by
eye before it is built.

**Chosen:** One page showing every input in every state (FR-021). No prototype first.

**Why:** Every input is daisyUI's stock input, and the README settles a close call in favour of
stock markup, so there is no design of the pack's own to judge in advance. The demo page is there
for looking at the result.

**ADR:** none — local to this feature
