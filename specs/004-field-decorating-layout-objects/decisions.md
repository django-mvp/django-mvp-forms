# Decisions: Layout objects that decorate a field

The reading of issue #8 this specification was written from, the assumptions made where the issue
is silent, and the reasoning too long to put in `spec.md`. Nobody was asked while it was written,
so every entry is a choice the maintainer can overrule on the pull request.

## The reading of the issue

Issue #8 asks for a layout to be able to change how one field is presented. django-crispy-forms
ships nine layout objects that do that: `PrependedText`, `AppendedText`, `PrependedAppendedText`,
`InlineCheckboxes`, `InlineRadios`, `FieldWithButtons`, `UneditableField`, `InlineField` and
`MultiWidgetField`. The feature is the pack drawing each of them as daisyUI markup for a developer
who places them in a `Layout`. The field keeps its label, required marker, help text and errors,
tied to the input, and the form submits what it would have submitted anyway. Each of the six kinds
of decoration gets a demo page, and the nine are listed in the README's public surface.

It serves G2, because these are layout objects django-crispy-forms ships and G2 names prepended
and appended text outright, and G3, because every one of them rearranges a label, a help text or
an error and could break the tie to the input while doing so.

The inputs belong to #5 and #6, the buttons to #7, and size, colour and variant to #11. Tabs,
accordion, modal and alert are #9. Joined inputs in general and floating labels are roadmap
item R7.

## D1. The nine layout objects are django-crispy-forms' own classes

**Chosen:** a layout imports these classes from django-crispy-forms and the pack supplies only how
they are drawn (FR-023).

**Rejected:** shipping our own classes with the same names. That gives a developer two imports for
one thing and makes every django-crispy-forms release a compatibility question. The constitution
(Article III) asks for no wrapper without a second use, and Article XIV asks the pack to match
documented django-crispy-forms behaviour.

**ADR:** none. It follows from Articles III and XIV, and whether the pack ships any class of its
own is decided where the first one is needed, not here.

## D2. Buttons attached to a field are drawn by FS-003, which makes #7 a dependency

**Chosen:** `FieldWithButtons` attaches whatever button layout objects the pack already draws
(FR-012). The issue's footer names only #6 as a dependency. #7 has to be added to it, because a
field with buttons cannot be shown or tested without a button.

**Rejected:** drawing `StrictButton` in this feature so that it needs only #6. Buttons are #7's
subject, and two features drawing buttons would disagree as soon as #11 gives buttons a size and a
colour.

#7 draws `StrictButton` along with the other buttons, which was settled in #21.

**ADR:** none. It is a boundary between two features, and nothing later inherits it.

## D3. An uneditable field is drawn disabled, and its value is not submitted

**Chosen:** `UneditableField` draws the input disabled with its current value (FR-015). The
documentation says the browser leaves the value out and that a form which needs it declares the
field disabled in the form class (FR-016).

**Rejected:** drawing it read-only so the value is still submitted. django-crispy-forms documents
this layout object as rendering a disabled field, and Article XIV says to match that. Read-only
also means nothing on a select, a checkbox or a radio, so the result would differ by widget. A
value that comes back from the browser is also not a protected value: only declaring the field
disabled in the form stops a changed value being accepted, and a read-only input would suggest
otherwise.

**Rejected:** drawing the value as plain text with no input. It would leave the label tied to
nothing, and it would not be what django-crispy-forms documents.

**ADR:** none. It is the documented behaviour of one layout object.

## D4. Prepended and appended text is drawn as markup

**Chosen:** the text a developer passes to `PrependedText`, `AppendedText` and
`PrependedAppendedText` is drawn as given, markup included (FR-007). The documentation warns that
it must not be built from untrusted input (FR-008). Everything that comes from the form or from
submitted data is still escaped (FR-026).

**Rejected:** escaping it. django-crispy-forms documents that the text "can be HTML like", and an
icon in front of an input is the commonest use after a currency sign. Escaping would break that
and every layout written from its documentation. The text is written in Python by the developer,
in the same place they would write an `HTML` layout object, so it is on the trusted side of the
boundary in Article V.

