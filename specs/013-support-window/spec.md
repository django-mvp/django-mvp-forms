# Feature Specification: A stated support window

**Feature Branch**: `013-support-window`

**Created**: 2026-10-03

**Status**: Draft

**Serves**: G7 (the package keeps pace with current Django, django-crispy-forms and daisyUI
releases)

**Roadmap**: R9 (a stated support window)

**Issue**: #89

**Depends on**: nothing still to be delivered. It builds on what v0.1.0 ships: the `daisyui`
template pack of FS-001 to FS-008, the test suite that draws forms through it, and the check from
FS-001 that every daisyUI class the pack writes is one daisyUI's CDN stylesheet defines
([ADR 0003](../../docs/adr/0003-daisyui-classes-and-tailwind-for-layout-only.md)).

**Input**: Someone deciding whether to adopt the pack needs to know which versions of Django,
django-crispy-forms and daisyUI it supports and how quickly a new release of each is picked up.
The package should state that, test against every version it names, and say what happens to a
version when it drops out of the window.

## Clarifications

### Session 2026-10-03

The coverage scan found five ambiguities. The maintainer was not available to answer, so each was
resolved from the issue, the roadmap item, the goals and the constitution. Longer rationale is in
`decisions.md`.

- **Q: Which versions are inside the window?**
  A: For Django, every release series the Django project itself still supports. For
  django-crispy-forms, every feature release of the current major series from a stated minimum
  upward. For daisyUI, the current major version from a stated minimum upward. Today that is
  Django 5.2, 6.0 and 6.1, django-crispy-forms 2.7, and daisyUI 5. Recorded as FR-003 to FR-005.

- **Q: daisyUI is not a Python dependency and the package ships no stylesheet. What does it mean
  to test against a daisyUI version?**
  A: Every daisyUI class the pack writes is defined by that version's CDN stylesheet. That is the
  check the suite already makes against one version, widened to each version the statement names.
  How a form looks under a version is not tested, because only a person looking at the page can
  judge it. Recorded as FR-011.

- **Q: "How quickly" needs a number. What is it?**
  A: Thirty days from the final release, for a new Django release series, a new feature release
  of django-crispy-forms in the current major series, and a new minor release of daisyUI in the
  current major version. A new major version of django-crispy-forms or daisyUI is a feature of its
  own with no period promised, and the statement says so. Recorded as FR-006 and FR-007.

- **Q: Does dropping a version count as a breaking change under Article XI?**
  A: No. A version leaves the window by a rule the statement publishes in advance, so the rule is
  the notice. A drop ships in a minor or major release of this package and never in a patch
  release. Recorded as FR-015 to FR-018.

- **Q: The versions the test workflow runs are set under `.github/`, which this feature may not
  change. What does "tests against every version it names" cover here?**
  A: Everything that can be delivered without a workflow change: one declaration of the window
  that the documentation, the package metadata and the suite are checked against, the daisyUI
  check for every named daisyUI version, and one documented command that runs the suite against
  any named Django and django-crispy-forms version. Having the test workflow read its versions
  from that declaration is a separate request for the maintainer, filed as #92.
  Recorded as FR-009 to FR-014.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Someone deciding whether to adopt reads what is supported (Priority: P1)

A developer is choosing a template pack for a host project. Their project runs a particular
Django, has django-crispy-forms installed at some version and loads some version of daisyUI. They
open the README, on GitHub or on the package index, and find in one place which versions of each
the package supports, how soon a new release of each is supported, and what will happen when a
version they depend on leaves. They can answer "will this work for us, and for how long" without
installing anything or reading the test configuration.

**Why this priority**: This is the request. Until the statement exists, the answer is spread
across the package metadata, a workflow file in another repository and a comment at the top of a
test data file, and no part of it says how soon a new release is supported or what happens to an
old one.

**Independent Test**: Read the README with three questions in hand: is my Django, my
django-crispy-forms and my daisyUI supported; how long after a new release of each can I expect
support; and what happens when one of mine leaves. Each has an answer in the same section. Then
compare that section with the package metadata on the package index: they name the same versions.

**Acceptance Scenarios**:

1. **Given** a developer reading the README, **When** they look for the versions the package
   supports, **Then** they find, in one section, the supported versions of Django,
   django-crispy-forms and daisyUI, and the Python versions the suite runs on.
2. **Given** the same section, **When** the developer looks for how soon a new release is
   supported, **Then** it gives a period for each of the three and says which kinds of release
   the period applies to.
