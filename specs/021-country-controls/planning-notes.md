# Planning notes: Country controls with a flag in each option

Things to consider when this feature is planned. Each one is answered by name in `research.md`.

This feature comes from a prototype the maintainer has seen and approved: branch
`prototype-countries`, its `PROTOTYPE.md`, and the prototype issue
[#272](https://github.com/django-mvp/django-mvp-forms/issues/272). This feature is the whole of
it except the demo project's changes under "The demo project" in `PROTOTYPE.md`, which are
separate work ([#274](https://github.com/django-mvp/django-mvp-forms/issues/274)). Its screens
and "Sam's decisions" are agreed.

**Shared piece: option and item templates for the pack's Tom Select widgets.**
`mvp_forms/static/mvp_forms/tomselect.js` reads `render.option` and `render.item` from
`data-tom-select` and fills each `${data.name}` with that value of the option, escaped, the syntax
django-tomselect uses for its own templates. Tom Select reads each `data-*` attribute of an option
into the option's data, so `data-flag` on the option is `data.flag` in the template. Whether
`TomSelect` gets a public setting for it or it stays internal to the country widgets is decided at
research.

**Shared piece: the flag row `FLAGGED`.** The flag image at its own size (16 × 11) and the name,
in a flex row of Tailwind utilities, inside an extra element because the pack's stylesheet sets
the display of the item in a single control. One string serves the widgets' templates and the
fetched control's.

**The django-tomselect quoting defect.** django-tomselect 2026.6.2 writes its `render` templates
into the page script unquoted, which stops the control. `country_config` keeps giving them already
quoted (`data_template_option` / `data_template_item`), with a comment naming the version. If a
django-tomselect release that fixes it exists at research, use that instead and record it. Never
file anything upstream.

**Design rules the maintainer gave.** Flags inside the options, never beside the select. Work
within the existing widgets and add no stylesheet. The flag stays before the name. Each demo field
is labelled with the field and widget it uses, never a made-up form's wording. No heading above
the countries first. The stock select stays as django-countries draws it. No continent or region
grouping.

**The look is ported, not redrawn.** The screens under "The look" in `PROTOTYPE.md` are
`/examples/countries/`, `/examples/countries/first/` and `/examples/countries/fetched/` at 390 and
1280, and the docs page `/third-party-support/django-countries/` at 1280. The files carrying them
are `mvp_forms/countries.py`, `mvp_forms/static/mvp_forms/tomselect.js`,
`demo/examples/third_party/countries.py`, `demo/examples/urls.py`, `demo/urls.py` and
`demo/docs/third-party-support/django-countries.md`. The plan names each of these and where it
lands on the default branch. The design review fails a plan that redraws a screen the prototype
has, and every story's merge is checked side by side against the prototype's screens.

**What it replaces on the default branch.** The demo's flag-beside-the-select field
(django-countries' `CountrySelectWidget`), the 250-row stock multiple select, the docs page
`demo/docs/third-party-support/django-countries.md` (rewritten), and
`tests/test_pack/test_countries.py` with `CountriesForm` in `tests/forms.py` (rewritten). The
existing tests of the stock select's drawing still hold and are kept in the rewrite.

**The empty choice.** The prototype's widgets write no option of empty value once the break
becomes a heading, so a single control on a field with a break starts on its first country. The
build keeps an empty option so the control starts empty (`decisions.md`, D6).

**Article XII.** The autocomplete view needs the constitution amended in the same pull request
(`decisions.md`, D5).
