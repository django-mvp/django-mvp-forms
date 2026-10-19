# ADR 0060 — An image input draws its thumbnail from its options, and brings one script

**Status:** accepted

## Decision

`ImageInput` is a widget a developer names for an image field. The pack does not draw every
`ImageField` with it, and a `FileField` keeps the clearable file input.

The thumbnail is daisyUI's `avatar`. Its shape and size are written into its own `style`
attribute, as `height: calc(<height> * 1rem); aspect-ratio: calc(<aspect_ratio>)`, with no width,
so the browser works the width out from the two and no class has to exist for a size. With no
`aspect_ratio` the thumbnail is square and the whole image is shown inside it. With one, the image
fills it. `mask` adds daisyUI's `mask` class and `mask-<name>` to the thumbnail, for any name. The
mask classes daisyUI has are written out in `mvp_forms/widgets.py`, so a Tailwind build that scans
the package finds them.

`mvp_forms/image-input.js` is named in the widget's media. It acts once however often a page
includes it, and listens on the document, so an input added later is covered. It shows a chosen
image before the form is sent, offers to revert it, keeps choosing a file and ticking the removal
checkbox apart, and draws a stored image that will not load as missing. With `show_input=False`
it takes the file input out of sight and out of the tab order and shows the thumbnail as a button
that opens the file picker. Without the script the file input stays where it is and works.

## Why

A preview of a chosen file needs a script, and a script reaches the page only through a widget's
media, as [ADR 0045](0045-mask-widgets-bring-one-script-that-acts-once.md) settles for the masks.
The pack cannot add one to a stock `ImageField`, so the widget is chosen by name.

Django refuses a form that sends a file and ticks the removal checkbox together, so the script
never lets both stand.

A thumbnail is the job daisyUI documents its avatar for, and Article XIV asks for daisyUI's
component where one exists. Its layout, the border and the band shown over a picker are Tailwind
utilities, because daisyUI has no class for them.

An inline style carries any number a developer passes, and a class for each height or ratio would
have to be in the host project's stylesheet. Writing a width beside the ratio would let the two
disagree.

It is tested in Chrome, as [ADR 0046](0046-the-mask-script-is-tested-in-a-browser.md) settles.

## Revisit if

daisyUI gains a component for an image upload, or a host project's Content-Security-Policy forbids
inline styles.
