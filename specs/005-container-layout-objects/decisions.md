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

- django-crispy-forms decides which tab or group is active in Python and hands the template an `active` flag. `TabHolder` resets every tab before picking one, so a developer's `active` on a `Tab` has no effect there. `Accordion` does not reset, so it does.
- The modal sits inside the form. daisyUI's usual close button is a form of its own with the dialog method, and a form nested in a form is not valid HTML. The close control needs another route.
- A modal drawn open for an error must still close. daisyUI's class that forces a modal open keeps it open until the class is removed.
- Radio inputs that drive tabs or a collapse are submitted unless they are detached from the form, and their group name has to be unique per holder for FR-020.
- daisyUI has nothing for dismissing an alert.
- #16 asks which Tailwind utilities the CDN build really includes. Its answer bounds what these templates may use.
- "Container layout object" is the roadmap's term for these six. It is not in `CONTEXT.md` yet. If the build needs the term in code or documentation, add it to the glossary in the same pull request.
