# ADR 0046 — The mask script is tested in a browser

**Status:** accepted

## Decision

What `mvp_forms/imask.js` does is tested by running it in Chrome, in `tests/test_imask_e2e.py`,
with the Playwright that the shared test tools already install. The tests are marked `e2e`. They
are skipped where Chrome cannot be launched and fail in CI.

The browser is launched by channel, as the installed Chrome, and not as Playwright's own
download.

IMask is served to the tests from a copy under `tests/data/`, by answering the page's request for
it. No test uses the network, and the copy is not part of the wheel or the sdist.

The tests assert what this package's script does: that a mask is applied with the options written
on the input, once, to inputs present and added later, that nothing happens without IMask, that
the event is sent, and what the form receives. They do not test IMask's masking rules beyond one
keystroke that shows the options arrived.

## Why

The first version of the script passed a check in a simulated DOM and failed for a person typing
into the page, because the simulation had removed the repeated script tags that caused the fault.
Only a browser runs the page as it is served.

The rest of the suite reads rendered markup, which can show that the options are on the input and
cannot show that anything happens to them.

The test workflow does not download Playwright's browsers, and GitHub's runners carry Chrome, so
launching by channel runs the tests in CI with no change to the workflow.

Testing IMask's own rules here would fail whenever IMask changed one, for a reason this package
has no say in.

## Revisit if

The test workflow installs Playwright's browsers, which would let the tests use them and stop
depending on what the runner carries.
