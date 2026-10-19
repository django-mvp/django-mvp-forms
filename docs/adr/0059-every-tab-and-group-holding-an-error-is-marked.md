# ADR 0059 — Every tab and accordion group holding an error is marked with a status dot and a hidden description

**Status:** accepted

## Decision

When a tab or an accordion group holds a field drawn as invalid, the pack marks it. The mark is
part of the default drawing and has no setting.

- A tab or group holds an error when its drawn fields contain `aria-invalid="true"`. This is the
  test `layout/modal.html` already uses to open a modal. It sees fields nested at any depth, it
  still sees an error the helper does not show, and it does not see an error on a hidden field,
  which Django and the pack show above the form.
- The visible mark is daisyUI's `status status-error` dot, placed as the `indicator-item` of an
  `indicator`. It is `aria-hidden`.
- What assistive technology hears comes from a `hidden` element holding the translated text
  "Contains a field with an error". The tab's radio, or the group's `<summary>`, names it with
  `aria-describedby`. Its id is the `Tab` or `AccordionGroup` id followed by `-error`.
- In a group, the `indicator` wraps the group's name inside the `<summary>`, so the dot sits at
  the corner of the name. The description element is drawn just before the `<details>`, because
  a closed `<details>` hides everything but its `<summary>`, and Chrome then reads no description
  from an element inside it.
- In a tab, the `indicator` is an empty element drawn after the tab's `tab-content`. daisyUI orders
  every `tab-content` after the tabs, so the empty indicator lands in the row of tabs right after
  the tab it belongs to, and its dot sits on that tab's top end corner.
- Which tab or group opens does not change. django-crispy-forms still decides it.

## Why

Issue #46 asked whether a person should see every tab or group holding an error, and not only the
one that opens. Sam decided it should be marked, by default, for sighted people and for assistive
technology alike, with daisyUI classes only.

A tab is a radio whose visible label is its `aria-label`, drawn by daisyUI's CSS. Nothing can be
put inside it, and putting text in the `aria-label` would change the name every tab is announced
by. daisyUI's other form of tab, a `<label>` holding the radio and an icon, was ruled out because
it changes every tab, with or without an error, and the radio would no longer sit directly
before its content as [ADR 0015](0015-a-tabs-radio-is-drawn-with-its-pane.md) requires. An
element between the radio and its content would break the same rule. An element before the radio
would put the dot on the previous tab's corner.

Error-coloured text was ruled out. daisyUI's `error` colour is not guaranteed to reach the
contrast normal text needs under every theme, and colour alone is not a mark (WCAG 1.4.1). The dot
is a shape as well as a colour. Under some of daisyUI's themes the dot itself falls short of 3 to
1 against the page or the group's `base-200`, as an invalid input's error border does. It is
measured and listed in the README's known exceptions on the same terms, because no stock daisyUI
class repairs it.

`aria-describedby` was chosen over a text alternative on the dot. Inside a `<summary>` the dot's
text would join the group's name, and outside a radio it would not reach the tab at all. A
description keeps every name as the developer gave it and is announced after it. An element with
`hidden` is still read when an attribute refers to it, and it needs no class.

## Revisit if

daisyUI lets a radio tab hold content of its own, django-crispy-forms gives a pane's template its
form, or a theme the pack supports draws `status-error` too faint to see against the tabs.