3. **Given** the same section, **When** the developer looks for what happens to a version that
   leaves, **Then** it says when a version leaves, what kind of release of this package carries
   the drop, and where to find the last release that supported a version that has left.
4. **Given** the README as shown on the package index, **When** the developer follows a link from
   that section, **Then** the link resolves.
5. **Given** the package metadata, **When** it is compared with the statement, **Then** the
   minimum Django and django-crispy-forms versions it requires and the versions it advertises
   are the ones the statement names.
6. **Given** a host project on a Django or django-crispy-forms release newer than any the
   statement names, **When** the package is installed, **Then** the installation is not refused
   on account of that newer release.
7. **Given** a new major version of django-crispy-forms or daisyUI, **When** the developer reads
   the statement, **Then** it tells them that a new major version is not covered by the period
   and is supported only once the statement names it.

---

### User Story 2 - Every version the statement names is tested (Priority: P2)

A developer trusts the statement because nothing in it is a guess. A contributor who adds a
version to it, or takes one out, finds that the suite fails until the statement, the package
metadata and what is tested agree again. A contributor who wants to see the suite pass on one
named version runs one documented command.

**Why this priority**: A statement that drifts from what is tested is worse than none, because a
host project plans around it. It comes second because there has to be a statement before there is
anything to hold to it.

**Independent Test**: Change the declared window in one direction at a time (add a Django series,
remove a daisyUI version, raise the django-crispy-forms minimum) without touching anything else,
and run the suite. Each change fails a check that names what no longer agrees. Then run the suite
against each named Django and django-crispy-forms version with the documented command, and
confirm each run reports the versions it ran on.

**Acceptance Scenarios**:

1. **Given** the window declared in the repository, **When** the README's statement names a
   version the declaration does not, or leaves one out, **Then** the suite fails and names the
   version.
2. **Given** the declared window, **When** the package metadata requires or advertises a version
   the declaration does not name, or omits one it does, **Then** the suite fails and names the
   version.
3. **Given** each daisyUI version the statement names, **When** the suite runs, **Then** it
   checks that every daisyUI class the pack writes is defined by that version's CDN stylesheet,
   and fails naming the class and the version when one is not.
4. **Given** a daisyUI version named in the declaration with nothing in the repository to check
   it against, **When** the suite runs, **Then** it fails. No named version passes
   unchecked.
5. **Given** a named Django version and a named django-crispy-forms version, **When** a
   contributor runs the documented command for that pair, **Then** the whole suite runs with
   those versions installed and reports which versions it ran on.
6. **Given** that command, **When** the versions installed for the run are not the ones asked
   for, **Then** the run fails and reports no result for a version it did not use.
7. **Given** the suite run on its own with no version asked for, **When** it finishes, **Then**
   it has run on versions inside the declared window, and fails a check when the locked
   development environment falls outside it.

---

### User Story 3 - A host project on a version that has left the window (Priority: P3)

A host project is still on a Django series that the Django project has stopped supporting. The
maintainers of this package drop that series. The host project's next install does not break: its
installer picks the last release of this package that supported its Django. When its developers
look for why they are not getting new releases, the changelog and the README tell them which
version was dropped, in which release, and which release to stay on.

**Why this priority**: The issue asks for it by name, and it is what makes the window safe to
rely on at its far edge. It is third because nothing leaves the window until Django's next end of
support, so the first two stories are useful without it.

**Independent Test**: Take the rule in the statement and a release that drops a version. Confirm
the release is not a patch release, that the changelog entry names the dropped version and the
last release that supported it, that the README lists the same, and that the package metadata of
the new release no longer admits the dropped version.

**Acceptance Scenarios**:

1. **Given** the statement, **When** a developer reads when a version leaves, **Then** they find
   a rule for each of Django, django-crispy-forms and daisyUI that lets them work out, ahead of
   time, when a version they use will leave.
2. **Given** a release of this package that drops a Django or django-crispy-forms version,
   **When** its metadata is read, **Then** the minimum it requires excludes the dropped version,
   so that an installer in a host project still on that version selects an earlier release.
3. **Given** a version that has left the window, **When** a developer reads the README, **Then**
   they find that version listed with the last release of this package that supported it.
4. **Given** a release that drops a version, **When** a developer reads the changelog, **Then**
   the entry for that release names the version dropped and the last release that supported it.
5. **Given** the declared window and the list of versions that have left, **When** a version
   appears in neither, or in both, **Then** the suite fails and names it.
