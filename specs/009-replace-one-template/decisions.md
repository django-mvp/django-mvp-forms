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

**ADR:** none. This is the record of how the specification was written, not a constraint on the
code.

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

**ADR:** expected. One record for the template surface, covering D2, D3 and D5.

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

**ADR:** expected, with D2.

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

**ADR:** none of its own. ADR 0012 already records that widget templates go through the form
renderer. The record in D2 names the two routes.

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

**ADR:** expected, with D2.

## D6. The list lives in the README and a check keeps it true

**Chosen:** the list is a section of the README's public surface, and the pack's test suite fails
when the list and the package disagree (FR-009, FR-011).

**Rejected:** a separate documentation page, and a list exposed from Python for host projects to
read. Article VI puts the public API in the README, and nothing in the issue needs the list at
run time.

**ADR:** none. It follows from Article VI.

## D7. Changing part of a template is left out

**Chosen:** a replacement is a whole template. The pack's templates gain no named blocks in this
feature.

**Why:** the issue says "replace that single template". Blocks would make every block name public
surface as well, and ADR 0023 records that a value set by a tag inside a block does not survive
the block, which limits where they could go. Whether they are wanted is the maintainer's to say.

**Open with the maintainer:** #91.

**ADR:** none.

## D8. A replacement is the host project's own

**Chosen:** the pack does not check a replacement, add to it or hold it to the pack's promises
about markup and accessibility (FR-006).

**Rejected:** drawing a missing error element or label back in when a replacement leaves it out.
The pack cannot tell an omission from a decision, and a project that replaces the frame may well
be moving the errors somewhere else.

**ADR:** none.

## D9. The per-form ways to name a template are left alone

**Chosen:** `template=` on a layout object, a helper's `field_template` and a helper's `template`
are django-crispy-forms' own, are documented by FS-003 to FS-006, and keep taking precedence for
the form that uses them (FR-008). This feature is about replacing a pack template for the whole
project.

**ADR:** none.

## D10. No demo page and no sketch

**Chosen:** the feature adds no demo page and is not sketched first.

**Why:** the standing rule is that a feature adds a demo page where it changes what a person sees.
This one changes nothing in a project that replaces nothing. A replacement placed in the demo
project would apply to every page of it, so it would change the pages the earlier features are
shown and tested on. The worked example is in the README, and the test suite draws it.

**ADR:** none.

## D11. Nothing under `.github/` changes

**Chosen:** the check in FR-011 runs in the existing test suite, on the existing test matrix. The
feature asks for no workflow change, so there is no separate request for the maintainer.

**ADR:** none.
