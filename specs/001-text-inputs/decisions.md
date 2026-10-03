# Decisions: text inputs drawn as daisyUI

Decisions taken while specifying this feature. The maintainer handed the specification over on 2026-10-03, so each reading below was settled from the repository's documents and the sibling feature requests without a question being put to him. Each one is open to veto on the pull request.

## Agreed statement

A host project that selects the pack gets every text-like field of a plain Django form drawn as a daisyUI input or textarea with no layout: text, email, URL, number, password, date, time and date-time inputs, and textareas. Each field is drawn with its label, a required marker, its help text and its errors, and these are tied to the input so assistive technology announces them. Form-wide errors and the form element are drawn too, through every way django-crispy-forms offers to draw a form. Every class in the output is one daisyUI's full CDN build defines, the templates are plain Django templates, and nothing depends on django-mvp. The feature adds one demo page and the README's installation, quickstart and first public-surface entry. Other widgets, layout objects, formsets and styling choices stay with their own feature requests.

## D1. The pack is selected by the name `daisyui`

**Ambiguous:** no document names the pack, and the name is public interface under Article XI from the first release.

**Chosen:** `daisyui`.

**Why defensible:** crispy packs are named after the CSS framework they emit (`bootstrap5`, `tailwind`, `bulma`), and the README describes the package as a daisyUI template pack. A name tied to the package (`mvp_forms`) would suggest the pack needs django-mvp, which G6 rules out. A versioned name (`daisyui5`) would force a rename at each daisyUI major, while roadmap item R9 plans for one pack tested across the daisyUI versions it supports. The cost is that crispy-daisyui uses the same name, so a project cannot have both installed. That pack is the one this package replaces, so a project has no reason to install both.

**ADR:** to be written with the build, as `docs/adr/NNNN-template-pack-name.md`. The branch carries only the specification until then.

## D2. Form-wide errors and the form element belong to this feature

**Ambiguous:** roadmap item R1 lists form-wide errors, and neither #5 nor #6 names them. Nothing says who draws the form element for the crispy tag.

**Chosen:** this feature draws both, along with the helper settings that govern the form element, the CSRF token, labels, errors, and the label and field classes.

**Why defensible:** #6 says it reuses "the label, help text and error handling" this feature introduces, so error handling as a whole starts here. Buttons and layouts are #7's, but a form with no layout still needs its element and token when drawn through the tag, and R1 names both the filter and the tag.

**ADR:** none. It is a boundary between two feature requests, and nothing later inherits it as a rule.

## D3. The pack never changes an input's type

**Ambiguous:** the request says "date and time", and Django draws those fields as plain text inputs by default.

**Chosen:** the pack draws the widget it is handed with the input type that widget declares. A developer who wants the browser's picker sets the type on the widget.

**Why defensible:** the input type decides the format the browser submits, and the field's parsing has to match it. Changing it in a template would break forms with their own input formats, and it would be per-form behaviour that G1 says the pack must not need. "Matching crispy-forms' documented behaviour wins over inventing a new one."

**ADR:** to be written with the build. It is a standing limit on what any template in the pack may do to a widget, and a later contributor will ask why date fields are not pickers.

## D4. Only classes found in daisyUI's CDN build

**Ambiguous:** Article XIV allows "daisyUI's component classes and Tailwind utilities as documented", and the request asks for a form that works on a page loading only daisyUI's CDN build.

**Chosen:** the stricter reading, as the maintainer ruled when the repository was set up. Every class the pack emits is one that build defines.

**Why defensible:** it is the only reading under which the request's last sentence is true. The gap in the article's wording is filed as #16.

**ADR:** to be written with the build, unless #16 amends Article XIV first, in which case the rule lives in the constitution and needs no record.

## D5. One field frame, shared by every later feature

**Ambiguous:** the request calls this feature "the base every other part of the pack draws through" without saying what is shared.

**Chosen:** the frame around a field (label, required marker, help text, errors and their links) is specified once here, and a field whose widget belongs to a later feature is already drawn inside it.

**Why defensible:** #6 depends on #5 for exactly this. Drawing uncovered widgets in the frame also means a form never loses a field while the pack is incomplete.

**ADR:** none. It follows directly from the dependency the feature requests already state.

## D6. Left out, and where each went

- Disabled and read-only drawing: #6 names it. This feature keeps the attributes Django emits.
- A field split across several inputs (split date and time): #8 lists the multi-widget field.
- Helper settings that place help text or errors inline: they choose an appearance, so the pack places each one way.
- Horizontal forms: not covered by any request. Filed as #14.
- Replacing a single template as a stable interface: roadmap item R6.

**ADR:** none. These are scope lines, each recorded in the specification.

## D7. A standalone demo page beside the shell page

**Ambiguous:** the demo project runs on django-mvp's shell and its packaged stylesheet, which says nothing about whether the pack works from the CDN build.

**Chosen:** the demo offers the same form on a second page that takes its styling from daisyUI's CDN build alone.

**Why defensible:** it is the only place a reviewer can see the "no build step" claim with their own eyes. The claim itself is checked by comparing emitted classes with the build, not by looking.

**ADR:** none. It concerns the demo project only.

## D8. No sketch before the build

**Chosen:** the feature is built without a prototype round.

**Why defensible:** the project's rule is that stock daisyUI markup wins over custom styling, so the look of each input is daisyUI's to decide. The demo page is a list of fields in their states and needs no design.

**ADR:** none.
