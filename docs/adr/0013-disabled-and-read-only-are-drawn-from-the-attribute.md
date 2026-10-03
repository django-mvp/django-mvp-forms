# ADR 0013 — Disabled and read-only are drawn from the attribute, and read-only is never imitated

**Status:** accepted, amended by [ADR 0027](0027-uneditable-field-writes-disabled.md): `UneditableField` is the one case where the pack writes `disabled`

## Decision

The pack adds no class and no attribute for either state, on any input it draws.

- **Disabled** means Django's `disabled` field argument. Django writes `disabled` on the input,
  on every option of a group and on a file field's removal checkbox. daisyUI draws its disabled
  state from that attribute.
- **Read-only** means a `readonly` attribute a developer puts on a widget. It reaches the input
  as written. On a text input or a textarea the browser shows the value, refuses edits,
  announces the state and still submits the value.
- A select, a checkbox, a radio button and a file input have no read-only state in HTML. The
  attribute does nothing on them and the pack does not imitate it. A field that must not be
  edited is marked disabled.

Every later input and widget in the pack follows the same rule.

## Why

Every disabled rule in daisyUI's stylesheet keys on the attribute, for each component the pack
uses, so a modifier class would add nothing.

daisyUI has no read-only rule for any component, and the pack writes only daisyUI's classes for
its inputs. So there is no class that could mean read-only.

Each way of imitating read-only on an input that has no such state costs something. Disabling the
input behind the developer's back stops its value being submitted, which changes what the form
does. Blocking it with script needs JavaScript the pack does not ship. Styling it to look fixed
while it still accepts input misleads the person using it. Django has no read-only field
argument either, only `disabled`, which it also enforces on the server.

## Revisit if

daisyUI gains a read-only modifier, or HTML gains a read-only state for selects or checkboxes.
