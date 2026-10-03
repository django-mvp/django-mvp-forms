# Decisions: Replace one template without forking the pack

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer was not available for questions on this feature, so every reading of the issue below was
made without him and is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. The reading of the issue was confirmed without the maintainer

**Chosen:** the feature is read as follows. A host project replaces any one of the pack's
templates by providing a template at the same path, and every other template stays the pack's. The
README lists every template the pack distributes, with what it draws, what it is handed and where
a replacement is found. From the release that publishes the list, a template's path and the names
it is handed are public API: they change only through a deprecation that lasts one minor version.
The feature serves G8 and sits in R6. It changes nothing any earlier feature draws, and it adds no
new way to choose a template for one form, because django-crispy-forms already has those.

**Why:** the issue is three sentences and the roadmap item is two, and neither conflicts with this
reading. Article XI already names "the template paths a host project can override" as part of the
public API, so the feature is the work of saying which paths those are and keeping the promise.
Each gap the reading fills is its own decision below.

**ADR:** none — the record of how the specification was written, not a constraint on the code.

## D2. Every template the pack distributes is replaceable and listed

**Chosen:** there are no private templates. The frame, the layout object templates, the widget
templates and the small templates the others include are all on the list (FR-001, FR-007).

**Rejected:** listing only the templates a project is likely to want, such as the frame and the
layout objects, and treating the small included ones as internal. A host project can shadow any
path whether or not the pack lists it, because that is how Django finds templates. A template left
off the list would still be replaced by somebody, and would then break without notice, which is
the outcome the issue asks to end. The roadmap item also says "any single template".

**Why defensible:** it is the only rule a host project can apply without reading the source, and
it is the one the roadmap states. Its cost is that the pack can no longer split or merge a
template freely. D5 is how it still can.

**ADR:** docs/adr/0029-every-pack-template-is-public.md

## D3. The promise covers what a template is handed as well as its path

**Chosen:** for each listed template the pack promises the path, what the template is asked to
draw, and the names it is handed. For a value the pack itself supplies, the promise reaches the
parts of it the pack's own template reads (FR-005, FR-009, FR-012).

**Rejected:**

- Promising the path alone. A replacement is a copy of the pack's template with edits. It reads
  what the original read. Django draws an unknown name as nothing and raises no error, so a
  renamed name breaks the replacement without anybody being told. A stable path with an unstable
  inside would meet the letter of the issue and miss its point.
- Promising the whole of every object a template can reach. That would freeze far more of the
  pack's Python than any template uses.

**Why defensible:** "whatever the pack's own template reads, a replacement may read" is a rule
with a clear edge. It can be checked by comparing the pack's templates with the list (FR-011), and
it freezes only what is already in use.

**What it costs:** the parts of the pack's Python that its templates read become public in the
same sense as the paths. A later feature that changes one goes through the deprecation in D5. The
maintainer may prefer a narrower promise. If so, FR-005, FR-009, FR-011, FR-012 and FR-014 narrow
with it and the first story is unaffected.

**ADR:** docs/adr/0029-every-pack-template-is-public.md

## D4. A replacement is found by Django's own template loading

**Chosen:** the pack adds no setting, no registry and no Python hook for replacing a template. A
host project puts a file at the listed path somewhere Django finds it before the pack's (FR-002).
The templates that draw a widget are loaded by the form renderer, which searches a different set
of places from the page templates, so the list says which route each template takes and the README
says what the host project needs for each (FR-009, FR-010).

**Rejected:** a setting that maps a pack template to a replacement. It would be a second mechanism
beside the one every Django developer already knows, and it would have to be kept in step with the
first. Article II asks for the simplest design that meets the requirement.

**Why defensible:** this is how every template pack for django-crispy-forms is customised, and how
ADR 0023 already tells a host project to change the frame. The one part that is not obvious, the
form renderer, is the part the feature documents and tests.

**ADR:** docs/adr/0029-every-pack-template-is-public.md

## D5. A change to a listed template goes through one minor version of deprecation

**Chosen:** when the pack renames a template or stops using one, a replacement at the old path
keeps taking effect for one minor version and the host project gets a deprecation warning that
names the old path and what replaces it. A project with nothing at the old path sees no warning.
When a name a template is handed is renamed or withdrawn, the old name keeps its value for one
minor version. In both cases the CHANGELOG says what replaces it and the list marks it
(FR-013 to FR-015).

**Rejected:**

- Freezing the paths until the next major version with no way to move one. Sibling features will
  add templates, and the first one that needs to split an existing template would be stuck.
- A warning when a replacement reads a name that is on its way out. The pack cannot see what a
  host project's template reads, so it could only warn every project or none. The CHANGELOG and
  the mark on the list carry that notice.
