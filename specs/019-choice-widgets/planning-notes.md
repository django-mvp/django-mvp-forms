# Planning notes: Choice widgets drawn as a scale, pills, chips or cards

Suggestions for how this might be built. Research answers each one by name: adopted or not
adopted, and why.

## 1. The look is already agreed: port it, do not redraw it

The four layouts have been designed and approved. The build brings that look into the package's
rules rather than designing a new one. What was agreed:

- **Scale.** One row of equal segments, one per choice, touching edge to edge with a small gap,
  each a tall target with its number centred. The chosen segment is filled with the primary colour.
  Under the row, the low end's words sit at the left and the high end's at the right, in small,
  quiet type. The end words are read out with the first and last segments.
- **Pills.** A wrapping row of rounded toggles with a gap between them, each a comfortable finger
  target. A chosen pill is filled. A multiple pill shows a tick before its label when chosen.
- **Chips.** As pills but larger, with a long label wrapping inside the chip rather than being cut
  off. The way to say "none" is drawn as a quieter chip, with a dashed edge and softer text. The
  fold control is a plain link-coloured line with a small circled plus and "N more", under the
  row.
- **Cards.** A grid of one, two or three columns on a wide screen and one on a phone. Each card has
  a small square icon tile at its left, then the short line in small capitals, the label in bold
  and the description in softer text, and a round mark at its right (square for a multiple card)
  that fills with a tick when chosen. A chosen card takes a primary-coloured edge and a light
  primary tint, and its icon tile fills with the primary colour. The fold is a disclosure under the
  grid whose summary is a circled plus, the words and the count.

## 2. Stock daisyUI markup for each

- Scale: daisyUI's `join` holding radio inputs drawn as `join-item btn`, each named by an
  `aria-label`, which daisyUI documents as a join of radio buttons. A checked radio with `btn` is
  drawn in the primary colour by daisyUI itself.
- Pills and chips: radio or checkbox inputs drawn as `btn` in a flex row that wraps, with Tailwind
  utilities for the rounded shape, a chip's height and wrapping. Not daisyUI's `filter`, which hides
  the other choices once one is chosen.
- Cards: a `label` drawn as a daisyUI `card card-border` holding its input, with Tailwind's
  `has-checked:` variant for the chosen card. The tick mark can be the input itself drawn as
  daisyUI's `radio` or `checkbox`.
- The fold: a native `<details>` and `<summary>` for a single-choice widget, so it needs no script.
  The multiple widgets may use the same disclosure, with the script keeping a ticked choice on show.
  Hidden choices use the `hidden` attribute, never a class of the package's own.

## 3. Reuse what the package already has

- The fold is the only piece that needs a script. The package already ships one script for each
  kind of widget that needs one (`mvp_forms/static/mvp_forms/imask.js`, `partial-date.js`), named
  in the widget's media. Follow the same shape: one file, no inline script, acting on content added later,
  acting once however often it is included.
- The rating (`mvp_forms/templates/daisyui/widgets/rating.html`) and the choice group templates
  (`group.html`, `inline_group.html`, `group_options.html`) are the nearest relatives. Reuse their
  structure (how the empty choice is found, how options are named, how the group is framed and
  how size, colour and the error state are resolved) rather than duplicating it.
- The pack finds a widget's component by its class, so a subclass of `RadioSelect` is a `radio`
  today and would be given the `radio` class. These widgets need their size and colour resolved
  into their context instead, as the file input's are.