6. **Given** a dropped version recorded with the last release that supported it, **When** the
   changelog records no such release, **Then** the suite fails and names the version.

---

### User Story 4 - The maintainer learns that the window has fallen behind (Priority: P3)

A new Django release series, a new django-crispy-forms release or a new daisyUI minor release
comes out. The period in the statement starts on that day. A maintainer runs one documented
command and is told, for each of the three, whether a release exists that the window does not yet
name. Keeping the promise no longer depends on someone happening to see the release notes.

**Why this priority**: The period in the first story is only as good as the maintainer's chance
of noticing a release. Python dependencies are already raised by the repository's dependency
updates, but daisyUI is not a dependency of anything here and nothing watches it. It is last
because a maintainer can watch release notes by hand until it exists.

**Independent Test**: Run the command once when the window is current and once against a
declaration with its newest daisyUI version taken out. The first run reports nothing outstanding.
The second names daisyUI and the release that is missing, and ends with a failing status.

**Acceptance Scenarios**:

1. **Given** a window that names the newest release of each of the three, **When** the maintainer
   runs the command, **Then** it reports nothing outstanding and ends with a passing status.
2. **Given** a release of Django, django-crispy-forms or daisyUI that falls under the period and
   is not named in the window, **When** the maintainer runs the command, **Then** it names the
   package and the release and ends with a failing status.
3. **Given** a new major version of django-crispy-forms or daisyUI, **When** the maintainer runs
   the command, **Then** it reports the major version separately from releases that fall under
   the period, and the major version alone does not make the status fail.
4. **Given** a pre-release of any of the three, **When** the maintainer runs the command,
   **Then** the pre-release is not counted as a release the window is missing.
5. **Given** no network, or a source of release information that does not answer, **When** the
   maintainer runs the command, **Then** it says it could not find out and does not report the
   window as current.
6. **Given** the test suite, **When** it runs, **Then** it does not run this command and needs no
   network on account of this feature.

---

### Edge Cases

- A Django release series and a django-crispy-forms release that do not support each other are
  both inside the window. The statement says which pairs are supported, and the documented command
  refuses a pair the statement does not offer.
- The newest django-crispy-forms release raises its own minimum Django above the oldest Django in
  the window. The older Django stays in the window for as long as some named django-crispy-forms
  release supports it, and the statement shows the pairing.
- A new release of one of the three breaks the pack. The period still applies: within it, either a
  release of this package supports the new version, or the statement says that version is not
  supported and names the issue tracking it.
- daisyUI publishes a minor release that removes or renames a class the pack writes. The check for
  that version fails, and the version is not named until the pack draws correctly with it.
- A host page loads daisyUI by its major version from the CDN, as the README's install does, and
  so receives a minor release the statement does not yet name. The statement says what a host
  project can expect in that interval.
- A host project builds its own stylesheet with Tailwind and a daisyUI version below the stated
  minimum. That version is outside the window and the statement says so.
- The pack writes a handful of Tailwind layout utilities that daisyUI's stylesheet does not
  define. They are outside the daisyUI check for every version, exactly as they are today, and
  whether they should be allowed at all is #16's question.
- A version is dropped and a defect is later found in the last release that supported it. No fix
  is issued for that release. The statement says this.
- The Python versions the suite runs on change. The statement follows what is tested. This feature
  promises no period for a new Python version.
- Two versions leave the window at once. One release may drop both, and the changelog names each.
- The window is declared with a version written at a different level of detail than the statement
  uses, such as a patch release where a release series is meant. The check that compares them
  fails.

## Requirements *(mandatory)*

### Functional Requirements

#### The statement

- **FR-001**: The README MUST carry one section that states the support window: the supported
  versions of Django, django-crispy-forms and daisyUI, and the Python versions the suite runs on.
  Its links MUST be absolute, so the section reads the same on the package index (Article VI).
- **FR-002**: A version MUST be named at the level a host project chooses it: a release series for
  Django, a feature release for django-crispy-forms, and a major version with a minimum minor
  release for daisyUI. The statement MUST say that the newest patch release of each named version
  is the one meant.
- **FR-003**: The window for Django MUST be every release series the Django project still
  supports, with mainstream or security fixes.
- **FR-004**: The window for django-crispy-forms MUST be every feature release of its current
  major series from a stated minimum upward. Where a named release does not support a Django
  series in the window, the statement MUST show which pairs are supported.
