# Decisions: FS-002 Choice, boolean and file inputs drawn as daisyUI

Each entry is a point the issue left open, the reading the specification takes, and why. The
issue is three sentences long and nobody was asked to settle these, so every one of them is a
reading made while writing the specification. Any of them can be reversed when it is reviewed.

## The reading the specification was written from

The pack already draws text-like fields (#5). This feature draws every other widget in
`django.forms`: select and multiple select, radio groups, single checkboxes, checkbox groups and
file inputs as daisyUI's own inputs, and hidden inputs with nothing shown. Each visible field
reuses the label, required marker, help text and errors #5 delivers, tied to its input for
assistive technology. A disabled field is drawn as unavailable, and so is a disabled or read-only text input from #5,
which leaves both states to this feature. With #5 and this together, a form
built from Django's own widgets draws completely with no layout and no per-field work. It serves
G1 and G3. Inline groups, uneditable fields, toggles, sizes and colours, and the inputs of a set
of forms stay with #8, #12, #11 and #10.

## D1. Disabled and read-only are drawn here for every input the pack draws

**Ambiguous:** The roadmap lists "disabled and read-only states" as one deliverable of R1, and it
appears in this issue and not in #5. It could mean the states of every input the pack draws, or
only of the inputs drawn here.

**Chosen:** Every input the pack draws, the text inputs of #5 included (FR-015, FR-023).

**Why:** The specification for #5 keeps the attributes Django emits and hands the drawing of both
states to this feature by name. Limiting them to this feature's inputs would leave text inputs
with no owner, and text inputs are the only ones HTML gives a read-only state, so the roadmap's
read-only deliverable would be delivered by nothing. The question was raised as #26 and settled
this way.

**ADR:** none — a reading of this feature's boundary

## D2. The pack does not imitate read-only where HTML has none

**Ambiguous:** The issue asks for read-only states, but a select, a checkbox, a radio button and a
file input have no read-only state in HTML. The attribute is ignored on all of them.

**Chosen:** On these inputs, a read-only attribute set by the developer reaches the input
unchanged, and the pack adds nothing to imitate the state. Text inputs and textareas have the
state and are drawn in it (FR-023). A field that must not be edited is marked disabled, which
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

## Decisions made while planning

The entries from here on were made when the feature was planned and built, against the code
FS-001 delivered. The evidence for each is in `research.md`.

## D9. A field of several inputs is framed as a fieldset with a legend

**Decision:** When Django marks a field's widget as a group (`use_fieldset`), the field frame is
a `<fieldset class="fieldset">` and the field's label is its `<legend class="fieldset-legend">`.
The fieldset is described by the help text and the error element. Every other field keeps the
`div` and the `label`.

**Why:** A radio group has no single input for a `label` to point at, and FR-007 asks for the
options to be announced as one group named by the field's label. A native fieldset does that with
no ARIA, it is what Django's own form templates draw, and it is daisyUI's own markup for the two
classes the frame already uses. ADR 0006 fixed the frame's element as a `div` so that it could
never be read from a page variable. `use_fieldset` is Django's flag on the widget and not a page
variable, so the reason stands and only the sentence changes.

**Revisit if:** a layout object needs a group drawn without a fieldset.

**ADR:** docs/adr/0008-a-group-is-framed-as-a-fieldset.md

## D10. The pack's own widget templates are drawn through a copy of the widget

**Decision:** Three widgets are drawn from templates of the pack's: a radio or checkbox group, a
date as three selects, and a clearable file input. `FieldInput` renders a shallow copy of the
field's widget with `template_name` pointed at the pack's template. It does so only when the
widget's `template_name` is still the one Django's class declares.

**Why:** Django's group template writes the widget's class on the wrapper as well as on every
option, and gives the option labels, the removal checkbox and the file link no class at all, so a
class alone cannot make them daisyUI's. A copy keeps ADR 0004's promise that nothing is written
to the form's widget. Checking the template name is what lets a host project's subclass keep a
template of its own (FR-004).

**Revisit if:** Django lets a caller name the template for one render.

**ADR:** docs/adr/0009-widget-templates-through-a-copy-of-the-widget.md

## D11. Read-only is the browser's state, and disabled is daisyUI's, both drawn from the attribute

**Decision:** The pack adds no class and no attribute for either state. A disabled field carries
Django's `disabled`, and daisyUI draws its disabled state from that attribute on every component
the pack uses. A `readonly` attribute reaches the input as the developer wrote it. On a text input
or a textarea the browser shows the value, refuses edits, announces the state and still submits
the value. On every other input it does nothing, and the pack does not imitate it (D2).

**Why:** daisyUI has no read-only rule for any component, and FR-023 limits the pack to daisyUI's
standard classes. Every disabled rule in daisyUI's stylesheet keys on the attribute, so a modifier
class would add nothing.

**Revisit if:** daisyUI gains a read-only modifier.

**ADR:** docs/adr/0010-disabled-and-read-only-are-drawn-from-the-attribute.md

## D12. A hidden field's error uses Django's own message

**Decision:** The form-wide alert lists each hidden field's errors as Django's
`"(Hidden field %(name)s) %(error)s"`, through `gettext` with the same msgid.

**Why:** It is what Django's own form rendering shows, and reusing the msgid gets every
translation Django ships with no catalogue in this package.

**Revisit if:** the package gains a catalogue of its own and wants other wording.

**ADR:** none — matches Django's own behaviour, and is local to one template

## D13. Three more layout utilities: `flex`, `flex-col`, `gap-2`

**Decision:** The options of a group are stacked with `flex flex-col gap-2`, and a date's three
selects are set side by side with `flex gap-2`. All three are named in the class test.

**Why:** daisyUI has no component that stacks a list of labels or puts selects in a row. ADR 0003
allows a Tailwind utility for layout in exactly that case.

**Revisit if:** daisyUI gains a component for either.

**ADR:** none — an application of ADR 0003, which already sets the rule

## D14. `w-full` goes on selects and file inputs, and not on checkboxes or radios

**Decision:** A select and a file input fill their container as text inputs do. A checkbox and a
radio button get no width.

**Why:** daisyUI gives `select` and `file-input` the same fixed width as `input`. A checkbox has
no width to fill.

**Revisit if:** ADR 0007 is revisited.

**ADR:** none — an application of ADR 0007

## D15. A split date and time stays uncovered

**Decision:** `SplitDateTimeWidget` is not given a component here. FS-001's tests that needed "a
widget the pack does not cover" are re-pointed at it, since the select, checkbox and file input
they used are now covered.

**Why:** FS-001's specification gives a field split across text inputs to #8.

**Revisit if:** #8 draws it.

**ADR:** none — a sibling boundary
