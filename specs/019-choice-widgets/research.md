# Research: Choice widgets drawn as a scale, pills, chips or cards

Read against `main` at `2f0044e` on 2026-11-22. Only the checks the specification depends on are
here. The full investigation is written when the feature is planned.

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
