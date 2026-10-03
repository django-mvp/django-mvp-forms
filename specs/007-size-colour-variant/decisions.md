# Decisions: size, colour and variant chosen from Python

Decisions taken while the specification was written, with the reasoning that is too long to
carry in `spec.md`. Each was settled without a question to the maintainer and is open to veto on
the specification's pull request.

Decisions marked *record candidate* meet the bar in `docs/adr/README.md` (durable, architectural,
non-obvious). They are written up under `docs/adr/` when the feature is built, so the record lands
with the code it explains.

## D1. Size is stated once for the form. Colour and variant are stated for inputs and for buttons separately

**What was ambiguous.** The request says a form's "inputs and buttons are small, or ghost, or a
given colour". Read literally, one statement of colour or variant would reach both.

**Chosen.** One size covers inputs and buttons. Colour and variant are held twice: once for the
form's inputs, once for its buttons.

**Why.** Size is the one choice that always wants to match across a form. Colour and variant do
not: a form with ghost inputs rarely wants ghost buttons, and a submit and a reset button drawn in
the same colour as every input says nothing about which is which. The variants also differ.
daisyUI gives inputs one (ghost) and buttons several, so a single statement could only ever name
the ones they share. The roadmap's wording for R5, "the same choices for buttons", reads as the
same three kinds of choice, which this keeps.

**Revisit if.** Real forms turn out to state the same colour and variant for both nearly every
time.

*Record candidate.*

## D2. The names are daisyUI's own, and the set is closed

**What was ambiguous.** Whether the developer writes the pack's own words (`small`, `large`) or
daisyUI's (`sm`, `lg`), and whether a name the pack does not know is passed through as a class.

**Chosen.** daisyUI's names, unchanged. A name outside daisyUI's set is refused with an error that
lists the allowed ones (FR-005, FR-020).

**Why.** The pack is limited to daisyUI's standard classes and modifiers so that a host page
loading the full CDN build needs no build step. Passing an unknown name through would emit a class
the build does not define, and the form would look unchanged with no error anywhere. A closed set
also means every class the pack can emit is known ahead of time, which is what a host project with
its own stylesheet build needs in order to include them. Using daisyUI's names means the
developer learns nothing new and the documentation they already read applies.

**Revisit if.** Host projects with custom daisyUI colours need to name them from Python.

*Record candidate.*

## D3. A form-wide choice that does not apply to a kind of input is passed over. The same choice on one field is an error

**What was ambiguous.** What to do with, say, a ghost variant on a form that includes a checkbox,
which has no ghost variant.

**Chosen.** Stated for the form: inputs of that kind are drawn without it and nothing is reported
(FR-021). Stated on that one field: an error (FR-022).

**Why.** A form-wide choice has to work on a form with mixed kinds of input, or it is useless on
most real forms. A choice made for one named field that can never apply is a mistake by the
developer, and the same reasoning as D2 says it should be loud.

## D4. An invalid field stays marked as in error whatever colour is chosen

**What was ambiguous.** daisyUI marks an invalid input with its error colour. A colour chosen for
the form or the field competes with that.

**Chosen.** The error marking stays (FR-018). How the two are combined in the markup is for
planning.

**Why.** G3 is Essential and is about a person being able to tell which field is wrong. A
decorative colour must never remove that.

## D5. The choice works under the crispy filter as well as the crispy tag, and with or without a layout

**What was ambiguous.** The request does not say where the choice is written. The obvious home for
a per-form statement in django-crispy-forms is the form's helper, which the crispy filter does not
use the way the tag does. The obvious home for a per-field statement is the field's entry in a
layout, which a form without a layout does not have.

**Chosen.** The specification fixes the outcome and leaves the mechanism to planning: a form-wide
choice takes effect under both the filter and the tag (FR-007), and one field can be singled out
without listing the others (FR-012).

**Why.** R1 promises both ways of drawing a form. A statement that silently did nothing under one
of them would be a trap. A layout that exists only to single out one field would have to name
every other field too, which is the repetition this feature is meant to remove.

**Left to planning.** Where each statement is written and what it is called. It has to be
reachable by the pack's plain Django templates and must not need django-mvp.

## D6. A field can undo the form's choice

**What was ambiguous.** "Override" could mean only "pick a different value".

**Chosen.** A field can also ask for the pack's ordinary drawing for one of the three choices
(FR-011).

**Why.** Colour and variant have no value that means "none" in daisyUI's names, so without this a
form-wide colour could never be switched off for one field.

## D7. Labels, help text and error text are untouched

**Chosen.** The choices change the input and the button only (FR-019).

**Why.** daisyUI defines size, colour and variant modifiers for inputs and buttons, not for the
text around them. Anything more would mean classes of the pack's own, which the constitution's
Article XIV rules out.

## D8. No project-wide default

**Chosen.** Out of scope. A choice is per form and per field, as G4 says.

**Why.** Nothing in the request or the roadmap asks for it, and a host project can already share
one statement across its forms in ordinary Python. It can be added later without changing anything
specified here.

## D9. Attached text and attached buttons are not decided here