- **FR-005**: The window for daisyUI MUST be its current major version from a stated minimum minor
  release upward. The statement MUST name the minimum and the newest minor release the suite
  checks, and MUST say that the releases between them are not checked one by one.
- **FR-006**: The statement MUST give the period within which a new release is supported: thirty
  days from the final release of a new Django release series, of a new feature release of
  django-crispy-forms in the current major series, and of a new minor release of daisyUI in the
  current major version. Where a new release cannot be supported inside the period, the statement
  MUST say so for that release and name the issue that tracks it.
- **FR-007**: The statement MUST say that a new major version of django-crispy-forms or daisyUI
  carries no period, and is supported only from the release of this package that names it.
- **FR-008**: The package metadata MUST agree with the statement: the minimum Django and
  django-crispy-forms versions it requires, and the framework and language versions it advertises.
  It MUST NOT put an upper limit on Django or django-crispy-forms, so that a host project can
  install the package beside a release newer than any the statement names.

#### Testing what is named

- **FR-009**: The window MUST be declared once in the repository, in a form a check can read. The
  README's statement, the package metadata and the list of versions that have left MUST each be
  checked against it by the test suite, and a disagreement MUST fail with the version named.
- **FR-010**: The suite MUST fail when the locked development environment holds a Django or
  django-crispy-forms version outside the declared window.