- A check at start-up that reports any template under the pack's directory that the pack does not
  ship. A host project may keep templates of its own there for layout objects it wrote, and the
  check would report those too.

**Why defensible:** it is Article XI applied to templates as written: "a deprecation lives one
minor version with a warning before it is removed, and the CHANGELOG says what replaces it". The
only reading added is what a warning means for a template path.

**ADR:** docs/adr/0029-every-pack-template-is-public.md

## D6. The list lives in the README and a check keeps it true

**Chosen:** the list is a section of the README's public surface, and the pack's test suite fails
when the list and the package disagree (FR-009, FR-011).

**Rejected:** a separate documentation page, and a list exposed from Python for host projects to
read. Article VI puts the public API in the README, and nothing in the issue needs the list at
run time.

**ADR:** none — it follows from Article VI, which already puts the public API in the README.

## D7. Changing part of a template is left out

**Chosen:** a replacement is a whole template. The pack's templates gain no named blocks in this
feature.

**Why:** the issue says "replace that single template". Blocks would make every block name public
surface as well, and ADR 0023 records that a value set by a tag inside a block does not survive
the block, which limits where they could go. Whether they are wanted is the maintainer's to say.

**Open with the maintainer:** #91.

**ADR:** none — nothing is decided: whether the pack offers blocks is asked in #91.

## D8. A replacement is the host project's own

**Chosen:** the pack does not check a replacement, add to it or hold it to the pack's promises
about markup and accessibility (FR-006).

**Rejected:** drawing a missing error element or label back in when a replacement leaves it out.
The pack cannot tell an omission from a decision, and a project that replaces the frame may well
be moving the errors somewhere else.

**ADR:** none — it states what the pack does not do, and the record of the template surface says a replacement is the host project's.

## D9. The per-form ways to name a template are left alone

**Chosen:** `template=` on a layout object, a helper's `field_template` and a helper's `template`
are django-crispy-forms' own, are documented by FS-003 to FS-006, and keep taking precedence for
the form that uses them (FR-008). This feature is about replacing a pack template for the whole
project.

**ADR:** none — the behaviour is django-crispy-forms' own and this feature leaves it alone.

## D10. No demo page and no sketch

**Chosen:** the feature adds no demo page and is not sketched first.

**Why:** the standing rule is that a feature adds a demo page where it changes what a person sees.
This one changes nothing in a project that replaces nothing. A replacement placed in the demo
project would apply to every page of it, so it would change the pages the earlier features are
shown and tested on. The worked example is in the README, and the test suite draws it.

**ADR:** none — local to this feature: it adds no page.

## D11. Nothing under `.github/` changes

**Chosen:** the check in FR-011 runs in the existing test suite, on the existing test matrix. The
feature asks for no workflow change, so there is no separate request for the maintainer.

**ADR:** none — local to this feature: it needed no workflow change.

## D12. The pack's templates do not change, and the first story is its tests

**Chosen:** no template in the pack is edited. Django's template loading already finds a file at
a pack template's path ahead of the pack's, on both routes (research R1). The first story writes
the tests that hold that in place for every distributed template.

**Why:** the behaviour was there and nothing said so or guarded it. A draw site that named a
template some other way, or a template drawn with a narrower context, would break a replacement
with every existing test still green.

**Revisit if:** a template is found that a replacement cannot reach.

**ADR:** none — it records that nothing had to be built, and the record of the template surface
states the rule the tests guard.

## D13. "Handed" means what the pack's own template reads, and the pack's objects one level down

**Chosen:** an entry's names are the ones the pack's template reads from outside itself, found by
compiling the template and walking its nodes. A value Django or django-crispy-forms supplies is
listed by its name. `drawn` and `table` are the pack's own objects, so each part a template reads
is listed with its dot, as `drawn.is_group` (research R5).

**Rejected:** listing every name in the context a template is drawn with. The context holds
whatever the page put there, and most of it is not the pack's to promise.

**Why:** it is D3 made checkable. The check compares what a template reads with its entry, so a
template cannot start reading a name without the list saying so.

**ADR:** docs/adr/0029-every-pack-template-is-public.md

## D14. A replacement at an old path is looked for where the template is drawn

**Chosen:** `mvp_forms/deprecation.py` holds the paths the pack has moved away from and one
function that asks whether the host project has a template at one. A draw site that moves asks
it first, draws what it finds and warns. The registry is empty in this release and no draw site
asks.

**Rejected:**

- A check when the project starts. Django's system checks do not run under a production server,
  and FR-013 asks for the warning no later than when a form is drawn.
- A second table in the README for paths on their way out, with a parser of its own. Nothing
  would exercise it until a path is withdrawn, so a withdrawn path stays a row of the one table.
- A template left at the old path that forwards to the new one. The pack could not tell its own
  forwarding template from a replacement, so it could not warn only the projects that have one.
