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

Whether #7 covers `StrictButton` is not stated anywhere. That is raised in #21.

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

**ADR:** pending, to be written when the feature is built. It is a standing exception to escaping
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

Neither of those issues names multi-widget fields, and `MultiField`, a Bootstrap 3 container
django-crispy-forms still ships, is named by no issue at all. Both are raised in #21.

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
