# Decisions: tabs, accordion, modal and alert in a layout

Decisions taken while specifying this feature. The maintainer handed the specification over on 2026-10-03, so each reading below was settled from the repository's documents, django-crispy-forms' own code and the sibling feature requests, without a question being put to him. Each one is open to veto on the pull request.

## Agreed statement

A developer who writes a `Layout` can group parts of a form behind tabs or an accordion, hold part of it in a modal, and place a notice among the fields, using the six layout objects django-crispy-forms ships for this: `TabHolder`, `Tab`, `Accordion`, `AccordionGroup`, `Modal` and `Alert`. The pack draws each with daisyUI's own tabs, collapse, modal and alert. When a submitted form comes back with a field error, the tab, accordion group or modal holding that field is already open. An alert can be dismissed unless the developer says otherwise. All of it works on a page that loads daisyUI's CDN build and nothing else, and none of it changes what the form submits. The feature adds a demo page for each of the four and their README entries. How fields, rows, fieldsets and buttons are drawn stays with #5 and #7. Colour, size and variant chosen from Python stay with #11.

## D1. Layouts use django-crispy-forms' own six classes

**Ambiguous:** django-crispy-forms keeps these classes in a module named after Bootstrap, and some of their defaults are Bootstrap class names. The request does not say whether a developer imports them from there or from this package.

**Chosen:** from django-crispy-forms, with the arguments it documents. The pack supplies templates and adds no layout object names in this feature.

**Why defensible:** G2 is that every layout object django-crispy-forms ships can be used. Article XIV says the pack matches documented behaviour, and the specification for #7 takes the same line for the structural objects. A second set of classes would be a wrapper with no second use (Article III).

**ADR:** none from this feature. The rule is the same one #7's specification records for all layout objects, and it should graduate once, from there.

## D2. The first tab or group holding an error opens, and only that one

**Ambiguous:** the request says the tab or group holding a field with an error "should be the one that opens". It does not say what happens when several do.

**Chosen:** the first in layout order, which is what django-crispy-forms' holder classes already compute. With no errors, the open one is whichever those classes pick, including the developer's own choice where the class lets them make one. Errors that belong to the form and to no field do not move anything.

**Why defensible:** the rule already exists in the Python the developer is using, and the pack draws the state it is handed. Writing a second rule in templates would make the pack disagree with the library it plugs into. Marking every tab or group with an error would be new behaviour, so it is put as a question in #46 and kept out of this feature.

**ADR:** none. The behaviour is django-crispy-forms' own and the pack inherits it.

## D3. A modal holding a field with an error is drawn open

**Ambiguous:** the request names tabs and accordion groups for the error handling and says nothing of the modal. django-crispy-forms has no rule for it.

**Chosen:** a modal holding a field with an error is drawn already open, and can still be closed.

**Why defensible:** the request gives its reason, "so nobody submits a form and sees nothing wrong". A modal is closed when a page arrives, so a field error inside one is the clearest case of that failure. This is the one place the feature adds behaviour django-crispy-forms does not have, and the README's tie-break (match documented behaviour) is not in play because there is no documented behaviour to match.

**ADR:** to be written with the build. It is the pack's own rule, a later contributor will ask why the modal template inspects errors, and any future layout object that hides fields inherits it.

## D4. The pack draws no control that opens a modal

**Ambiguous:** the request says "a form shown in a modal" and does not say what opens it.

**Chosen:** the pack draws the modal with the developer's id. The host project opens it in any way daisyUI documents. The demo page and the README show one.

**Why defensible:** this is what django-crispy-forms' `Modal` does, and the control that opens a modal usually sits somewhere the layout does not reach, such as a toolbar or a table row. The modal stays inside the form it was laid out in, so its fields submit with the rest. A modal that wraps a whole form, with the form fetched and submitted in place, is a form view and page template concern and belongs to django-mvp (Article XII).

**ADR:** none. It follows the library and is local to one layout object.

## D5. daisyUI alone is enough, and the containers never touch submitted data

**Ambiguous:** the maintainer's ruling is that the pack keeps to daisyUI's standard classes so a page loading the CDN build needs no build step. It does not mention scripts. daisyUI's tabs and collapse are usually built on radio inputs, which would be submitted with the form.

**Chosen:** two requirements. The host project loads daisyUI and nothing else: no script file, no stylesheet, no build step (FR-018). The controls these layout objects draw add nothing to what the form submits and never submit it (FR-019).