- Changing every `{% include %}` in the pack to go through the tag now. It would change what
  every form costs to draw for a registry with nothing in it.

**Why:** the pack no longer ships the old path, so anything found there is the host project's.
One lookup answers both "is there a replacement" and "which template to draw".

**Revisit if:** django-crispy-forms renames one of the paths it chooses, which the pack cannot
intercept from a template.

**ADR:** docs/adr/0029-every-pack-template-is-public.md

## D15. The check reads the README

**Chosen:** the list is one markdown table in the README and the test suite parses it. The
helpers that read the package and the README live in `tests/template_surface.py`.

**Why:** D6 puts the list in the README and keeps it out of the package. A second copy of the
list in Python would be the thing the check exists to prevent.

**ADR:** none — it follows from D6.

## D16. Whether the pack's template tags are public is left open

**Chosen:** the list covers paths and names. It does not say whether `daisyui_field` and the
other tags a copied template calls are public in the same sense.

**Why:** the specification promises paths and names. A renamed tag fails with
`TemplateSyntaxError` the first time it is drawn, which is loud, so it is outside the quiet
break the issue describes.

**Open with the maintainer:** #115.

**ADR:** none — nothing is decided.

## D17. The design review's findings, all applied

**Chosen:** one medium and eight low findings, each applied to the plan before any code.

- The suite cleared four of django-crispy-forms' five cached templates; the first task adds the
  fifth, so a replacement of `whole_uni_formset.html` does not depend on test order.
- `host_template` returns the path to draw, so what replaces a withdrawn path is stated once.
- A withdrawn path stays a row of the one table. The second table and its parser are dropped.
- The helper's own tests are in `tests/test_template_surface.py`, and the helper is one class.
- `{% csrf_token %}` counts as reading `csrf_token`. What the pack's tags read in Python is
  outside the list.
- The README says how a deprecation warning is seen.
- The renderer case of the tag's tests runs under the default renderer.
- The worked example has a reader of its own, since it is a template and is not run.

**ADR:** none — corrections to the plan, not decisions that outlive it.

## D18. The every-template comparison collapses runs of whitespace, and two states are added

**Chosen:** the test removes the marker and collapses each run of whitespace to one space on
both sides before comparing the outputs as strings. Two entries are added at the end of
`STATES`: a form with media, through the filter and through the tag.

**Why:** Django's form renderer strips what a widget template draws, so a marker at the start of
a widget template leaves a newline in the copy's output that the pack's own output has lost.
Collapsing whitespace keeps the comparison a string comparison and ignores only what the
renderer decides. Every template was already reached by some state, but dropping `form.media`
from `uni_form.html` changed no output until a form with media was drawn through the filter.

**Revisit if:** a template's output ever depends on the whitespace between two words, or a
dropped name is found that no state reaches.

**ADR:** none — a choice about the tests.

## D19. The helper's own tests are in `tests/test_pack/`

**Chosen:** the tests of `tests/template_surface.py` are in `tests/test_pack/test_template_surface.py`,
not `tests/test_template_surface.py`.

**Why:** the conformance step accepts a test module with no source module to mirror only as
`test_factories.py`, `test_smoke.py` or under a path `[tool.forge.conformance]
non-mirror-paths` declares. `tests/test_pack/` is declared; a top-level `test_template_surface.py`
is not, and it failed the step. Declaring it would change `pyproject.toml`, which this story
may not touch.

**Revisit if:** the repository declares `tests/test_template_surface.py` as a non-mirror path,
when the file can move back beside the helper.

**ADR:** none — a choice about where tests live.

## D20. One existing test module's import line was changed

**Chosen:** the check on changes to existing tests flagged `tests/test_pack/test_documented_examples.py`.
The change is to its imports only: `HelpedForm`, `PACK_TEMPLATES` and `TemplateSurface` are
imported for the worked example's test, which is added at the end of the file. No existing test
or assertion is changed.

**ADR:** none — a record of a flag that was read and found harmless.

## D21. Existing test modules were extended, none of their tests changed

**Chosen:** the brief names three existing test modules for additions: `tests/test_templatetags/test_daisyui.py`
(imports for `warnings`, `override_settings`, `WITHDRAWN` and `clear_crispy_template_caches`, and two
new classes and a widget at the end), `tests/test_pack/test_template_surface.py` (an import and three
tests added to `TestDisagreements`) and `tests/test_pack/test_template_list.py` (the real registry passed
as the third argument of `TemplateSurface`). No existing test body or assertion is edited, and
`tests/conftest.py` is not touched, so the cases that need withdrawn paths build a `TemplateSurface`
from the one the `template_surface` fixture returns.

**Why:** the brief asks for exactly these additions, and the check on changes to existing tests may
flag them as it flagged D20.

**ADR:** none — a record of a flag that is expected and harmless.
