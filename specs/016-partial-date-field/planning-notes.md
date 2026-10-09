# Planning notes: Partial date field

Suggestions from the maintainer on how this might be built, in his words. Research answers each
one by name: adopted or not adopted, and why.

## 1. A regex or pattern IMask widget

"I propose two separate widgets. a) a regex or pattern IMask widget"

"A user should not be able to enter a month over 12 in the IMask widget. Allowed days in the
IMask should change based on month."

## 2. A multi-widget on a daisyUI join

"b) a multiwidget that uses a daisyui join and asks for year, month, day separately."

"The number of days in the day widget should react to the selection of both the month and year
field."

## 3. The partial date package

"This does not necessarily have to 'support' the partial_date package but it must validate and
return an ISO date partial string."

## 4. One field with a swappable widget

"On the python side, I would prefer if we use a single field with a swappable widget for a more
consistent experience for users that might wish to switch."

## 5. A select for the year

"the user should be able to designate a select box for the year field too."