**ADR:** pending, written when the feature converges. It is a standing exception to escaping
that every later template taking developer-supplied text will be measured against, and a reader
would reasonably ask why it exists.

## D5. An inline field gives up its visible label and nothing else

**Chosen:** `InlineField` draws no visible label, keeps the label as the input's accessible name,
offers it as the placeholder when the widget has none, and still draws errors and ties help text
to the input (FR-017 to FR-019). A single checkbox keeps its label beside it (FR-020).

**Rejected:** matching the templates other packs ship, which draw no errors for an inline field.
A person would submit the form and see nothing wrong, and G3 would not hold. django-crispy-forms
does not document that omission as behaviour, so Article XIV does not bind the pack to it.

**Rejected:** using the placeholder as the only name for the input. A placeholder disappears when
the person types and is not a reliable accessible name.

**ADR:** none. It is local to one layout object and follows from G3.

## D6. Attached text is tied to the input for assistive technology

**Chosen:** the prepended or appended text is announced with the field (FR-004). A currency sign
or a unit changes what the value means, so someone who cannot see it needs to hear it.

**Rejected:** leaving it as decoration. Other packs do, and a screen reader then reads an amount
field with no currency.

**ADR:** none. It is local to these three layout objects.

## D7. A layout object on a field it does not suit still draws the field

**Chosen:** prepended text on a checkbox, inline radios on a field with no choices, and similar
mismatches draw a usable field and never drop it (FR-025). What the decoration looks like in
those cases is deliberately not promised.

**Rejected:** raising an error. django-crispy-forms does not, and a layout that works with another
pack would fail here for a reason the developer cannot see in the documentation.

**Rejected:** specifying the result for each mismatch. There are many, none is a case anyone asks
for, and each would become a test that only records a choice.

**ADR:** none. It is local to this feature.

## D8. `input_size` is accepted and means nothing yet

**Chosen:** `PrependedAppendedText` and `FieldWithButtons` accept `input_size`, as their
signatures in django-crispy-forms require, and this feature gives it no effect (FR-027).

**Rejected:** mapping it to a daisyUI size here. The argument holds another pack's class name, and
size chosen from Python is #11's subject. Whether attached text and buttons follow a field's size
is already raised in #15.

**ADR:** none. It defers to #11.

## D9. How a multi-widget field draws without a layout object is not this feature's

**Chosen:** this feature adds the per-part attributes of `MultiWidgetField` and requires each part
to be drawn as the pack's input for its kind (FR-021, FR-022). Drawing a multi-widget field in a
plain form is assumed to belong to #5 and #6, which cover the widgets Django ships.

#21 settled both this and `MultiField`, the Bootstrap 3 container django-crispy-forms still
ships: a multi-widget field is drawn part by part under #5 and #6, and `MultiField` is drawn by #7.

On main, earlier features do not class or name the parts of a multi-widget field, so this
feature does, for every multi-widget field, with or without the layout object (D16).
`MultiWidgetField` draws through the ordinary field template, so the two cannot be separated.

**ADR:** none. It is a boundary between features.

## D10. One demo page for each kind of decoration

**Chosen:** six demo pages, one per user story, each showing its layout objects valid and with an
error (FR-030). The roadmap asks for a demo page for each, and a page per kind keeps each story's
page in the story that builds it.

**Rejected:** one page for all nine. It would be owned by no story and be finished only when the
last one is.

**ADR:** none. It concerns the demo project only.

## D11. No sketch before the build

**Chosen:** the feature is built without a prototype stage. Every decoration is drawn from stock
daisyUI markup, the README says stock markup wins over custom styling, and the only new pages are
demo pages that nobody outside the project sees.

**ADR:** none. It is about how this one feature is delivered.

## D12. A layout object decorates a field through options on the tag that draws it

**Chosen:** each of the six templates django-crispy-forms asks for is two lines: it calls
`daisyui_field` with an option naming the decoration, then includes the one frame. `FieldInput`
and the frame's body draw the decoration (plan, *One frame, told how the field is decorated*).