**Chosen.** Whether text prepended or appended to an input, and buttons attached to a field,
follow the field's size is left open and tracked in
[#15](https://github.com/django-mvp/django-mvp-forms/issues/15).

**Why.** Those layout objects belong to "Layout objects that decorate a field" (#8). Neither
feature depends on the other, so whichever is built second has to settle it, and specifying it
here would be specifying a sibling's behaviour.

## D10. No sketch before the build

**Chosen.** The feature goes straight to planning with no prototype stage.

**Why.** It adds no page design of its own. The inputs and buttons are stock daisyUI, and the demo
page is a catalogue of them inside the demo project's existing page frame.

## D11. The form's choices are one attribute on its helper, `helper.daisyui`

**What was open.** D5 left where the form-wide statement is written to planning.

**Chosen.** `helper.daisyui = FormChoices(...)`. Under the crispy tag the value reaches every
template through the context, because django-crispy-forms passes a helper's own attributes into
it. Under the crispy filter, which never reads a helper, the pack reads `field.form.helper`. The
statement is set on the helper instance, because django-crispy-forms passes instance attributes
into the context and not class attributes.

**Why.** A button in a layout is drawn before the form is in the context, so an attribute on the
form cannot reach it. The helper's attributes can. One constructor refuses a keyword it does not
know, where a plain attribute per choice (`helper.size`) would let a misspelt name do nothing.
Research R2 has the options weighed.

**Revisit if.** django-crispy-forms stops passing a helper's own attributes into the context.

## D12. One layout object, `Choice`, states a choice for what it holds

**What was open.** How one field or one button states its own choice. ADR 0008 says the package
defines no layout classes and names this feature as the reason to look again.

**Chosen.** `Choice("search", size="lg")` and `Choice(Submit("save", "Save"), color="accent")`.
It places itself in the context while it renders what it holds. Holding nothing, the same class
is the value in `FormChoices(fields={"search": Choice(size="lg")})`, which is how a form drawn
without a layout singles out one field.

**Why.** `Field` and the button classes turn every keyword argument into an HTML attribute, so
they cannot carry it. Subclassing each would add five names that shadow upstream ones, which is
what ADR 0008 ruled out. One wrapper adds one name and leaves every upstream object as documented.

**Revisit if.** django-crispy-forms gives layout objects a way to carry arguments a template
pack can read.

## D13. `None` on a field means the pack's ordinary drawing

**Chosen.** An argument of `Choice` that is left out inherits. `None` asks for no modifier
(FR-011). The default is a module constant, `INHERIT`, that a developer never has to write.

**Why.** `color=None` reads as "no colour", and Python needs some default that is not `None` to
tell the two apart.

## D14. A field drawn as in error does not get the chosen colour

**Chosen.** The error modifier is written and the colour modifier is not. Size and variant still
apply. With errors off the field takes its colour.

**Why.** Both classes set the same property, and which wins depends on the order of the rules in
daisyUI's stylesheet. FR-018 should not rest on that (research R5).

## D15. A mistake is reported when the form is drawn, as `InvalidChoice`

**Chosen.** Names are checked where they are resolved, which is the one place that knows the
field or the button. The error is `InvalidChoice`, a `ValueError` carrying `kind`, `value`,
`allowed` and `target`. `FieldInput` and `DrawnButton` resolve in `__init__`.

**Why.** A `Choice` in the by-name mapping is built before it knows its field, so a constructor
cannot name it (FR-020). Django's `{% if %}` swallows an exception raised inside `and`, `or` and
`not`, so the check must not wait for a property the frame reads (research R6).

## D16. The keyword is `color`

**Chosen.** `color`, `button_color`. The prose of the documentation says colour.

**Why.** FR-005 has the developer write daisyUI's names, and daisyUI's documentation, like CSS
and the rest of the Python the developer writes, spells it `color`.

## D17. The removal checkbox of a file field takes the size and the colour

**Chosen.** A filter turns the file input's class string into the checkbox's.

**Why.** SC-003 leaves no visible input at the ordinary size, and only the widget's final
attributes reach the pack's widget template (research R7). `file-input-error` is never mapped,
so the checkbox is not marked in error, as today, and a chosen colour of error does not reach it.

## D18. A `Choice` applies to everything inside it, and an inner one wins

**Chosen.** A `Choice` may hold several fields, buttons or containers. A `Choice` inside another
is merged over it, each of the three kinds separately. One `color` on a `Choice` is the input's
colour for a field inside it and the button's for a button inside it.

**Why.** It falls out of placing the choice in the context, and refusing it would take code.

## D19. A button given a colour drops the default `btn-primary`

**Chosen.** When a colour resolves for a `Submit`, the `btn-primary` django-crispy-forms writes by
default is left out. One the developer passed as `css_class` is kept. With no colour resolved
nothing changes.

**Why.** The same reasoning as D14: two colour modifiers on one element leave the result to the
order of daisyUI's rules.

## D20. Design review, 2026-10-03

One reviewer, three lenses: approve, with four medium and three low findings and no high or
critical one. All seven were applied to the plan and tasks before any code was written.

- DR-001 (medium): the removal checkbox would have gained `checkbox-error` on a form that states
  nothing. The filter never maps `file-input-error` (D17).
- DR-002 (medium): comparing an empty statement with none does not prove SC-005. T002 and T004
  now compare every state's markup before and after the task.
- DR-003 (medium): a `Submit` given a colour would carry two colour modifiers (D19).
- DR-004 (medium): a class attribute on a helper subclass reaches inputs and not layout buttons.
  The statement is set on the instance, and the README says so (D11).
- DR-005 (low): a page variable named `daisyui` is treated as absent; only the helper's own
  attribute raises `TypeError`.
- DR-006 (low): the `class` attribute of a `StrictButton` is matched with its leading space.
  Watch item in T004.
- DR-007 (low): the demo's per-size and per-colour forms hold one input and one button.
