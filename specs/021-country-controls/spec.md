# Feature Specification: Country controls with a flag in each option

**Feature Branch**: `021-country-controls`

**Created**: 2026-11-27

**Status**: Draft

**Serves**: G12 (fields and widgets from popular third-party Django packages draw well in the
pack) and G11 (the package offers its own widgets, each looking native beside the pack's own
inputs)

**Roadmap**: none. Fields and widgets carry no roadmap item (Article XV).

**Issue**: #273

**Depends on**: nothing still to be delivered. It builds on the pack's Tom Select widgets
(FS-017), the pack's drawing of django-tomselect controls and their option groups (FS-014), and
the pack's drawing of django-countries' form fields.

**Input**: A developer whose form has a django-countries field should be able to give it a
searchable control with each country's flag, rather than the stock select of 250 countries. One
version writes the countries into the page with the form. One fetches them from a view as a person
types, through django-tomselect. Both honour the countries django-countries is configured to list
first. The prototype on the `prototype-countries` branch
([#272](https://github.com/django-mvp/django-mvp-forms/issues/272)) shows each of them, and this
specification describes what its screens do.

## Why

django-countries gives a form an ordinary select of some 250 countries. A single one can be
scrolled, slowly. A multiple one is a box of 250 rows that has to be held with a modifier key to
choose more than one. django-countries' own flag widget puts one image beside the select, which
shows the chosen country but helps nobody find it.

The pack already has Tom Select controls that search a long list (FS-017), and already draws
django-tomselect's controls, which fetch their options as a person types (FS-014). A country
field gets neither without the developer writing an option template, a script setting and, for
the fetched control, a view of their own. This feature gives them all three, with the flag drawn
inside each option and each chosen value.

## Clarifications

### Session 2026-11-27

Each question below came from the specification's ambiguity scan and was answered from the
prototype, its hand-over notes and the maintainer's recorded decisions. `decisions.md` holds the
longer reasoning.

- Q: Are the three things in the request three features or one? → A: One feature, three stories.
  All three give a django-countries field a control with flags, and the third extends the first
  two (D1).
- Q: What happens to the field the stock select draws today? → A: Nothing. The stock select stays
  exactly as django-countries and the pack draw it now, including django-countries' flag widget.
  The new controls are widgets a developer names (D3).
- Q: Does a person filling in the form have a story of their own? → A: No. Searching a Tom Select
  control and reading its options is what the person already does with the pack's controls. What
  they see is stated as outcomes under each developer story (D2).
- Q: What does a single control with a break start on, when the field holds no value? → A: No
  country. django-countries uses the break as the field's empty choice, and the control must not
  choose the first country for the person because the empty choice became a heading (D6).
- Q: Is `first_repeat` honoured? → A: No. A Tom Select control holds one option per value, so a
  country listed first is not listed again among the rest. The documentation says so (D7).
- Q: Does the fetched control need a stylesheet or settings beyond django-tomselect's? → A: No.
  Everything django-tomselect's `TomSelectConfig` takes still applies, and the flag template comes
  with the configuration (FR-011).
- Q: The package ships no views (Article XII). Does the autocomplete view break that? → A: It is
  the one exception the maintainer asked for, a view for a supported package that the host
  project routes itself. The package still ships no URL. The constitution is amended in the same
  pull request (D5).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer gives a country field a searchable control with flags (Priority: P1)

A developer has a django-countries field on a form, single or multiple. They give it
`CountrySelect` or `CountrySelectMultiple` as its widget. A person filling in the form then gets
the pack's Tom Select control, searches the countries by typing, and sees each country's flag
before its name, both in the list and in each chosen value. Every setting `TomSelect` and
`TomSelectMultiple` take still works on these widgets: placeholder, clear button, remove buttons,
the largest number of values, and a counted control. The countries are written into the page with
the form, so the control makes no request.

**Why this priority**: It is the case the request starts from: a country field that can be
searched, with flags, and a multiple one that is usable at all. The other two stories extend it.

**Independent Test**: Draw a form with a `CountryField` given `CountrySelect` and a
`CountryField(multiple=True)` given `CountrySelectMultiple`, render it, start the controls in a
browser, search for a country and choose it.

**Acceptance Scenarios**:

1. **Given** a single country field with `CountrySelect`, **When** the form is drawn, **Then** the
   select carries every country of the field as an option, each option carries the address of its
   country's flag, and the select is marked for the pack's Tom Select script.
2. **Given** that form in a browser that loads the form's media, **When** a person opens the
   control and types part of a country's name, **Then** the list narrows to the matching
   countries, and each option shows the flag image of its country ahead of its name.
3. **Given** that control, **When** a person chooses a country, **Then** the chosen value shows
   the country's flag ahead of its name, and the form, once posted, cleans to that country's code
   as django-countries' own field does.
4. **Given** a multiple country field with `CountrySelectMultiple(remove_button=True)`, **When** a
   person chooses several countries, **Then** each chosen value shows its flag ahead of its name
   and has a remove button, and the posted form cleans to the list of their codes.
5. **Given** `CountrySelectMultiple(counted=True)`, **When** a person chooses countries, **Then**
   the control shows how many it holds and ticks each chosen country in its list, as every
   counted control does, and each option in the list shows its flag.
6. **Given** a country widget with `placeholder`, `clear_button` or `max_items`, **When** the
   control is started, **Then** each setting takes effect exactly as it does on `TomSelect` or
   `TomSelectMultiple`, and a value that cannot be right is refused with the same error.
7. **Given** a single country field that holds no value, **When** the control is started,
   **Then** it holds no country, and its placeholder shows when one is stated.
8. **Given** a form drawn with a value already chosen, or posted back in error, **When** the
   control is started, **Then** it holds that country, shown with its flag.
9. **Given** the size, colour or variant stated for the form or the field, or a field in error or
   disabled, **When** the form is drawn, **Then** the select carries the same classes and
   attributes a `TomSelect` select on any other choice field carries.
10. **Given** a country widget in a formset, a modal or content htmx adds to the page later,
    **When** its select reaches the page, **Then** its control starts with flags, as every Tom
    Select widget of the pack's does.
11. **Given** a project that installs django-countries and not django-tomselect, **When** it uses
    `CountrySelect` and `CountrySelectMultiple`, **Then** both work, and nothing of the package
    needs django-tomselect for them.

---

### User Story 2 - A developer routes a country autocomplete and builds a fetched country field (Priority: P2)

A developer whose project uses django-tomselect, and who would rather the page did not carry the
whole list of countries, routes `CountryAutocomplete` at a URL of their choosing and builds a
django-tomselect field with `country_config(<URL name>, ...)`. A person filling in the form opens
the control and the countries arrive from the view as they type, each drawn with its flag ahead of
its name, in the list and in each chosen value. Every setting `TomSelectConfig` takes can be given
to `country_config`.

**Why this priority**: It serves the projects that already fetch their options through
django-tomselect, and pages where the list of countries should not be written out with every form.
It builds on nothing in User Story 1 but the flag drawn inside the option.

**Independent Test**: Route `CountryAutocomplete`, build a `TomSelectChoiceField` and a
`TomSelectMultipleChoiceField` with `country_config`, request the view with a search, then open
each control in a browser and choose a country.

**Acceptance Scenarios**:

1. **Given** `CountryAutocomplete` routed at a URL, **When** it is requested with no search,
   **Then** it answers with the countries django-countries lists, in its order, each result
   holding the country's code, its name and the address of its flag, a page at a time.
2. **Given** that view, **When** it is requested with a search, **Then** it answers with the
   countries whose name or code holds the search, ignoring case.
3. **Given** a django-tomselect field built with `country_config`, **When** the form is drawn,
   **Then** the page holds no country but the one already chosen, and the control is drawn by the
   pack's template for django-tomselect.
4. **Given** that form in a browser, **When** a person opens the control and types, **Then** the
   control fetches the countries from the view and shows each option with its flag ahead of its
   name, and the page has no script error.
5. **Given** a person chooses one country, or several in a multiple field, **When** the form is
   posted, **Then** each chosen value has been shown with its flag ahead of its name, and the
   field cleans to the countries' codes.
6. **Given** other settings given to `country_config`, such as a placeholder, a clear button or a
   remove button, **When** the control is started, **Then** each takes effect as it does through
   `TomSelectConfig`.
7. **Given** a project without django-tomselect, **When** it imports the country widgets of User
   Story 1, **Then** the import succeeds, and only `CountryAutocomplete` and `country_config` are
   unavailable.

---

### User Story 3 - A developer lists some countries first (Priority: P3)

A developer configures django-countries' `first` and `first_break`, either on a `Countries`
subclass given to the field or with django-countries' settings for every field. Both kinds of
control then list those countries at the top and the rest under a heading carrying the break's
text. Without `first_break` the countries first are at the top with no heading. For the fetched
control, the developer gives `CountryAutocomplete.as_view()` the `Countries` to answer from, or
relies on the settings.

**Why this priority**: It is a refinement of the two controls above, for forms where most people
pick one of a few countries. django-countries offers the setting and the stock select honours it,
so a control that ignored it would be a step back for projects that use it.

**Independent Test**: Give a `CountryField` a `Countries` subclass with three countries first and
a break, draw it with `CountrySelect` and with `CountrySelectMultiple`, route
`CountryAutocomplete` with the same subclass, and open each control.

**Acceptance Scenarios**:

1. **Given** a field whose countries put three first with a break, **When** it is drawn with
   `CountrySelect` or `CountrySelectMultiple`, **Then** the three countries are options outside
   every group, ahead of all others, and every other country is in one option group whose heading
   is the break's text.
2. **Given** that field with no `first_break`, **When** it is drawn with a country widget,
   **Then** the countries first are listed at the top and no option group is written.
3. **Given** a field whose countries set `first_repeat`, **When** it is drawn with a country
   widget, **Then** each country appears once, among the countries first.
4. **Given** the countries first configured with django-countries' settings rather than a
   subclass, **When** a country field is drawn with a country widget, **Then** it is grouped
   exactly as in scenario 1.
5. **Given** a single country field with a break that holds no value, **When** its control is
   started, **Then** it holds no country, and the break is a heading, never a value a person can
   choose.
6. **Given** a person searches such a control, **When** the search matches countries both first
   and among the rest, **Then** the matches among the countries first are listed above the
   heading and the others under it.
7. **Given** `CountryAutocomplete` given a `Countries` with countries first and a break, **When**
   it is requested, **Then** the countries first come first in its results and every other result
   carries the break's text as its option group, so the pack's django-tomselect template lists
   them under that heading.
8. **Given** the same field drawn by django-countries' own select, **When** the form is drawn,
   **Then** it is drawn exactly as before this feature, break included.

---

### Edge Cases

- **The empty choice.** django-countries adds an empty choice to a field that may be left blank,
  and with `first_break` the break itself is the empty choice (checked, `research.md`). Tom Select
  offers no option with an empty value, so the empty choice is never listed as a country and
  carries no flag. A single control that holds no value starts empty in both cases (D6).
- **The stock select and the flag widget.** A field given no widget, or django-countries'
  `CountrySelectWidget`, is drawn as the pack draws it today. Nothing in this feature changes it.
- **django-countries' flag address.** The flag is the image django-countries gives each country,
  so a project that changes where its flags come from gets its own images in the controls.
- **Translated names.** The controls show each country's name as django-countries gives it in the
  active language, and the autocomplete answers in the language of the request. A search matches
  the name in that language.
- **Escaping.** A country's name and its flag address reach the option through Tom Select's
  escaping, never written into markup unescaped.
- **django-tomselect's own option templates.** django-tomselect 2026.6.2, the latest release
  (checked, `research.md`), writes a template given through its `render` attribute into the page
  script unquoted, which stops the control. `country_config` must give its template in a form
  that release reads without error, and keep working when the defect is fixed.
- **A field whose countries are restricted.** A `Countries` subclass with `only` lists only those
  countries. The widgets and the autocomplete list what django-countries lists and nothing more.
- **Several controls on one page.** Each control keeps its own options and settings, and the
  script acts once however many forms carry it.

### Out of scope

- Grouping by continent or region. django-countries has no such data and no other source is
  added.
- A heading above the countries first.
- Changing how the pack draws django-countries' stock select or its `CountrySelectWidget`.
- A stylesheet. The controls are the pack's Tom Select controls, drawn by the existing stylesheet.
- A Tom Select setting or plugin the pack's widgets do not already carry.
- Choosing a URL for the autocomplete. The host project routes it.
- The demo project's documentation theme and its user model, which are separate work.

## Requirements *(mandatory)*

### Functional Requirements

**Countries that come with the form (User Story 1)**

- **FR-001**: The package MUST offer `CountrySelect`, a widget for a single django-countries
  field, and `CountrySelectMultiple`, one for a multiple field, each drawing the pack's Tom Select
  control.
- **FR-002**: `CountrySelect` MUST take every setting `TomSelect` takes, and
  `CountrySelectMultiple` every setting `TomSelectMultiple` takes, with the same checks and the
  same errors.
- **FR-003**: Each option of a country widget that holds a country MUST carry the address of that
  country's flag as django-countries gives it. The empty choice MUST carry none.
- **FR-004**: The control a country widget starts MUST show each option and each chosen value as
  the country's flag image followed by its name.
- **FR-005**: The pack's Tom Select script MUST draw an option and a chosen value from a template
  the widget writes in its settings, filling each named value of the option from the option's
  data, escaped. A select that states no template MUST be drawn as it is today.
- **FR-006**: A country widget MUST be drawn with the classes, attributes, label, help text and
  error ties a `TomSelect` select carries on any other choice field, and MUST clean to the values
  django-countries' field cleans to.
- **FR-007**: A single country control whose field holds no value MUST start holding no country.
- **FR-008**: The country widgets MUST need django-countries and nothing else beyond what the
  pack's Tom Select widgets need. No other module of the package MAY import django-countries.

**Countries fetched as a person types (User Story 2)**

- **FR-009**: The package MUST offer `CountryAutocomplete`, a django-tomselect autocomplete view
  that the host project routes, answering with each country's code, its name and its flag
  address, a page at a time.
- **FR-010**: `CountryAutocomplete` MUST match a search against a country's name and its code,
  ignoring case, and MUST answer from django-countries' list by default.
- **FR-011**: The package MUST offer `country_config`, which takes the name of the URL serving
  `CountryAutocomplete` and any setting of `TomSelectConfig`, and returns a configuration whose
  control fetches from that view and shows each option and chosen value as the country's flag
  followed by its name.
- **FR-012**: A control configured with `country_config` MUST start and draw its options with no
  script error under django-tomselect 2026.6.2, and the code that works round that release MUST
  name it.
- **FR-013**: `CountryAutocomplete` and `country_config` MUST be available only where
  django-tomselect is installed, and their absence MUST NOT stop the country widgets of FR-001
  from being imported.
- **FR-014**: CONSTITUTION.md Article XII MUST be amended to allow an autocomplete view for a
  supported package, routed by the host project, the package still shipping no URL.

**Countries first (User Story 3)**

- **FR-015**: Where a field's countries name some first and set a break, the country widgets MUST
  list those countries ahead of all others, outside every option group, and every other country
  in one option group headed by the break's text.
- **FR-016**: Where the countries first have no break, the country widgets MUST list them at the
  top and write no option group.
- **FR-017**: The country widgets and `CountryAutocomplete` MUST list each country once, among the
  countries first where it is one of them, whatever `first_repeat` says.
- **FR-018**: The break MUST never be a value a person can choose in a country control.
- **FR-019**: `CountryAutocomplete` MUST accept the `Countries` to answer from as a setting of the
  view, MUST put the countries first ahead of the rest in its results, and MUST give every other
  result the break's text as its option group.
- **FR-020**: django-countries' settings for the countries first MUST take effect on the country
  widgets and on `CountryAutocomplete` with no setting of the package's own.

**Documentation and demo (every story)**

- **FR-021**: The documentation page for django-countries MUST describe the stock select, the
  country widgets, the countries first and the fetched control, each with a live example, and say
  that `first_repeat` has no effect on the country controls.
- **FR-022**: The README's section on django-countries, its template list where it changes, and
  the CHANGELOG MUST describe the new widgets, the view and `country_config`.
- **FR-023**: The demo MUST show the stock select, each country widget and the fetched control on
  the screens the prototype has, with each field labelled by the field and widget it uses, and
  MUST no longer show django-countries' flag beside the select.

### Requirement coverage

| Story | Requirements |
|---|---|
| User Story 1 | FR-001 to FR-008, FR-021 to FR-023 |
| User Story 2 | FR-009 to FR-014, FR-021 to FR-023 |
| User Story 3 | FR-015 to FR-020, FR-021 to FR-023 |

### Key Entities

- **Country widget**: `CountrySelect` or `CountrySelectMultiple`. A Tom Select widget of the
  package whose options carry their country's flag and whose control draws it.
- **Country autocomplete**: `CountryAutocomplete`, a django-tomselect view answering with
  countries, routed by the host project.
- **Countries first**: the countries a django-countries `Countries` names in `first`, and the
  break's text in `first_break` that heads the rest.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer gives a django-countries field a searchable control with flags by naming
  one widget, with no template, script or stylesheet of their own.
- **SC-002**: A developer gives a django-tomselect field fetched countries with flags by routing
  one view and calling one function, with no template of their own.
- **SC-003**: A person finds a country in any of the controls by typing part of its name, in a
  single or a multiple field.
- **SC-004**: A field configured with countries first lists them at the top in every country
  control, with the rest under the break's heading where a break is set.
- **SC-005**: Every control on the demo's three country screens starts with no script error under
  the django-tomselect release the package is tested against.
- **SC-006**: The demo's three country screens on the default branch match the prototype's, side
  by side, at a phone's width and a desktop's.
- **SC-007**: No stylesheet is added, and the stock select of a django-countries field is drawn
  exactly as before.

## Assumptions

- The host project lists `django_countries` in `INSTALLED_APPS`, so its flag images are served as
  static files, as the README already asks.
- The host project's Tailwind build scans the whole installed package, as the README's
  installation section asks, so the utilities in the flag row are generated.
- The flag image needs no text of its own, since the country's name is beside it.
- django-countries 9.1.0 and django-tomselect 2026.6.2 are the releases tested against.
