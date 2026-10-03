# Decisions: A stated support window

Rationale too long to inline in `spec.md`, and the ambiguities resolved while specifying. The
maintainer was not available for questions on this feature, so every reading of the issue below
was made without him and is his to overturn when he reviews the specification.

Records under `docs/adr/` are written when the feature is built, alongside the code they explain.
Each decision says here whether it is expected to earn one.

## D1. The reading of the issue was confirmed without the maintainer

**Chosen:** the feature is read as follows. The README gains one section stating which versions of
Django, django-crispy-forms and daisyUI the package supports, how soon a new release of each is
supported, and what happens to a version that leaves. The window is declared once in the
repository, and the README, the package metadata and the test suite are checked against that
declaration, so the statement cannot drift from what is tested. A version that leaves is dropped
in a minor or major release, the package's minimum is raised so an installer on the old version
picks the last release that supported it, and the README and changelog name that release. A
maintainer has one command that reports a release the window does not yet name. The feature
serves G7 and sits in R9. It draws nothing, so the pack's templates, the choices of FS-007 and
FS-008 and the demo pages are untouched.

**Why:** the issue is three sentences and the roadmap deliverable is one, and neither conflicts
with this reading. Each gap it fills is recorded as its own decision below.

**ADR:** none. This is the record of how the specification was written.

## D2. What is inside the window

**Chosen:** Django: every release series the Django project still supports, which today is 5.2,
6.0 and 6.1. django-crispy-forms: every feature release of the current major series from a stated
minimum, which today is 2.7 alone. daisyUI: the current major version, 5, from a stated minimum
minor release (FR-003 to FR-005).

**Rejected:**

- Only the newest release of each. django-mvp projects sit on the long-term-support Django for
  years, and the package already declares and tests 5.2.
- A fixed number of Django releases, such as "the last three". It would name a release Django
  itself has abandoned, or drop one Django still patches, depending on the calendar.
- A lower django-crispy-forms minimum than 2.7. The package requires 2.7 today, 2.7 is the
  newest release, and nothing in FS-001 to FS-008 was tested on anything older.

**Why defensible:** it describes what the package already requires and what its tests already
run on, and it borrows Django's own published support schedule, which a host project already
plans around.

**ADR:** expected, together with D4 and D5: one record for how the window is defined, how a
version enters and how one leaves.

## D3. Testing against a daisyUI version means checking its classes

**Chosen:** a daisyUI version is supported when its CDN stylesheet defines every daisyUI class the
pack writes. The suite checks the minimum and the newest minor release the statement names, and
the statement says the releases between them are not checked one by one (FR-005, FR-011).

**Rejected:**

- Drawing the demo pages under each version and comparing them. Only a person looking at the page
  decides whether it is right, and the testing standard rules that out as a test.
- Checking every minor release from the minimum to the newest. daisyUI 5 has had eight minor
  releases so far. One list of some 3,500 class names for each would be
  kept in the repository for little gain, since daisyUI adds classes inside a major version and
  removes them at one.
- Naming only "daisyUI 5". A host project with its own Tailwind build chooses an exact version,
  and an early 5.x release may lack a class the pack writes.

**Why defensible:** the package ships markup and no stylesheet, so the only contract it has with
daisyUI is the class names. The suite already makes this check against one version. This widens
it to the versions the statement names.

**Open with the maintainer:** #16 asks whether the Tailwind layout utilities the pack writes
should be allowed at all. This specification leaves them outside the daisyUI check, as they are
today, and takes no side.

**ADR:** none of its own. It applies ADR 0003 to more than one version.

## D4. The period is thirty days, and a new major version has none

**Chosen:** a new Django release series, a new django-crispy-forms feature release in the current
major series and a new daisyUI minor release in the current major version are each supported
within thirty days of their final release. Where one cannot be, the statement says so and names
the issue tracking it. A new major version of django-crispy-forms or daisyUI carries no period
(FR-006, FR-007).

**Rejected:**

- No number, only "promptly". The issue asks how quickly, and a reader cannot plan around an
  adverb.
- Support on the day of release, by testing against pre-releases. It needs a scheduled workflow,
  which this feature may not add, and it promises more than one maintainer can be sure of.
- A period for a new major version. daisyUI 4 to 5 renamed and removed components. Supporting a
  major version is a feature with its own specification, and promising a date for work of unknown
  size would be a guess.

