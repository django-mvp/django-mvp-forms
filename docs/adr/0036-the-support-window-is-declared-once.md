# ADR 0036 — The support window is declared once, and a version leaves by a published rule

**Status:** accepted

## Decision

The versions of Django, django-crispy-forms and daisyUI the package supports are declared in one
file, `support-window.toml` at the repository root. The README's "Supported versions" section
states them, and the test suite fails when the README, the package metadata, the lockfile, the
installed versions, the changelog or the daisyUI class lists disagree with that file.

**What is in the window.**

- Django: every release series the Django project still supports.
- django-crispy-forms: every feature release of its current major series, from a stated minimum.
- daisyUI: its current major version, from a stated minimum minor release to the newest one
  checked. Supporting a daisyUI version means its CDN stylesheet defines every daisyUI class the
  pack writes ([ADR 0003](0003-daisyui-classes-and-tailwind-for-layout-only.md)). The suite
  checks the two ends of the range and not the releases between them.

**How a version enters.** A new Django release series, a new django-crispy-forms feature release
in the current major series and a new daisyUI minor release in the current major version are each
supported within thirty days of their final release, or the README says that release is not
supported and names the issue. A new major version of django-crispy-forms or daisyUI has no
period and is a feature of its own.

**How a version leaves.** A Django series leaves when the Django project ends its support. The
django-crispy-forms minimum is raised only when a release no longer supports any Django in the
window or the pack needs something a later release provides. The daisyUI minimum is raised only
when the pack needs a class a later minor release provides.

**A drop is not a removal under Article XI.** It needs no deprecation release and no warning. It
ships in a minor or major release of this package, never in a patch release. The release that
drops a Django or django-crispy-forms version raises the minimum in the package metadata, so an
installer in a host project still on that version selects the last release that supported it.
The declaration, the README and the changelog record the dropped version with that release, and
that release is not fixed further.

**The metadata has a minimum and no maximum.** A Django or django-crispy-forms release newer than
any the window names installs. The window says what is tested, and the metadata says only what
cannot work.

**Nothing that checks or reports versions is distributed.** `support-window.toml` and
`support_window.py` sit outside `mvp_forms/`.

## Why

Before this, the answer to "which versions" was spread across the package metadata, the defaults
of a test workflow in another repository and a comment at the top of a test data file, and no
part of it said how soon a new release is supported or what happens to an old one. One file that
everything else is checked against cannot drift from what is tested without the suite failing.

Django's own support schedule was borrowed, because a host project already plans around it. A
fixed count of releases, such as the last three, would name a series Django has abandoned or drop
one it still patches, depending on the calendar.

Treating a drop as a removal under Article XI would mean a warning for one minor version first.
Raised at import on an old Django, it would fire in every host project's test run, for a date
that is already public on Django's schedule. A major version of this package for every drop
would stop the major number meaning anything about the markup contract, since Django ends
support for a series about every eight months. The rule in the README is the advance notice, and
the installer does the rest.

An upper limit in the metadata would turn every upstream release into an install failure until
this package published, and would stop a host project trying a new Django on the day it comes
out.

Thirty days is short enough to matter to a project waiting to upgrade and long enough for one
maintainer to keep. A new major version gets no period because the work is of unknown size:
daisyUI 4 to 5 renamed and removed components.

## Revisit if

The package gains a second maintainer or a scheduled check of new releases, either of which
could shorten the period. Django changes its support schedule or how it numbers a release series.
The test workflow comes to read its versions from the declaration, which would let a second
django-crispy-forms release be named and run. Or a host project is found pinned to a dropped
version with a defect in the last release that supported it, which would test whether "no
further fixes" holds.