- **FR-011**: For every daisyUI version the statement names, the suite MUST check that each
  daisyUI class the pack writes is defined by that version's CDN stylesheet, and MUST fail naming
  the class and the version otherwise. A named version with nothing to check it against MUST fail
  the suite. The Tailwind layout utilities the pack is allowed today stay outside this check for
  every version (#16).
- **FR-012**: A contributor MUST be able to run the whole suite against one named Django version
  and one named django-crispy-forms version with a single documented command. The run MUST report
  the versions it ran on and MUST fail when they are not the ones asked for.
- **FR-013**: The contributing documentation MUST say how to add a version to the window and how
  to take one out, so that the declaration, the statement, the metadata and what is checked change
  together.
- **FR-014**: This feature MUST NOT change anything under `.github/`. The test workflow runs the
  suite on each named Django and Python version today, and on the one django-crispy-forms release
  the window names. Having the workflow take its versions from the declared window, which becomes
  necessary when a second django-crispy-forms release is named, is a separate request for the
  maintainer, filed as #92, and the specification MUST be complete without it.

#### A version that leaves

- **FR-015**: The statement MUST give the rule by which a version leaves. A Django release series
  leaves when the Django project ends its support. A django-crispy-forms release leaves when the
  minimum is raised, which happens only when it no longer supports any Django in the window or
  when the pack needs something a later release provides. The daisyUI minimum is raised only when
  the pack needs a class a later minor release provides, and a daisyUI major version leaves only
  when this package's own major version changes.
- **FR-016**: A drop MUST ship in a minor or major release of this package and never in a patch
  release. The contributing documentation of FR-013 MUST say so where it describes taking a
  version out.
- **FR-017**: A release that drops a Django or django-crispy-forms version MUST raise the minimum
  its metadata requires, so that an installer in a host project still on the dropped version
  selects the last release that supported it.
- **FR-018**: The README MUST list each version that has left with the last release of this
  package that supported it, and MUST say that an earlier release receives no fixes. The CHANGELOG
  entry of the release that drops a version MUST name the version and that last release. The
  suite MUST fail when a version is in both the declared window and that list, or when the last
  release recorded for a dropped version is not one the CHANGELOG records.

#### Noticing a new release

- **FR-019**: A maintainer MUST be able to find out, with one documented command, whether a final
  release of Django, django-crispy-forms or daisyUI exists that falls under the period in FR-006
  and is not named in the declared window. The command MUST name each such release and end with a
  failing status when there is one.
- **FR-020**: That command MUST report a new major version of django-crispy-forms or daisyUI
  separately and MUST NOT fail on that account alone. It MUST ignore pre-releases. When it cannot
  reach its source of release information it MUST say so and MUST NOT report the window as
  current.
- **FR-021**: The test suite MUST NOT run that command and MUST NOT need a network connection on
  account of this feature.

#### Constraints the package keeps

- **FR-022**: The feature MUST add no runtime dependency, MUST add no import from django-mvp
  (Article XIII), and MUST leave the output of every pack template unchanged. A form drawn before
  this feature is drawn the same after it.
- **FR-023**: Nothing this feature adds for checking or reporting versions is distributed with the
  package. The wheel and the source distribution hold what they hold today.

#### Shipping it

- **FR-024**: The README MUST carry the statement of FR-001 and the list of FR-018, the
  contributing section MUST carry what FR-012, FR-013 and FR-019 call documented, and the
  CHANGELOG MUST record the addition (Article VI). The feature changes nothing a person sees in a
  drawn form, so it adds no demo page.

### Requirement coverage

| Story | Requirements |
|---|---|
| US-1: Someone deciding whether to adopt reads what is supported | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, FR-022, FR-024 |
| US-2: Every version the statement names is tested | FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, FR-023, FR-024 |
| US-3: A host project on a version that has left the window | FR-009, FR-013, FR-015, FR-016, FR-017, FR-018, FR-024 |
| US-4: The maintainer learns that the window has fallen behind | FR-019, FR-020, FR-021, FR-023, FR-024 |

FR-024 lands with the first story and is extended by the stories that follow, so each story
documents its own part.

### Key Entities

- **Support window**: the versions of Django, django-crispy-forms and daisyUI the package states
  it works with and checks itself against, together with the rule by which a version enters and
  the rule by which one leaves.
- **Named version**: one version inside the window, written at the level a host project chooses
  it. Django 5.2 is a named version. Django 5.2.17 is a patch release of it.
- **Period**: the time from a new release's final publication within which the package supports
  it or says that it does not yet.
- **Dropped version**: a version that has left the window, kept on record with the last release
  of this package that supported it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer reading only the README can say, for their own Django,
  django-crispy-forms and daisyUI versions, whether each is supported, without opening the
  package metadata, a workflow file or the test suite.
- **SC-002**: For each of the three, the statement gives a period for new releases and a rule for
  leaving, so a developer can work out ahead of time when a version they use will be supported
  and when it will stop being.
- **SC-003**: Every version the statement names is checked: each named Django and
  django-crispy-forms version can be run with one command, and each named daisyUI version is
  checked on every run of the suite. No named version is without a check.
- **SC-004**: A change that makes the statement, the package metadata, the declared window or the
  list of dropped versions disagree fails the suite before it can be merged, with the version
  named.
- **SC-005**: A host project on a dropped Django or django-crispy-forms version that installs the
  package receives the last release that supported that version, and can find that release named
  in the README and the changelog.
- **SC-006**: A maintainer finds out with one command whether any release under the period is
  missing from the window, for all three at once.
- **SC-007**: Every form the pack draws is byte for byte the same before and after this feature.

## Assumptions

- The window today is Django 5.2, 6.0 and 6.1, django-crispy-forms 2.7 and daisyUI 5. The daisyUI
  minimum is the oldest daisyUI 5 minor release whose CDN stylesheet defines every daisyUI class
  the pack writes. The build finds it. If none older than the release checked today qualifies,
  that release is the minimum.
- Thirty days is a period a single maintainer can keep, and it is the maintainer's to change. A
  different number changes FR-006 and nothing else.
- Python versions are stated because nobody can install the package without knowing them, and the
  statement follows what the suite runs on. This feature promises no period for a new Python
  version and does not widen the Python versions tested, which are set by the test workflow.
- Dropping a version is not the removal of public API in the sense of Article XI, so it needs no
  deprecation release with a warning. The rule in the statement is the advance notice. The
  constitution is not amended by this feature.
- "Tests against" means the checks a specification, a contract or a computation can decide: the
  suite passes on a named Django and django-crispy-forms version, and a named daisyUI version
  defines the classes the pack writes. Whether a form looks right under a version is judged by
  eye on the demo project and is not part of the window's promise.
- Checking the two ends of the daisyUI range is enough, because daisyUI adds classes within a
  major version and removes them at a major version. A minor release that breaks this is caught
  when it becomes the newest one checked.
- The repository's dependency updates already raise a new Django or django-crispy-forms release
  as a pull request against the locked environment. The command of FR-019 does not replace them.
  It covers daisyUI, which they cannot see, and answers for all three in one place.
- Running the command of FR-019 on a schedule, and running the suite in the test workflow on
  versions read from the declared window, both need a change under `.github/` and are requested
  in #92. Neither is part of this feature.
- The words "support window", "named version" and "dropped version" are added to `CONTEXT.md`
  when the feature is built.
- Support for a new major version of django-crispy-forms or daisyUI, when one appears, is a
  feature request of its own.
- No sketch is needed before the build. The feature adds a README section and checks, and changes
  nothing a person sees in a form.