**Why defensible:** thirty days is short enough to mean something to a host project waiting to
upgrade and long enough for one maintainer to keep through a holiday. It is a number, so it can
be changed by changing a number.

**ADR:** expected, with D2.

## D5. Dropping a version is not a breaking change

**Chosen:** a version leaves by a rule the statement publishes: Django's own end of support, or a
raised minimum for django-crispy-forms and daisyUI. The drop ships in a minor or major release,
never a patch. The package's minimum is raised so an installer on the old version selects the
last release that supported it. The README lists the dropped version with that release, and
earlier releases get no fixes (FR-015 to FR-018).

**Rejected:**

- Treating a drop as a removal under Article XI, with a warning for one minor version first. A
  warning raised at import on an old Django would fire in every host project's test run, and the
  date is already public on Django's own schedule.
- A major version of this package for every drop. Django ends support for a series about every
  eight months, so the major number would stop meaning anything about the markup contract.
- Keeping a dropped version working "while it still happens to". Nobody could say whether a given
  release supports it, which is the question this feature exists to answer.
- A check that fails when a version is removed in a branch with a patch-level version number.
  The version is bumped by the release pull request after the change has merged, so the branch
  that makes the drop always carries the previous release's number.

**Why defensible:** it is the convention Django packages generally follow, and the installer does
the work: a host project on a dropped Django keeps getting the last release that supported it
without doing anything.

**ADR:** expected, with D2. This is the part most likely to be questioned later.

## D6. No upper limit on Django or django-crispy-forms

**Chosen:** the package metadata requires a minimum and no maximum (FR-008). A release newer than
any the statement names installs, and the statement simply does not vouch for it yet.

**Rejected:** capping at the newest named version. A cap stops a host project from trying a new
Django on the day it is released and turns every upstream release into an install failure until
this package publishes.

**Why defensible:** the statement says what is tested. The metadata says what cannot work. They
answer different questions, and only the lower bound is something the package knows cannot work.

**ADR:** none. It is the current behaviour, and D2's record covers it in a line.

## D7. One declaration, checked from the suite, and nothing under `.github/`

**Chosen:** the window is declared once in the repository. The suite fails when the README, the
metadata, the locked environment or the list of dropped versions disagrees with it. A contributor
runs the suite on any named Django and django-crispy-forms version with one documented command.
The test workflow is left alone, and the request to have it read its versions from the
declaration is #92 (FR-009 to FR-014).

**Rejected:**

- Leaving the workflow as the source of truth. Its versions are defaults of a shared workflow in
  another repository, so a check in this one cannot read them and they can move without a change
  here.
- Waiting for the workflow change before specifying anything. Today the workflow's Django and
  Python versions match the window, and the one django-crispy-forms release named is the locked
  one, so every named version is already run. The gap opens only when a second
  django-crispy-forms release is named.

**Why defensible:** it delivers the whole of "tests against every version it names" that can be
delivered without a workflow change, and names the one remaining part and where it is tracked.
Where the declaration lives and what form it takes is for the build.

**ADR:** none expected. If the build puts the declaration somewhere a reader would not look for
it, that choice earns one.

## D8. Python is stated and not promised

**Chosen:** the statement names the Python versions the suite runs on. There is no period for a
new Python version and this feature does not widen what is tested.

**Why:** the issue names three things and Python is not one of them, but a reader cannot install
the package without knowing it, and the metadata already declares it. Python 3.14 is not in the
test matrix. Whether it joins is part of #92, because the matrix is set under `.github/`.

**ADR:** none.

## D9. A command to notice a new release is in scope

**Chosen:** one command reports, for all three, a final release the window does not name. It
needs the network, so the suite never runs it (FR-019 to FR-021).

**Rejected:** leaving it out. The repository's dependency updates raise a new Django or
django-crispy-forms release as a pull request, but daisyUI is loaded from a CDN by the host page
and is a dependency of nothing here. Without something that looks, the thirty days for daisyUI
would be kept by luck.

**Why defensible:** it is the smallest thing that makes the period a promise the maintainer can
keep on purpose. Running it on a schedule would need a workflow, so that part is in #92.

**ADR:** none.

## D10. No demo page and no sketch

**Chosen:** the feature adds no demo page and needs no sketch before the build.

**Why:** a feature adds a demo page where it changes what a person sees. This one changes a
README section, the package metadata and the test suite. Every form is drawn exactly as before
(FR-022).

**ADR:** none.
