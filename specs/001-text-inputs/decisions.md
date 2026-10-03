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

**Superseded by D9**, the maintainer's ruling for the build.

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

## D9. Class policy, as ruled for the build

**Ruled by the maintainer, 2026-10-03, and it replaces the reading in D4:** every input, button
and component is built from daisyUI component classes and modifiers. A plain Tailwind layout
utility is allowed only where daisyUI has no component for the job, such as laying columns side
by side. daisyUI's documented CDN install loads Tailwind's browser build beside the stylesheet,
so no build step is needed either way. The package ships no stylesheet and defines no class.

**In this feature:** no Tailwind utility is needed. The field frame is daisyUI's `fieldset`, and
a test compares every class the pack emits with the class names in daisyUI's CDN stylesheet.

## D10. The pack draws inputs with its own tag, not django-crispy-forms' `crispy_field`

**Decision:** `{% daisyui_input field %}`, backed by the class `FieldInput`, passes the pack's
class to `BoundField.as_widget` for one render.

**Why:** `crispy_field` appends the widget's class name in lower case (`textinput`), which no
daisyUI build defines, and it writes into `widget.attrs`, so the change outlives the render.

**Revisit if:** django-crispy-forms offers a way to add a class without either effect.

## D11. The ids around a field are Django's own

**Decision:** help text carries the id `<auto_id>_helptext`, and one element carrying
`<auto_id>_error` holds every error message. The pack invents no id for these.

**Why:** Django 5.2, 6.0 and 6.1 all put `aria-describedby` on the input naming exactly those two
ids. Per-message ids, as crispy-tailwind writes, would leave the input describing itself by an
element that is not on the page.

**Revisit if:** a supported Django version changes the ids it names.

## D12. Where the pack corrects what Django puts on the input

**Decision:** three cases, and no others. With errors turned off by the helper, the description
names the help text only, or is removed. With the browser's required attribute turned off on the
form, the input carries `aria-required`. With labels turned off, the input carries `aria-label`.
A developer's own `aria-describedby` or `aria-label` on the widget is never replaced.

**Why:** in each case Django's attributes and what the pack draws would otherwise disagree.
Removing a description is the one thing `as_widget` cannot be asked to do, so that case builds
the attributes and renders the widget directly.

**Revisit if:** Django lets a caller suppress the description it adds.

## D13. The pack adds no text of its own

**Decision:** the required marker is an asterisk hidden from assistive technology. The
requirement is carried by `required` or `aria-required`.

**Why:** with no string of its own the pack needs no translation catalogue, and Article VIII says
not to ship an empty one.

**Revisit if:** a later feature has to add wording, at which point the package gains a catalogue.

## D14. Search, telephone and colour inputs are left to the fallback

**Decision:** the covered widgets are the ones the specification lists. Django's `SearchInput`,
`TelInput` and `ColorInput` are drawn inside the frame with no daisyUI class.

**Why:** the specification names nine kinds. Whether to add these is an open question on the
tracker.

## D15. Design review, 2026-10-03

One reviewer, three lenses, on the plan at `375882c`. Verdict: changes requested, one high
finding. Each was applied to the plan and tasks before any code.

- **DR-001 (high).** The frame took its element name from a context variable named `tag`, and
  through the crispy tag the whole page context reaches the field template. The frame's element
  is now a fixed `div` and reads neither `tag` nor `wrapper_class`.
- **DR-002.** The pack adds no ARIA attribute to a widget drawn as a group, and adds
  `aria-required` only when the form turns the browser's required attribute off.
- **DR-003.** The test that draws a form without django-mvp clears django-crispy-forms' cached
  templates going in and coming out, or it would pass on a template compiled by the full engine.
- **DR-004.** The README does not list the pack's own tag or its template paths. A documented
  template interface is roadmap item R6.
- **DR-005.** Help text and errors are written inside the frame, not in templates of their own.
- **DR-006.** A label copied into `aria-label` has its tags stripped.
- **DR-007.** The label's `for` is written only when there is an id to point at.
- **DR-008.** No wrapper class around BeautifulSoup in the tests.

## D16. Help text and errors are in the frame from US1

**Decision:** `daisyui/field.html` writes the help text and error elements, with the ids of D11,
in the story that introduces the frame, not in US2.

**Why:** US1's acceptance for a field whose widget the pack does not cover is that it keeps its
label, help text and errors (FR-009), and a test can only show that if the frame draws them. US2
still owns the label's marker, the description and invalid attributes tied to the input, the error
modifier, escaping and prefixes, and tests them.

**Revisit if:** US2 splits the frame into smaller templates.