**Why defensible:** a script file the host project must load would break the "daisyUI alone" promise as surely as a stylesheet would. An extra key in the submitted data is harmless to Django on a POST but pollutes the query string of a search or filter form, and can collide with a field name. Both are behaviours a developer would report as defects.

**ADR:** to be written with the build, as one record: the pack's interactive layout objects need nothing from the host project beyond daisyUI, and how that is achieved. It depends on the answer to #47.

## D6. A dismissed alert is not remembered, and alert content is trusted

**Ambiguous:** the roadmap says "dismissible or not". Nothing says whether dismissal lasts, or how content is treated.

**Chosen:** dismissing hides the alert on the page in front of the person and nothing more. Content is drawn as the developer wrote it, markup included. The README says it is trusted and must not carry unescaped input from a person.

**Why defensible:** remembering a dismissal needs storage, which means a view, a session or a script, none of which this package has. Drawing content as markup is django-crispy-forms' documented behaviour and matches its `HTML` layout object. Article V is met because the content is written by the developer in Python, and the documentation says where the line is.

**ADR:** none. Both are local to the alert.

## D7. Arguments with no daisyUI counterpart are accepted

**Ambiguous:** `Alert` takes `block`, and several of these classes carry Bootstrap class names as defaults. daisyUI has no equivalent.

**Chosen:** such arguments are accepted and do not raise. What, if anything, they change in the markup is left to planning.

**Why defensible:** a layout copied from django-crispy-forms' documentation should draw. Raising on a documented argument would break that for no gain. Class names inside the markup are outside the public surface (Article XI), so planning is free to drop the Bootstrap defaults.

**ADR:** none. Local detail.

## D8. Four demo pages, and no prototype before the build

**Ambiguous:** the roadmap says "a demo page for each".

**Chosen:** one page each for tabs, accordion, modal and alert. Three of them can be submitted with invalid data to show the error case. No prototype stage: the markup is stock daisyUI and its structure is the documented one, so there is no new design to judge by eye.

**ADR:** none.

## Notes for planning

These are observations, not requirements. They are here so the build does not rediscover them.

- django-crispy-forms decides which tab or group is active in Python and hands the template an `active` flag. `TabHolder` resets every tab before picking one, so a developer's `active` on a later `Tab` has no effect there. (Corrected at the design review: `active=` on the first `Tab` leaves no tab active. See D14.) `Accordion` does not reset, so it does.
- The modal sits inside the form. daisyUI's usual close button is a form of its own with the dialog method, and a form nested in a form is not valid HTML. The close control needs another route.
- A modal drawn open for an error must still close. daisyUI's class that forces a modal open keeps it open until the class is removed.
- Radio inputs that drive tabs or a collapse are submitted unless they are detached from the form, and their group name has to be unique per holder for FR-020.
- daisyUI has nothing for dismissing an alert.
- #16 asks which Tailwind utilities the CDN build really includes. Its answer bounds what these templates may use.
- "Container layout object" is the roadmap's term for these six. It is not in `CONTEXT.md` yet. If the build needs the term in code or documentation, add it to the glossary in the same pull request.

## D9. A tab's radio is drawn with its pane, and the holder names the group

**Ambiguous:** daisyUI's script-free tabs need each radio directly before its content, and radios
form a group by a shared name. django-crispy-forms draws all panes, then all links, and hands a
pane's template nothing but its own `Tab`.

**Chosen:** the pane template draws the radio and then the content, with a fixed placeholder for
the group name. The holder's template passes the drawn panes through `daisyui_tab_group`, which
swaps the placeholder for a random name made for that drawing. The link template is empty.

**Why defensible:** the alternatives were tabs switched by an inline script, which the planning
notes rule out where a script-free mechanism exists; drawing each pane twice, which
django-crispy-forms reports as an error; and keeping each drawn pane on its `Tab`, which would let
one request read another's fields from a shared layout. A random name keeps two forms drawn from
one class apart without asking anything of the developer (research R3, R4).

## D10. An accordion group is a `details` element with no group name

**Ambiguous:** daisyUI's accordion examples give the groups a shared name so only one is open at
a time. django-crispy-forms can mark more than one group active.

**Chosen:** each group is a `details` element drawn open when django-crispy-forms marks it
active, with no shared name. Groups open and close on their own.

**Why defensible:** with a shared name the browser keeps only the first open group. When a
developer's own open group comes before the group holding an error, the browser would close the
one with the error, which is the failure this feature exists to prevent (research R6). FR-007
asks that the groups django-crispy-forms picks are the ones open.