**Rejected:** a frame per layout object. Six copies of the label, required marker, help text and
error handling would drift, and ADR 0006 exists to prevent that.

**Rejected:** template inheritance with a block for the input. A value set by a tag inside a
block is gone when the block ends, so a child template could not say how the input is drawn.

**ADR:** pending, written when the feature converges.

## D13. Attached text is daisyUI's label inside an input, and the wrapper is a label element

**Chosen:** the wrapper carries the component class, the width and the error modifier, and the
input inside is drawn bare. The wrapper is a `<label>`, so the text is part of the input's name
(research R2).

**Rejected:** `aria-describedby` with an id per text, and `join` with a separate element.
Reasons in research R2.

**ADR:** pending, with D12.

## D14. Buttons joined to a field are left as they were drawn

**Chosen:** the pack puts `join` on the group and `join-item` on the input. The buttons are the
string django-crispy-forms already drew (research R3). daisyUI squares a button's joined corners
from the container alone.

**Rejected:** drawing each button again from a copy with `join-item`. A second render evaluates
already-rendered text as a template.

**ADR:** none. It is local to one layout object, and the reason is in research R3.

## D15. The frame takes `wrapper_class` from the context

**Chosen:** the tag reads `wrapper_class` and the frame writes it as a class on its outer
element (research R5). FR-024 requires it and django-crispy-forms offers no other route.

**Rejected:** honouring it only for `PrependedText`, `AppendedText` and `PrependedAppendedText`,
the three that always supply it. The other five that document it would ignore it without a word.

**ADR:** pending. It amends ADR 0006.

## D16. The parts of a multi-widget field are classed and named on a copy

**Chosen:** a deep copy of the widget, each part given its component class after its own
classes and an `aria-label` when it has none: `Date` and `Time` for a split date and time, the
field's label otherwise (research R6).

**Rejected:** passing one class to `as_widget`. It replaces every part's own class, which is
exactly what `MultiWidgetField` exists to set.

**ADR:** pending. It extends ADR 0012.

## D17. One standalone page for all six kinds

**Chosen:** six shell pages, as D10 has it, and one standalone page that draws the forms of all
six on daisyUI's CDN install alone, which is what SC-005 is checked against. FS-005 did the same
for its four.

**ADR:** none. It concerns the demo project only.

## D18. Dispatch

One implementer per story, six in sequence in the feature worktree, because every story edits
the same shared files (plan, *Story order*).

**ADR:** none. It is about how this one feature is delivered.

## D19. The crispy filter does not draw a layout, so the spec's edge case was wrong

The specification's last edge case said the crispy tag and the crispy filter draw these layout
objects the same way. They cannot. `{{ form|crispy }}` in django-crispy-forms 2.7 renders the
form's fields one by one and never reads the helper's layout
(`crispy_forms/templatetags/crispy_forms_filters.py:48-61`), so no layout object of any kind is
drawn through it. The design review found this before any code was written (DR-001).

**Chosen:** the edge case in `spec.md` is reworded to say what happens, with a dated note, and
the test that would have compared the two is dropped from T001. No requirement or acceptance
scenario changes. All gates on this feature are open, so the amendment is recorded here and
reported with the pull request.

**ADR:** none. It corrects one sentence of this specification.

## D20. What the design review changed

One reviewer read the plan against the specification, for security and for structure. Verdict:
approve. Applied:

- DR-001, medium: D19.
- DR-002, low: the inline arrangement is asserted by the widget template that drew it and by
  nothing else.
- DR-003, low: each of `inline`, `join`, `disabled` and `unlabelled` arrives in the task that
  gives it behaviour.
- DR-004, low: attached text and `join-item` never apply to a group, so a date drawn as three
  selects is drawn undecorated.
- DR-005, low: `uneditable-input` joins `UPSTREAM_ONLY_CLASSES` and an input drops that one name
  only. Running an input's classes through the whole set would drop a developer's own `active`
  or `error` from every input.
- DR-006, low: `UneditableField` writing `disabled` amends ADR 0013 and a sentence in the README.

**ADR:** none. It is a record of this feature's review.
