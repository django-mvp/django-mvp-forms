# Research: Choice widgets drawn as a scale, pills, chips or cards

Read against `main` at `2f0044e` on 2026-11-22.

## Assumptions checked

- **A radio or checkbox group is framed as a fieldset.** Django's `RadioSelect` and
  `CheckboxSelectMultiple` set `use_fieldset`, and `is_group` in
  `mvp_forms/templatetags/daisyui.py` reads it, so a subclass is framed with a legend, the help
  text and the errors as a group is. Holds (FR-024).
- **A widget that names its own template is drawn by it.** `template_name` in the same module
  returns the pack's template only while the widget still has its class's `template_name` and
  `option_template_name`. A subclass with templates of its own keeps them. Holds (FR-003).
- **The pack would give these widgets the `radio` or `checkbox` class.** `component_of` matches
  by `isinstance`, so a subclass of `RadioSelect` is the `radio` component and its inputs would be
  given `radio` and the size and colour modifiers for a radio. Fails as things stand: the build
  must resolve size and colour for these widgets into their context, as `file_context` does for a
  file input, and keep the radio class off their inputs. A requirement to meet, not an upstream
  defect (FR-021, planning note 3).
- **daisyUI draws radio inputs as joined buttons.** daisyUI's join page documents
  `<input class="join-item btn" type="radio" aria-label="…">` inside a `join`. `join`,
  `join-item`, `btn`, `card` and `card-border` are all in `tests/data/daisyui-classes-5.0.txt`,
  the oldest release in the support window. Holds (FR-003).
- **A widget names a script in its media.** `MaskInput.Media` names `mvp_forms/imask.js` and
  `PartialDateInput.Media` names `mvp_forms/partial-date.js`, and `{% crispy %}` writes the form's
  media. Holds (FR-017).
- **A rating clears through the empty choice.** The README's "Rating and range" section draws the
  choice whose value is the empty string as the way to clear, and a field with no empty choice
  offers none. The new widgets follow the same rule. Holds (FR-007).

## Planning notes answered

1. **The look is already agreed: port it, do not redraw it.** Adopted. Each layout's markup and
   look is carried over and brought inside the pack's rules (see the table in `plan.md`, "The
   agreed look"). The structure of the agreed markup is kept: a row of equal segments with the end
   words under it, a wrapping row of toggles, a larger toggle with a dashed "none", a card with an
   icon tile, a text block and a round or square mark, and a fold control that is a circled plus.
2. **Stock daisyUI markup for each.** Adopted, with one fallback named. The scale and the pills are
   radio or checkbox inputs drawn as `btn`, named by `aria-label`, which is how daisyUI documents a
   join of radio buttons. Chips use the same, with a height that is not fixed and text that wraps. If
   a browser does not wrap or tick a label drawn through `aria-label` (checked in headless Chrome
   during the build), a chip is a `label` drawn as `btn` that holds a visually hidden input, and
   the plan's decision record says so. Cards are a `label` drawn as `card card-border` with
   Tailwind's `has-checked:` and `has-focus-visible:` variants, holding the input drawn as daisyUI's
   `radio` or `checkbox` as the round or square mark. daisyUI's `filter` is not used: it hides the
   other choices once one is chosen. The fold is a native `details` with a `summary`.
3. **Reuse what the package already has.** Adopted. The rating's way of finding the empty choice
   and writing classes onto each option (`rating_context`, `name_input`) is the model for the
   context the pack resolves for these widgets. The script follows `partial-date.js`: one file,
   guarded so it acts once, acting on content added later. The size and colour are not resolved by
   `component_of`'s class match, which would call these widgets radios: each widget names its own
   component and the tag resolves from that.

## The agreed look: what it was drawn from

The look was approved in an application's prototype. Its templates and styles were read in full
for the build and are named by the build's brief, never in the repository. What each layout takes
from it is the table in `plan.md`.

## What already exists

One line per piece of new code, with the first place on the list where the search stopped.

| Piece | Where the search stopped |
|---|---|
| Seven widget classes | New code. Django's `RadioSelect` and `CheckboxSelectMultiple` are the base. No installed package draws these layouts |
| Option extras (description, icon, meta) and the shown and folded split | New code on `create_option` and `get_context`, which Django provides for exactly this |
| Resolving the empty choice and naming inputs | This repo: `rating_context` and `name_input` in `mvp_forms/templatetags/daisyui.py`. The new context follows the same shape and reuses `name_input` |
| Group frame, legend, help text, errors, `aria-invalid`, `disabled` | This repo: `is_group` and the frame. `use_fieldset` is set by Django's two base widgets |
| Size and colour tables | This repo: `Modifiers`. Two components are added, nothing new in how they resolve |
| The fold's disclosure | The browser: `details` and `summary` |
| The fold's script | New code, about forty lines. The browser's `toggle` event and a delegated `change` listener do the work. No package does this |
| The widgets' media | Django's `Media`, as `MaskInput` and `PartialDateInput` use it |
| Demo page, README, catalogue | This repo's existing shape for a widget group, e.g. `demo/docs/custom-widgets/range-inputs.md` |
| Legibility pairings | This repo: `tests/legibility/` |