## D11. The modal is a `dialog`, found open by Django's own mark on an invalid input

**Ambiguous:** FR-012 needs the modal drawn open when it holds a field with an error.
django-crispy-forms hands the modal's template the drawn fields and no form.

**Chosen:** the template looks in the drawn fields for
`aria-invalid="true"`, the attribute Django writes on every visible input of a field with errors.
The modal is a `dialog` element drawn with the `open` attribute, and its close control is a
button with a one-line inline handler.

**Why defensible:** the specification rules out a `Modal` class of the pack's own, so the drawn
fields are the only evidence the template has. A person's input cannot forge the attribute
because Django escapes it. daisyUI's checkbox modal needs no script, but its close control is a
label the keyboard cannot reach, which fails FR-010. A hidden field's error does not open the
modal; nothing draws that error yet, and FS-002's FR-013 owns it (research R7, R8).

## D12. Dismissing an alert removes it, by an inline handler

**Ambiguous:** daisyUI has nothing for dismissing an alert.

**Chosen:** the dismiss control is a `type="button"` button whose inline handler removes the
alert from the page.

**Why defensible:** there is no script-free mechanism to use, and the planning notes allow an
inline handler in exactly that case. Removing the element needs no class to win against the
alert's own display rule. Issue #47 stays open on whether a strict Content Security Policy must
be supported (research R9).

## D13. One standalone demo page for all four

**Ambiguous:** FR-024 asks for one demo page for each of the four. The earlier features also gave
each page a twin outside the shell.

**Chosen:** four pages on the shell and one standalone page that draws all four forms.

**Why defensible:** the standalone page exists to show the four working on daisyUI's CDN install
alone (SC-003). One page shows that as well as four would, and the shell pages are the ones
FR-024 counts.

## D14. When django-crispy-forms marks no tab active, the first is open

**Ambiguous:** FR-002 says exactly one tab is marked open. The specification also assumes the
pack adds no rule of its own for tabs. django-crispy-forms marks no tab active when the first
`Tab` was given `active=` and no tab holds an error, which the design review found by running it.

**Chosen:** the holder's filter checks the first radio when none of that holder's radios is
checked.

**Why defensible:** with no radio checked every pane is hidden until a person picks a tab, which
FR-002 exists to prevent. The fallback only acts where django-crispy-forms picked nothing, so it
never disagrees with a choice the library made, and it is the same tab the library opens by
default.

## D15. Design review, 2026-10-03: approve, findings applied

One reviewer, three lenses, on the plan before any code. No critical or high finding.

- DR-001 (medium): no tab open when the first `Tab` is given `active=`. Applied: D14.
- DR-002 (medium): the first translatable strings need the base English catalogue Article VIII
  asks for. Applied: `mvp_forms/locale/en/LC_MESSAGES/django.po` is in T005 and T007. (The
  catalogue itself arrived on main with FS-002 before the build began, so the two tasks add to it.)
- DR-003 (low): `daisyui_invalid` had one caller. Applied: the modal template tests with `in`
  and the filter is dropped.
- DR-004 (low): `daisyui_tab_group` must not mark its input safe. Applied: `is_safe=True`.
- DR-005 (low): no test for a hidden field's error opening a tab or group. Applied: T001, T003.
- DR-006 (low): SC-005 traced nowhere. Applied: one sentence in the plan.
- DR-007 (low): the demo's posting forms need `novalidate` for the error case to be produced by
  hand. Applied: the plan and T002.
- DR-008 (low): invoker commands not weighed for closing a modal. Applied: research R8.

Watch items for the build: `Tab.render` strips the substring `active` from an inactive tab's
classes, so a test must not use a developer class containing it; a developer's own `active`
class is dropped from buttons and a `MultiField` as well, and the README says so.

## D16. Which form a standalone post belongs to (US2)

**Decision**: `ContainersStandaloneView.post` binds the accordion form when the post names the
accordion's submit button (`<prefix>-submit`) and otherwise binds the tabs form, as before. Each
shell page binds its own form on any post.

**Why**: the standalone page now holds two forms to post, and a browser sends the name of the
submit button that was pressed, so that name says which form was posted. The tests US1 wrote post
an empty body to the standalone page and expect the tabs form bound, so a body that names no
button keeps binding the tabs form rather than binding nothing. No registry or dispatcher: one
`if` for two forms.

**Revisit if**: US3 and US4 each add a posting form to the page, which makes three `if`s and is
the point to look again.
